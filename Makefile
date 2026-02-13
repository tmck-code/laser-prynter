pypi/build:
	uv build
	
pypi/publish:
	tree dist/
	@echo -e "\e[93mPress [Enter] to continue uploading to PyPI...\e[0m"
	@read 
	twine upload dist/*

test:
	python3 -m unittest discover -s test

.PHONY: pypi/build pypi/publish test
