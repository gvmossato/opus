import random

from .database import data


def generate_avatar(db=data):
    url = 'https://avataaars.io/?avatarStyle=Transparent'

    for key, value in db.items():
        item = random.choice(value)
        url += f'&{key}={item}'

    return url
