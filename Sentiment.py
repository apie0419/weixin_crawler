from collections       import Counter
from functools         import partial
from sklearn           import preprocessing
from utility.DBUtility import DBUtility
from datetime          import date, timedelta
import pandas as pd
import jieba, re


dbutils = DBUtility()

# Dict functions

aus_accounts = ["华人瞰世界", "今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]

def convert_polar_sentiment(polar):
    if polar == 2:
        return -1
    elif polar == 1:
        return 1
    elif polar == 0:
        return 0
    else:
        return 'both'

def sent_scores(row):
    '''
    return sent_scores: tuples(pos, neg), for example(3, 0) denotes positive 3
    '''
    convert_sent = row['convert']
    intensity = row[' 强度']
    if convert_sent == 'both':
        return(intensity, -1 * intensity)
    elif convert_sent == 1:
        return(intensity, 0)
    elif convert_sent == -1:
        return(0, -1 * intensity)
    else:
        return(0, 0)

def compute_article_sentiments(article):
    '''
    function apply to article_df to compute scores
    '''
    
    article_sum=0
    for index , row in sent_dict.iterrows():
        term = row['词语']
        pos_score, neg_score =  row['sent_scores']
        if term in article:
            article_sum += pos_score + neg_score
    return article_sum

# Pre-processing functions

def get_emoji(content):
    pattern =re.compile(u"\[[a-zA-Z\u4e00-\u9fa5]+\]")
    result=re.findall(pattern,content)
    return result

def create_counter(seg_list):
    c = Counter()
    for x in seg_list:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    return c

def find_cut_sent_class(cut_dict, sent_df, sent_classes):
    c = Counter() 
    c.update({x:0 for x in sent_classes})

    
    intersect = cut_dict.keys() & sent_df.index
    
    for item in intersect:
        freq = cut_dict[item]
        try:
            c[sent_df.loc[item][' 情感分类']] += freq
        except Exception as e: 
            print(item)
            print(e)

    return c

def count_generator(counts):
    
    return sum(counts.values())

# Load Dict
def get_sentiment(start, end):
    sent_dict = pd.read_csv('sent_dicts.csv', error_bad_lines=False)
    sent_dict['convert'] = sent_dict[' 极性'].apply(convert_polar_sentiment)
    sent_dict['sent_scores'] = sent_dict.apply(sent_scores, axis=1)
    sent_dict[' 情感分类']=sent_dict[' 情感分类'].str.replace(" ","")
    sent_classes = list(set(sent_dict[' 情感分类']))

    print('Dict loaded....')

    # Processing sentiment dictionary

    sent_index_dict = sent_dict.set_index('词语')
    sent_index_dict = sent_index_dict.loc[~sent_index_dict.index.duplicated(keep='first')]

    # Load Data

    days = (end - start).days

    all_articles = list()

    for i in range(days+1):
        now = start + timedelta(days = i)
        articles = dbutils.GetArticles({"time": str(now)})
        for article in articles:
            if article["account"] not in aus_accounts:
                all_articles.append(article)

    hr_cut = pd.DataFrame(all_articles)

    hr_cut['cut_counter'] = hr_cut['segs'].apply(create_counter)

    sent_freq = partial(find_cut_sent_class, sent_df=sent_index_dict, sent_classes = sent_classes)
    hr_cut['sent_freq'] = hr_cut['cut_counter'].apply(sent_freq)

    print('Sentiment frequency computed...')

    # Getting individual classes counts

    hr_columns = hr_cut['sent_freq'].apply(pd.Series)

    print(hr_columns.head())

    pos_terms = ['PH', 'PE', 'PG', 'PB', 'PK', 'PC', 'PF', 'PA', 'PD']
    neg_terms = ['NK', 'NN', 'NI', 'NA', 'NL', 'NC', 'NJ', 'NB', 'NE', 'ND', 'NH', 'NG']

    hr_columns['pos_sum'] = hr_columns[pos_terms].sum(axis=1)
    hr_columns['neg_sum'] = hr_columns[neg_terms].sum(axis=1)

    hr_cut['jieba_cut'] = hr_cut['content'].apply(jieba.cut)

    hr_columns['num_words'] = hr_cut['cut_counter'].apply(count_generator)

    hr_columns['sent_sum'] = hr_columns['pos_sum'] + hr_columns['neg_sum']

    hr_final = hr_cut[['_id', 'content']].join(hr_columns)

    print('Work done... Saving...')

    hr_final.to_csv(str(start) + "~" + str(end) + '_sentiment.csv', index=0)