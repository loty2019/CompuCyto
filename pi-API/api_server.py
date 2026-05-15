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
import asyncio
import logging
import subprocess
import threading
import time
from typing import Dict, List, Optional, Union

try:
    import adafruit_dht
    import board
    dht11_import_error = None
except ImportError as e:
    adafruit_dht = None
    board = None
    dht11_import_error = e

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
DHT11_PIN = settings.dht11_pin  # GPIO pin number for DHT11 data wire
DHT11_READ_ATTEMPTS = max(settings.dht11_read_attempts, 1)
DHT11_RETRY_SECONDS = max(settings.dht11_retry_seconds, 1.0)
DHT11_MIN_READ_SECONDS = 1.0

# Motor GPIO assignments
# DM542 common-ground wiring:
# PUL-/DIR- -> Pi GND, PUL+ -> step GPIO, DIR+ -> direction GPIO.
# ENA is disconnected, so no enable pin is driven.
MOTOR_AXES = {
    "x": {"step": 5, "direction": 27},
    "y": {"step": 6, "direction": 19},
    "z": {"step": 26, "direction": 22},
}

LIMIT_SENSOR_PINS = {
    "x": settings.limit_x_pin,
    "y": settings.limit_y_pin,
    "z": settings.limit_z_pin,
}

STEP_PULSE_SECONDS = settings.step_pulse_seconds
STEP_LOW_SECONDS = settings.step_low_seconds
DIRECTION_SETTLE_SECONDS = settings.direction_settle_seconds
DIRECTION_POSITIVE = 1
DIRECTION_NEGATIVE = 0
LIMIT_SENSOR_ACTIVE_STATE = 1 if settings.limit_sensor_active_state else 0
LIMIT_POLL_SECONDS = max(settings.limit_poll_seconds, 0.0005)
LIMIT_DEBOUNCE_SECONDS = max(settings.limit_debounce_seconds, LIMIT_POLL_SECONDS)
HOMING_FAST_STEP_SECONDS = settings.homing_fast_step_seconds
HOMING_SLOW_STEP_SECONDS = settings.homing_slow_step_seconds
HOMING_MAX_STEPS = settings.homing_max_steps
HOMING_BACKOFF_STEPS = settings.homing_backoff_steps
AXIS_MAX_POSITIONS = {
    "x": settings.max_x_position,
    "y": settings.max_y_position,
    "z": settings.max_z_position,
}

h = None
led_lamp_isOn = False
psu_isOn = False
led_flr_isOn = False
gpio_initialized = False
drawer_is_open = False
is_scanning = False
axis_positions = {"x": 0, "y": 0, "z": 0}
axis_is_moving = {"x": False, "y": False, "z": False}
axis_is_homing = {"x": False, "y": False, "z": False}
axis_is_homed = {"x": False, "y": False, "z": False}
axis_move_direction = {"x": 0, "y": 0, "z": 0}
axis_stop_events = {axis: threading.Event() for axis in MOTOR_AXES}
axis_motion_locks = {axis: threading.Lock() for axis in MOTOR_AXES}
limit_sensor_states = {axis: False for axis in MOTOR_AXES}
limit_sensor_raw_states = {axis: None for axis in MOTOR_AXES}
limit_sensor_changed_at = {axis: time.monotonic() for axis in MOTOR_AXES}
limit_sensor_pending_states = {axis: False for axis in MOTOR_AXES}
limit_sensor_pending_since = {axis: time.monotonic() for axis in MOTOR_AXES}
limit_sensor_lock = threading.Lock()
dht11_device = None
dht11_lock = threading.Lock()
dht11_last_read_at = 0.0
dht11_last_reading = None

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

class EnvironmentReading(BaseModel):
    temperature_c: Optional[float]
    temperature_f: Optional[float]
    humidity: Optional[float]
    pin: int
    sensor: str = "DHT11"
    healthy: bool
    message: str

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

class LimitSensorState(BaseModel):
    axis: str
    pin: int
    active: bool
    raw_state: Optional[int]
    homed: bool

class StageMoveResponse(BaseModel):
    success: bool
    status: str
    target_position: StagePosition
    limit_sensors: Dict[str, LimitSensorState]
    message: str

