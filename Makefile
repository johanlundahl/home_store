MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_DIR := $(dir $(MKFILE_PATH))

autostart:
	(crontab -l; echo "@reboot cd $(CURRENT_DIR) && python3 -m home_store.app") | crontab -u pi -
	
clean:
	find . -name '*.pyc' -delete

init:
	pip3 install -r requirements.txt
	python3 -m home_store.cmdtool init

logging:
	tail -f application.log

run:
	python3 -m home_store.app

test:
	python3 -m unittest tests/test_app.py
		
update:
	git pull
	pip3 install -r requirements.txt	
