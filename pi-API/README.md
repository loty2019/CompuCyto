# CytoPi API

FastAPI server to control Incucyte with Raspberry Pi 5 via HTTP endpoints.

## Setup

1. Install dependencies:
```bash
python3 -m pip install --break-system-packages fastapi uvicorn lgpio adafruit-circuitpython-dht
```

Or use the requirements file:
```bash
python3 -m pip install --break-system-packages -r pi-API/requirements.txt
```

Raspberry Pi OS may show `externally-managed-environment` if the
`--break-system-packages` flag is omitted. That is expected on newer Pi OS
images when installing into the system Python.

If the DHT11 data wire is not on GPIO23, set `DHT11_PIN=<gpio_number>` in
`pi-API/.env`. This value uses BCM GPIO numbering, not physical header pin
numbering. The default `DHT11_PIN=23` is physical header pin 16.

Wire DHT11 modules to the Pi using 3.3V:

- DHT11 VCC/+ -> Pi 3.3V, physical pin 1 or 17
- DHT11 DATA/S/OUT -> Pi BCM GPIO23, physical pin 16 by default
- DHT11 GND/- -> Pi GND, for example physical pin 6

Do not power common DHT11 modules from Pi 5V unless the module documentation
proves the data output is level-shifted to 3.3V. Many modules pull DATA up to
VCC, and Raspberry Pi GPIO pins are not 5V tolerant.

Optional DHT11 tuning values:

```bash
DHT11_PIN=23
DHT11_READ_ATTEMPTS=3
DHT11_RETRY_SECONDS=1.2
```

## To start the FastAPI server, run:
```bash
sudo systemctl restart cytopi-api.service
sleep 2
sudo systemctl status cytopi-api.service
```

## Example API Requests

Toggle LED Lamp:
```bash

curl -X POST http://localhost:8000/led-lamp/toggle

Get LED Lamp State:
```bash

curl http://localhost:8000/led-lamp/state
```

## API Documentation

Access the interactive API docs at: `http://<Raspberry_Pi_IP>:8000/docs`

## Management Dashboard
Access the management dashboard at: `http://<Raspberry_Pi_IP>:9090`
