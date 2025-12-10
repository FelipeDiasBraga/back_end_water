from decouple import Config 
from loguru import logger as log
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pingo.db")
