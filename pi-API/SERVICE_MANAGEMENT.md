# CytoPi API Service Management

## Service Name
`cytopi-api.service`

## Service Commands

### Check Service Status
```bash
sudo systemctl status cytopi-api.service
```

### View Live Logs
```bash
sudo journalctl -u cytopi-api.service -f
```

### View Recent Logs
```bash
sudo journalctl -u cytopi-api.service -n 100
```

### View Logs Since Boot
```bash
sudo journalctl -u cytopi-api.service -b
```

### View Logs for Specific Time Range
```bash
sudo journalctl -u cytopi-api.service --since "10 minutes ago"
sudo journalctl -u cytopi-api.service --since "2025-11-16 10:00:00"
```

### Start Service
```bash
sudo systemctl start cytopi-api.service
```

### Stop Service
```bash
sudo systemctl stop cytopi-api.service
```

### Restart Service
```bash
sudo systemctl restart cytopi-api.service
```

### Reload Service (after code changes)
```bash
sudo systemctl restart cytopi-api.service
```

### Enable Service (start on boot)
```bash
sudo systemctl enable cytopi-api.service
```

### Disable Service (don't start on boot)
```bash
sudo systemctl disable cytopi-api.service
```

### View Service Configuration
```bash
sudo systemctl cat cytopi-api.service
```

## Troubleshooting

### Service won't start
1. Check logs: `sudo journalctl -u cytopi-api.service -n 50`
2. Check file permissions: `ls -la /home/linkbiosystems/Desktop/CytoPiAPI/api_server.py`
3. Test script manually: `python3 /home/linkbiosystems/Desktop/CytoPiAPI/api_server.py`

### View errors only
```bash
sudo journalctl -u cytopi-api.service -p err
```

### Clear old logs
```bash
sudo journalctl --vacuum-time=7d
```