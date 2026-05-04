#!/usr/bin/env python3
"""
FastAPI server for Raspberry Pi 5
Now supports direct frontend access with JWT authentication.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import lgpio
import uvicorn
import logging
import subprocess
import threading
import time
from typing import Optional, Union

from config import settings
from auth import verify_jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pi Control API", description="Control Pi via HTTP API")

# CORS middleware for direct frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GPIO configuration 
LED_LAMP_PIN = 13  # GPIO13 - LED Lamp (existing LED)
PSU_PIN = 21  # GPIO21 - PSU Green
LED_FLR_PIN = 12  # GPIO12 - LED FLR (gray cable)
SWITCH_SENSOR_PIN = 17  # GPIO17 - Switch sensor
FRONT_PANEL_LED_PIN = 20  # GPIO20 - Front Panel LED

# Motor GPIO assignments
# DM542 common-ground wiring:
# PUL-/DIR- -> Pi GND, PUL+ -> step GPIO, DIR+ -> direction GPIO.
# ENA is disconnected, so no enable pin is driven.
MOTOR_AXES = {
    "x": {"step": 5, "direction": 27},
    "y": {"step": 6, "direction": 19},
    "z": {"step": 26, "direction": 22},
}

STEP_PULSE_SECONDS = 0.005
STEP_LOW_SECONDS = 0.005
DIRECTION_SETTLE_SECONDS = 0.02
DIRECTION_POSITIVE = 1
DIRECTION_NEGATIVE = 0

h = None
led_lamp_isOn = False
psu_isOn = False
led_flr_isOn = False
gpio_initialized = False
drawer_is_open = False
is_scanning = False
axis_positions = {"x": 0, "y": 0, "z": 0}
axis_is_moving = {"x": False, "y": False, "z": False}
axis_stop_events = {axis: threading.Event() for axis in MOTOR_AXES}
axis_motion_locks = {axis: threading.Lock() for axis in MOTOR_AXES}

# Pydantic models
class LEDState(BaseModel):
    is_on: bool
    pin: int

class ToggleResponse(BaseModel):
    success: bool
    is_on: bool
    pin: int
    message: str

class HealthCheck(BaseModel):
    healthy: bool

class ClosetState(BaseModel):
    is_open: bool
    pin: int
    label: str = "closet"

class ShutdownResponse(BaseModel):
    success: bool
    message: str

class StagePosition(BaseModel):
    x: int = 0
    y: int
    z: int = 0
    is_moving: bool

class StageMoveRequest(BaseModel):
    x: Optional[Union[int, float]] = None
    y: Optional[Union[int, float]] = None
    z: Optional[Union[int, float]] = None
    relative: bool = False

class StageMoveResponse(BaseModel):
    success: bool
    status: str
    target_position: StagePosition
    message: str

class StageCommandResponse(BaseModel):
    success: bool
    status: str
    position: StagePosition
    message: str


def current_stage_position() -> StagePosition:
    return StagePosition(
        x=axis_positions["x"],
        y=axis_positions["y"],
        z=axis_positions["z"],
        is_moving=any(axis_is_moving.values()),
    )


def run_axis_move(axis: str, target_position: int):
    """Pulse one DM542 axis until its tracked position reaches target_position."""
    pins = MOTOR_AXES[axis]

    try:
        delta = target_position - axis_positions[axis]
        if delta == 0:
            return

        direction = DIRECTION_POSITIVE if delta > 0 else DIRECTION_NEGATIVE
        step_increment = 1 if delta > 0 else -1
        lgpio.gpio_write(h, pins["direction"], direction)
        time.sleep(DIRECTION_SETTLE_SECONDS)

        for _ in range(abs(delta)):
            if axis_stop_events[axis].is_set():
                logger.warning(
                    "%s movement stopped at %s steps",
                    axis.upper(),
                    axis_positions[axis],
                )
                break

            lgpio.gpio_write(h, pins["step"], 1)
            time.sleep(STEP_PULSE_SECONDS)
            lgpio.gpio_write(h, pins["step"], 0)
            time.sleep(STEP_LOW_SECONDS)
            axis_positions[axis] += step_increment
    except Exception as e:
        logger.error("%s movement failed: %s", axis.upper(), e)
    finally:
        lgpio.gpio_write(h, pins["step"], 0)
        with axis_motion_locks[axis]:
            axis_is_moving[axis] = False
            axis_stop_events[axis].clear()


def start_axis_move(axis: str, target_position: int):
    """Start one non-blocking axis move."""
    if h is None:
        raise HTTPException(status_code=503, detail="GPIO is not initialized")

    with axis_motion_locks[axis]:
        if axis_is_moving[axis]:
            raise HTTPException(
                status_code=409,
                detail=f"{axis.upper()} axis is already moving",
            )
        axis_stop_events[axis].clear()
        axis_is_moving[axis] = True

    motion_thread = threading.Thread(
        target=run_axis_move,
        args=(axis, target_position),
        daemon=True,
    )
    motion_thread.start()


def monitor_switch_sensor():
    """Continuously monitor and print switch sensor state"""
    global h, drawer_is_open
    last_state = None
    while True:
        try:
            if h is not None:
                switch_state = lgpio.gpio_read(h, SWITCH_SENSOR_PIN)
                # switch_state == 0 means OPEN (based on existing code)
                drawer_is_open = (switch_state == 0)
                switch_status = "OPEN" if drawer_is_open else "CLOSED"
                
                # Only print when state changes
                if switch_status != last_state:
                    print(f"Drawer: {switch_status}")
                    last_state = switch_status
            time.sleep(0.1)  # Check more frequently
        except Exception as e:
            print(f"Error reading switch sensor: {e}")
            time.sleep(1)

def led_control_loop():
    """Control the front panel LED based on system state"""
    global h, drawer_is_open, is_scanning
    
    while True:
        if h is None:
            time.sleep(1)
            continue
            
        try:
            if drawer_is_open:
                # Drawer Open: Blink very fast continuously
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 1)
                time.sleep(0.1)
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)
                time.sleep(0.1)
            elif is_scanning:
                # Scanning Active: Blink slowly
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 1)
                time.sleep(0.5)
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)
                time.sleep(0.5)
            else:
                # Idle: Off for a second then 2 very fast blinks
                
                # 1. OFF for 1s (checking state frequently)
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)
                interrupted = False
                for _ in range(20): # 20 * 0.1s = 2s
                    if drawer_is_open or is_scanning: 
                        interrupted = True
                        break
                    time.sleep(0.1)
                
                if interrupted: continue

                # 2. Blink 1
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 1)
                time.sleep(0.1)
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)
                time.sleep(0.1)
                
                if drawer_is_open or is_scanning: continue

                # 3. Blink 2
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 1)
                time.sleep(0.1)
                lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error in LED loop: {e}")
            time.sleep(1)

def setup_gpio():
    """Initialize GPIO settings"""
    global h, led_lamp_isOn, psu_isOn, led_flr_isOn
    try:
        h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(h, LED_LAMP_PIN, 0)
        lgpio.gpio_claim_output(h, PSU_PIN, 0)
        lgpio.gpio_claim_output(h, LED_FLR_PIN, 0)
        lgpio.gpio_claim_output(h, FRONT_PANEL_LED_PIN, 0)
        for pins in MOTOR_AXES.values():
            lgpio.gpio_claim_output(h, pins["step"], 0)
            lgpio.gpio_claim_output(h, pins["direction"], 0)
        # Configure switch sensor with pull-up resistor
        lgpio.gpio_claim_input(h, SWITCH_SENSOR_PIN, lgpio.SET_PULL_UP)
        
        # Ensure Lamps/flr are OFF at startup (inverted logic: 1=off)
        # PSU use normal logic (1=on, 0=off)
        lgpio.gpio_write(h, LED_LAMP_PIN, 1)
        lgpio.gpio_write(h, LED_FLR_PIN, 1)
        lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)  # Front Panel LED starts off
        lgpio.gpio_write(h, PSU_PIN, 1)
        led_lamp_isOn = False
        led_flr_isOn = False
        psu_isOn = True
        
        axis_pin_summary = ", ".join(
            f"{axis.upper()}_STEP={pins['step']}, {axis.upper()}_DIR={pins['direction']}"
            for axis, pins in MOTOR_AXES.items()
        )
        print(f"GPIO pins initialized: LED_LAMP={LED_LAMP_PIN}({led_lamp_isOn}), PSU={PSU_PIN}({psu_isOn}), LED_FLR={LED_FLR_PIN}({led_flr_isOn}), {axis_pin_summary}")
    except Exception as e:
        print(f"Error setting up GPIO: {e}")
        raise


def cleanup_gpio():
    """Clean up GPIO settings"""
    global h, gpio_initialized
    if h is not None:
        try:
            lgpio.gpio_write(h, LED_LAMP_PIN, 1)
            lgpio.gpio_write(h, PSU_PIN, 0)
            lgpio.gpio_write(h, LED_FLR_PIN, 1)
            lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)
            for pins in MOTOR_AXES.values():
                lgpio.gpio_write(h, pins["step"], 0)
            lgpio.gpiochip_close(h)
            gpio_initialized = False
            logger.info("GPIO cleanup completed successfully")
        except lgpio.error as e:
            logger.error(f"lgpio error during cleanup: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize GPIO on server startup"""
    setup_gpio()
    # Start threads
    monitor_thread = threading.Thread(target=monitor_switch_sensor, daemon=True)
    monitor_thread.start()
    # Start LED control loop
    led_thread = threading.Thread(target=led_control_loop, daemon=True)
    led_thread.start()
    print("API started")
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up GPIO on server shutdown"""
    cleanup_gpio()


@app.get("/")
async def root():
    """Root Pi endpoint"""
    return {
        "message": "Pi Control API",
        "endpoints": {
            "GET /health": "Health check endpoint",
            "GET /led-lamp/state": "Get current LED Lamp state",
            "POST /led-lamp/toggle": "Toggle LED Lamp on/off",
            "GET /psu/state": "Get current PSU state",
            "POST /psu/toggle": "Toggle PSU on/off",
            "GET /led-flr/state": "Get current FLR LED state",
            "POST /led-flr/toggle": "Toggle FLR LED on/off",
            "POST /system/shutdown": "Shutdown the Raspberry Pi gracefully",
            "POST /scan/start": "Start scanning mode",
            "POST /scan/stop": "Stop scanning mode",
            "GET /closet/state": "Get current closet open/closed state",
            "GET /position": "Get current stage position",
            "POST /move": "Move X/Y/Z axes",
            "POST /home": "Reset tracked X/Y/Z position to zero",
            "POST /stop": "Stop stage movement"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify API and GPIO status"""
    return HealthCheck(healthy=True)

