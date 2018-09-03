import os
from flask import Flask, render_template, request, redirect, session, url_for

import vk_adapter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'MY_SECRET_KEY'
app.debug = False


CLIENT_ID = '6679398'
CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or 'hazGa7YPdcoNhj1T6fkO'
REDIRECT_URI = 'http://192.168.0.102:5000/oauth'
VERSION = '5.84'


@app.route('/', methods=['GET'])
def index():
    """
    Если у пользователя нет сессии с access_token, то рендерим страницу с кнопкой, иначе - страницу с друзьями
    """
    user_id, access_token = session.get('user_id'), session.get('access_token')
    if not (user_id and access_token):
        url = vk_adapter.get_oauth_url(CLIENT_ID, REDIRECT_URI)
        return render_template('index.html', url=url)
    vk = vk_adapter.VkAdapter(user_id, access_token, VERSION)
    user = vk.users_get([user_id], 'photo_100')[0]
    friends = vk.friend_list()
    return render_template('friends.html', user=user, friends=friends)


@app.route('/oauth', methods=['GET'])
def oauth():
    """
    Получаем access_token и user_id и сохраняем их в сессии
    """
    code = request.args.get('code', None)
    if not code:
        return redirect(url_for('index'))
    user_id, access_token = vk_adapter.auth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, code)
    if user_id and access_token:
        session['user_id'], session['access_token'] = user_id, access_token
    return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    """
    Очищаем сессии
    """
    session.pop('user_id')
    session.pop('access_token')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
