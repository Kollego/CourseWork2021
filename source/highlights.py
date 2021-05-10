import pandas as pd

from chat_downloader import ChatDownloader


def get_timestamps(video_id):
    chat = get_twitch_chat(video_id)
    df = get_chat_dataframe(chat)
    df_features = get_chat_features(df)
    return [str(i) for i in list(df_features.sort_values(by='count', ascending=False).iloc[:20].index * 20 - 20)]


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