class StageCommandResponse(BaseModel):
    success: bool
    status: str
    position: StagePosition
    limit_sensors: Dict[str, LimitSensorState]
    message: str


def current_stage_position() -> StagePosition:
    return StagePosition(
        x=axis_positions["x"],
        y=axis_positions["y"],
        z=axis_positions["z"],
        is_moving=any(axis_is_moving.values()),
    )


def read_limit_sensor(axis: str) -> LimitSensorState:
    """Return the latest cached optical home/limit sensor state."""
    with limit_sensor_lock:
        active = limit_sensor_states[axis]
        raw_state = limit_sensor_raw_states[axis]

    return LimitSensorState(
        axis=axis,
        pin=LIMIT_SENSOR_PINS[axis],
        active=active,
        raw_state=raw_state,
        homed=axis_is_homed[axis],
    )


def read_limit_sensors() -> Dict[str, LimitSensorState]:
    return {axis: read_limit_sensor(axis) for axis in MOTOR_AXES}


def update_limit_sensor_cache(axis: str) -> None:
    """Poll one sensor once and update debounced active/raw state."""
    if h is None:
        return

    try:
        raw_state = lgpio.gpio_read(h, LIMIT_SENSOR_PINS[axis])
        sampled_active = raw_state == LIMIT_SENSOR_ACTIVE_STATE
    except Exception as e:
        logger.error("Failed to read %s limit sensor: %s", axis.upper(), e)
        return

    now = time.monotonic()
    with limit_sensor_lock:
        if sampled_active != limit_sensor_pending_states[axis]:
            limit_sensor_pending_states[axis] = sampled_active
            limit_sensor_pending_since[axis] = now

        if (
            sampled_active != limit_sensor_states[axis]
            and now - limit_sensor_pending_since[axis] >= LIMIT_DEBOUNCE_SECONDS
        ):
            limit_sensor_states[axis] = sampled_active
            limit_sensor_changed_at[axis] = now

        limit_sensor_raw_states[axis] = raw_state


def refresh_limit_sensors() -> None:
    for axis in MOTOR_AXES:
        update_limit_sensor_cache(axis)


def limit_active(axis: str) -> bool:
    with limit_sensor_lock:
        return limit_sensor_states[axis]


def limit_stably_active(axis: str) -> bool:
    """Use the cached debounced monitor state; no GPIO reads or sleeps in the motion path."""
    with limit_sensor_lock:
        return limit_sensor_states[axis]


def request_stage_stop():
    """Ask every active axis thread to stop and drop step pins low."""
    for stop_event in axis_stop_events.values():
        stop_event.set()

    if h is not None:
        for pins in MOTOR_AXES.values():
            try:
                lgpio.gpio_write(h, pins["step"], 0)
            except Exception as e:
                logger.warning("Failed to drop step pin during stop: %s", e)


def set_axis_direction(axis: str, direction: int) -> None:
    pins = MOTOR_AXES[axis]
    axis_move_direction[axis] = 1 if direction == DIRECTION_POSITIVE else -1
    lgpio.gpio_write(h, pins["direction"], direction)
    time.sleep(DIRECTION_SETTLE_SECONDS)


def pulse_axis(axis: str, pulse_seconds: float, low_seconds: Optional[float] = None) -> None:
    pins = MOTOR_AXES[axis]
    lgpio.gpio_write(h, pins["step"], 1)
    time.sleep(pulse_seconds)
    lgpio.gpio_write(h, pins["step"], 0)
    time.sleep(low_seconds if low_seconds is not None else pulse_seconds)


def setup_dht11():
    """Initialize the DHT11 temperature/humidity sensor if its library is present."""
    global dht11_device

    if adafruit_dht is None or board is None:
        logger.warning(
            "DHT11 support unavailable: install adafruit-circuitpython-dht (%s)",
            dht11_import_error,
        )
        return

    board_pin_name = f"D{DHT11_PIN}"
    board_pin = getattr(board, board_pin_name, None)
    if board_pin is None:
        logger.warning("DHT11 GPIO%s is not available as board.%s", DHT11_PIN, board_pin_name)
        return

    try:
        dht11_device = adafruit_dht.DHT11(board_pin, use_pulseio=False)
        logger.info("DHT11 initialized on GPIO%s (BCM numbering, physical header pin 18)", DHT11_PIN)
    except Exception as e:
        dht11_device = None
        logger.error("Failed to initialize DHT11 on GPIO%s: %s", DHT11_PIN, e)


