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

If the DHT11 data wire is not on GPIO24, set `DHT11_PIN=<gpio_number>` in
`pi-API/.env`.

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
