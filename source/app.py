from flask import Flask, jsonify, request
import dataclasses

from . concert import *

app = Flask(__name__)

@app.route("/build-program")
def build_program():
    concert_webpage = request.args.get('concert_webpage')
    if concert_webpage is None:
        return "URL parameter 'concert_webpage' is required!", 400

    concert_program = retrieve_concert_program(concert_webpage)
    if concert_program is None:
        return f"Failed to get concert program from {concert_webpage}", 500
 
    concert = analyze_concert_program(concert_program)
    if concert is None:
        return "Provided 'concert_webpage' does not include a concert program!", 400

    d = dataclasses.asdict(concert)
    return jsonify(d)
