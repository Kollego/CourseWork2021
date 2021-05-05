from flask import jsonify, request, render_template

from source import app, celery
from .utils import *
from .highlights import *


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/videos', methods=['GET'])
def videos():
    videos = [
        {
            'image': 'https://static-cdn.jtvnw.net/cf_vods/dgeft87wbj63p/9ecf755420932ed0daf1_funspark_csgo_41825646556_1618926743//thumb/thumb0-320x180.jpg',
            'profile': 'https://static-cdn.jtvnw.net/jtv_user_pictures/d207bd33-d461-4262-92b1-b1f327b38fe7-profile_image-70x70.png',
            'name': '(EN) BIG vs Extra Salt | FunSpark: Ulti EU/CIS | by @hugoootv & @justharrygg',
            'author': 'Funspark_CSGO',
            'game': 'Counter-Strike: Global Offensive'
        }
    ]
    return render_template('videos.html', videos=videos)


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
    result = get_highlights.delay(jsdata['video-id'])
    print(result.wait())
    data['thumbnail_url'] = change_thumbnail_size(data['thumbnail_url'])
    # do highlights
    return data


@celery.task(name='__main__.get_highlights')
def get_highlights(video_id):
    return get_timestamps(video_id)
