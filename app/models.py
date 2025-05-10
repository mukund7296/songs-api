from app import mongo
from bson.objectid import ObjectId
from flask import current_app
import re

class SongModel:
    @staticmethod
    def get_songs(page=1, per_page=None):
        """Get paginated songs"""
        if per_page is None:
            per_page = current_app.config['SONGS_PER_PAGE']
            
        skip = (page - 1) * per_page
        
        # Use projection to avoid retrieving unnecessary fields for large datasets
        cursor = mongo.db.songs.find(
            {}, 
            {'artist': 1, 'title': 1, 'difficulty': 1, 'level': 1, 'released': 1}
        ).skip(skip).limit(per_page)
        
        # Convert MongoDB IDs to strings for JSON serialization
        songs = []
        for song in cursor:
            song['_id'] = str(song['_id'])
            songs.append(song)
            
        # Get total count for pagination metadata
        total = mongo.db.songs.count_documents({})
        
        return {
            'songs': songs,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total // per_page) + (1 if total % per_page > 0 else 0)
        }

    @staticmethod
    def get_average_difficulty(level=None):
        """Get average difficulty of all songs, optionally filtered by level"""
        match_stage = {}
        if level is not None:
            match_stage = {'level': level}
            
        # Use aggregation pipeline for efficient computation on server side
        pipeline = [
            {'$match': match_stage},
            {'$group': {
                '_id': None,
                'avg_difficulty': {'$avg': '$difficulty'},
                'count': {'$sum': 1}
            }}
        ]
        
        result = list(mongo.db.songs.aggregate(pipeline))
        
        if not result:
            return {'average_difficulty': None, 'count': 0}
            
        return {
            'average_difficulty': result[0]['avg_difficulty'],
            'count': result[0]['count']
        }
    
    @staticmethod
    def search_songs(message):
        """Search songs by artist or title"""
        if not message:
            return []
            
        # Create case-insensitive regex pattern for efficient text search
        regex = re.compile(re.escape(message), re.IGNORECASE)
        
        # Use index-supported query for artist and title
        query = {
            '$or': [
                {'artist': regex},
                {'title': regex}
            ]
        }
        
        cursor = mongo.db.songs.find(query)
        
        songs = []
        for song in cursor:
            song['_id'] = str(song['_id'])
            songs.append(song)
            
        return songs
    
    @staticmethod
    def add_rating(song_id, rating):
        """Add a rating for a song"""
        try:
            # Validate song existence
            song = mongo.db.songs.find_one({'_id': ObjectId(song_id)})
            if not song:
                return None, 'Song not found'
                
            # Insert rating into separate collection for better scalability
            rating_doc = {
                'song_id': ObjectId(song_id),
                'rating': rating
            }
            
            result = mongo.db.ratings.insert_one(rating_doc)
            
            return str(result.inserted_id), None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_song_ratings(song_id):
        """Get rating statistics for a song"""
        try:
            # Validate song existence
            song = mongo.db.songs.find_one({'_id': ObjectId(song_id)})
            if not song:
                return None, 'Song not found'
                
            # Use aggregation for efficient server-side computation
            pipeline = [
                {'$match': {'song_id': ObjectId(song_id)}},
                {'$group': {
                    '_id': None,
                    'avg_rating': {'$avg': '$rating'},
                    'min_rating': {'$min': '$rating'},
                    'max_rating': {'$max': '$rating'},
                    'count': {'$sum': 1}
                }}
            ]
            
            results = list(mongo.db.ratings.aggregate(pipeline))
            
            if not results:
                return {'average': None, 'lowest': None, 'highest': None, 'count': 0}, None
                
            result = results[0]
            return {
                'average': result['avg_rating'],
                'lowest': result['min_rating'],
                'highest': result['max_rating'],
                'count': result['count']
            }, None
        except Exception as e:
            return None, str(e)
