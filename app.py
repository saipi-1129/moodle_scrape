import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import json
from cryptography.fernet import Fernet

# 認証情報を保存するファイルパス
credentials_file = 'credentials.json'
key_file = 'secret.key'

# 暗号化キーを生成または読み込み
def load_or_generate_key():
    if os.path.exists(key_file):
        with open(key_file, 'rb') as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as file:
            file.write(key)
        return key

key = load_or_generate_key()
cipher = Fernet(key)

def save_credentials(username, password):
    credentials = json.dumps({'username': username, 'password': password}).encode()
    encrypted_credentials = cipher.encrypt(credentials)
    with open(credentials_file, 'wb') as file:
        file.write(encrypted_credentials)

def load_credentials():
    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as file:
            encrypted_credentials = file.read()
        decrypted_credentials = cipher.decrypt(encrypted_credentials)
        return json.loads(decrypted_credentials.decode())
    return None

# 認証情報の読み込み
credentials = load_credentials()
if credentials:
    username = credentials['username']
    password = credentials['password']
else:
    username = input("ユーザーネームを入力してください:")
    password = input("パスワードを入力してください:")
    save_credentials(username, password)
#moodleのログインページを指定
login_url = ''

# 次の日のURLを生成
def get_next_day_url():
    next_day = datetime.now() + timedelta(days=1)
    timestamp = int(next_day.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    return f'https://moodle2024.mc2.osakac.ac.jp/2024/calendar/view.php?view=day&time={timestamp}'

def get_login_token(session, login_url):
    login_page = session.get(login_url)
    login_page_soup = BeautifulSoup(login_page.content, 'html.parser')
    return login_page_soup.find('input', {'name': 'logintoken'})['value']

def login(session, login_url, username, password, logintoken):
    login_data = {
        'anchor': '',
        'logintoken': logintoken,
        'username': username,
        'password': password
    }
    return session.post(login_url, data=login_data)

def scrape_events(session, target_url):
    response = session.get(target_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all('div', class_='event')

def print_event_details(events):
    for event in events:
        title = event.find('h3', class_='name').get_text()
        date_time = event.find('div', class_='col-11').find('a').get_text()
        
        description_tag = event.find('div', class_='description-content')
        description = description_tag.get_text(strip=True) if description_tag else '説明なし'
        
        course = event.find_all('div', class_='col-11')[-1].find('a').get_text()
        
        print('タイトル:', title)
        print('日時:', date_time)
        print('詳細:', description)
        print('コース:', course)
        print('-' * 20)

def main():
    session = requests.Session()
    logintoken = get_login_token(session, login_url)
    login_response = login(session, login_url, username, password, logintoken)

    if 'あなたはログインしていません' in login_response.text:
        print('ログインに失敗しました。認証情報を確認してください。')
    else:
        print('ログインに成功しました。')
        target_url = get_next_day_url()
        events = scrape_events(session, target_url)
        print_event_details(events)

if __name__ == '__main__':
    main()
