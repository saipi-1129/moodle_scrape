from flask import Flask, jsonify, request, render_template, redirect, url_for  # render_templateをインポート
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # ログインページを表示

@app.route('/fetch_assignments', methods=['POST'])  # POSTメソッドを使用
def fetch_assignments():
    print("fetch_assignmentsが呼び出されました")  # デバッグ用
    data = request.json  # JSONデータを取得
    NAME = data.get("user_id")  # ユーザー名を取得
    PASS = data.get("password")  # パスワードを取得

    driver = webdriver.Chrome()
    driver.get("https://moodle2024.mc2.osakac.ac.jp/2024/login/index.php")

    # ログインの自動化
    elem_username = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[1]/input")
    elem_username.send_keys(NAME)
    elem_password = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[2]/input")
    elem_password.send_keys(PASS)
    element_form = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[3]/button")
    element_form.click()
    dashboard_form = driver.find_element("xpath","/html/body/div[1]/div[2]/div/div[2]/section/aside/section[1]/div/div/ul/li/ul/li[1]/p/a/span")
    dashboard_form.click()

    # ダッシュボードへ移動
    driver.get("https://moodle2024.mc2.osakac.ac.jp/2024/calendar/view.php?view=day&time=1729004400")

    assignments = []  # 課題を格納するリスト

    # 課題一覧を表示
    for i in range(10):
        try:
            # 課題名
            h3 = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[1]/div[3]/h3')
            # 期限
            limit = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[1]/div[2]/span/a')
            # 詳細
            try:
                p = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[3]/div[2]/div/p[1]")
                detail = p.text
            except NoSuchElementException:
                detail = "詳細はありません"

            assignments.append({
                "title": h3.text,
                "limit": limit.text,
                "detail": detail
            })
        except NoSuchElementException:
            continue

    driver.quit()  # ドライバーを終了

    # 課題のリストをJSON形式で返す
    return jsonify(assignments)  # 課題のリストをJSON形式で返す

@app.route('/kadai')
def kadai():
    return render_template('kadai.html')  # 課題リストを表示するページ

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  