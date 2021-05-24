import pandas as pd

from chat_downloader import ChatDownloader

import os
import librosa
import numpy as np
import pickle


def get_timestamps(video_id):
    chat = get_twitch_chat(video_id)
    df = get_chat_dataframe(chat)
    df_features = get_chat_features(df)
    return


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
    return df_features


def extract_result(chat_features):
    return [str(i) for i in list(chat_features.sort_values(by='count', ascending=False).iloc[:20].index * 20 - 20)]


def predict_emotions(id):
    path = id
    df = pd.DataFrame(columns=['mel_spectrogram'])
    counter = 0
    filename = os.listdir(path)
    for f in filename:
        X, sample_rate = librosa.load(path, res_type='kaiser_fast', duration=3, sr=44100, offset=0.5)

        spectrogram = librosa.feature.melspectrogram(y=X, sr=sample_rate, n_mels=128, fmax=8000)
        db_spec = librosa.power_to_db(spectrogram)

        log_spectrogram = np.mean(db_spec, axis=0)
        df.loc[counter] = [log_spectrogram]
        counter = counter + 1


    audio_df = pd.DataFrame(emotion)
    audio_df = audio_df.replace(
        {1: 'neutral', 2: 'calm', 3: 'happy', 4: 'sad', 5: 'angry', 6: 'fear', 7: 'disgust', 8: 'surprise'})
    audio_df = pd.concat([pd.DataFrame(gender), audio_df, pd.DataFrame(actor)], axis=1)
    audio_df.columns = ['gender', 'emotion', 'actor']
    audio_df = pd.concat([audio_df, pd.DataFrame(file_path, columns=['path'])], axis=1)
    model = pickle.load('model.nn')
    return model.predict(audio_df)