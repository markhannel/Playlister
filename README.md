# Playlister

Playlister is a Flask-based web service that automatically creates Spotify playlists given the URL of a website containing a concert program or list of songs. 
It scrapes concert listings, identifies pieces and composers, and finds recordings using the Spotify API.

```
flask --app source.app run
```

Example
```
curl http://localhost:5000/preview-program?concert_webpage=https://www.nyphil.org/concerts-tickets/2425/slatkin-shostakovich
curl http://localhost:5000/make-playlist?concert_webpage=https://www.nyphil.org/concerts-tickets/2425/slatkin-shostakovich
```

## Environment Variables

Create a `.env` file in the project root with the following keys:

- `OPENAI_API_KEY` - API key for OpenAI.
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_USER_ID` - API Keys from spotify
- Manually add `SPOTIFY_REDIRECT_URI`=https://developer.spotify.com


## Installation

```bash
git clone https://github.com/your-username/playlister.git
cd playlister
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
