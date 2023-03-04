import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time 
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
import re

# set url address
url = "https://www.google.com/maps/..."

# open web driver
driver = selenium.webdriver.Chrome(r"...\chromedriver.exe")
driver.get(url)
time.sleep(5)

# open url
wait = WebDriverWait(driver, 10)

# sort comments by relevant
menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, "//body/jsl[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[7]/div[2]/div[1]/button[1]")))  
menu_bt.click()
time.sleep(5)
recent_rating_bt = driver.find_elements_by_xpath("//body/jsl[1]/div[3]/div[4]/div[1]/ul[1]/li[1]")[0]
recent_rating_bt.click()
time.sleep(5)

# scroll review box
for _ in range(10): #in each scroll 10 new comments will be showed
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',driver.find_element_by_css_selector('body.keynav-mode-off.highres.screen-mode:nth-child(2) div.vasquette.id-app-container.pane-open-mode div.id-content-container:nth-child(9) div.widget-pane.widget-pane-visible div.widget-pane-content.cYB2Ge-oHo7ed:nth-child(1) div.widget-pane-content-holder div.section-layout.section-layout-root > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc'))
    time.sleep(2.2)

# wait for load page completely (be sure for "click" on "More" will be happen)
time.sleep(5)

# click on "more" in long reviews
for _ in range(0,100):
    more_bt = driver.find_elements_by_xpath("/html[1]/body[1]/jsl[1]/div[3]/div[9]/div[7]/div[1]/div[1]/div[1]/div[1]/div[2]/div[9]/div[{}]/div[1]/div[3]/div[3]/jsl[1]/button[1]".format(m))[0]
    more_bt.click()
            
# get HTML text & extract features
response = BeautifulSoup(driver.page_source, 'html.parser')
review_text = pd.Series(response.find_all('span', class_='section-review-text')).to_frame(name='review_text')
star_rate = pd.Series(response.find_all('span', class_='section-review-stars')).to_frame(name='star_rate')
publish_review = pd.Series(response.find_all('span', class_='section-review-publish-date')).to_frame(name='publish_date')
comments = pd.concat([review_text,star_rate,publish_review] , axis=1)

# close web driver
driver.close()
   
# data cleaning
english_comments = pd.DataFrame(comments['review_text'].str.extract(r'>(.+?)</span>', re.DOTALL))
non_english_comments = pd.DataFrame(comments['review_text'].str.extract(r'\(Translated by Google\) (.+?)\(Original\)', re.DOTALL))
all_comments = non_english_comments.combine_first(english_comments)
star_rate = pd.DataFrame(comments['star_rate'].str.extract(r'aria-label=" (.+?) star'))
publish_date = pd.DataFrame(comments['publish_date'].str.extract(r'>(.+?)</span>'))
cleaned_comments = pd.concat([review_text_cleaned,star_rate_cleaned,publish_date_cleaned] , axis=1)
cleaned_comments = cleaned_comments.columns = ['review_text','star_rate','publish_date']
cleaned_comments = cleaned_comments.dropna() # remove empty reviews
cleaned_comments = cleaned_comments[cleaned_comments['review_text'].map(len) > 1] # remove one char reviews
cleaned_comments = cleaned_comments[~cleaned_comments.review_text.str.contains("(Translated by Google)")] # remove raw contain (Translated by Google)

# export cleaned data
raw_data_step_three.to_csv(r'...\\cleaned_comments.csv' ,encoding='utf-8-sig')


