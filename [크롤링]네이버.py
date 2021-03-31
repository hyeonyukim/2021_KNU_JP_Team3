#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("Enter keyword you'd like to crawl")
keyword = input()


# In[11]:


import requests
from urllib.request import Request
import urllib.parse as parse
import urllib.request as request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains as AC
import json
import time
import pandas as pd


# In[12]:


def getNaverURLs(keyword, driver):
    page=1
    naverURLs = list()
    idDict = dict()
    latitudes = list()
    longtitudes = list()
    addresses = list()
    names = list()
    
    while(True):
        url = ('https://map.naver.com/v5/api/search?caller=pcweb&query='+keyword+
               '&type=restaurant&searchCoord=128.4675979614258;35.871525056258626&page='+str(page)+
               '&displayCount=10&isPlaceRecommendationReplace=true&lang=ko')
#         print('url-->')
#         print(url)
        driver.get(url)
        
        #for page in count(1):
        response = driver.page_source
        soup = BeautifulSoup(response,'html.parser')
#         print('response-->')
#         print(soup.text)
        
        JSON=json.loads(soup.text)
        if(JSON.get('error')==None):
            print('Reading page',page)
            searchResult = JSON.get('result').get('place').get('list')
            for item in searchResult:
                itemID = item.get('id')
#                 name = item.get('name')
                longtitude = item.get('x')
                latitude = item.get('y')
                address = item.get('address')
                name = item.get('name')
                
                if not(itemID in idDict):
                    reviewURL = 'https://pcmap.place.naver.com/restaurant/'+itemID+'/review/visitor?entry=pll&from=map'
                    naverURLs.append(reviewURL)
                    idDict[itemID] = True
                    longtitudes.append(longtitude)
                    latitudes.append(latitude)
                    addresses.append(address)
                    names.append(name)
            page = page + 1
            
        else:
            break
    return naverURLs, latitudes, longtitudes, addresses, names


# In[37]:


import pandas as pd

def getlink(url, longtitude, latitude, address, name, driver):
    driver.get(url)
    
    df = pd.DataFrame(columns=['date','reviews','stars', 'category', 'address','lat', 'lng','name'])
    
    #clickCnt=0
    count = 0 
    while count<80:
        try: 
            a = driver.find_element_by_css_selector("a._3iTUo")
            if a.get_attribute('href')[:-1]!=driver.current_url:
                print('except: no 더보기 button')
                return df
            a.click()
            count=count+1
            
            time.sleep(1)
        except:
            break
    try:
        stars = driver.find_elements_by_xpath("//span[@class='_2tObC']")
        reviews = driver.find_elements_by_xpath("//span[@class='WoYOw']")
        date_div = driver.find_elements_by_xpath("//div[@class='ZvQ8X']")
        date = [item.find_element_by_xpath(".//span[@class='_3WqoL']") for item in date_div]
        category = driver.find_element_by_xpath("//span[@class='_3ocDE']")
        #name = driver.find_element_by_xpath("//span[@class='_3XamX']")
        #print(name.text)
        datas = driver.find_elements_by_xpath("//div[@class='_1Z_GL']")
    except:
        return df
        
#         date = [] 
#         for i, item in enumerate(date_raw):
#             if i%3==0:
#                 date.append(item)
                
#         print(len(date), len(stars))

    reviews_str = list()
    stars_str = list()
    date_str = list()
    
    for i in range(0, len(reviews)):
        reviews_str.append(reviews[i].text)
    for i in range(0, len(stars)):
        stars_str.append(stars[i].text)
    for i in range(0, len(date)):
        date_str.append(date[i].text)
    
    for i in range(0, len(datas)):
        if datas[i].get_attribute('innerHTML').find('WoYOw')==-1:
            reviews_str.insert(i, "")
#             if datas[i].get_attribute('innerHTML').find('_2tObC')==-1:
#                 stars_str.insert(i, "")
    
    #df['names']=name.text
    df['date']=date_str
    
    df['reviews']=reviews_str
    
    df['stars']=stars_str
    df['category']=category.text
    df['address']=address
    df['lat']=latitude
    df['lng']=longtitude
    df['name'] = name
    return df


# In[64]:


#driver = webdriver.Chrome()
driver = webdriver.Chrome('/Users/ji_brisbane/downloads/chromedriver-2')
driver.implicitly_wait(3)
naverURLs, addresses, latitudes, longtitudes, names = getNaverURLs(keyword, driver)


# In[65]:


len(naverURLs), len(addresses), len(latitudes), len(longtitudes), len(names)


# In[66]:


naverURLs


# In[67]:


df = getlink(naverURLs[1], addresses[1], latitudes[1], longtitudes[1], names[1], driver)


# In[68]:


df


# In[74]:


driver = webdriver.Chrome('/Users/ji_brisbane/downloads/chromedriver-2')
driver.implicitly_wait(3)
df = pd.DataFrame(columns=['date','reviews','stars', 'category','location', 'address','lat', 'lng'])
for i in range(0, len(naverURLs)):
    df = pd.concat([df, getlink(naverURLs[i], longtitudes[i], latitudes[i], addresses[i], driver)], ignore_index = True)


# In[59]:


df.to_csv("대구-명소.csv", index=False, encoding='cp949')


# In[ ]:





# In[ ]:




