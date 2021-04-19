from traceback import format_exc

from flask import jsonify, request, render_template

from source import app


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')
