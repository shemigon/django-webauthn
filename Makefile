fulltest: flake8 runtests coveragereport

test: flake8 baretests

flake8:
	flake8 webauthn

runtests:
	coverage run --branch --source=webauthn `which django-admin.py` test --settings=webauthn.test_settings webauthn

baretests:
	`which django-admin.py` test --settings=webauthn.test_settings webauthn

coveragereport:
	coverage report --omit=webauthn/test*

clean:
	rm -rf build
	rm -rf *.egg-info

testenv:
	pip install -e .
	pip install -r requirements-test.txt
	pip install django

.PHONY: fulltest test baretests runtests flake8 coveragereport clean
