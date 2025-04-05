import dataclasses
from typing import List, Optional
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import bs4
import requests

load_dotenv()

@dataclasses.dataclass
class Song:
    title: str
    artist: str

@dataclasses.dataclass
class Concert:
    title: str
    songs: List[Song]


def call_open_ai(prompt: str) -> str:
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


def analyze_concert_program(concert_program: str) -> Optional[Concert]:
    prompt = f"""
    Does the following text include the program for a music concert?
    Answer either "yes" or "no" with no additional output.
    
    {concert_program}"""

    response = call_open_ai(prompt)
    print(f"is concert program?", response)
    if "no" in response:
        return None

    prompt = f"""
    Inspect the following text which includes the program for a music concert.
    Generate a title for the concert of the form "date at venue".
    List all of the songs with the artist and title specified separately.
    Return this data in a JSON blob.
    Do not enclose the JSON in code block tags.
    
    {concert_program}"""

    response = call_open_ai(prompt)
    print("parsed concert program:", response)
    return Concert(**json.loads(response))


def retrieve_concert_program(url: str) -> Optional[str]:
    session = requests.Session()
    headers = {
        "User-Agent": "Playlister/1.0 (Turn concert webpages into Spotify playlists; playlister@jpfennell.com)",
    }
    session.headers.update(headers)
    response = session.get(url)
    if not response.ok:
        return None
    soup = bs4.BeautifulSoup(response.text, features="lxml")
    return soup.get_text("\n\n", strip=True)

