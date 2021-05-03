"""
Anaconda 가상환경 필수
python 3.6 , selenium , openpyxl , xlrd == 1.2.0 , pandas 설치 후 실행
chromedriver 필요
"""

import multiprocessing
from multiprocessing import Manager
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time, re
import pandas as pd

# --------------     set argument     --------------
ChromeDriver_Path = 'C:/경로/chromedriver.exe'
SaveFile_Path = 'C:/경로/test.xlsx'
min_reviewCnt = 5
MaxTread = 8     # Parameter value of Pool => CPU Thread Count x 2 가 최대
Trip_attr_URL = 'https://www.tripadvisor.co.kr/Attractions-g297886-Activities-Daegu.html'
# -------------- Chrome Options  --------------
options = webdriver.ChromeOptions()
# Hide Chrome Window #
options.add_argument('headless')
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")


def attraction_urls(MinReviews):
    driver = webdriver.Chrome(ChromeDriver_Path, options=options)
    driver.get(Trip_attr_URL)
    urls = list()

    print('#-------------------------- URL 리스트 받아오기 --------------------------------#')
    driver.implicitly_wait(15)
    time.sleep(2)
    ## 주기적인 경로 변경 필수 ##
    driver.find_element_by_xpath('//button[@class="_3L3LNeQW _3UmqBW4M _39EfpzKn UXe6zT9I"]').click()
    time.sleep(8)
    # 현재 페이지에 있는 모든 즐길거리 긁어오기
    for Page in driver.find_elements_by_xpath('//div[@class="_27vELSNT"]'):
        # 해당 즐길거리의 리뷰 개수를 읽어서 정수로 변환
        ReviewCnt = int(re.sub('[^0-9]', '', Page.find_element_by_xpath('.//span[@class="DrjyGw-P _26S7gyB4 _14_buatE _1dimhEoy"]').text))
        # 리뷰 갯수가 기준점을 넘는 경우 url 리스트에 추가
        if ReviewCnt >= MinReviews:
            PageUrl = Page.find_element_by_xpath('.//div[@class="_3W_31Rvp _1nUIPWja _17LAEUXp _2b3s5IMB"]/a').get_attribute("href")
            urls.append(PageUrl)
            print(PageUrl)
        else:
            print('리뷰 갯수 부족')
    # 다음 페이지로 이동
    driver.find_element_by_xpath('//a[@class="_23XJjgWS _1hF7hP_9 _2QvUxWyA"]').click()
    driver.implicitly_wait(10)
    # 두번째 페이지부터는 첫번째와는 페이지 양식이 다름 #
    while True:
        # 현재 페이지에 있는 모든 즐길거리 긁어오기

        for Page in driver.find_elements_by_xpath('//div[@class="_27vELSNT"]'):
            # 해당 즐길거리의 리뷰 개수를 읽어서 정수로 변환
            if "건의 리뷰" in Page.text: #<<<<<<<<<<<<<<<<<<<<<<< 여기서부터 수정해야함 하 시발 진짜 누가 또 사이트 구조 바꿔놨냐 시부레
                reviewTxt = Page.find_element_by_xpath(
                    './/span[@class="DrjyGw-P _26S7gyB4 _14_buatE _1dimhEoy"]').text
                reviewCnt = int(re.sub('[^a-zA-Z0-9]', '', reviewTxt).strip())
                # 리뷰 갯수가 기준점을 넘는 경우 url 리스트에 추가
                if reviewCnt >= MinReviews:
                    PageUrl = Page.find_element_by_xpath('.//a[@class="_1QKQOve4"]').get_attribute("href")
                    urls.append(PageUrl)
                    print(PageUrl)
                else:
                    print('리뷰 갯수 부족')
        try:
            driver.find_element_by_xpath('//a[@class="ui_button nav next primary "]').click()
            time.sleep(3)
        except:
            driver.quit()
            return urls

def CrawlPage(result_list, link):
    driver = webdriver.Chrome(ChromeDriver_Path, options=options)
    driver.get(link)
    driver.implicitly_wait(60)

    AttrName = driver.find_element_by_id("HEADING").text
    try:
        Address = driver.find_element_by_xpath('//div[@class="LjCWTZdN"]/span[2]').text
    except:
        Address = '제공되지 않음'
    # 전체언어로 설정
    driver.find_element_by_xpath('//li[@class="ui_radio _3gEj_Jb5"]').click()
    time.sleep(3)

    while True:
        for review in driver.find_elements_by_xpath('//div[@class="Dq9MAugU T870kzTX LnVzGwUB"]'):
            if ('Google 번역기' in review.text) or ('번역 평가하기' in review.text):
                temp = list()
                # 이름
                temp.append(AttrName)
                # 방문 날짜
                try:
                    temp.append(review.find_element_by_xpath('.//span[@class="_34Xs-BQm"]').text[7:])
                except NoSuchElementException:
                    print(AttrName + " : 여기서 에러남")
                    temp.append('0000년 0월')
                # 리뷰
                temp.append(review.find_element_by_xpath('.//a[@class="ocfR3SKN"]/span/span').text + ' ' + \
                            review.find_element_by_xpath('.//q[@class="IRsGHoPm"]/span').text)

                # 별점
                temp.append(float(review.find_element_by_xpath('.//div[@class="nf9vGX55"]/span')\
                                  .get_attribute('class')[-2:]) / 10.0)
                # 주소
                temp.append(Address)
                # 외국인 체크
                temp.append(1)
                # 결과 리스트에 저장
                result_list.append(temp)
                print(temp)
            # Go to the next review
        try:
            driver.find_element_by_xpath('//a[@class="ui_button nav next primary "]').click()
            time.sleep(3)
        # last review page
        except:
            driver.quit()
            break

if __name__ == "__main__":
    # Read url
    print(min_reviewCnt)
    urls = attraction_urls(min_reviewCnt)
    print('#################### Start Crawling ########################')
    # Performance measurement
    start = time.time()
    # Parameter value of Pool => CPU Thread Count x 2
    pool = multiprocessing.Pool(MaxTread)
    # Manage Crawled Data Merge
    m1 = Manager()
    review_list = m1.list()
    pool.starmap(CrawlPage, [(review_list, link) for link in urls])
    pool.close()
    pool.join()
    print("#################        Crawling time : %s     #################" % (time.time()-start))
    df_out = pd.DataFrame(list(review_list), columns=['name', 'date', 'reviews', 'stars', 'address', 'is foreigner'])
    df_out.to_excel(SaveFile_Path)
