from flask import Flask, jsonify, request
import dataclasses

from . import concert
from . import spotify_utilities as spotify

app = Flask(__name__)

@app.route("/preview-program")
def preview_program():
    concert_webpage = request.args.get('concert_webpage')
    if concert_webpage is None:
        return "URL parameter 'concert_webpage' is required!", 400

    concert_program = concert.retrieve_concert_program(concert_webpage)
    if concert_program is None:
        return f"Failed to get concert program from {concert_webpage}", 500
 
    parsed_concert = concert.analyze_concert_program(concert_program)
    if parsed_concert is None:
        return "Provided 'concert_webpage' does not include a concert program!", 400

    d = dataclasses.asdict(parsed_concert)
    return jsonify(d)

@app.route("/make-playlist")
def make_playlist():
    concert_webpage = request.args.get('concert_webpage')
    if concert_webpage is None:
        return "URL parameter 'concert_webpage' is required!", 400

    concert_program = concert.retrieve_concert_program(concert_webpage)
    if concert_program is None:
        return f"Failed to get concert program from {concert_webpage}", 500
 
    parsed_concert = concert.analyze_concert_program(concert_program)
    if parsed_concert is None:
        return "Provided 'concert_webpage' does not include a concert program!", 400

    d = dataclasses.asdict(parsed_concert)

    access_token = spotify.get_access_token()  # Get the access token after user authorization
    all_track_uris = []
    
    for song in parsed_concert.songs:
        tracks = spotify.search_tracks(access_token, song["title"], song.get("artist"))
        all_track_uris.extend([track["uri"] for track in tracks])
    
    playlist_id = spotify.create_playlist(access_token, parsed_concert.title)
    spotify.add_tracks_to_playlist(access_token, playlist_id, all_track_uris)
    print(f"Playlist created: https://open.spotify.com/playlist/{playlist_id}")

    return {
        "playlist": f"https://open.spotify.com/playlist/{playlist_id}",
        "concert": d,
    }
