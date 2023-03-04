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
import nltk
#nltk.download('vader_lexicon')
#nltk.download('stopwords')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
sid = SentimentIntensityAnalyzer()


######################################################### data scraping

country_name = "Portugal"

with open(r'D:\\Sina\\Desktop\\mac donald\\data\\urls per country\\urls_of_{}.csv'.format(country_name) ,encoding='utf-8-sig', newline='') as f:
    reader = csv.reader(f)
    data = pd.DataFrame(reader)

append_raw_data = []  
    
for n in range(0,2):
#for n in range(0,len(data)):
    try:
        # active web driver
        driver = selenium.webdriver.Chrome(r"D:\Software\chromedriver.exe")

        # get URLs
        try:
            url = data.iloc[n,0]
            driver.get(url)
            time.sleep(5)
        except: continue

        # open url
        wait = WebDriverWait(driver, 10)

        # sort by relevant
        try:
            menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, "//body/jsl[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[7]/div[2]/div[1]/button[1]")))  
            menu_bt.click()
            time.sleep(5)
            recent_rating_bt = driver.find_elements_by_xpath("//body/jsl[1]/div[3]/div[4]/div[1]/ul[1]/li[1]")[0]
            recent_rating_bt.click()
            time.sleep(5)
        except: continue

        # scroll review box
        for i in range(0,120): #in each scroll 10 new comments will be showed
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',driver.find_element_by_css_selector('body.keynav-mode-off.highres.screen-mode:nth-child(2) div.vasquette.id-app-container.pane-open-mode div.id-content-container:nth-child(9) div.widget-pane.widget-pane-visible div.widget-pane-content.cYB2Ge-oHo7ed:nth-child(1) div.widget-pane-content-holder div.section-layout.section-layout-root > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc'))
            time.sleep(2.2)

        # wait for load page completely (be sure for "click" on "More" will be happen)
        time.sleep(5)

        # click on "more" in long reviews
        for m in range(0,4000):
            try:
                more_bt = driver.find_elements_by_xpath("/html[1]/body[1]/jsl[1]/div[3]/div[9]/div[7]/div[1]/div[1]/div[1]/div[1]/div[2]/div[9]/div[{}]/div[1]/div[3]/div[3]/jsl[1]/button[1]".format(m))[0]
                more_bt.click()
            except: continue
            
        # get HTML text & extract features
        response = BeautifulSoup(driver.page_source, 'html.parser')

        review_text = pd.Series(response.find_all('span', class_='section-review-text')).to_frame(name='review_text')
        star_rate = pd.Series(response.find_all('span', class_='section-review-stars')).to_frame(name='star_rate')
        publish_review = pd.Series(response.find_all('span', class_='section-review-publish-date')).to_frame(name='publish_date')

        one_branch_raw_data = pd.concat([review_text,star_rate,publish_review] , axis=1)

        # close page
        try:
            driver.close()
        except: continue

        # append to all row data
        append_raw_data.append(one_branch_raw_data)
    
    except: continue

# concat data
concat_raw_data = pd.concat(append_raw_data)

# export concat raw data
concat_raw_data.to_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\raw data per country\\concat_raw_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')

# data cleaning
concat_raw_data = pd.read_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\raw data per country\\concat_raw_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')

review_text_english = pd.DataFrame(concat_raw_data['review_text'].str.extract(r'>(.+?)</span>', re.DOTALL))
review_text_non_english = pd.DataFrame(concat_raw_data['review_text'].str.extract(r'\(Translated by Google\) (.+?)\(Original\)', re.DOTALL))
review_text_cleaned = review_text_non_english.combine_first(review_text_english)

star_rate_cleaned = pd.DataFrame(concat_raw_data['star_rate'].str.extract(r'aria-label=" (.+?) star'))
publish_date_cleaned = pd.DataFrame(concat_raw_data['publish_date'].str.extract(r'>(.+?)</span>'))

