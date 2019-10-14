from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
from utility.DBUtility import DBUtility
from datetime import date
import matplotlib as plt
import numpy as np
import pandas as pd
import pickle, time, pyLDAvis, csv


start = date(2018, 11, 1)
end = date(2019, 10, 6)

stpwrdpath = "stop_word_all.txt"
STOPWORDS = list()
n_components = range(80, 105, 10)
learning_decay = [.7]

search_params = {'n_components': n_components, 'learning_decay': learning_decay}

with open(stpwrdpath, 'r', encoding = "utf-8-sig") as stopwords :
    for word in stopwords :
        STOPWORDS.append(word.replace("\n", ""))

def Get_Data_Vectors(contents):

    cntVector = CountVectorizer(stop_words = STOPWORDS)

    cntTf = cntVector.fit_transform(contents)

    return cntTf, cntVector

def Get_LDA_BestModel(cntTf):
    
    #model = GridSearchCV(lda, param_grid = search_params, cv = 3, n_jobs = 4, verbose = 10)
    #model.fit(cntTf)
    #Get_LDA_Model_Performance(model)
    for i in range(60, 105, 10):
        lda = LatentDirichletAllocation(n_topics = i, verbose = 10, learning_decay = .7, n_jobs = 1)

        t0 = time.time()

        lda.fit(cntTf)
    
        gamma = lda.transform(cntTf)

        perplexity = lda.perplexity(cntTf, gamma)

        print ("Spent %.3f sec, Perplexity = %.3f"%(time.time() - t0, perplexity))

        with open("perplexity.csv", "a+", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([i, performances])

    return lda
    #return model.best_estimator_

def Get_LDA_Model_Performance(model):
    log_likelyhoods_7 = [round(gscore.mean_validation_score) for gscore in model.grid_scores_ if gscore.parameters['learning_decay']==0.7]

    # Show graph
    plt.figure(figsize=(12, 8))
    plt.plot(n_topics, log_likelyhoods_7, label='0.7')
    plt.title("Choosing Optimal LDA Model")
    plt.xlabel("Num Topics")
    plt.ylabel("Log Likelyhood Scores")
    plt.legend(title='Learning decay', loc='best')
    plt.save("performances.png")

def LDA_Distribution(model, cntTf, ids):
    
    lda_output = model.transform(cntTf)

    topicnames = ["Topic" + str(i) for i in range(model.n_topics)]

    df_document_topic = pd.DataFrame(np.round(lda_output, 2), columns = topicnames, index = ids)
    """
    def color_green(val):
        color = 'green' if val > .1 else 'black'
        return 'color: {col}'.format(col=color)

    def make_bold(val):
        weight = 700 if val > .1 else 400
        return 'font-weight: {weight}'.format(weight=weight)

    df_document_topic = df_document_topic.style.applymap(color_green).applymap(make_bold)
    """
    df_document_topic.to_csv("LDA_Distribution.csv", encoding = "utf-8")

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
        "segs": 1
    }
    
    articles = dbutils.GetArticles({"state": "cn"}, field)

    articles_df = pd.DataFrame(articles)

    articles_df["time"] = pd.to_datetime(articles_df["time"])

    articles_df = articles_df.loc[(articles_df["time"] >= pd.Timestamp(start)) & (articles_df["time"] < pd.Timestamp(end))]

    articles_df["segs"] = articles_df["segs"].apply(" ".join)

    contents = list(articles_df["segs"])

    ids = list(articles_df["_id"])

    del articles_df

    cntTf, cntVector = Get_Data_Vectors(contents)

    words = cntVector.get_feature_names()
    
    best_model = Get_LDA_BestModel(cntTf)

    print (best_model.get_params())
    
    file = open('best_model.pickle', 'wb')

    pickle.dump(best_model, file)

    file.close()

    

    """    
    file = open('best_model.pickle', 'rb')
    best_model = pickle.load(file)
    file.close()
    """

    LDA_Distribution(best_model, cntTf, ids)

    # Get_MetaData(articles_df)

    Get_Keywords_Distribution(best_model, words)
