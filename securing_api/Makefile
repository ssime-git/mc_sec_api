.PHONY: run clean install

install:
	pip install -r requirements.txt

run:
	python run_all_apis.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete