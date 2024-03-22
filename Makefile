start:
	poetry run uvicorn stakewolle.app:app --host 0.0.0.0 --port 8000 --workers 4

dev:
	poetry run python main.py

alembic_init:
	poetry run alembic init alembic -t async

alembic_revision:
	poetry run alembic revision --autogenerate -m 'init'

alembic_upgrade:
	poetry run alembic upgrade head

install:
	poetry install

build:
	$(MAKE) install
	$(MAKE) alembic_upgrade