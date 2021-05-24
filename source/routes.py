from flask import jsonify, request, render_template, redirect, make_response, send_file
from flask_jwt_extended import create_access_token, get_jwt_identity, \
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
    resp = make_response(redirect('/'))
    unset_jwt_cookies(resp)
    return resp, 302


@jwt.expired_token_loader
def expired_token_callback(callback):
    resp = make_response(redirect('/'))
    unset_access_cookies(resp)
    return resp, 302


@app.route("/identity", methods=["GET"])
@jwt_required()
def identity():
    current_user = get_jwt_identity()
    print(get_jwt())
    return jsonify(user=current_user), 200


@app.route('/videos', methods=['GET'])
@jwt_required()
def videos():
    channel_id = request.args.get('channel')
    if channel_id:
        channel = Author.query.filter_by(id=channel_id).first()
        channel_name = channel.name
    else:
        channel = None
        channel_name = None
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if channel:
        vids = []
        for v in user.videos:
            if int(channel_id) == v.author_id:
                vids.append(v.serialize)
    else:
        vids = [v.serialize for v in user.videos]
    return render_template('videos.html', videos=vids, channel_name=channel_name)


@app.route('/channels', methods=['GET'])
@jwt_required()
def channels():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    channels_list = [v.author.serialize for v in user.videos]
    channels_list = list({v['id']: v for v in channels_list}.values())
    return render_template('channels.html', channels=channels_list)


@app.route('/highlights', methods=['GET'])
@jwt_required()
def highlights():
    video_id = request.args.get('id')
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if int(video_id) not in [v.id for v in user.videos]:
        resp = make_response(redirect('/videos'))
        return resp, 302
    video = Video.query.filter_by(id=int(video_id)).first()
    video_data = video.serialize
    video_data['highlights'] = []
    for h in video.highlights:
        video_data['highlights'].append((h.offset, parse_timestamp(h.offset)))

    return render_template('highlights.html', video=video_data)


@app.route('/get-highlights', methods=['POST'])
@jwt_required()
def post_highlights():
    jsdata = request.get_json(force=True)
    data = get_video(jsdata['video-id'])
    if data.get('error'):
        return jsonify(msg=f'Video {jsdata["video-id"]} not found'), 400
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if int(data['id']) in [v.id for v in user.videos]:
        return jsonify(msg=f'Video {jsdata["video-id"]} already exists'), 401
    data['thumbnail_url'] = change_thumbnail_size(data['thumbnail_url'])

    get_highlights.delay(data, username)

    return data


@app.route('/drop-video', methods=['POST'])
@jwt_required()
def post_drop():
    jsdata = request.get_json(force=True)
    username = get_jwt_identity()
    result = drop_video(jsdata['video-id'], username)
    if not result:
        return jsonify(msg=f'Video {jsdata["video-id"]} not found'), 400

    return jsonify(msg='ok')


@app.route('/download', methods=['POST'])
def download():
    return jsonify(msg='ok')


@celery.task(name='__main__.get_highlights')
def get_highlights(data, username):
    user = User.query.filter_by(username=username).first()
    video = Video.query.filter_by(id=int(data['id'])).first()
    if video:
        user.videos.append(video)
        db.session.commit()
    else:
        video = Video(id=int(data['id']),
                      name=data['title'],
                      image_url=data['thumbnail_url'],
                      processed=False,
                      author_id=int(data['user_id']))
        user.videos.append(video)
        db.session.commit()
        timestamps = get_timestamps(data['id'])
        load_timestamps(data['id'], timestamps)
        video.processed = True
        db.session.commit()
