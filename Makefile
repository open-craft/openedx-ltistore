lint:
	black lti_store

test:
	pytest --cov-report term-missing lti_store
