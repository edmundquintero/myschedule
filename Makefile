PREFIX=/usr/local
export PREFIX
PYTHON=python

all: build

build:
	$(PYTHON) setup.py build
clean:
	$(PYTHON) setup.py clean --all
	find . -name '*.py[co]' -exec rm -f "{}" ';'
	rm -rf build dist myschedule.egg-info temp
install:
	$(PYTHON) setup.py install --prefix="$(PREFIX)"
