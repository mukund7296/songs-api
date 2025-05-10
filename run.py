import os
from app import create_app
from app.utils import load_songs_to_db

app = create_app()

# Import songs when the app starts
@app.before_first_request
def before_first_request():
    # Get the path to the songs.json file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, 'data', 'songs.json')
    
    # Load songs to MongoDB if not already loaded
    if os.path.exists(json_file):
        count = load_songs_to_db(json_file)
        app.logger.info(f"Loaded {count} songs into the database")

if __name__ == '__main__':
    app.run(debug=True)
