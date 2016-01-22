VERSION = 1.0.0-dev
NAME = sdreaper

build: clean
	python setup.py sdist bdist_wheel

clean:
	$(RM) build dist *.egg-info .coverage htmlcov

very-clean: clean
	$(RM) .eggs .cache
	find . -name '*.pyc' | xargs rm -f

install:
	python setup.py install
	pip install \
	    pep8 \
	    mock

test:
	pep8 setup.py sdreaper
	py.test

.PHONY: build clean very-clean install test
