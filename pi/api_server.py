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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LED Control API", description="Control LED via HTTP API")

# GPIO configuration
LED_PIN = 23  # GPIO23 - Physical pin 16

h = None
led_isOn = False
gpio_initialized = False

# Pydantic models aka schemas for request and response bodies
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


def setup_gpio():
    """Initialize GPIO settings"""
    global h
    try:
        h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(h, LED_PIN, 0)
        print(f"✓ GPIO pin {LED_PIN} initialized")
    except Exception as e:
        print(f"Error setting up GPIO: {e}")
        raise


def cleanup_gpio():
    """Clean up GPIO settings"""
    global h, gpio_initialized
    if h is not None:
        try:
            lgpio.gpio_write(h, LED_PIN, 0)
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
            "GET /led/state": "Get current LED state",
            "POST /led/toggle": "Toggle LED on/off"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify API and GPIO status"""
    return HealthCheck(healthy=True)


@app.get("/led/state", response_model=LEDState)
async def get_led_isOn():
    """Get the current state of the LED"""
    return LEDState(is_on=led_isOn, pin=LED_PIN)


@app.post("/led/toggle", response_model=ToggleResponse)
async def toggle_led():
    """Toggle the LED on or off"""
    global led_isOn
    
    try:
        # Toggle the state
        led_isOn = not led_isOn
        
        # Write to GPIO
        lgpio.gpio_write(h, LED_PIN, 1 if led_isOn else 0)
        
        return ToggleResponse(
            success=True,
            is_on=led_isOn,
            pin=LED_PIN,
            message=f"LED turned {'ON' if led_isOn else 'OFF'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle LED: {str(e)}")


if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
