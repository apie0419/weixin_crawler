import jieba
from multiprocessing import Queue, Process, Lock, Manager, Value, cpu_count
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer
from utility.DBUtility import DBUtility
import sys
import time
import re
import numpy as np
from datetime import date, timedelta
import pickle
import csv


STOPWORDS = list()

WORKERS = cpu_count()

words = None

tfidf = None

dbutils = DBUtility()

sn_list = list()

aus_accounts = ["华人瞰世界", "今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]

aus_articles = list()

# jieba.enable_parallel()

# jieba.load_userdict("user_dict.txt")

# print ("Loading Stopwords...")

# with open('stop_word_all.txt','r', encoding='utf-8-sig') as stopword:
# 	for word in stopword:
# 		STOPWORDS.append(word.replace("\n", ""))


def Segmentation(articles_queue, segementations) :

	global STOPWORDS
	global dbutils


	while True :
		try :
			article = articles_queue.get()
		except Exception :
			break

		dt_list = article["time"].split("-")
		dt = date(int(dt_list[0]), int(dt_list[1]), int(dt_list[2]))
		

		content = article["content"]
		sn = article["_id"]
		ws = jieba.cut(content.replace("\t", "").replace(" ", ""), cut_all=False)
		keyword = []
		for word in ws :
			if word not in STOPWORDS:
				keyword.append(word)
		segementations.append({sn: "yes"})
		data = {
			"segs": keyword
		}
		dbutils.UpdateArticle(sn, data)

def Calculate_Sim(num, lock, writelock, finish, start, end) :
	global words
	global tfidf
	global dbutils
	global sn_list

	while True :
		lock.acquire()
		now = start + timedelta(days = num.value)
		if now > end :
			finish.value += 1
			lock.release()
			break
		articles = dbutils.GetArticles({"time": str(now)})
		num.value += 1
		lock.release()

		contents = list()
		id_list = list()

		for article in articles:
			contents.append(" ".join(article["segs"]))
			id_list.append(article["_id"])

		vectorizer = CountVectorizer()

		transformer = TfidfTransformer()

		tfidf = transformer.fit_transform(vectorizer.fit_transform(contents))

		results = list()
		for i in range(tfidf.shape[0]):
			weights = tfidf.getrow(i).toarray()[0]
			for j in range(i + 1, tfidf.shape[0]):
				w = np.dot(weights, tfidf.getrow(j).toarray()[0])
				results.append([w, str(now), id_list[i], id_list[j]])

		writelock.acquire()

		with open("output.csv", "a+", newline="", encoding = "utf-8-sig") as csvfile :
			writer = csv.writer(csvfile)
			for result in results:
				writer.writerow(result)

		writelock.release()



if __name__ == '__main__':
	lock = Lock()
	writelock = Lock()
	tfidf_queue = Queue()
	articles_queue = Queue()
	manager = Manager()
	num = Value("i", 0)
	finish = Value("i", 0)
	segementations = manager.list()
	start = date(2019, 5, 1)
	end = date(2019, 5, 31)

	days = (end - start).days

	# articles = dbutils.GetArticles({"segs": None})


	# for article in articles :
	# 	#if article["account"] not in aus_accounts :
	# 	articles_queue.put(article)

	# total = articles_queue.qsize()

	# sys.stdout.write('\r')
	# sys.stdout.write("Doing Segmentation... 0%")
	# sys.stdout.flush()

	# for _ in range(WORKERS) :
	# 	t = Process(target = Segmentation, args = (articles_queue, segementations))
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
	# contents = list()

	sys.stdout.write('\r')
	sys.stdout.write("Calculating Similarity... 0%")
	sys.stdout.flush()

	for _ in range(WORKERS) :
		t = Process(target = Calculate_Sim, args = (num, lock, writelock, finish, start, end))
		t.daemon = True
		t.start()

	while True :
		percent = round(num.value/(days+1)*100, 2)
		sys.stdout.write('\r')
		sys.stdout.write("Calculating Similarity... {}%".format(percent))
		sys.stdout.flush()
		time.sleep(0.1)
		if finish == WORKERS and percent >= 100:
			break