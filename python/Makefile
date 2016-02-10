VERSION = 1.0.0-dev
NAME = sdreaper

build: clean
	python setup.py -q sdist bdist_wheel

clean:
	rm -fr build dist *.egg-info .coverage htmlcov

very-clean: clean
	rm -fr .eggs .cache
	find . -name '*.pyc' | xargs rm -f

install: build
	pip -qq install --upgrade dist/*.tar.gz

uninstall:
	pip -qq uninstall -y sdreaper || echo 'not installed'

install-dev:
	pip install \
	    pep8 \
	    mock

test-release: build test
	twine upload -r pypitest dist/*

release: build test
	twine upload dist/*

test:
	pep8 setup.py sdreaper
	py.test

.PHONY: build clean very-clean uninstall install install-dev test-release release test