def cleanup_dht11():
    """Release DHT11 resources."""
    global dht11_device

    if dht11_device is not None:
        try:
            dht11_device.exit()
        except Exception as e:
            logger.warning("DHT11 cleanup failed: %s", e)
        finally:
            dht11_device = None


def read_dht11() -> EnvironmentReading:
    """Read temperature and humidity from the DHT11 sensor."""
    global dht11_last_read_at, dht11_last_reading

    if dht11_device is None:
        return EnvironmentReading(
            temperature_c=None,
            temperature_f=None,
            humidity=None,
            pin=DHT11_PIN,
            healthy=False,
            message="DHT11 is not initialized",
        )

    with dht11_lock:
        now = time.monotonic()
        if dht11_last_reading is not None and now - dht11_last_read_at < DHT11_MIN_READ_SECONDS:
            return dht11_last_reading

        last_error = None
        for attempt in range(1, DHT11_READ_ATTEMPTS + 1):
            try:
                temperature_c = dht11_device.temperature
                humidity = dht11_device.humidity

                if temperature_c is None or humidity is None:
                    last_error = "DHT11 did not return a reading"
                    if attempt < DHT11_READ_ATTEMPTS:
                        time.sleep(DHT11_RETRY_SECONDS)
                    continue

                rounded_temperature_c = round(float(temperature_c), 1)
                dht11_last_reading = EnvironmentReading(
                    temperature_c=rounded_temperature_c,
                    temperature_f=round((rounded_temperature_c * 9 / 5) + 32, 1),
                    humidity=round(float(humidity), 1),
                    pin=DHT11_PIN,
                    healthy=True,
                    message="OK",
                )
                dht11_last_read_at = time.monotonic()
                return dht11_last_reading
            except RuntimeError as e:
                last_error = str(e)
                if attempt < DHT11_READ_ATTEMPTS:
                    time.sleep(DHT11_RETRY_SECONDS)
            except Exception as e:
                logger.error("DHT11 read failed: %s", e)
                dht11_last_reading = EnvironmentReading(
                    temperature_c=None,
                    temperature_f=None,
                    humidity=None,
                    pin=DHT11_PIN,
                    healthy=False,
                    message=f"DHT11 read failed: {e}",
                )
                dht11_last_read_at = time.monotonic()
                return dht11_last_reading

        dht11_last_reading = EnvironmentReading(
            temperature_c=None,
            temperature_f=None,
            humidity=None,
            pin=DHT11_PIN,
            healthy=False,
            message=(
                f"{last_error}. Check DHT11 VCC is 3.3V, GND is Pi GND, "
                f"DATA is BCM GPIO{DHT11_PIN}, and the .env DHT11_PIN value uses BCM numbering."
            ),
        )
        dht11_last_read_at = time.monotonic()
        return dht11_last_reading


@app.get("/environment/diagnostics", response_model=EnvironmentReading)
async def get_environment_diagnostics(user: dict = Depends(verify_jwt)):
    """Force a fresh DHT11 read and return the detailed status message."""
    global dht11_last_read_at

    dht11_last_read_at = 0.0
    reading = read_dht11()
    if not reading.healthy:
        logger.warning("DHT11 diagnostic failed on GPIO%s: %s", reading.pin, reading.message)
    return reading


def run_axis_move(axis: str, target_position: int):
    """Pulse one DM542 axis until its tracked position reaches target_position."""
    pins = MOTOR_AXES[axis]

    try:
        delta = target_position - axis_positions[axis]
        if delta == 0:
            return

        direction = DIRECTION_POSITIVE if delta > 0 else DIRECTION_NEGATIVE
        step_increment = 1 if delta > 0 else -1
        set_axis_direction(axis, direction)

        if step_increment < 0 and limit_active(axis):
            axis_positions[axis] = 0
            axis_is_homed[axis] = True
            logger.warning("%s negative move blocked: home sensor is already active", axis.upper())
            return

        for _ in range(abs(delta)):
            if step_increment < 0 and limit_stably_active(axis):
                axis_positions[axis] = 0
                axis_is_homed[axis] = True
                axis_stop_events[axis].set()
                logger.warning("%s movement stopped by home/limit sensor", axis.upper())
                break

            if axis_stop_events[axis].is_set():
                logger.warning(
                    "%s movement stopped at %s steps",
                    axis.upper(),
                    axis_positions[axis],
                )
                break

            pulse_axis(axis, STEP_PULSE_SECONDS, STEP_LOW_SECONDS)
            axis_positions[axis] += step_increment
    except Exception as e:
        logger.error("%s movement failed: %s", axis.upper(), e)
    finally:
        lgpio.gpio_write(h, pins["step"], 0)
        with axis_motion_locks[axis]:
            axis_is_moving[axis] = False
            axis_move_direction[axis] = 0
            axis_stop_events[axis].clear()


