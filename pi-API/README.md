# CytoPi API

FastAPI server to control Incucyte with Raspberry Pi 5 via HTTP endpoints.

## Setup

1. Install dependencies:
```bash
pip install --break-system-packages fastapi uvicorn lgpio
```

Or use the requirements file:
```bash
pip install --break-system-packages -r requirements.txt
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