runlocal:
	@echo "Running local copy"
	FLASK_DEBUG=1 FLASK_APP="statsapp:create_app" flask run

initialise_environment:
	@echo "Clearing existing env"
	-rm -rf env
	@echo "Building new env"
	virtualenv -p python3 env
	@echo "Activating environment"
	. env/bin/activate
	@echo "Installing dependencies"
	pip install -r requirements.txt

test:
	python -m pytest

coverage:
	python -m pytest --cov=statsapp