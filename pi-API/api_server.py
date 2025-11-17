#!/usr/bin/env python3
"""
FastAPI server for Raspberry Pi 5
"""
# TODO: add better validation

from operator import add
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import lgpio
import uvicorn
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LED Control API", description="Control LED via HTTP API")

# GPIO configuration
LED_LAMP_PIN = 13  # GPIO13 - LED Lamp (existing LED)
RELAY_PIN = 21  # GPIO21 - Relay Green
LED_FLR_PIN = 12  # GPIO12 - LED FLR (gray cable)

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
relay_isOn = False
led_flr_isOn = False
gpio_initialized = False

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


def setup_gpio():
    """Initialize GPIO settings"""
    global h, led_lamp_isOn, relay_isOn, led_flr_isOn
    try:
        h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(h, LED_LAMP_PIN, 0)
        lgpio.gpio_claim_output(h, RELAY_PIN, 0)
        lgpio.gpio_claim_output(h, LED_FLR_PIN, 0)
        
        # Ensure LED_LAMP is OFF at startup (inverted logic: 1=off)
        lgpio.gpio_write(h, LED_LAMP_PIN, 1)
        led_lamp_isOn = False
        
        # Read current GPIO states for relay and LED_FLR
        relay_state = lgpio.gpio_read(h, RELAY_PIN)
        led_flr_state = lgpio.gpio_read(h, LED_FLR_PIN)
        
        # Relay and LED_FLR use normal logic (1=on, 0=off)
        relay_isOn = (relay_state == 1)
        led_flr_isOn = (led_flr_state == 1)
        
        print(f"✓ GPIO pins initialized: LED_LAMP={LED_LAMP_PIN}({led_lamp_isOn}), RELAY={RELAY_PIN}({relay_isOn}), LED_FLR={LED_FLR_PIN}({led_flr_isOn})")
    except Exception as e:
        print(f"Error setting up GPIO: {e}")
        raise


def cleanup_gpio():
    """Clean up GPIO settings"""
    global h, gpio_initialized
    if h is not None:
        try:
            lgpio.gpio_write(h, LED_LAMP_PIN, 0)
            lgpio.gpio_write(h, RELAY_PIN, 0)
            lgpio.gpio_write(h, LED_FLR_PIN, 0)
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
            "GET /relay/state": "Get current relay state",
            "POST /relay/toggle": "Toggle relay on/off",
            "GET /led-flr/state": "Get current FLR LED state",
            "POST /led-flr/toggle": "Toggle FLR LED on/off",
            "POST /system/shutdown": "Shutdown the Raspberry Pi gracefully"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify API and GPIO status"""
    return HealthCheck(healthy=True)


@app.get("/led-lamp/state", response_model=LEDState)
async def get_led_lamp_state():
    """Get the current state of the LED Lamp"""
    global led_lamp_isOn
    try:
        # Read actual GPIO state
        current_state = lgpio.gpio_read(h, LED_LAMP_PIN)
        led_lamp_isOn = (current_state == 0)  # Inverted logic
        return LEDState(is_on=led_lamp_isOn, pin=LED_LAMP_PIN)
    except Exception as e:
        return LEDState(is_on=led_lamp_isOn, pin=LED_LAMP_PIN)


@app.post("/led-lamp/toggle", response_model=ToggleResponse)
async def toggle_led_lamp():
    """Toggle the LED Lamp on or off"""
    global led_lamp_isOn
    
    try:
        # Read current hardware state to ensure sync
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


@app.get("/relay/state", response_model=LEDState)
async def get_relay_state():
    """Get the current state of the relay"""
    global relay_isOn
    try:
        # Read actual GPIO state
        current_state = lgpio.gpio_read(h, RELAY_PIN)
        relay_isOn = (current_state == 1)
        return LEDState(is_on=relay_isOn, pin=RELAY_PIN)
    except Exception as e:
        return LEDState(is_on=relay_isOn, pin=RELAY_PIN)


@app.post("/relay/toggle", response_model=ToggleResponse)
async def toggle_relay():
    """Toggle the relay on or off"""
    global relay_isOn
    
    try:
        # Read current hardware state to ensure sync
        current_state = lgpio.gpio_read(h, RELAY_PIN)
        relay_isOn = (current_state == 1)
        
        # Toggle the state
        relay_isOn = not relay_isOn
        
        # Write to GPIO
        lgpio.gpio_write(h, RELAY_PIN, 1 if relay_isOn else 0)
        
        return ToggleResponse(
            success=True,
            is_on=relay_isOn,
            pin=RELAY_PIN,
            message=f"Relay turned {'ON' if relay_isOn else 'OFF'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle relay: {str(e)}")


@app.get("/led-flr/state", response_model=LEDState)
async def get_led_flr_state():
    """Get the current state of the FLR LED"""
    global led_flr_isOn
    try:
        # Read actual GPIO state
        current_state = lgpio.gpio_read(h, LED_FLR_PIN)
        led_flr_isOn = (current_state == 1)
        return LEDState(is_on=led_flr_isOn, pin=LED_FLR_PIN)
    except Exception as e:
        return LEDState(is_on=led_flr_isOn, pin=LED_FLR_PIN)


@app.post("/led-flr/toggle", response_model=ToggleResponse)
async def toggle_led_flr():
    """Toggle the FLR LED on or off"""
    global led_flr_isOn
    
    try:
        # Read current hardware state to ensure sync
        current_state = lgpio.gpio_read(h, LED_FLR_PIN)
        led_flr_isOn = (current_state == 1)
        
        # Toggle the state
        led_flr_isOn = not led_flr_isOn
        
        # Write to GPIO
        lgpio.gpio_write(h, LED_FLR_PIN, 1 if led_flr_isOn else 0)
        
        return ToggleResponse(
            success=True,
            is_on=led_flr_isOn,
            pin=LED_FLR_PIN,
            message=f"FLR LED turned {'ON' if led_flr_isOn else 'OFF'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle FLR LED: {str(e)}")


@app.post("/system/shutdown", response_model=ShutdownResponse)
async def shutdown_system():
    """Gracefully shutdown the Raspberry Pi"""
    try:
        logger.info("Shutdown command received via API")
        # Clean up GPIO before shutdown
        cleanup_gpio()
        # Use shutdown now command
        result = subprocess.run(["sudo", "shutdown", "-h", "now"], capture_output=True, text=True)
        logger.info(f"Shutdown command executed: stdout={result.stdout}, stderr={result.stderr}")
        return ShutdownResponse(
            success=True,
            message="System shutdown initiated. Raspberry Pi will power off shortly."
        )
    except Exception as e:
        logger.error(f"Failed to initiate shutdown: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to shutdown system: {str(e)}")


if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
