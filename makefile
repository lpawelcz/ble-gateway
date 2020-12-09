prepare:
	sudo cp ble-gateway.service /etc/systemd/system/

unprepare:
	sudo rm /etc/systemd/system/ble-gateway.service

start:
	sudo systemctl start ble-gateway.service

enable:
	sudo systemctl enable ble-gateway.service

disable:
	sudo systemctl disable ble-gateway.service

stop:
	sudo systemctl stop ble-gateway.service

restart:
	sudo systemctl restart ble-gateway.service

status:
	sudo systemctl status ble-gateway.service

logs:
	sudo journalctl -u ble-gateway.service

launch: prepare start enable
	echo "Launched Low Reliability BLE Gateway!"

clean: disable stop unprepare
	echo "Cleaned up Low Reliability BLE Gateway!"

.SILENT: launch clean
