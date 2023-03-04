import pandas as pd
import numpy as np
import csv
import re
import nltk
#nltk.download('vader_lexicon')
#nltk.download('stopwords')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



############################################## data Pre-processing: tokenization, stemming, and removal of stop words

cleaned_comments = pd.read_csv(r'...\\cleaned_comments.csv', encoding='utf-8-sig')

# change to lower case
cleaned_comments['review_text'] = cleaned_comments['review_text'].str.lower()

# Tokenization
def identify_tokens(row):
    review = row['review_text']
    tokens = nltk.word_tokenize(review)
    token_words = [w for w in tokens if w.isalpha()]
    return token_words
cleaned_comments['words'] = cleaned_comments.apply(identify_tokens, axis=1)

# Stemming
stemming = PorterStemmer()
def stem_list(row):
    my_list = row['words']
    stemmed_list = [stemming.stem(word) for word in my_list]
    return (stemmed_list)
cleaned_comments['stemmed_words'] = cleaned_comments.apply(stem_list, axis=1)

# Removing stop words
stops = set(stopwords.words("english"))
def remove_stops(row):
    my_list = row['stemmed_words']
    meaningful_words = [w for w in my_list if not w in stops]
    return (meaningful_words)
cleaned_comments['stem_meaningful'] = cleaned_comments.apply(remove_stops, axis=1)

# Rejoin words
def rejoin_words(row):
    my_list = row['stem_meaningful']
    joined_words = ( " ".join(my_list))
    return joined_words
cleaned_comments['processed'] = cleaned_comments.apply(rejoin_words, axis=1)
cleaned_comments['processed'] = cleaned_comments['processed'].astype('str')

# sentiment analysis
cleaned_comments['scores'] = cleaned_comments['processed'].apply(lambda processed: sid.polarity_scores(processed))
cleaned_comments['compound']  = cleaned_comments['scores'].apply(lambda score_dict: score_dict['compound'])
cleaned_comments['comp_score'] = cleaned_comments['compound'].apply(lambda c: 'pos' if c >=0 else 'neg')


# save sentiment analysis results
cleaned_comments.to_csv(r'...\\sentiment_analysis_results.csv', encoding='utf-8-sig')

