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

check:
	@echo -e "\n\e[1;97mRunning checks...\e[0m\n"
	@echo -e "\e[1;93m> ruff check\e[0m"
	@ruff check
	@echo -e "\n\e[1;93m> mypy\e[0m"
	@mypy .
	@echo -e "\n\e[1;93m> unittest\e[0m"
	@python3 -m unittest discover -s test

.PHONY: pypi/clean pypi/build pypi/publish
.PHONY: check test
