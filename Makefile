build/pypi:
	rm -rf build/ dist/ laser_prynter.egg-info/
	python3 -m build --wheel --sdist
	python3 -m twine check dist/*
	
	@echo -e "\e[93mPress [Enter] to continue uploading to PyPI...\e[0m"
	@read 
	twine upload dist/*

.PHONY: build/pypi
