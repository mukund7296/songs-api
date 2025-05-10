import json
from app import mongo
import os

def load_songs_to_db(json_file):
    """
    Load songs from JSON file to MongoDB
    Returns the number of documents inserted
    """
    # Check if songs collection is already populated
    if mongo.db.songs.count_documents({}) > 0:
        return 0
        
    # Import songs from the JSON file
    songs = []
    
    with open(json_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    song = json.loads(line)
                    songs.append(song)
                except json.JSONDecodeError:
                    continue
    
    if songs:
        # Create indexes for better query performance
        mongo.db.songs.create_index([('artist', 'text'), ('title', 'text')])
        mongo.db.songs.create_index('level')  # For queries filtering by level
        mongo.db.ratings.create_index('song_id')  # For queries filtering by song_id
        
        # Insert songs
        result = mongo.db.songs.insert_many(songs)
        return len(result.inserted_ids)
    
    return 0
