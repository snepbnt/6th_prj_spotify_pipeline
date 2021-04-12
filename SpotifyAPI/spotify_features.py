
from typing import Any, Sequence
import requests
import sys
import base64
import json
import logging
import time
import pymysql


def get_bts_features(client_id: str, client_secret: str, params:Sequence) -> Any :

    #가수목록 가져오기
    headers = get_access_token(client_id, client_secret)
    endpoint = "https://api.spotify.com/v1/audio-features"
    query_params = params

    # 1차 에러 핸들링 try - catch
    try:
        info = requests.get(url=endpoint, headers=headers, params=query_params)

    except:
        logging.error(info.text)
        sys.exit(0)

    #2차 에러 핸들링
    if info.status_code != 200:
        logging.error(json.loads(info.text))
        # 1. 데이터 전송이 기준치 초과
        if info.status_code == 429:
            retry = json.loads(info.headers)['retry-After']
            time.sleep(int(retry))

            info = requests.get(url=endpoint, headers=headers, params=query_params)
        # 2. 접속 에러
        elif info.status_code == 401:

            headers = get_access_token(client_id, client_secret)
            info = requests.get(url=endpoint, headers=headers, params=query_params)
        else:
            sys.exit(1)

    feature_infos = json.loads(info.text)
    feature = []
    feature.extend(feature_infos['audio_features'])

    return feature

# access token 얻기
def get_access_token(client_id: str, client_secret: str) -> Any :
    # 1. access token 을 얻기 위한 인증절차
    endpoint = "https://accounts.spotify.com/api/token"
    encoded = base64.b64encode(f'{client_id}:{client_secret}'.encode('UTF-8')).decode()
    headers = {"Authorization" : f'Basic {encoded}'}
    body = {"grant_type" : "client_credentials"}
    access_info = requests.post(url=endpoint, headers=headers, data=body)

    access_token = json.loads(access_info.text)['access_token']
    #print(access_token)

    # 2. web api 얻기위한 형태로 체인지
    get_access_token = {"Authorization" : f'Bearer {access_token}'}
    return get_access_token



if __name__ == "__main__":

    #mysql 연결시키기
    host = 'localhost'
    port = 3306
    username = 'root'
    password = "jinwon15"
    database = "btsalbum"

    # 에러 체크
    try:
        conn = pymysql.connect(host=host, user=username, passwd=password, db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("could not connect mysql")
        sys.exit(1)

    # albums 에 저장된 앨범 아이디들 리스트로 가져오기
    select_query = 'select track_id from tracks'
    cursor.execute(select_query)

    rows = cursor.fetchall()
    track_list = []
    for row in rows:
        row = list(row)
        track_list.extend(row)

    print(track_list)

    # api authentication
    client_id = "aacad961f47a4eea8870140406fd0d88"
    client_secret = "2634a4b3b13a4c36a7e53819400623b8"

    features = []

    for i in track_list:
        params = {
            "ids": i
        }
        tracks = get_bts_features(client_id, client_secret, params)
        id = tracks[0]['id']
        print(id)
        tempo = tracks[0]['tempo']
        valence = tracks[0]['valence']
        liveness = tracks[0]['liveness']
        acousticness = tracks[0]['acousticness']
        speechiness = tracks[0]['speechiness']
        danceability = tracks[0]['danceability']
        energy = tracks[0]['energy']
        loudness = tracks[0]['loudness']
        instrumentalness = tracks[0]['instrumentalness']

        features.append([id, tempo, valence, liveness, acousticness, speechiness, danceability, energy, loudness, instrumentalness])
        insert_query = 'insert ignore into features (id, tempo, valence, liveness, acousticness, speechiness, danceability, energy, loudness, instrumentalness) ' \
                       'values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'. \
            format(id, tempo, valence, liveness, acousticness, speechiness, danceability, energy, loudness,instrumentalness)
        cursor.execute(insert_query)
        conn.commit()








