import os
import base64
import json
from dotenv import load_dotenv
import requests
from urllib.parse import urlencode
import webbrowser

from . concert import retrieve_concert_program, analyze_concert_program

# Load environment variables from .env file
load_dotenv()

# Access the variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "playlist-modify-private playlist-modify-public"
USER_ID = os.getenv("SPOTIFY_USER_ID")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

class AccessTokenMissing(Exception):
    pass


def make_post_request(url, data=None, headers=None):
    """Helper to make POST requests with error handling."""
    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.json())
    return response


def get_user_id(access_token):
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("id")


def get_access_token_from_refresh_token():
    # Step 1: Make a POST request to get a new access token using the refresh token
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    # Prepare the authorization header
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}"
    }

    response = make_post_request(url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    raise AccessTokenMissing("Access token not found.")


def get_access_token():

    try:
        return get_access_token_from_refresh_token()
    except AccessTokenMissing:
        print("Missing access token.. falling back to authorization.")
        pass

    # Step 1: Redirect the user to Spotify for authorization
    auth_url = f"""https://accounts.spotify.com/authorize?{urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    })}"""

    # Open the authorization URL in the browser
    print("Please visit the following URL to authorize the application:")
    print(auth_url)
    webbrowser.open(auth_url)

    # Step 2: After the user authorizes, they will be redirected to the redirect URI
    # You'll need to capture the authorization code from the URL, which will look like:
    # https://developer.spotify.com?code=YOUR_AUTHORIZATION_CODE
    # The code will be passed as a URL parameter "code"

    # Manually handle the redirect or automate this step with a local server
    code = input("Enter the code from the URL after authorization: ")

    # Step 3: Exchange the authorization code for an access token
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    access_token =  response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")

    # (TODO) Save refresh
    
    return access_token


def search_tracks(access_token, track_name, artist_name=None):
    url = "https://api.spotify.com/v1/search"
    query = f"track:{track_name}"
    if artist_name:
        query += f" artist:{artist_name}"
    params = {"q": query, "type": "track", "limit": 10}
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, params=params)
    tracks = response.json().get("tracks", {}).get("items", [])
    return tracks


def create_playlist(access_token, name, description="Playlist created via API"):
    USER_ID = get_user_id(access_token)
    url = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = json.dumps({"name": name, "description": description, "public": True})
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code != 201:  # Check for successful creation
        print(f"Error: {response.status_code}")
        print(response.json())  # Print the error details from the API response
        return None
    
    return response.json().get("id")


def add_tracks_to_playlist(access_token, playlist_id, track_uris) -> None:
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = json.dumps({"uris": track_uris})
    requests.post(url, headers=headers, data=data)

