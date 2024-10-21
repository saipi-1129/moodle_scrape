import selenium

print(selenium.__version__)

chrome_options = Options()
chrome_options.add_argument("--log-level=3")  # エラーレベルのログのみ表示


driver = webdriver.Chrome(options=chrome_options)


