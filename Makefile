VENV = .venv
PIP = $(VENV)/bin/pip

.PHONY: venv

venv:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt