import os

import uvicorn
from dotenv import load_dotenv


load_dotenv()
DEBUG = os.getenv('DEBUG', False)

if __name__ == '__main__':
    uvicorn.run('stakewolle.app:app', host='0.0.0.0', port=8000, reload=DEBUG)
