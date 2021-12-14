import random
from .database import data

global db
db = data

def generate_avatar():
    url = 'https://avataaars.io/?avatarStyle=Transparent'

    for key, value in db.items():
        item = random.choice(value)
        url += f'&{key}={item}'

    return url
