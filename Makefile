all: bin/pserve lib/python*/site-packages/SnakeMUD.egg-link

run: bin/pserve lib/python*/site-packages/SnakeMUD.egg-link
	bin/pserve development.ini --reload

clean:
	find -name '*.pyc' -delete

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/python bin/pip:
	virtualenv --no-site-packages .

lib/python*/site-packages/SnakeMUD.egg-link:
	bin/python setup.py develop
