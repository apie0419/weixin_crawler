from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
from utility.DBUtility import DBUtility
from datetime import date
import matplotlib as plt
import pandas as pd


start = date(2018, 11, 1)
end = date(2019, 10, 6)

stpwrdpath = "stop_word_all.txt"
STOPWORDS = list()
n_components = range(40, 105, 5)
learning_decay = [.5, .7, .9]

search_params = {'n_components': n_components, 'learning_decay': learning_decay}

with open(stpwrdpath, 'r', encoding = "utf-8-sig") as stopwords :
    for word in stopwords :
        STOPWORDS.append(word.replace("\n", ""))

def Get_Data_Vectors(contents):

    cntVector = CountVectorizer(stop_words = STOPWORDS)

    cntTf = cntVector.fit_transform(contents)

    return cntTf, cntVector

def Get_LDA_BestModel(cntTf):
    
    lda = LatentDirichletAllocation()
    model = GridSearchCV(lda, param_grid = search_params)
    model.fit(cntTf)
    Get_LDA_Model_Performance(model)


    return model.best_estimator_

def Get_LDA_Model_Performance(model):
    log_likelyhoods_5 = [round(gscore.mean_validation_score) for gscore in model.grid_scores_ if gscore.parameters['learning_decay']==0.5]
    log_likelyhoods_7 = [round(gscore.mean_validation_score) for gscore in model.grid_scores_ if gscore.parameters['learning_decay']==0.7]
    log_likelyhoods_9 = [round(gscore.mean_validation_score) for gscore in model.grid_scores_ if gscore.parameters['learning_decay']==0.9]

    # Show graph
    plt.figure(figsize=(12, 8))
    plt.plot(n_topics, log_likelyhoods_5, label='0.5')
    plt.plot(n_topics, log_likelyhoods_7, label='0.7')
    plt.plot(n_topics, log_likelyhoods_9, label='0.9')
    plt.title("Choosing Optimal LDA Model")
    plt.xlabel("Num Topics")
    plt.ylabel("Log Likelyhood Scores")
    plt.legend(title='Learning decay', loc='best')
    plt.save("performances.png")

def LDA_Distribution(model, cntTf, ids):
    
    lda_output = model.transform(cntTf)

    topicnames = ["Topic" + str(i) for i in range(best_lda_model.n_topics)]

    df_document_topic = pd.DataFrame(np.round(lda_output, 2), columns = topicnames, index = ids)

    def color_green(val):
        color = 'green' if val > .1 else 'black'
        return 'color: {col}'.format(col=color)

    def make_bold(val):
        weight = 700 if val > .1 else 400
        return 'font-weight: {weight}'.format(weight=weight)

    df_document_topics = df_document_topics.style.applymap(color_green).applymap(make_bold)
    df_document_topics.to_csv("LDA_Distribution.csv", encoding = "utf-8")

def Get_MetaData(df):

    df = df.drop(columns = ["NER", "tfidf", "segs", "url"])

    df["content"] = df["content"].str.replace("\n", "").str.replace("\t", "")

    df.to_csv("metadata.csv", encoding = "utf-8")

def Get_Keywords_Distribution(model, words):
    
    topicnames = ["Topic" + str(i) for i in range(model.n_topics)]

    distribution = model.components_ / model.components_.sum(axis=1)[:, np.newaxis]

    df_topic_keywords = pd.DataFrame(distribution)

    df_topic_keywords.columns = words
    
    df_topic_keywords.index = topicnames

    df_topic_keywords.to_csv("keywords_distribution.csv", encoding = "utf-8")

def Model_Visualize(best_model, cntTf, cntVector):

    panel = pyLDAvis.sklearn.prepare(best_model, cntTf, cntVector, mds='tsne')
    pyLDAvis.save_html(panel, 'lda.html')



if __name__ == "__main__":
    dbutils = DBUtility()
    
    field = {
        "_id": 1,
        "time": 1,
        "segs": 1,
    }

    articles = dbutils.GetArticles({"state": "cn"}, field)

    articles_df = pd.DataFrame(articles)

    articles_df["time"] = pd.to_datetime(articles_df["time"])

    articles_df = articles_df.loc[(articles_df["time"] >= pd.Timestamp(start)) & (articles_df["time"] < pd.Timestamp(end))]

    articles_df["segs"] = articles_df["segs"].apply(" ".join)

    contents = list(articles_df["segs"])

    cntTf, cntVector = Get_Data_Vectors(contents)

    words = cntVector.get_feature_names()

    best_model = Get_LDA_BestModel(cntTf)

    ids = list(articles_df["_id"])

    LDA_Distribution(best_model, cntTf, ids)

    Get_MetaData(df)

    Get_Keywords_Distribution(best_model, words)