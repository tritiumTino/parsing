import requests
from json import dump

# task_1

USER = 'tritiumTino'
API_URL = 'https://api.github.com/users/{user}/repos'
response = requests.get(API_URL.format(user=USER))

with open('task_1.json', 'w', encoding='utf-8') as f_obj:
    dump(response.json(), f_obj)


# task_2
"""
используемое API - API ВКонтакте
"""
TOKEN = '2f2db4e92f2db4e92f2db4e9252f5424c322f2d2f2db4e94e77a41666f28eff17d6cc5a'
API_URL = 'https://api.vk.com/method/users.get?user_ids=210700286&fields=bdate&access_token={token}&v=5.131'
response = requests.get(API_URL.format(token=TOKEN))

with open('task_2.json', 'w', encoding='utf-8') as f_obj:
    dump(response.json(), f_obj)