@app.get("/closet/state", response_model=ClosetState)
async def get_closet_state(user: dict = Depends(verify_jwt)):
    """Get the current closet switch state. Protected endpoint."""
    global drawer_is_open
    try:
        switch_state = lgpio.gpio_read(h, SWITCH_SENSOR_PIN)
        drawer_is_open = (switch_state == 0)
    except Exception:
        pass

    return ClosetState(is_open=drawer_is_open, pin=SWITCH_SENSOR_PIN)


@app.get("/position", response_model=StagePosition)
async def get_stage_position():
    """Return tracked stage position."""
    return current_stage_position()


@app.post("/move", response_model=StageMoveResponse)
async def move_stage(request: StageMoveRequest):
    """Move one or more axes."""
    requested_moves = {
        "x": request.x,
        "y": request.y,
        "z": request.z,
    }
    targets = {}

    for axis, requested_position in requested_moves.items():
        if requested_position is None:
            continue

        requested_steps = int(round(requested_position))
        if request.relative and requested_steps == 0:
            continue

        targets[axis] = (
            axis_positions[axis] + requested_steps
            if request.relative
            else requested_steps
        )

    if not targets:
        return StageMoveResponse(
            success=True,
            status="idle",
            target_position=current_stage_position(),
            message="No movement requested",
        )

    for axis, target_position in targets.items():
        start_axis_move(axis, target_position)

    target_stage_position = StagePosition(
        x=targets.get("x", axis_positions["x"]),
        y=targets.get("y", axis_positions["y"]),
        z=targets.get("z", axis_positions["z"]),
        is_moving=True,
    )

    return StageMoveResponse(
        success=True,
        status="moving",
        target_position=target_stage_position,
        message="Stage movement started",
    )


@app.post("/home", response_model=StageCommandResponse)
async def home_stage():
    """Reset tracked position to zero. No limit-switch homing is implemented yet."""

    if any(axis_is_moving.values()):
        raise HTTPException(status_code=409, detail="Stop movement before homing")

    for axis in axis_positions:
        axis_positions[axis] = 0

    return StageCommandResponse(
        success=True,
        status="homed",
        position=current_stage_position(),
        message="Stage position reset to zero",
    )


@app.post("/stop", response_model=StageCommandResponse)
async def stop_stage():
    """Request an immediate stop for active stage movement."""
    for stop_event in axis_stop_events.values():
        stop_event.set()

    return StageCommandResponse(
        success=True,
        status="stopping" if any(axis_is_moving.values()) else "idle",
        position=current_stage_position(),
        message="Stage stop requested",
    )


@app.get("/led-lamp/state", response_model=LEDState)
async def get_led_lamp_state(user: dict = Depends(verify_jwt)):
    """Get the current state of the LED Lamp. Protected endpoint."""
    global led_lamp_isOn
    try:
        current_state = lgpio.gpio_read(h, LED_LAMP_PIN)
        led_lamp_isOn = (current_state == 0)  # Inverted logic
        return LEDState(is_on=led_lamp_isOn, pin=LED_LAMP_PIN)
    except Exception as e:
        return LEDState(is_on=led_lamp_isOn, pin=LED_LAMP_PIN)


@app.post("/led-lamp/toggle", response_model=ToggleResponse)
async def toggle_led_lamp(user: dict = Depends(verify_jwt)):
    """Toggle the LED Lamp on or off. Protected endpoint."""
    global led_lamp_isOn
    
    try:
        current_state = lgpio.gpio_read(h, LED_LAMP_PIN)
        led_lamp_isOn = (current_state == 0)  # Inverted logic
        
        # Toggle the state
        led_lamp_isOn = not led_lamp_isOn
        
        # Write to GPIO
        lgpio.gpio_write(h, LED_LAMP_PIN, 0 if led_lamp_isOn else 1)
        
        return ToggleResponse(
            success=True,
            is_on=led_lamp_isOn,
            pin=LED_LAMP_PIN,
            message=f"LED Lamp turned {'ON' if led_lamp_isOn else 'OFF'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle LED Lamp: {str(e)}")


@app.get("/psu/state", response_model=LEDState)
async def get_psu_state(user: dict = Depends(verify_jwt)):
    """Get the current state of the PSU. Protected endpoint."""
    global psu_isOn
    try:
        current_state = lgpio.gpio_read(h, PSU_PIN)
        psu_isOn = (current_state == 1)
        return LEDState(is_on=psu_isOn, pin=PSU_PIN)
    except Exception as e:
        return LEDState(is_on=psu_isOn, pin=PSU_PIN)


@app.post("/psu/toggle", response_model=ToggleResponse)
async def toggle_psu(user: dict = Depends(verify_jwt)):
    """Toggle the PSU on or off. Protected endpoint."""
    global psu_isOn
    
    try:
        current_state = lgpio.gpio_read(h, PSU_PIN)
        psu_isOn = (current_state == 1)
        psu_isOn = not psu_isOn
        lgpio.gpio_write(h, PSU_PIN, 1 if psu_isOn else 0)
        
        return ToggleResponse(
            success=True,
            is_on=psu_isOn,
            pin=PSU_PIN,
            message=f"PSU turned {'ON' if psu_isOn else 'OFF'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle PSU: {str(e)}")


@app.get("/led-flr/state", response_model=LEDState)
async def get_led_flr_state(user: dict = Depends(verify_jwt)):
    """Get the current state of the FLR LED. Protected endpoint."""
    global led_flr_isOn
    try:
        current_state = lgpio.gpio_read(h, LED_FLR_PIN)
        led_flr_isOn = (current_state == 0)
        return LEDState(is_on=led_flr_isOn, pin=LED_FLR_PIN)
    except Exception as e:
        return LEDState(is_on=led_flr_isOn, pin=LED_FLR_PIN)


@app.post("/led-flr/toggle", response_model=ToggleResponse)
async def toggle_led_flr(user: dict = Depends(verify_jwt)):
    """Toggle the FLR LED on or off. Protected endpoint."""
    global led_flr_isOn
    
    try:
        current_state = lgpio.gpio_read(h, LED_FLR_PIN)
        led_flr_isOn = (current_state == 0)
        led_flr_isOn = not led_flr_isOn
        lgpio.gpio_write(h, LED_FLR_PIN, 0 if led_flr_isOn else 1)
        
        return ToggleResponse(
            success=True,
            is_on=led_flr_isOn,
            pin=LED_FLR_PIN,
            message=f"FLR LED turned {'ON' if led_flr_isOn else 'OFF'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle FLR LED: {str(e)}")


@app.post("/system/shutdown", response_model=ShutdownResponse)
async def shutdown_system(user: dict = Depends(verify_jwt)):
    """Gracefully shutdown the Raspberry Pi. Protected endpoint."""
    try:
        logger.info("Shutdown command received via API")
        cleanup_gpio()
        result = subprocess.run(["sudo", "shutdown", "-h", "now"], capture_output=True, text=True)
        logger.info(f"Shutdown command executed: stdout={result.stdout}, stderr={result.stderr}")
        return ShutdownResponse(
            success=True,
            message="System shutdown initiated. Raspberry Pi will power off shortly."
        )
    except Exception as e:
        logger.error(f"Failed to initiate shutdown: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to shutdown system: {str(e)}")


@app.post("/scan/start", response_model=ToggleResponse)
async def start_scan(user: dict = Depends(verify_jwt)):
    """Start scanning mode. Protected endpoint."""
    global is_scanning
    is_scanning = True
    return ToggleResponse(
        success=True,
        is_on=True,
        pin=0,
        message="Scanning started"
    )

@app.post("/scan/stop", response_model=ToggleResponse)
async def stop_scan(user: dict = Depends(verify_jwt)):
    """Stop scanning mode. Protected endpoint."""
    global is_scanning
    is_scanning = False
    return ToggleResponse(
        success=True,
        is_on=False,
        pin=0,
        message="Scanning stopped"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
