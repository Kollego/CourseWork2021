from flask import jsonify, request, render_template, redirect, make_response
from flask_jwt_extended import create_access_token, get_jwt_identity,\
    jwt_required, unset_jwt_cookies, unset_access_cookies, set_access_cookies, get_jwt

from source import app, celery, db, jwt
from .utils import *
from .highlights import *
from .models import *

from datetime import datetime, timedelta, timezone


@app.route('/', methods=['GET'])
def main():
    msg = request.args.get('msg')
    return render_template('index.html', msg=msg)


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    user = User.get_user_with_username_and_password(data["username"], data["password"])
    if user:
        response = jsonify(msg='login successful')
        access_token = create_access_token(user.username)
        set_access_cookies(response, access_token)
        return response

    return jsonify(error=True), 403


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify(msg="logout successful")
    unset_jwt_cookies(response)
    return response


@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return redirect('/?msg=1', 302)


@jwt.invalid_token_loader
def invalid_token_callback(callback):
    # Invalid Fresh/Non-Fresh Access token in auth header
    resp = make_response(redirect('/'))
    unset_jwt_cookies(resp)
    return resp, 302


@jwt.expired_token_loader
def expired_token_callback(callback):
    resp = make_response(redirect('/'))
    unset_access_cookies(resp)
    return resp, 302


@app.route("/identity", methods=["POST"])
@jwt_required()
def identity():
    current_user = get_jwt_identity()
    print(current_user)
    return jsonify(user=current_user), 200


@app.route('/videos', methods=['GET'])
@jwt_required()
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
