# Playlister

```
flask --app source.app run
```

Example
```
curl http://localhost:5000/build-program?concert_webpage=https://www.nyphil.org/concerts-tickets/2425/slatkin-shostakovich
```

## Environment variables

- `OPENAI_API_KEY` - API key for OpenAI.
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_USER_ID` - API Keys from spotify
- Manually add `SPOTIFY_REDIRECT_URI`=https://developer.spotify.com

