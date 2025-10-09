.PHONY: run
run:
	uvicorn app.main:app --reload

.PHONY: run_public
run_public:
	ngrok http 8000

.PHONY: install
install:
	poetry install

.PHONY: install_prod
install_prod:
	poetry install --no-dev

.PHONY: precommit
precommit:
	poetry run pre-commit run --all-files