from dotenv import load_dotenv
import os
import requests
import base64
import json
from urllib.parse import urlencode
import webbrowser

from concert import retrieve_concert_program, analyze_concert_program

# Load environment variables from .env file
load_dotenv()

# Access the variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "playlist-modify-private playlist-modify-public"  # Add any scopes you need
USER_ID = os.getenv("SPOTIFY_USER_ID")

def get_user_id(access_token):
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("id")  # Returns the user ID

def get_access_token():
    # Step 1: Redirect the user to Spotify for authorization
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    })}"

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

    return response_data.get("access_token")

# Function to search for tracks
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

# Function to create a playlist
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

# Function to add tracks to playlist
def add_tracks_to_playlist(access_token, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = json.dumps({"uris": track_uris})
    requests.post(url, headers=headers, data=data)

# Main function
def main():

    URL = "https://www.carnegiehall.org/Calendar/2025/03/21/Nobuyuki-Tsujii-Piano-0800PM"
    #URL = "https://www.nyphil.org/concerts-tickets/2425/slatkin-shostakovich/"

    concert_program = retrieve_concert_program(URL)
    concert = analyze_concert_program(concert_program)
    
    
    access_token = get_access_token()  # Get the access token after user authorization
    all_track_uris = []
    
    for song in concert.songs:
        tracks = search_tracks(access_token, song["title"], song.get("artist"))
        all_track_uris.extend([track["uri"] for track in tracks])
    
    playlist_id = create_playlist(access_token, concert.title)
    add_tracks_to_playlist(access_token, playlist_id, all_track_uris)
    print(f"Playlist created: https://open.spotify.com/playlist/{playlist_id}")

if __name__ == "__main__":
    main()
