start:
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