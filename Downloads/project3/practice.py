import praw # imports praw for reddit access
import pandas as pd # imports pandas for data manipulation
import datetime as dt # imports datetime to deal with dates
import os
import sqlite3
import nltk
import pickle
from nltk.corpus import stopwords
import re
import wordcloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from os import path
import io
import urllib, base64
def get_data(Title) :
    reddit = praw.Reddit(client_id='Fr6oljX7QOBRCUspR2IqSg', 
                        client_secret='0H_AEaXyJ2sZ--B7sk4haGIaZX8uTQ', 
                        user_agent='Your_api_name', 
                        username='no-Shame-4595', 
                        password='rnjsaltjq12@@')
    subreddit = reddit.subreddit('wallstreetbets')
    DD_subreddit = subreddit.search(f'title:{Title} flair:"DD"', limit=100,sort='new')
    DD_dict = { "title":[],
                "score":[],
                "id":[],
                "url":[],
                "comms_num": [], 
                "date": [],
                "body":[]}
    for posts in DD_subreddit:
        DD_dict["title"].append(posts.title)
        DD_dict["score"].append(posts.score)
        DD_dict["id"].append(posts.id)
        DD_dict["url"].append(posts.url)
        DD_dict["comms_num"].append(posts.num_comments)
        DD_dict["date"].append(posts.created)
        DD_dict["body"].append(posts.selftext)
    # First convert dictionary to DataFrame
    DD_data = pd.DataFrame(DD_dict)
    # Function takes a variable type numeric and converts to date
    def get_date(date):
        return dt.datetime.fromtimestamp(date)
    # We run this function and save the result in a new object
    _date = DD_data["date"].apply(get_date)
    # We replace the previous date variable with the new date variableDD_data = DD_data.assign(date = _date)
    # Let's check the output table
    DB_FILENAME = 'DB_API.db'
    DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    #테이블 존재시 중복되지 않는 데이터 추가 기능 필요 ->replace로 우회
    DD_data.to_sql(f'{Title}',conn,if_exists='replace')
    conn.commit()
    return DD_data
##정규표현식을 통한 문자열 치환
def clean_text(inputString):
    text_rmv = re.sub('[-=+,#/\?%;:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', ' ', inputString)
    return text_rmv
def word_cloud(DD_data): 
    ##nltk 라이브러리를 통한 문자 토큰화
    DD_data['body']=DD_data['body'].str.lower()
    T_data=DD_data.body.apply(clean_text).apply(nltk.word_tokenize)
    ##nltk pos_tag 함수를 사용하여 품사 태깅
    Taged_data= T_data.apply(nltk.pos_tag)
    t_list =[]
    for i in Taged_data : 
        t_list.append(i)
    t_list = sum(t_list, [])
    NN_words = []
    for word, pos in t_list:
        if 'NN' in pos:
            NN_words.append(word)
    wlem = nltk.WordNetLemmatizer()
    lemmatized_words = []
    for word in NN_words:
        new_word = wlem.lemmatize(word)
        lemmatized_words.append(new_word)
    stopwords_list = stopwords.words('english') #nltk에서 제공하는 불용어사전 이용
    #print('stopwords: ', stopwords_list)
    unique_NN_words = set(lemmatized_words)
    final_NN_words = lemmatized_words

    # 불용어 제거
    for word in unique_NN_words:
        if word in stopwords_list:
            while word in final_NN_words: final_NN_words.remove(word)
    customized_stopwords = ['http', 'png', 'jpg', "company", "com",'www','stock','price'] # 직접 만든 불용어 사전

    unique_NN_words1 = set(final_NN_words)
    for word in unique_NN_words1:
        if word in customized_stopwords:
            while word in final_NN_words: final_NN_words.remove(word)
    from collections import Counter
    c = Counter(final_NN_words) # input type should be a list of words (or tokens)
    k = 20
    print(c.most_common(k)) # 빈도수 기준 상위 k개 단어 출력
    noun_text = ''
    for word in final_NN_words:
        noun_text = noun_text +' '+word

    wordcloud = WordCloud(max_font_size=60, relative_scaling=.5).generate(noun_text) # generate() 는 하나의 string value를 입력 받음
    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    image = io.BytesIO()
    plt.savefig(image,format="png")
    image.seek(0)
    string = base64.b64encode(image.read())
    image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)
    return image_64
plt.show(word_cloud(get_data('apple')))