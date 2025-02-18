install:
	python run_all_apis.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +