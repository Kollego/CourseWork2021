from flask import jsonify, request, render_template
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from source import app, celery, db
from .utils import *
from .highlights import *
from .models import *


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')


@app.route("/login", methods=["POST"])
def get_token():
    data = request.get_json(force=True)
    user = User.get_user_with_username_and_password(data["username"], data["password"])
    if user:
        return jsonify(token=create_access_token(user))

    return jsonify(error=True), 403


@app.route('/videos', methods=['GET'])
def videos():
    vids = [
        {
            'image': 'https://static-cdn.jtvnw.net/cf_vods/dgeft87wbj63p/9ecf755420932ed0daf1_funspark_csgo_41825646556_1618926743//thumb/thumb0-320x180.jpg',
            'profile': 'https://static-cdn.jtvnw.net/jtv_user_pictures/d207bd33-d461-4262-92b1-b1f327b38fe7-profile_image-70x70.png',
            'name': '(EN) BIG vs Extra Salt | FunSpark: Ulti EU/CIS | by @hugoootv & @justharrygg',
            'author': 'Funspark_CSGO',
            'game': 'Counter-Strike: Global Offensive'
        }
    ]

    return render_template('videos.html', videos=vids)


@app.route('/highlights', methods=['GET'])
def highlights():
    video_id = request.args.get('id')
    video = {
        'image': 'https://static-cdn.jtvnw.net/cf_vods/dgeft87wbj63p/9ecf755420932ed0daf1_funspark_csgo_41825646556_1618926743//thumb/thumb0-320x180.jpg',
        'profile': 'https://static-cdn.jtvnw.net/jtv_user_pictures/d207bd33-d461-4262-92b1-b1f327b38fe7-profile_image-70x70.png',
        'name': '(EN) BIG vs Extra Salt | FunSpark: Ulti EU/CIS | by @hugoootv & @justharrygg',
        'author': 'Funspark_CSGO', 'game': 'Counter-Strike: Global Offensive',
        'highlights': [6260, 8500, 11820, 4100, 7160, 9700, 8400, 7640, 7260, 8200, 7600, 9720, 8320, 11480, 11920,
                       6980, 8220]}
    for i in range(len(video['highlights'])):
        video['highlights'][i] = (video['highlights'][i], parse_timestamp(video['highlights'][i]))

    return render_template('highlights.html', video=video)


@app.route('/get-highlights', methods=['POST'])
def get_post_javascript_data():
    jsdata = request.get_json(force=True)
    data = get_video(jsdata['video-id'])
    if data.get('error'):
        return data, 400
    get_highlights.delay(jsdata['video-id'])
    data['thumbnail_url'] = change_thumbnail_size(data['thumbnail_url'])
    return data


@celery.task(name='__main__.get_highlights')
def get_highlights(video_id):
    timestamps = get_timestamps(video_id)
    load_timestamps(video_id, timestamps)
