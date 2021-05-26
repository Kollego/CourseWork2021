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
    chat = get_twitch_chat(video_id)
    df = get_chat_dataframe(chat)
    chat_features = get_chat_features(df)
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
    for item in chat:
        messages.append({'timestamp': item['time_in_seconds'],
                         'author': item['author']['name'],
                         'message': item['message']})
    return messages


def clear_chat_dataframe(df):
    df = df[~df['author'].str.contains('bot')]
    df = df.loc[df['author'].shift() != df['author']]
    return df


def get_chat_dataframe(chat):
    df = pd.DataFrame(chat).set_index('timestamp')
    return clear_chat_dataframe(df)


def get_chat_features(df):
    df_features = df
    df_features['message_length'] = df_features['message'].str.len()
    df_features = df.groupby(df.index // 20).agg({'message_length': ['count', 'mean']})
    df_features.columns = df_features.columns.droplevel()
    scaler = MinMaxScaler()
    df_features[['score']] = scaler.fit_transform(df_features[['count']]) * 100
    df_features['score'] = df_features['score'].astype(int)

    return df_features


def get_chat_results(chat_features, vid=False):
    timestamps = [i for i in list(chat_features.sort_values(by='count', ascending=False).iloc[:25].index * 20)]
    scores = [i for i in list(chat_features.sort_values(by='count', ascending=False).iloc[:25].score)]
    result = []
    result_timestamps = []
    for i in range(len(timestamps)):
        if timestamps[i] not in result_timestamps and (timestamps[i] - 20) not in result_timestamps and (
                timestamps[i] + 20) not in result_timestamps:
            result_timestamps.append(timestamps[i])
            result.append((int(timestamps[i]), scores[i]))
    if not vid:
        for i in range(len(result)):
            result[i] = (str(result[i][0] - 20), str(result[i][1]))

    return result


def get_video_results(video_name, chat_results):
    if os.getcwd()[-4:] != 'vods':
        os.chdir("vods/")
    mean = 1
    std = 1
    results = []
    for timestamp, score in chat_results:
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
            results.append((timestamp - 45 + emotions * 3, int(score * 1.3)))
        else:
            results.append((timestamp - 20, score))

    return results
