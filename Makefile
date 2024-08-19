lint:
	black lti_store

test:
	pytest --cov-report term-missing lti_store

ensure-piptools:
	pip install pip-tools

update-requirements: ensure-piptools
	pip-compile requirements/base.in -o requirements/base.txt
	pip-compile requirements/dev.in -o requirements/dev.txt

requirements: ensure-piptools
	pip-sync requirements/base.txt

dev-requirements: ensure-piptools
	pip-sync requirements/dev.txt