def start_axis_move(axis: str, target_position: int):
    """Start one non-blocking axis move."""
    if h is None:
        raise HTTPException(status_code=503, detail="GPIO is not initialized")
    validate_axis_target(axis, target_position)

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


def validate_axis_target(axis: str, target_position: int) -> None:
    """Reject unsafe moves before any axis thread is started."""
    if not axis_is_homed[axis]:
        raise HTTPException(
            status_code=409,
            detail=f"{axis.upper()} axis must be homed before movement",
        )
    if target_position < 0:
        raise HTTPException(
            status_code=400,
            detail=f"{axis.upper()} target cannot be below the home position",
        )
    if target_position > AXIS_MAX_POSITIONS[axis]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{axis.upper()} target {target_position} exceeds max "
                f"{AXIS_MAX_POSITIONS[axis]}"
            ),
        )


def run_axis_homing(axis: str) -> None:
    """Run one axis negative until its optical home sensor triggers, then zero it."""
    if h is None:
        raise HTTPException(status_code=503, detail="GPIO is not initialized")

    pins = MOTOR_AXES[axis]
    with axis_motion_locks[axis]:
        if axis_is_moving[axis]:
            raise HTTPException(status_code=409, detail=f"{axis.upper()} axis is already moving")
        axis_stop_events[axis].clear()
        axis_is_moving[axis] = True
        axis_is_homing[axis] = True
        axis_is_homed[axis] = False

    try:
        logger.info("%s axis homing started", axis.upper())
        set_axis_direction(axis, DIRECTION_NEGATIVE)
        for _ in range(HOMING_MAX_STEPS):
            update_limit_sensor_cache(axis)
            if limit_stably_active(axis):
                axis_positions[axis] = 0
                axis_is_homed[axis] = True
                logger.info("%s axis homed on GPIO%s", axis.upper(), LIMIT_SENSOR_PINS[axis])
                return

            if axis_stop_events[axis].is_set():
                raise RuntimeError(f"{axis.upper()} homing stopped")

            pulse_axis(axis, HOMING_FAST_STEP_SECONDS)
            axis_positions[axis] -= 1
            update_limit_sensor_cache(axis)
            if limit_stably_active(axis):
                axis_positions[axis] = 0
                axis_is_homed[axis] = True
                logger.info("%s axis homed on GPIO%s", axis.upper(), LIMIT_SENSOR_PINS[axis])
                return

        raise RuntimeError(
            f"{axis.upper()} home sensor was not reached within {HOMING_MAX_STEPS} steps"
        )
    finally:
        lgpio.gpio_write(h, pins["step"], 0)
        with axis_motion_locks[axis]:
            axis_is_moving[axis] = False
            axis_is_homing[axis] = False
            axis_move_direction[axis] = 0
            axis_stop_events[axis].clear()


def run_homing_sequence(axes: List[str]) -> None:
    """Home axes serially."""
    for axis in axes:
        run_axis_homing(axis)


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


