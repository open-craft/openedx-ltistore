lint:
	black lti_store

test:
	pytest --cov-report term-missing lti_store


piptools: ## install uv
	if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements/pip.txt; \
	else \
		pip install -r requirements/pip.txt; \
	fi

requirements: piptools ## install development environment requirements
	uv venv --allow-existing
	uv pip sync -q requirements/dev.txt requirements/private.*

# Define PIP_COMPILE_OPTS=-v to get more information during make upgrade.
PIP_COMPILE = uv pip compile --upgrade $(PIP_COMPILE_OPTS)

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: piptools $(COMMON_CONSTRAINTS_TXT) ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	uv venv --allow-existing
	# Make sure to compile files after any other files they include!
	$(PIP_COMPILE) -o requirements/pip.txt requirements/pip.in
	uv pip install -qr requirements/pip.txt
	$(PIP_COMPILE) -o requirements/base.txt requirements/base.in
	$(PIP_COMPILE) -o requirements/dev.txt requirements/dev.in
	$(PIP_COMPILE) -o requirements/test.txt requirements/dev.in
	# Let tox control the Django version for tests
	sed -i '/^[dD]jango==/d' requirements/test.txt
