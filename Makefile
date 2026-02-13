pypi/clean:
	rm -rf build/ dist/ *.egg-info

pypi/build: pypi/clean
	uv build

pypi/publish:
	tree dist/
	@echo -e "\e[93mPress [Enter] to continue uploading to PyPI...\e[0m"
	@read
	uv publish

test:
	python3 -m unittest discover -s test

.PHONY: pypi/clean pypi/build pypi/publish test