concat_cleaned_data = pd.concat([review_text_cleaned,star_rate_cleaned,publish_date_cleaned] , axis=1)

rename_cleaned_data = concat_cleaned_data.columns = ['review_text','star_rate','publish_date']

# export data
concat_cleaned_data.to_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\raw data per country\\raw_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')


# In[2]:


############################################## data cleaning

country_name = "Austria"
raw_data = pd.read_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\raw data per country\\raw_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')

# remove empty reviews
raw_data_step_one = raw_data.dropna()

# remove one char reviews
raw_data_step_two = raw_data_step_one[raw_data_step_one['review_text'].map(len) > 1]

# remove raw contain (Translated by Google)
raw_data_step_three = raw_data_step_two[~raw_data_step_two.review_text.str.contains("(Translated by Google)")]

# export cleaned data
raw_data_step_three.to_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\cleaned data per country\\cleaned_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')


# In[100]:


############################################## data Pre-processing: tokenization, stemming, and removal of stop words

#remove this step bacause it makes corollation score more less rather than same score before pre-processing


country_name = "Vietnam"
cleaned_data = pd.read_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\cleaned data per country\\cleaned_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')

# change to lower case
cleaned_data['review_text'] = cleaned_data['review_text'].str.lower()

# Tokenization
def identify_tokens(row):
    review = row['review_text']
    tokens = nltk.word_tokenize(review)
    # taken only words with using .isalpha (not punctuation) you could use .isalnum if you wanted to keep in numbers as well
    token_words = [w for w in tokens if w.isalpha()]
    return token_words

cleaned_data['words'] = cleaned_data.apply(identify_tokens, axis=1)

# Stemming
stemming = PorterStemmer()
def stem_list(row):
    my_list = row['words']
    stemmed_list = [stemming.stem(word) for word in my_list]
    return (stemmed_list)

cleaned_data['stemmed_words'] = cleaned_data.apply(stem_list, axis=1)

# Removing stop words
stops = set(stopwords.words("english"))
def remove_stops(row):
    my_list = row['stemmed_words']
    meaningful_words = [w for w in my_list if not w in stops]
    return (meaningful_words)

cleaned_data['stem_meaningful'] = cleaned_data.apply(remove_stops, axis=1)

# Rejoin words
def rejoin_words(row):
    my_list = row['stem_meaningful']
    joined_words = ( " ".join(my_list))
    return joined_words

cleaned_data['processed'] = cleaned_data.apply(rejoin_words, axis=1)

# Save processed data
cleaned_data.to_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\pre processed data per country\\pre_processed_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')


# In[101]:


######################################################### data analyzing

country_name = "Slovenia"
analyzed_data = pd.read_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\pre processed data per country\\pre_processed_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')

#since strings data types have variable length, it is by default stored as object dtype
analyzed_data['processed'] = analyzed_data['processed'].astype('str')

# Adding Scores and Labels to the DataFrame
analyzed_data['scores'] = analyzed_data['processed'].apply(lambda processed: sid.polarity_scores(processed))
analyzed_data['compound']  = analyzed_data['scores'].apply(lambda score_dict: score_dict['compound'])
analyzed_data['comp_score'] = analyzed_data['compound'].apply(lambda c: 'pos' if c >=0 else 'neg')

analyzed_data.to_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\analyzed data per country\\analyzed_data_{}.csv'.format(country_name) ,encoding='utf-8-sig')


# In[102]:


######################################################### corrolation test

#country_name = "Vietnam"
analyzed_data = pd.read_csv(r'D:\\Sina\\Desktop\\mac donald\\data\\analyzed data per country\\analyzed_data_{}_porter_version.csv'.format(country_name) ,encoding='utf-8-sig')

# corrolation between star rate and compound
analyzed_data_corr = analyzed_data.corr(method ='pearson')
starrate_compound_corr = analyzed_data_corr.iloc[4]['compound']
starrate_compound_corr


# In[ ]:




