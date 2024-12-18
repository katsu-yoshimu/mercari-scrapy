# トライアル版スクリプト
key_word = '時計 tag heuer'

from selenimuContorller import selenimuContorller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

ctrl = selenimuContorller()

# メルカリトップページ
# 「お使いのブラウザがWebサイトに対応していない、または最新版でない可能性があります。…」
# と表示される ★ToDo★ 表示されないように対応すること → これは分からない。リクエストヘッダは同じはず
ctrl.getUrl('https://jp.mercari.com/')

# 横幅が狭いときに検索キーワードの入力できないため横幅広げる
ctrl.driver.set_window_size(1048, 1048)

# 検索キーワード入力＋「Enter」キー押す
ctrl.wait(10, By.XPATH, '//input[@aria-label="検索キーワードを入力"]')
ctrl.send_keys(By.XPATH, '//input[@aria-label="検索キーワードを入力"]', key_word + Keys.ENTER)

# ソート順を「新しい順」に変更
ctrl.wait(10, By.XPATH, '//select[@name="sortOrder"]')
ctrl.select_by_index(By.XPATH, '//select[@name="sortOrder"]', 1)

time.sleep(10)   # このwaitは必要。早くスクロールを開始すると「おすすめ順」に戻ることがある

# 「新しい順」になっていなければエラーメッセージを出力して異常終了
sort_order = ctrl.driver.find_element(By.XPATH, '//select[@name="sortOrder"]').get_attribute('value')
if 'created_time:desc' != sort_order:
    raise Exception(f'ソート順=[{sort_order}]が「新しい順=created_time:desc」でない')

# 下までスクロールする。そうしないと全件表示できない
ctrl.scroll(4)

# 「次へ」リンクの有無判定 1:リンクあり/0：リンクなし
next_link_count = ctrl.get_element_count(By.XPATH, '//a[contains(text(), "次へ")]')

# 一覧データの取得
data = []
items = ctrl.driver.find_elements(By.XPATH, '//li[@data-testid="item-cell"]//a')
for item in items:
    # 商品詳細ページURL
    detail_url = item.get_attribute('href')
    # 商品名と価格
    name_price = item.find_element(By.XPATH, 'div').get_attribute('aria-label')
    # メルカリID
    mercari_id = item.find_element(By.XPATH, 'div').get_attribute('id')
    # サムネイル画像URL
    thumb_url = item.find_element(By.XPATH, './/img').get_attribute('src')

    data.append(
        {
            'mercari_id' : mercari_id,
            'detail_url' : detail_url,
            'name_price' : name_price,
            'thumb_url'  : thumb_url,
        }   
    )

data_detail = []
# 詳細ページ
data_count = len(data)
for i, link in enumerate(data):
    print(f'商品詳細ページ取得[{i+1}/{data_count}]回')

    # データ初期化
    detail_url = link['detail_url']
    name = ''
    price = ''
    desc = ''
    img_url = []

    # 詳細ページ
    ctrl.getUrl(detail_url)
    try:
        ctrl.wait(10, By.XPATH, '//*[@data-testid="description"]') # 要素表示するまで待つ
    except Exception as e:
        continue
        # ★ToDo★ リトライとリトライアウトの組み込み

    if ('/item/' in detail_url):
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

    data_detail.append({
            'detail_url' : detail_url,
            'name'       : name,
            'price'      : price,
            'desc'       : desc,
            'img_urls'    : img_url,
        })

# ブラウザ閉じる  
ctrl.close()

import os
import sys
# カレントディレクトリ変更
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Excel出力
from outputExcel import outputExcel
outputExcel(key_word, data, data_detail)