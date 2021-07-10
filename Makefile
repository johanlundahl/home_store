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
	coverage run -m pytest tests/*_test.py

cov:
	coverage report
	coverage html

lint:
	flake8 --statistics --count
		
update:
	git pull
	pip3 install -r requirements.txt	
