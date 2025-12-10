from decouple import config 
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:

    SECRET_KEY = config("SECRET_KEY")
    JWT_SECRET_KEY = config("JWT_SECRET_KEY")
    DATABASE_URL = config("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False


