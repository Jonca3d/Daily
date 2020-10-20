import os
from dotenv import load_dotenv

load_dotenv()

DRIVER_NAME = os.getenv('DRIVERNAME')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')
