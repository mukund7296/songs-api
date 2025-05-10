import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/songs_db')
    SONGS_PER_PAGE = 10  # Default pagination size
