import json
import requests


def make_url(uri, **kwargs):
    """
    Возвращает ссылку, подставляя kwargs как части GET-запроса
    """
    url = uri + '?'
    for key, value in kwargs.items():
        url += '&' + str(key) + '=' + str(value)
    return url


def get_oauth_url(client_id, redirect_uri, version='5.84', display='page', scope='friends'):
    return make_url(
        'https://oauth.vk.com/authorize',
        client_id=client_id,
        display=display,
        redirect_uri=redirect_uri,
        scope=scope,
        v=version
    )


def auth(client_id, client_secret, redirect_uri, access_code):
    """
    Получает на вход access_code, возвращает user_id и access_token
    """
    url = make_url(
            'https://oauth.vk.com/access_token',
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            code=access_code,
        )
    vk_response = requests.get(url)
    vk_json = json.loads(vk_response.content)
    return vk_json.get('user_id'), vk_json.get('access_token')


class VkAdapter:
    """
    Интерфейс для работы с api
    """

    def __init__(self, user_id, access_token, version):
        self.user_id = user_id
        self.access_token = access_token
        self.version = version

    def friends_get(self, order, count):
        """
        Возвращает список из <count> id друзей
        """
        url = make_url(
            'https://api.vk.com/method/friends.get',
            user_id=self.user_id,
            order=order,
            count=count,
            access_token=self.access_token,
            v=self.version,
        )
        vk_response = requests.get(url)
        return json.loads(vk_response.content).get('response').get('items')

    def users_get(self, user_ids, fields):
        """
        Возвращает список словарей с информацией о друзьях
        """
        user_ids = ','.join(str(user_id) for user_id in user_ids)
        url = make_url(
            'https://api.vk.com/method/users.get',
            fields=fields,
            user_ids=user_ids,
            access_token=self.access_token,
            v=self.version,
        )
        vk_response = requests.get(url)
        return json.loads(vk_response.content).get('response')

    def friend_list(self, order='random', count='5', fields='nickname, photo_50'):
        """
        Результат для задания
        """
        friend_ids = self.friends_get(order, count)
        friends_list = self.users_get(friend_ids, fields)
        return friends_list
