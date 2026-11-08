### Environment Preparation
```
pip install python-dotenv
```

## Basic Eflow VM commands:
### Connect to VM:
```
Connect-EflowVm
```

### Execute command on the VM:
```
Invoke-EflowVmCommand -command "sudo iotedge list"
```

### View file content while logged into VM
```
cat /path/to/your-file.txt
```

### List Deployed Modules
```
sudo iotedge list                    # is telemetrysim "running"?
```

### View System Logs
```
sudo iotedge logs edgeAgent          # image pull or registry credential errors show here
sudo iotedge logs edgeHub            # routing or connectivity issues
sudo iotedge system logs -- -f       # runtime daemon logs (aziot-edged)
```

### View Module Logs
```
sudo iotedge logs telemetrysim -f                 # continuous logs
sudo iotedge logs telemetrysim --tail 50          # last 50 lines
sudo iotedge logs telemetrysim --since 10m        # last 10 minutes
sudo iotedge logs telemetrysim --since 10m -f     # recent history, then follow
```
