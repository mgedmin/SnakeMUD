all: bin/pserve lib/python*/site-packages/SnakeMUD.egg-link

run: bin/pserve lib/python*/site-packages/SnakeMUD.egg-link
	bin/pserve development.ini --reload

start: bin/pserve lib/python*/site-packages/SnakeMUD.egg-link
	savelog pyramid.log
	bin/pserve --daemon production.ini
	sleep 0.5 && tail pyramid.log

stop:
	bin/pserve --stop-daemon

restart:
	$(MAKE) stop || true
	$(MAKE) start

update:
	git pull
	make restart

clean:
	find -name '*.pyc' -delete

wipe-sessions:
	rm -f data/sessions/

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/python bin/pip:
	virtualenv --no-site-packages .

lib/python*/site-packages/SnakeMUD.egg-link: bin/python setup.py
	bin/python setup.py develop
