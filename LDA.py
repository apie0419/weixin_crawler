from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from multiprocessing import cpu_count
import pickle
import csv
from utility.DBUtility import DBUtility


dbutils = DBUtility()

stpwrdpath = "stop_word_all.txt"
STOPWORDS = list()

aus_accounts = ["今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]
aus_articles = list()

with open(stpwrdpath, 'r', encoding = "utf-8-sig") as stopwords :
    for word in stopwords :
        STOPWORDS.append(word.replace("\n", ""))

with open("./segmentation.pickle", "rb") as f :
    segementations = pickle.load(f)

articles = dbutils.GetArticles({})
for article in articles :
    if article["account"] not in aus_articles :
        aus_articles.append(article["_id"])

sn_list = list()
contents = list()

for s in segementations :
    if s[0] in aus_articles:
        sn_list.append(s[0])
        contents.append(" ".join(s[1]))


cntVector = CountVectorizer(stop_words=STOPWORDS)
cntTf = cntVector.fit_transform(contents)
feature_names = cntVector.get_feature_names()

lda = LatentDirichletAllocation(n_components=100, learning_offset=50, random_state=0, n_jobs=cpu_count())
docres = lda.fit_transform(cntTf)

with open("output_topic100.csv", "w+", newline="", encoding = "utf-8-sig") as f:
    writer = csv.writer(f)
    for i in range(len(sn_list)) :
        sn = sn_list[i]
        doc = docres[i]
        writer.writerow([sn, list(doc)])

# with open("output_topic100.csv", "w+", newline="", encoding = "utf-8-sig") as f :
#     for topic_idx, topic in enumerate(lda.components_):
#         writer = csv.writer(f)
#         writer.writerow([topic])
#         print ("Topic%d :" % (topic_idx))
#         print (str(topic))
#         # print (" ".join([feature_names[i] for i in topic.argsort()[:-11:-1]]))