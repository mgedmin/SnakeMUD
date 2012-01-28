all: bin/pserve

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/python bin/pip:
	virtualenv --no-site-packages .
