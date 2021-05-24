import requests
import json
import re

import os

from source import db, app
from .models import *

with open('credentials.json', 'r') as f:
    creds = json.loads(f.read())
    headers = {key: creds[key] for key in ['Authorization', 'client-id']}


# GENERAL UTILS


def parse_timestamp(timestamp):
    hours = str(timestamp // 3600).zfill(2)
    mins = str(timestamp % 3600 // 60).zfill(2)
    secs = str(timestamp % 60).zfill(2)
    return f"{hours}:{mins}:{secs}"


def change_thumbnail_size(url):
    url = re.sub('%{width}', '320', url)
    url = re.sub('%{height}', '180', url)
    return url


# TWITCH API


def get_video(id):
    params = {'id': id}
    r = requests.get('https://api.twitch.tv/helix/videos', params=params, headers=headers)
    if r.status_code == 404:
        return r.json()
    data = r.json()['data'][0]
    params = {'id': data['user_id']}
    r = requests.get('https://api.twitch.tv/helix/users', params=params, headers=headers)
    if r.status_code == 404:
        return r.json()
    author_data = r.json()['data'][0]
    author = Author.query.filter_by(id=int(data['user_id'])).first()
    if not author:
        author = Author(id=author_data['id'],
                        name=author_data['display_name'],
                        image_url=author_data['profile_image_url'])
        db.session.add(author)
        db.session.commit()
    else:
        author.name = author_data['display_name']
        author.image_url = author_data['profile_image_url']
        db.session.commit()

    data['profile_image'] = author_data['profile_image_url']

    return data


# CELERY


def get_celery_worker_status(app):
    i = app.control.inspect()
    availability = i.ping()
    stats = i.stats()
    registered_tasks = i.registered()
    active_tasks = i.active()
    scheduled_tasks = i.scheduled()
    result = {
        'availability': availability,
        'stats': stats,
        'registered_tasks': registered_tasks,
        'active_tasks': active_tasks,
        'scheduled_tasks': scheduled_tasks
    }
    return result


# DATABASE


def load_timestamps(video_id, timestamps):
    video_id = int(video_id)
    for t in timestamps:
        h = Highlight(video_id=video_id, offset=int(float(t)), score=1)
        db.session.add(h)
    db.session.commit()


def drop_video(video_id, username):
    user = User.query.filter_by(username=username).first()
    video = Video.query.filter_by(id=video_id).first()
    if video in user.videos:
        user.videos.remove(video)
        db.session.commit()
    return True


def get_ffmpeg_video(length, path):
    for i in range(length/3):
        os.run(f"ffmpeg -i {path} -ss 60 - t 3 aud.wav")


def download_video(id):
    os.run(f'twitch-dl {id} -d videos')
