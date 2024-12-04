# トライアル版スクリプト
key_word = '時計 tag heuer'

from selenimuContorller import selenimuContorller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
import time
import json

ctrl = selenimuContorller()

# メルカリトップページ
# 「お使いのブラウザがWebサイトに対応していない、または最新版でない可能性があります。…」
# と表示される ★ToDo★ 表示されないように対応すること
ctrl.getUrl('https://jp.mercari.com/')

# 横幅が狭いときに検索キーワードの入力できないため横幅広げる
ctrl.driver.set_window_size(1048, 1048)

# 検索キーワード入力＋「Enter」キー押す
ctrl.wait(10, By.XPATH, '//input[@aria-label="検索キーワードを入力"]') # 要素表示するまで待つ
ctrl.send_keys(By.XPATH, '//input[@aria-label="検索キーワードを入力"]', key_word + Keys.ENTER)

# ソート順を「新しい順」に変更
time.sleep(5)   # 入力可能かどうか？をwaitにする ★ToDo★
ctrl.select_by_index(By.XPATH,
    '//select[@name="sortOrder"]',
    1)

time.sleep(5)   # スクロール可能かどうか？をwaitする ★ToDo★

# ★ToDo★ パッケージに昇格 下までスクロールすると全件表示できない
height = ctrl.driver.execute_script("return document.body.scrollHeight")
for x in range(1, height):
    ctrl.driver.execute_script("window.scrollTo(0, " + str(x) + ");")

time.sleep(5)   # 商品情報がすべて表示されているかどうか？をwaitする ★ToDo★

data = []
items = ctrl.driver.find_elements(By.XPATH, '//li[@data-testid="item-cell"]//a')
for item in items:
    # 商品詳細ページURL
    url_detail = item.get_attribute('href')
    # 商品名と価格
    name_price = item.find_element(By.XPATH, 'div').get_attribute('aria-label')
    # メルカリID
    mercari_id = item.find_element(By.XPATH, 'div').get_attribute('id')
    # サムネイル画像URL
    thumb_url = item.find_element(By.XPATH, './/img').get_attribute('src')

    data.append(
        {
            'mercari_id' : mercari_id,
            'url_detail' : url_detail,
            'name_price' : name_price,
            'thumb_url'  : thumb_url,
        }   
    )

# 一覧ページのスクレイピング結果表示
print(json.dumps(data, indent=4, ensure_ascii = False))

# 詳細ページ
for link in data:
    # データ初期化
    url_detail = link['url_detail']
    name = ''
    price = ''
    desc = ''
    img_url = []

    # 詳細ページ
    ctrl.getUrl(url_detail)
    try:
        ctrl.wait(10, By.XPATH, '//*[@data-testid="description"]') # 要素表示するまで待つ
    except Exception as e:
        continue
        # ★ToDo★ リトライとリトライアウトの組み込み

    if ('/item/' in url_detail):
        # 商品名
        name = ctrl.driver.find_element(By.XPATH, '//*[@data-testid="name"]//h1').get_attribute('textContent')
        # 価格
        price = ctrl.driver.find_element(By.XPATH, '//*[@data-testid="price"]').get_attribute('textContent')

    else:
        # 商品名
        name = ctrl.driver.find_element(By.XPATH, '//*[@data-testid="display-name"]//h1').get_attribute('textContent')
        # 価格
        price = ctrl.driver.find_element(By.XPATH, '//*[@data-testid="product-price"]').get_attribute('textContent')

    # 商品説明
    desc = ctrl.driver.find_element(By.XPATH, '//*[@data-testid="description"]').get_attribute('textContent')
    
    # 画像URL
    els = ctrl.driver.find_elements(By.XPATH, '//*[@data-testid="carousel-item"]//img')
    for el in els:
        img_url.append(el.get_attribute('src'))

    data = {
            'url_detail' : url_detail,
            'name'       : name,
            'price'      : price,
            'desc'       : desc,
            'img_url'    : img_url,
        }
    
    # 詳細ページのスクレイピング結果の表示
    print(json.dumps(data, indent=4, ensure_ascii = False))
    
ctrl.close()