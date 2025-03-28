import dataclasses
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

@dataclasses.dataclass
class Song:
    title: str
    artist: str

@dataclasses.dataclass
class Concert:
    title: str
    songs: List[Song]


def analyze_concert_program(concert_program: str) -> Concert:
    prompt = f"""Inspect the following text which describes a concert program.
    Generate a title of the form "date at venue".
    List all of the songs with the artist and title specified separately.
    Return all of this data as a JSON blob.
    Do not enclose the JSON in code block tags.
    
    {concert_program}"""

    from openai import OpenAI
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

    import json
    response = json.loads(completion.choices[0].message.content)
    return Concert(**response)


def retrieve_concert_program(url: str) -> str:
    import requests
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Priority": "u=0, i",
        "TE": "trailers"
    }
    session.headers.update(headers)
    response = session.get(URL)
    import bs4
    soup = bs4.BeautifulSoup(response.text, features="lxml")
    return soup.get_text("\n\n", strip=True)


URL = "https://www.carnegiehall.org/Calendar/2025/03/21/Nobuyuki-Tsujii-Piano-0800PM"
URL = "https://www.nyphil.org/concerts-tickets/2425/slatkin-shostakovich/"

concert_program = retrieve_concert_program(URL)
concert = analyze_concert_program(concert_program)
print(concert)
