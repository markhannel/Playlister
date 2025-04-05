from flask import Flask, jsonify, request
import dataclasses

from . concert import *

app = Flask(__name__)

@app.route("/build-program")
def build_program():
    url = request.args.get('concert_webpage')
    if url is None:
        return "URL parameter 'concert_webpage' is required!", 400

    concert_program = retrieve_concert_program(url)
    concert = analyze_concert_program(concert_program)
    d = dataclasses.asdict(concert)
    return jsonify(d)
