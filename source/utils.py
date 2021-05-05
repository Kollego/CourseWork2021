import requests
import json

with open('credentials.json', 'r') as f:
    headers = json.loads(f.read())


def parse_timestamp(timestamp):
    hours = str(timestamp//3600).zfill(2)
    mins = str(timestamp%3600//60).zfill(2)
    secs = str(timestamp%60).zfill(2)
    return f"{hours}:{mins}:{secs}"


def get_video(id):
    params = {'id': id}
    r = requests.get('https://api.twitch.tv/helix/videos', params=params, headers=headers)
    return r.json()['data'][0]