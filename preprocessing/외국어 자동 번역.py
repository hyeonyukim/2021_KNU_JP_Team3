"""
Anaconda 가상환경 필수
python 3.6 , selenium , openpyxl , xlrd == 1.2.0 , pandas , emoji 설치 후 실행
chromedriver 필요
번역할 파일에 반드시 'reviews' 열이 있어야함
"""

import multiprocessing
from multiprocessing import Manager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import emoji

BACKSPACE='/ue003'
ENTER='/ue007'
TAB='/ue004'
import pandas as pd
import time

# --------------     set argument     --------------
ChromeDriver_Path = ''
input_Path = '.xlsx'
output_Path = '.xlsx'
URL = 'https://translate.google.co.kr/?hl=ko&tab=TT&sl=auto&tl=ko&op=translate'
# --------------     Chrome Options    --------------
options = webdriver.ChromeOptions()
# Hide Chrome Window #
# options.add_argument('headless')
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")

def genReviewList():
    df = pd.read_excel(input_Path)
    df_raw = df['reviews']
    raw_reviews = df_raw.tolist()
    return raw_reviews

def remove_emoji(text):
    return emoji.get_emoji_regexp().sub(u'', text)

def translate():
    raw_reviews = genReviewList()
    driver = webdriver.Chrome(ChromeDriver_Path)
    driver.get(URL)
    driver.implicitly_wait(5)
    input = driver.find_element_by_xpath('//textarea[@aria-label="원본 텍스트"]')
    translated_reviews = list()
    print('#------------------------ 번역 시작 -------------------------')
    for review in raw_reviews:
        input.click()
        input.send_keys(remove_emoji(review))
        time.sleep(1.3)
        translated_reviews.append(driver.find_element_by_xpath('//div[@class="zkZ4Kc dHeVVb"]').get_attribute('data-text'))
        print('번역 결과 : ' + driver.find_element_by_xpath('//div[@class="zkZ4Kc dHeVVb"]').get_attribute('data-text'))
        # 히브리어로 인한 예외발생
        # driver.find_element_by_xpath('//button[@class="VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ q7sDqe GA2I6e"]').click()
        input.clear()
    df_kor = pd.DataFrame(translated_reviews, columns=['translated'])
    df_kor.to_excel(output_Path)

translate()
