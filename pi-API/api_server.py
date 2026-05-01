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
# Based on pinout: Purple=Enable/Disable, Yellow=Step, Orange=Direction
# X-motor
X_MOTOR_ENABLE = 5      # Purple - Disable/Enable
X_MOTOR_STEP = 11       # Yellow - Step
X_MOTOR_DIRECTION = 10  # Orange - Direction
# Y-motor
Y_MOTOR_ENABLE = 26     # Purple - Disable/Enable
Y_MOTOR_STEP = 19       # Yellow - Step
Y_MOTOR_DIRECTION = 6   # Orange - Direction
# Z-motor
Z_MOTOR_ENABLE = 9      # Purple - Disable/Enable
Z_MOTOR_STEP = 27       # Yellow - Step
Z_MOTOR_DIRECTION = 22  # Orange - Direction

h = None
led_lamp_isOn = False
psu_isOn = False
led_flr_isOn = False
gpio_initialized = False
drawer_is_open = False
is_scanning = False

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

class ShutdownResponse(BaseModel):
    success: bool
    message: str


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
        # Configure switch sensor with pull-up resistor
        lgpio.gpio_claim_input(h, SWITCH_SENSOR_PIN, lgpio.SET_PULL_UP)
        
        # Ensure Lamps/flr are OFF at startup (inverted logic: 1=off)
        # PSU use normal logic (1=on, 0=off)
        lgpio.gpio_write(h, LED_LAMP_PIN, 1)
        lgpio.gpio_write(h, LED_FLR_PIN, 1)
        lgpio.gpio_write(h, FRONT_PANEL_LED_PIN, 0)  # Front Panel LED starts off
        lgpio.gpio_write(h, PSU_PIN, 0)
        led_lamp_isOn = False
        led_flr_isOn = False
        psu_isOn = False
        
        print(f"✓ GPIO pins initialized: LED_LAMP={LED_LAMP_PIN}({led_lamp_isOn}), PSU={PSU_PIN}({psu_isOn}), LED_FLR={LED_FLR_PIN}({led_flr_isOn})")
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
            "POST /scan/stop": "Stop scanning mode"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify API and GPIO status"""
    return HealthCheck(healthy=True)


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