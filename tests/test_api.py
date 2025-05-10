import os
import json
import pytest
from app import create_app, mongo
from bson.objectid import ObjectId

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongodb://localhost:27017/songs_test_db'
    })
    
    # Create test client
    with app.test_client() as client:
        # Set up
        with app.app_context():
            # Clear database collections
            mongo.db.songs.delete_many({})
            mongo.db.ratings.delete_many({})
            
            # Load test data
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_file = os.path.join(os.path.dirname(current_dir), 'data', 'songs.json')
            
            songs = []
            with open(json_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            song = json.loads(line)
                            songs.append(song)
                        except json.JSONDecodeError:
                            continue
            
            if songs:
                mongo.db.songs.insert_many(songs)
                
            # Create indexes
            mongo.db.songs.create_index([('artist', 'text'), ('title', 'text')])
            mongo.db.songs.create_index('level')
            mongo.db.ratings.create_index('song_id')
            
        yield client
        
        # Tear down
        with app.app_context():
            mongo.db.songs.delete_many({})
            mongo.db.ratings.delete_many({})

def test_get_songs(app):
    """Test Route A: get songs list with pagination"""
    # Test default pagination
    response = app.get('/api/songs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'songs' in data
    assert 'page' in data
    assert 'total' in data
    assert len(data['songs']) <= data['per_page']
    
    # Test custom pagination
    response = app.get('/api/songs?page=1&per_page=5')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['songs']) <= 5
    
    # Test invalid pagination
    response = app.get('/api/songs?page=0')
    assert response.status_code == 400

def test_get_average_difficulty(app):
    """Test Route B: get average difficulty"""
    # Test without level filter
    response = app.get('/api/songs/avg/difficulty')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'average_difficulty' in data
    assert 'count' in data
    
    # Test with level filter
    response = app.get('/api/songs/avg/difficulty?level=13')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'average_difficulty' in data
    
    # Test with invalid level
    response = app.get('/api/songs/avg/difficulty?level=abc')
    assert response.status_code == 400

def test_search_songs(app):
    """Test Route C: search songs"""
    # Test valid search
    response = app.get('/api/songs/search?message=The')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'songs' in data
    assert 'count' in data
    assert data['count'] > 0
    
    # Test case insensitivity
    response = app.get('/api/songs/search?message=the')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] > 0
    
    # Test missing search parameter
    response = app.get('/api/songs/search')
    assert response.status_code == 400

def test_add_rating(app):
    """Test Route D: add rating"""
    # Get a song ID first
    response = app.get('/api/songs')
    songs = json.loads(response.data)['songs']
    song_id = songs[0]['_id']
    
    # Test valid rating
    response = app.post('/api/songs/rating', 
                         json={'song_id': song_id, 'rating': 4})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Test invalid rating value
    response = app.post('/api/songs/rating', 
                         json={'song_id': song_id, 'rating': 6})
    assert response.status_code == 400
    
    # Test missing parameters
    response = app.post('/api/songs/rating', json={'song_id': song_id})
    assert response.status_code == 400
    
    # Test invalid song ID
    response = app.post('/api/songs/rating', 
                         json={'song_id': 'invalid_id', 'rating': 3})
    assert response.status_code == 400

def test_get_song_ratings(app):
    """Test Route E: get song ratings"""
    # First add some ratings to a song
    response = app.get('/api/songs')
    songs = json.loads(response.data)['songs']
    song_id = songs[0]['_id']
    
    # Add multiple ratings
    app.post('/api/songs/rating', json={'song_id': song_id, 'rating': 3})
    app.post('/api/songs/rating', json={'song_id': song_id, 'rating': 5})
    app.post('/api/songs/rating', json={'song_id': song_id, 'rating': 1})
    
    # Test getting ratings
    response = app.get(f'/api/songs/{song_id}/ratings')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'average' in data
    assert 'lowest' in data
    assert 'highest' in data
    assert 'count' in data
    assert data['count'] == 3
    assert data['lowest'] == 1
    assert data['highest'] == 5
    
    # Test invalid song ID
    response = app.get('/api/songs/invalid_id/ratings')
    assert response.status_code == 400
