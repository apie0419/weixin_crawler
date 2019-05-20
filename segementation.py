import csv
import jieba
from threading import Thread
import threading
import sys
import time
import re
import numpy as np
import pickle
from datetime import date
from utility.DBUtility import DBUtility

raw_contents = []
articles = []
STOPWORDS = []
WORKERS = 10
num = 0
block = threading.Lock()
segmentation_finish = 0
ch = re.compile(u'[\u3400-\u9FFF]+')
dbutils = DBUtility()
results = []



def Segmentation() :
	global raw_contents
	global STOPWORDS
	global articles
	global num
	global block
	global segmentation_finish

	while True :
		with block :
			now = num
			if now >= len(articles) :
				segmentation_finish += 1
				break
			num += 1
		dt_list = articles[now]["time"].split("-")
		dt = date(int(dt_list[0]), int(dt_list[1]), int(dt_list[2]))
		bound = date(2019, 3, 31)
		if dt > bound :
			continue

		content = articles[now]["content"]
		sn = articles[now]["_id"]
		words = jieba.cut(content.replace("\t", "").replace(" ", ""), cut_all=False)
		keyword = []
		for word in words :
			if word not in STOPWORDS:
				keyword.append(word)
		results.append((sn, keyword))


jieba.enable_parallel()

jieba.load_userdict("user_dict.txt")

print ("Loading Stopwords...")

with open('stop_word_all.txt','r', encoding='utf8') as stopword:
	for word in stopword:
		STOPWORDS.append(word.replace("\n",""))

articles = dbutils.GetArticles({})

sys.stdout.write('\r')
sys.stdout.write("Doing Segmentation... 0%")
sys.stdout.flush()

for i in range(WORKERS) :
	t = Thread(target = Segmentation)
	t.daemon = True
	t.start()

while True :
	percent = round(num/len(articles)*100)
	sys.stdout.write('\r')
	sys.stdout.write("Doing Segmentation... {}%".format(str(percent)))
	sys.stdout.flush()
	time.sleep(0.1)
	if segmentation_finish == WORKERS and percent >= 100:
		break

with open("segmentation.pickle", "wb+") as f :
	f.write(pickle.dumps(results))

