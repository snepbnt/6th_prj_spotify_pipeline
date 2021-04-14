
import tweepy

# 트위터 계정에서 토큰 가져오기
consumer_key = "YfyoxwdnsVZIYWhDHgGhHSG1B" # api key
comsumer_secret = "B4LmE5VJLKGfJsm4sYjiZRULeVWIxRZT7IjDEMeWQnORNT5IV1" # api secret key
access_token = "1381615798158958593-Ac12ve0Y4uwUb0RJR5bwSD0qODUvgh"
access_token_secret = "FjJxEcVcjriDK3upZQVXNWqBicF3ZQzxqOM2PcrAryrb6"

# 계정 승인
auth = tweepy.OAuthHandler(consumer_key=consumer_key, consumer_secret=comsumer_secret)
api = tweepy.API(auth)

result = []
for tweet in tweepy.Cursor(api.search, q="BTS", since="2021-04-10", count = 1, language=["kr"]).items():
    result.append(tweet)
    print(result)
print(len(result))

# 데이터 가공 후에 rebbitmq 로 연결하여 스트림한다음에 nosql 에 담을 수 있는지 연구해보자

# rebbit mq 연결