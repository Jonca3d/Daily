from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from .config import DATABASE

engine = create_engine(URL(**DATABASE))