from traceback import format_exc

from flask import jsonify, request, render_template

from source import app


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/videos', methods=['GET'])
def videos():
    return render_template('videos.html')


@app.route('/vod-highlights', methods=['GET'])
def vod_highlights():
    return 'hello'