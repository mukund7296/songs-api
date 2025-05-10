from flask import Blueprint, request, jsonify
from app.models import SongModel
from bson.objectid import ObjectId

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/songs', methods=['GET'])
def get_songs():
    """
    Route A: Return a list of songs with pagination
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Songs per page (default: from config)
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = request.args.get('per_page')
        
        if per_page:
            per_page = int(per_page)
            
        if page < 1:
            return jsonify({'error': 'Page number must be positive'}), 400
            
        result = SongModel.get_songs(page, per_page)
        return jsonify(result)
    except ValueError:
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/songs/avg/difficulty', methods=['GET'])
def get_average_difficulty():
    """
    Route B: Return the average difficulty for all songs
    
    Query parameters:
    - level: Filter by level (optional)
    """
    try:
        level = request.args.get('level')
        
        if level:
            try:
                level = int(level)
            except ValueError:
                return jsonify({'error': 'Level must be an integer'}), 400
                
        result = SongModel.get_average_difficulty(level)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/songs/search', methods=['GET'])
def search_songs():
    """
    Route C: Return a list of songs matching the search string
    
    Query parameters:
    - message: Search string (required)
    """
    message = request.args.get('message')
    
    if not message:
        return jsonify({'error': 'Search message is required'}), 400
        
    try:
        songs = SongModel.search_songs(message)
        return jsonify({'songs': songs, 'count': len(songs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/songs/rating', methods=['POST'])
def add_rating():
    """
    Route D: Add a rating for a given song
    
    JSON body:
    - song_id: Song ID (required)
    - rating: Rating value between 1-5 (required)
    """
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    song_id = data.get('song_id')
    rating = data.get('rating')
    
    if not song_id:
        return jsonify({'error': 'Song ID is required'}), 400
        
    if not rating:
        return jsonify({'error': 'Rating is required'}), 400
        
    try:
        rating = int(rating)
    except ValueError:
        return jsonify({'error': 'Rating must be an integer'}), 400
        
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
    try:
        # Validate song_id format
        ObjectId(song_id)
    except:
        return jsonify({'error': 'Invalid song ID format'}), 400
        
    # Add the rating
    rating_id, error = SongModel.add_rating(song_id, rating)
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify({'success': True, 'rating_id': rating_id}), 201

@api_bp.route('/songs/<song_id>/ratings', methods=['GET'])
def get_song_ratings(song_id):
    """
    Route E: Return rating statistics for a given song
    
    Path parameters:
    - song_id: Song ID (required)
    """
    try:
        # Validate song_id format
        ObjectId(song_id)
    except:
        return jsonify({'error': 'Invalid song ID format'}), 400
        
    ratings, error = SongModel.get_song_ratings(song_id)
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(ratings)
