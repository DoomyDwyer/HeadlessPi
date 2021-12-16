#!/bin/bash -e

# Adapted by Steve Dwyer form the original version presented by Patrick Hundal at:
# https://hacks.mozilla.org/2017/02/headless-raspberry-pi-configuration-over-bluetooth/
#
# Edit the display name of the RaspberryPi so you can distinguish
# your unit from others in the Bluetooth console (mine is doom-rasp)
#
# run this script once as root (or sudo) to create the service and enable it.
# Once enabled, it will run on startup whenever the Pi boots, until you disable it

# Edit /lib/systemd/system/bluetooth.service to enable BT services
sudo sed -i: 's|^Exec.*toothd$| \
ExecStart=/usr/lib/bluetooth/bluetoothd -C \
ExecStartPost=/usr/bin/sdptool add SP \
ExecStartPost=/bin/hciconfig hci0 piscan \
|g' /lib/systemd/system/bluetooth.service

# enable the new rfcomm service
sudo systemctl enable rfcomm

# start the rfcomm service
sudo systemctl restart rfcomm
