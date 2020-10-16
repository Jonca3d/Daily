import os
from dotenv import load_dotenv

load_dotenv()
DATABASE = {
    'drivername': os.getenv('DRIVERNAME'),
    'host': os.getenv('HOST'),
    'port': os.getenv('PORT'),
    'username': os.getenv('USERNAME'),
    'password': os.getenv('PASSWORD'),
    'database': os.getenv('DATABASE')
}