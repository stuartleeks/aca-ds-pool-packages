install_requirements:
	@echo "Installing requirements..."
	@pip install -r src/requirements.txt

run:
	@echo "Running the application..."
	@python src/app.py