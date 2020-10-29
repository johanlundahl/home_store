
run:
	python3 -m home_store.app

update:
	git pull
	pip3 install -r requirements.txt	
	
clean:
	find . -name '*.pyc' -delete

init:
	pip3 install -r requirements.txt
	python3 -m home_store.cmdtool init

logging:
	tail -f application.log
