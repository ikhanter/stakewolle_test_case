### Stakewolle test case

#### Description
It is necessary to develop a simple RESTful API service for the referral system.

#### Functional requirements
- user registration and authentication (JWT, Oauth 2.0);
- an authenticated user must be able to create or delete their referral code. Only 1 code can be active at a time. When creating a code, its expiration date must be specified;
- the ability to receive a referral code by email address of the referrer;
- the ability to register using a referral code as a referral;
- obtaining information about referrals by referrer id;
- UI documentation (Swagger/ReDoc).

#### System requirements
- Python 3.10.12^
- Poetry 1.6.1^
- PostgreSQL 15^
- fastapi ^0.110.0
- asyncio ^3.4.3
- fastapi-users ^13.0.0
- aiosqlite ^0.20.0
- python-dotenv ^1.0.1
- uvicorn ^0.28.0
- alembic ^1.13.1
- asyncpg ^0.29.0
- pytz ^2024.1
- flake8 ^7.0.0
- sqlalchemy ^2.0.28

#### Environment Variables
- DATABASE_URL
- SECRET_KEY
- DEBUG

#### build command
```make build```

#### start command
```make start```

#### dev command
```make dev```
