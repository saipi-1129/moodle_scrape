from flask import Flask, render_template, request, session, redirect, url_for
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from config.config import config

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 

def get_moodle_data(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(config.login_url)

        # ログインの自動化
        elem_username = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[1]/input")
        elem_username.send_keys(username)
        elem_password = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[2]/input")
        elem_password.send_keys(password)
        element_form = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/section/div/div/div/div/form/div[3]/button")
        element_form.click()

        driver.get(config.dashboard_url)

        assignments = []
        for i in range(15):
            try:
                h3 = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[1]/div[3]/h3')
                assignment = {"name": h3.text}


                try:
                    limit = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[1]/div[2]/span/a')
                    assignment["deadline"] = limit.text
                except NoSuchElementException:
                    assignment["deadline"] = "N/A"
                if assignment["deadline"] == "N/A":
                    try:
                        deadline = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[1]/div[2]/a')
                        assignment["deadline"] = deadline.text
                    except NoSuchElementException:
                        pass

                assignment["jyugyou"] = "N/A"
                for n in [3, 4]:
                    try:
                        jyugyou = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[{n}]/div[2]/a')
                        assignment["jyugyou"] = jyugyou.text
                        break
                    except NoSuchElementException:
                        continue
                
                if assignment["jyugyou"] == "N/A":
                    try:
                        jyugyou = driver.find_element("xpath", f'/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[3]/div[2]/a')
                        assignment["jyugyou"] = jyugyou.text
                    except NoSuchElementException:
                        pass

                assignment["details"] = "N/A"
                try:
                    p = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[3]/div[2]/div/p")
                    assignment["details"] = p.text
                except NoSuchElementException:
                    pass
                
                if assignment["details"] == "N/A":
                    try:
                        p = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[3]/div[2]/div/p[2]")
                        assignment["details"] = p.text
                    except NoSuchElementException:
                        pass

                try:
                    a_element = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/section/div/div/div[1]/div/div[2]/div[2]/div[{i + 1}]/div/div[2]/div[3]/div[2]/a")
                    assignment["url"] = a_element.get_attribute("href")
                except NoSuchElementException:
                    assignment["url"] = "N/A"


                assignments.append(assignment)

            except NoSuchElementException:
                break

        return assignments

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password
        return redirect(url_for('assignments'))
    return render_template('login.html')

@app.route('/assignments')
def assignments():
    if 'username' in session and 'password' in session:
        assignments = get_moodle_data(session['username'], session['password'])
        return render_template('assignments.html', assignments=assignments)
    return redirect(url_for('index'))

@app.route('/404')
def not_found():
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
