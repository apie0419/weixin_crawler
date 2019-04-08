import jieba
from multiprocessing import Queue, Process, Lock, Manager, Value, cpu_count
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
from utility.DBUtility import DBUtility
import sys
import time
import re
import numpy as np
from datetime import date
import pickle
import csv


STOPWORDS = list()

WORKERS = cpu_count()

words = None

tfidf = None

dbutils = DBUtility()

sn_list = list()

aus_accounts = ["今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]

aus_articles = list()

# jieba.load_userdict("user_dict.txt")

# print ("Loading Stopwords...")

# with open('stop_word_all.txt','r', encoding='utf-8-sig') as stopword:
# 	for word in stopword:
# 		STOPWORDS.append(word.replace("\n", ""))


def Segmentation(articles_queue, segementations) :

	global STOPWORDS

	while True :
		try :
			article = articles_queue.get()
		except Exception :
			break

		dt_list = article["time"].split("-")
		dt = date(int(dt_list[0]), int(dt_list[1]), int(dt_list[2]))
		bound = date(2019, 3, 31)

		if dt > bound :
			continue

		content = article["content"]
		sn = article["_id"]

		ws = jieba.cut(content.replace("\t", "").replace(" ", ""), cut_all=False)
		keyword = []
		for word in ws :
			if word not in STOPWORDS:
				keyword.append(word)
		
		segementations.append((sn, " ".join(keyword)))



def Count_Keyword(num, lock, writelock, finish) :
	global words
	global tfidf
	global dbutils
	global sn_list

	while True :
		lock.acquire()
		now = num.value
		if now >= len(sn_list) - 1 :
			finish.value += 1
			break
		num.value += 1
		lock.release()


		sn = sn_list[now]
		weights = list(tfidf.getrow(now).toarray()[0])
		words_weight = np.argsort(weights).flatten()[::-1]
		top10_keywords = list(words[words_weight][:10])
		
		writelock.acquire()

		with open("output.csv", "a+", newline="", encoding = "utf-8-sig") as csvfile :
			writer = csv.writer(csvfile)
			writer.writerow([sn, str(top10_keywords)])

		writelock.release()

		# data = {
		# 	"tfidf": top10_keywords
		# }

		# dbutils.UpdateArticle(sn, data)



if __name__ == '__main__':
	lock = Lock()
	writelock = Lock()
	tfidf_queue = Queue()
	articles_queue = Queue()
	manager = Manager()
	num = Value("i", 0)
	finish = Value("i", 0)
	# segementations = manager.list()

	# articles = dbutils.GetArticles({})

	# total = len(articles)

	# for article in articles :
	# 	articles_queue.put(article)

	# sys.stdout.write('\r')
	# sys.stdout.write("Doing Segmentation... 0%")
	# sys.stdout.flush()

	# for _ in range(WORKERS) :
	# 	t = Process(target = Segmentation, args = (articles_queue, segementations, ))
	# 	t.daemon = True
	# 	t.start()

	# while True :
	# 	percent = round(len(segementations)/total*100, 2)
	# 	sys.stdout.write('\r')
	# 	sys.stdout.write("Doing Segmentation... {}%".format(str(percent)))
	# 	sys.stdout.flush()
	# 	time.sleep(0.1)
	# 	if percent >= 100:
	# 		break
	
	# print ("\n")

	# with open("segmentations.pickle", "wb+") as f :
	# 	f.write(pickle.dumps(segementations))

	articles = dbutils.GetArticles({})
	for article in articles :
		if article["account"] not in aus_accounts :
			aus_articles.append(article["_id"])

	with open("./segmentation.pickle", "rb") as f :
		segementations = pickle.load(f)

	contents = list()

	for s in segementations :
		if s[0] in aus_articles:
			sn_list.append(s[0])
			contents.append(" ".join(s[1]))
	# contents = [" ".join(s[1]) if s[0] in aus_articles for s in segementations]

	vectorizer = CountVectorizer()

	transformer = TfidfTransformer()

	tfidf = transformer.fit_transform(vectorizer.fit_transform(contents))

	del segementations

	del contents

	words = np.array(vectorizer.get_feature_names())

	sys.stdout.write('\r')
	sys.stdout.write("Counting Top10 Keywords... 0%")
	sys.stdout.flush()

	for _ in range(WORKERS) :
		t = Process(target = Count_Keyword, args = (num, lock, writelock, finish))
		t.daemon = True
		t.start()

	while True :
		percent = round(num.value/len(sn_list)*100, 2)
		sys.stdout.write('\r')
		sys.stdout.write ("Counting Top10 Keywords... {}%".format(percent))
		sys.stdout.flush()
		time.sleep(0.1)
		if finish == WORKERS and percent >= 100:
			break