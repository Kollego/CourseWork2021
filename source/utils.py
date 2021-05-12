import requests
import json
import re

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
    return r.json()['data'][0]


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
        h = Highlight(video_id=video_id, offset=int(t))
        db.session.add(h)
    db.session.commit()

# auth


FOUR_WEEKS = 2419200



