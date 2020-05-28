clean:
	rm -rf dist build

build:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	python setup.py sdist bdist_wheel

upload:
	twine upload -s dist/*

publish: build upload clean
