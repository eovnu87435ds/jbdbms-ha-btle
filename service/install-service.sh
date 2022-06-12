#!/bin/bash
cp ha-bms.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ha-bms.service
echo "Installed ha-bms.service. Please reboot."
