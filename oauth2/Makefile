.PHONY: install run-auth run-resource run-demo clean

install:
	pip install -r requirements.txt

run-auth:
	python auth_server/auth_server.py

run-resource:
	python resource_server/resource_server.py

run:
	python run_demo.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +