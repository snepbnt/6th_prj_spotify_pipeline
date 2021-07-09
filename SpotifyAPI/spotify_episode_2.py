
from typing import Any, Sequence
import requests
import sys
import base64
import json
import logging
import time
import pymysql

def get_bts_episode(client_id : str, client_secret: str, params: Sequence) -> Any:

    # 앨범 목록 가져오기
    headers = get_access_token(client_id, client_secret)
    endpoint = "https://api.spotify.com/v1/episodes"
    query_params = params

    # 1차 에러 핸들링 try - catch
    try:
        info = requests.get(url=endpoint, headers=headers, params=query_params)

    except:
        logging.error(info.text)
        sys.exit(0)

    # 2차 에러 핸들링
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

    episode_infos = json.loads(info.text)
    episode = []
    #episode.extend(episode_infos['audio_features'])

    return episode_infos



# access token 얻기
def get_access_token(client_id: str, client_secret: str) -> Any:
    # 1. access 토큰 얻기위한 인증 전차
    endpoint = "https://accounts.spotify.com/api/token"
    encoded = base64.b64encode(f'{client_id}:{client_secret}'.encode('UTF-8')).decode()
    headers = {"Authorization": f'Basic {encoded}'}
    body = {"grant_type": "client_credentials"}
    access_info = requests.post(url=endpoint, headers=headers, data=body)

    access_token = json.loads(access_info.text)['access_token']
    print(access_token)

    # 2. web api 얻기위한 형태로 체인지
    get_access_token = {"Authorization": f'Bearer {access_token}'}
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
    select_query = 'select distinct("00EpTcZPrp4vNv8aToYBpv") from tracks'
    cursor.execute(select_query)

    rows = cursor.fetchall()
    track_list = []
    for row in rows:
        row = list(row)
        track_list.extend(row)

    print(track_list)

    # api authentication
    client_id = "spotify_id"
    client_secret = "spotify_pwd"
    params = {"ids" : "512ojhOuo1ktJprKbVcKyQ"}

    episodes = get_bts_episode(client_id, client_secret, params)

    # for i in track_list:
    #     params = {
    #         "id" : i
    #     }


    print(episodes)