def monitor_limit_sensors():
    """Continuously monitor home/limit sensors and request a stop if a moving axis hits one."""
    last_states = {axis: None for axis in MOTOR_AXES}

    while True:
        try:
            if h is not None:
                for axis in MOTOR_AXES:
                    update_limit_sensor_cache(axis)
                    active = limit_active(axis)
                    if active != last_states[axis]:
                        state_label = "ACTIVE" if active else "clear"
                        logger.info(
                            "%s home sensor GPIO%s: %s",
                            axis.upper(),
                            LIMIT_SENSOR_PINS[axis],
                            state_label,
                        )
                        last_states[axis] = active

                    if (
                        limit_stably_active(axis)
                        and axis_is_moving[axis]
                        and not axis_is_homing[axis]
                        and axis_move_direction[axis] < 0
                    ):
                        # The motion thread performs the precise axis zeroing. This is a backup stop path.
                        axis_stop_events[axis].set()
            time.sleep(LIMIT_POLL_SECONDS)
        except Exception as e:
            print(f"Error reading home sensors: {e}")
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
        limit_pull_flag = (
            lgpio.SET_PULL_DOWN
            if settings.limit_sensor_pull.lower() == "down"
            else lgpio.SET_PULL_UP
        )
        for pin in LIMIT_SENSOR_PINS.values():
            lgpio.gpio_claim_input(h, pin, limit_pull_flag)
        refresh_limit_sensors()
        
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
        limit_pin_summary = ", ".join(
            f"{axis.upper()}_HOME={pin}"
            for axis, pin in LIMIT_SENSOR_PINS.items()
        )
        print(f"GPIO pins initialized: LED_LAMP={LED_LAMP_PIN}({led_lamp_isOn}), PSU={PSU_PIN}({psu_isOn}), LED_FLR={LED_FLR_PIN}({led_flr_isOn}), {axis_pin_summary}, {limit_pin_summary}")
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
    setup_dht11()
    # Start threads
    monitor_thread = threading.Thread(target=monitor_switch_sensor, daemon=True)
    monitor_thread.start()
    limit_thread = threading.Thread(target=monitor_limit_sensors, daemon=True)
    limit_thread.start()
    # Start LED control loop
    led_thread = threading.Thread(target=led_control_loop, daemon=True)
    led_thread.start()
    print("API started")
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up GPIO on server shutdown"""
    cleanup_dht11()
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
            "GET /environment": "Get DHT11 temperature and humidity",
            "GET /position": "Get current stage position",
            "GET /limits": "Get X/Y/Z home sensor states",
            "POST /move": "Move X/Y/Z axes",
            "POST /home": "Home X/Y/Z axes by moving negative until optical sensors trigger",
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


@app.get("/environment", response_model=EnvironmentReading)
async def get_environment(user: dict = Depends(verify_jwt)):
    """Get current temperature and humidity from the DHT11 sensor."""
    reading = read_dht11()
    if reading.healthy:
        logger.info(
            "DHT11 reading: %.1f C / %.1f F, %.1f%% humidity on GPIO%s",
            reading.temperature_c,
            reading.temperature_f,
            reading.humidity,
            reading.pin,
        )
    else:
        logger.warning("DHT11 reading unavailable on GPIO%s: %s", reading.pin, reading.message)

    return reading


@app.get("/position", response_model=StagePosition)
async def get_stage_position():
    """Return tracked stage position."""
    return current_stage_position()


@app.get("/limits", response_model=Dict[str, LimitSensorState])
async def get_limit_sensors():
    """Return current optical home/limit sensor states."""
    return read_limit_sensors()


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
            limit_sensors=read_limit_sensors(),
            message="No movement requested",
        )

    for axis, target_position in targets.items():
        validate_axis_target(axis, target_position)

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
        limit_sensors=read_limit_sensors(),
        message="Stage movement started",
    )


@app.post("/home", response_model=StageCommandResponse)
async def home_stage():
    """Home all axes against the optical limit sensors."""

    if any(axis_is_moving.values()):
        raise HTTPException(status_code=409, detail="Stop movement before homing")

    try:
        await asyncio.to_thread(run_homing_sequence, ["x", "y", "z"])
    except RuntimeError as e:
        request_stage_stop()
        logger.error("Stage homing failed: %s", e)
        raise HTTPException(status_code=409, detail=str(e))

    return StageCommandResponse(
        success=True,
        status="homed",
        position=current_stage_position(),
        limit_sensors=read_limit_sensors(),
        message="Stage homed at zero on optical sensors",
    )


@app.post("/stop", response_model=StageCommandResponse)
async def stop_stage():
    """Request an immediate stop for active stage movement."""
    request_stage_stop()

    return StageCommandResponse(
        success=True,
        status="stopping" if any(axis_is_moving.values()) else "idle",
        position=current_stage_position(),
        limit_sensors=read_limit_sensors(),
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
