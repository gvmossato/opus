import environ # django-environ package
import os

from .prod import * # Use production settings by default 
from pathlib import Path


# Initialize env and read vars
env = environ.Env() 
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent, '.env'))


### Set vars ###

SECRET_KEY = env('SECRET_KEY')

EMAIL_HOST_USER = env('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
