import time,sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config.config import config

# Chromeオプションの設定
chrome_options = Options()
chrome_options.add_argument("--log-level=3")  # エラーレベルのログのみ表示


driver = webdriver.Chrome(options=chrome_options)

if not config.NAME  or not config.PASS :
    print("usernameまたはpasswordが入力されていません。\n")
    sys.exit()
    
def main():

    driver.get(config.login_url)

    #ログイン情報
    NAME = config.NAME
    PASS = config.PASS

    #ログインの自動化
    elem_username = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[1]/input")
    elem_username.send_keys(NAME)
    elem_password = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[2]/input")
    elem_password.send_keys(PASS)
    element_form = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[3]/button")
    try:
        element_form.click()
    except (NoSuchElementException, TimeoutException):
        print("ログインに失敗しました。認証情報やネットワークを確認してください。\n")
        driver.quit()
        sys.exit()
    dashboard_form = driver.find_element("xpath","/html/body/div[1]/div[2]/div/div[2]/section/aside/section[1]/div/div/ul/li/ul/li[1]/p/a/span")
    dashboard_form.click()

    #ダッシュボードへ移動
    event_form = driver.find_element("xpath","/html/body/div[1]/div[2]/div/div[1]/section/div/aside/section[2]/div/div/div[1]/div/div[2]/table/tbody/tr[3]/td[3]/div[1]/a")
    current_timestamp = int(time.time())

    driver.get(config.dashboard_url)

    #課題一覧を表示
    for i in range(15):
        # 課題名
        try:
            h3 = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[1]/div[3]/h3')
        except NoSuchElementException:
            # print("課題名が見つかりませんでした。ループを終了します。")
            break  # ループを終了

        # 期限
        limit = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[1]/div[2]/span/a')
        
        try:  # 詳細がない場合のハンドリング
            p = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[3]/div[2]/div/p[1]")
        except NoSuchElementException:
            print("詳細はありません\n")
        
        print("#######################################################################################################")
        print(f"~{h3.text}~")
        print("\n")
        # print(f"期限:{limit.text}")
        print(f"詳細\n:{p.text}")

    driver.quit()
main()
