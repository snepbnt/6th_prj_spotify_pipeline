
from typing import Any, Sequence
import requests
import sys
import base64
import json
import logging
import time
import pymysql

# api authentication
client_id = "client_id"
client_secret = "client_secret"
params = {
        "q" : "BTS",
        "type" : "album"
    }

def get_bts_albums(client_id: str, client_secret: str, params:Sequence) -> Any :

    #가수목록 가져오기
    headers = get_access_token(client_id, client_secret)
    endpoint = "https://api.spotify.com/v1/search"
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

    id = json.loads(info.text)['albums']['items'][0]['artists'][0]['id']
    bts_url = f'https://api.spotify.com/v1/artists/{id}/albums'
    # BTS 앨범 가져오기
    bts_get = requests.get(url=bts_url, headers=headers)
    bts_raw = json.loads(bts_get.text)
    # bts 앨범의 총 개수
    total = bts_raw['total']

    # bts 앨범 관련 정보 모두 리스트에 담기
    albums = []
    albums.extend(bts_raw['items'])

    count = 0

    while count < total and next:
        r = requests.get(url=bts_raw['next'], headers=headers)
        raw = json.loads(r.text)

        albums.extend(raw['items'])
        count = len(albums)
        if raw['next'] == None:
            break

    return albums

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
    albums = get_bts_albums(client_id, client_secret, params)
    print(len(albums))

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

    for i in range(len(albums)):
        # 필요한 데이터 추출
        ids = albums[i]['id']
        name = albums[i]['name']
        release_date = albums[i]['release_date']
        total_tracks = albums[i]['total_tracks']
        type = albums[i]['type']

        insert_query = 'insert ignore into albums (id, name, release_date, total_tracks, type) values ("{}","{}","{}","{}","{}")'.format(ids,name,release_date,total_tracks,type)
        cursor.execute(insert_query)
        conn.commit()







