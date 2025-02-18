clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

create_requirements:
	uv pip freeze > requirements.txt
	uv pip sync requirements.txt pyproject.toml