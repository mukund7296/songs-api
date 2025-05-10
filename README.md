# Songs API

A Flask-based API for managing songs and ratings, with MongoDB as the datastore.

## Features

- List songs with pagination
- Get average difficulty (overall or by level)
- Search songs by artist or title
- Add ratings to songs
- Get rating statistics for songs

## Requirements

- Python 3.8+
- MongoDB 4.4+
- Docker (optional, for running MongoDB)

## Project Structure

```
songs_api/
├── app/                 # Application package
│   ├── __init__.py      # App initialization
│   ├── models.py        # Database models
│   ├── routes.py        # API routes
│   └── utils.py         # Helper functions
├── tests/               # Tests package
│   ├── __init__.py      
│   └── test_api.py      # API tests
├── data/                # Data files
│   └── songs.json       # Songs data
├── config.py            # Configuration
├── run.py               # Application entry point
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd songs_api
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start MongoDB

You can run MongoDB using Docker:

```bash
docker run --detach --name songs_db --publish 127.0.0.1:27017:27017 mongo:4.4
```

Or connect to an existing MongoDB instance by setting the `MONGO_URI` environment variable.

### 4. Create a .env file for environment variables (optional)

```bash
echo "MONGO_URI=mongodb://localhost:27017/songs_db" > .env
```

### 5. Create the data directory and add songs.json

```bash
mkdir -p data
# Copy your songs.json file to the data directory
```

### 6. Run the application

```bash
python run.py
```

The API will be available at `http://localhost:5000/api/`.

## API Endpoints

### A: Get Songs List

```
GET /api/songs
```

Query parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)

### B: Get Average Difficulty

```
GET /api/songs/avg/difficulty
```

Query parameters:
- `level`: Filter by level (optional)

### C: Search Songs

```
GET /api/songs/search
```

Query parameters:
- `message`: Search string (required)

### D: Add Rating

```
POST /api/songs/rating
```

Request body (JSON):
```json
{
  "song_id": "song_id_here",
  "rating": 4
}
```

- `rating` must be between 1 and 5 inclusive

### E: Get Song Ratings

```
GET /api/songs/{song_id}/ratings
```

Path parameters:
- `song_id`: ID of the song

## Running Tests

```bash
pytest
```

For more verbose output:

```bash
pytest -v
```

## Scalability Considerations

This API is designed to handle millions of songs and ratings:

1. **Efficient MongoDB Queries**:
   - Uses proper indexing on frequently queried fields
   - Leverages MongoDB's aggregation pipeline for server-side computations
   - Uses projection to limit data retrieval to necessary fields

2. **Pagination**:
   - All list endpoints implement pagination to limit memory usage

3. **Denormalization**:
   - Ratings stored in a separate collection from songs for better write performance
   - Aggregation used for computing statistics on-demand

4. **Error Handling**:
   - Comprehensive error handling for resilient operation
