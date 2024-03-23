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

#### linter command
```make lint```

### Task 2

Description: For an exchange, get all trading pairs, their latest prices and trading volume for 24 hours
    Task: 
        Create a class inherited from the BaseExchange class. 
        Write the implementation of the methods and fill in the required fields (marked as "todo")
    Note: 
        Feel free to add another internal methods. 
        It is important that the example from the main function runs without errors
    The flow looks like this:
        1. Request data from the exchange
        2. We bring the ticker to the general format
        3. We extract from the ticker properties the last price, 
            the 24-hour trading volume of the base currency 
            and the 24-hour trading volume of the quoted currency. 
            (at least one of the volumes is required)
        4. Return the structure in the format: 
            ```
            {
                "BTC/USDT": TickerInfo(last=57000, baseVolume=11328, quoteVolume=3456789),
                "ETH/BTC": TickerInfo(last=4026, baseVolume=4567, quoteVolume=0)
            }
            ```

#### start task 2 command
```make task2```
