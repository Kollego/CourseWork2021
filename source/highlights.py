import pandas as pd

from chat_downloader import ChatDownloader
from .utils import download_video, get_ffmpeg_video

import os
import librosa
import numpy as np
import pickle

from sklearn.preprocessing import MinMaxScaler

model = pickle.load(open('bin/model.pkl', 'rb'))
mean = np.load('bin/mean.npy')
std = np.load('bin/std.npy')


def get_timestamps(video_id, do_vid=False):
    chat, chat_emotes, emotes_images = get_twitch_chat(video_id)
    df = get_chat_dataframe(chat)
    chat_features = get_chat_features(df, chat_emotes, emotes_images)
    if do_vid:
        chat_results = get_chat_results(chat_features, True)
        video_name = download_video(video_id)
        video_results = get_video_results(video_name, chat_results)
        return video_results
    else:
        chat_results = get_chat_results(chat_features)
        return chat_results


def get_twitch_chat(video_id):
    url = 'https://www.twitch.tv/videos/' + str(video_id)
    chat = ChatDownloader().get_chat(url)
    messages = []
    chat_emotes = []
    emotes_images = {}
    for item in chat:
        messages.append({'timestamp': item['time_in_seconds'],
                         'author': item['author']['name'],
                         'message': item['message']})
        if item.get('emotes'):
            for e in item['emotes']:
                chat_emotes.append({'timestamp': item['time_in_seconds'],
                                    'id': e['id']})
                if e['id'] not in emotes_images.keys():
                    emotes_images[e['id']] = e['images'][1]['url']

    return messages, chat_emotes, emotes_images


def clear_chat_dataframe(df):
    df = df[~df['author'].str.contains('bot')]
    df = df.loc[df['author'].shift() != df['author']]
    return df


def get_chat_dataframe(chat):
    df = pd.DataFrame(chat).set_index('timestamp')
    return clear_chat_dataframe(df)


def get_chat_features(df, chat_emotes, emotes_images):
    df_features = df
    df_features['message_length'] = df_features['message'].str.len()
    df_features = df_features.groupby(df_features.index // 20).agg({'message_length': ['count', 'mean']})
    df_features.columns = df_features.columns.droplevel()
    scaler = MinMaxScaler()
    df_features[['score']] = scaler.fit_transform(df_features[['count']]) * 100
    df_features['score'] = df_features['score'].astype(int)

    df_emotes = pd.DataFrame(chat_emotes).set_index('timestamp')
    df_emotes = df_emotes.groupby(df_emotes.index // 20).agg({'id': lambda x: x.value_counts().index[0]})
    df_emotes = df_emotes.replace({'id': emotes_images})
    df_emotes.columns = ['emote_image']

    return df_features.join(df_emotes)


def get_chat_results(chat_features, vid=False):
    timestamps = [i for i in list(chat_features.sort_values(by='count', ascending=False).iloc[:25].index * 20)]
    scores = [i for i in list(chat_features.sort_values(by='count', ascending=False).iloc[:25].score)]
    emotes = [i for i in list(chat_features.sort_values(by='count', ascending=False).iloc[:25].emote_image)]
    result = []
    result_timestamps = []
    for i in range(len(timestamps)):
        if timestamps[i] not in result_timestamps and (timestamps[i] - 20) not in result_timestamps and (
                timestamps[i] + 20) not in result_timestamps:
            result_timestamps.append(timestamps[i])
            result.append((int(timestamps[i]), scores[i], emotes[i]))
    if not vid:
        for i in range(len(result)):
            result[i] = (str(result[i][0] - 20), str(result[i][1]), result[i][2])

    return result


def get_video_results(video_name, chat_results):
    if os.getcwd()[-4:] != 'vods':
        os.chdir("vods/")
    mean = 1
    std = 1
    results = []
    for timestamp, score, emote in chat_results:
        data = []
        for offset in range(timestamp - 40, timestamp, 3):
            get_ffmpeg_video(video_name, offset)
            X, sample_rate = librosa.load(f"aud{offset}.wav", res_type='kaiser_fast', duration=3, sr=44100)
            spectrogram = librosa.feature.melspectrogram(y=X, sr=sample_rate, n_mels=128, fmax=8000)
            db_spec = librosa.power_to_db(spectrogram)

            log_spectrogram = np.mean(db_spec, axis=0)
            data.append(log_spectrogram)
            os.remove(f"aud{offset}.wav")
        df = pd.DataFrame(data)

        df = df.fillna(0)
        X = df.iloc[:, :]
        X = (X - mean) / std
        X = np.array(X)
        res = model.predict(X)
        emotions = -1
        for i in range(len(res)):
            if res[i] == 1:
                emotions = i
                break
        if emotions != -1:
            results.append((timestamp - 45 + emotions * 3, int(score * 1.3), emote))
        else:
            results.append((timestamp - 20, score, emote))

    return results
