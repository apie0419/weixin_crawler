from datetime                        import date, timedelta
from Sentiment                       import get_sentiment
from multiprocessing                 import Queue, Process, Lock, Manager, Value, cpu_count
from utility.DBUtility               import DBUtility
from utility.Mail                    import Send_Mail
from matplotlib.ticker               import PercentFormatter
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
import numpy             as np
import pandas            as pd
import matplotlib.pyplot as plt
import sys, jieba, time, re, csv, os


### Setting

GET_KEYWORDS = True

wanted_word = "香港"

export_dir = "Outputs"

# start = date(2019, 9, 8)
# end = date(2019, 9 ,13)

start = date.today() - timedelta(days = 7)

end = date.today() - timedelta(days = 1) 

###

STOPWORDS = list()

WORKERS = cpu_count()

tfidf = None

sn_list = list()

aus_accounts = ["华人瞰世界", "今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]

aus_articles = list()

base_path = os.path.dirname(os.path.abspath(__file__))


def Segmentation(articles_queue, segementations, lock, dbutils) :

	global STOPWORDS


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
		lock.acquire()
		segementations.value += 1
		lock.release()
		data = {
			"segs": keyword
		}
		dbutils.UpdateArticle(sn, data)

def Calculate_Sim(num, lock, writelock, finish, dbutils) :
	
	global tfidf
	global sn_list
	global start
	global end

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
		keywords_ids = list()

		for article in articles:
			contents.append(" ".join(article["segs"]))
			id_list.append(article["_id"])

			if GET_KEYWORDS:
				if wanted_word in article["content"]:
					keywords_ids.append(article["_id"])


		vectorizer = CountVectorizer()

		transformer = TfidfTransformer()

		tfidf = transformer.fit_transform(vectorizer.fit_transform(contents))

		results = list()
		keywords_results = list()

		for i in range(tfidf.shape[0]):
			weights = tfidf.getrow(i).toarray()[0]
			for j in range(i + 1, tfidf.shape[0]):
				w = np.dot(weights, tfidf.getrow(j).toarray()[0])
				if id_list[j] in keywords_ids and id_list[i] in keywords_ids:
					keywords_results.append([w, str(now), id_list[i], id_list[j]])
				results.append([w, str(now), id_list[i], id_list[j]])


		writelock.acquire()

		with open(os.path.join(base_path, "output.csv"), "a+", newline="", encoding = "utf-8-sig") as csvfile :
			writer = csv.writer(csvfile)
			for result in results:
				writer.writerow(result)
		
		if GET_KEYWORDS:
			with open(os.path.join(base_path, "keywords_output.csv"), "a+", newline="", encoding = "utf-8-sig") as csvfile :
				writer = csv.writer(csvfile)
				for result in keywords_results:
					writer.writerow(result)

		writelock.release()

def Statistic(df, filename):

	global start
	global end

	df["date"] = pd.to_datetime(df["date"])

	days = (end - start).days

	results = list()

	for i in range(days+1):
		now = start + timedelta(days = i)
		chosen_article = df.loc[df["date"] == pd.Timestamp(now)]
		total = len(chosen_article.index)
		over_03 = chosen_article.loc[chosen_article["sims"] > 0.3]
		if total == 0 :
			results.append([now, total, len(over_03.index), 0])
		else:
			results.append([now, total, len(over_03.index), str(len(over_03.index)/total)])


	with open(os.path.join(base_path, export_dir + "/" + filename + ".csv"), "w+", encoding = "utf-8-sig", newline = "") as f :
		writer = csv.writer(f)
		writer.writerow(["Date", "Total", "Over_0.3", "Over_0.3/Total"])
		for res in results:
			writer.writerow(res)

	x = [i for i in np.arange(0.0, 1.05, 0.05)]

	plt.figure(figsize=(15, 5))

	plt.hist(df["sims"], bins = x, weights = [1. / len(df.index)] * len(df.index))

	plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

	plt.xticks(np.arange(0.0, 1.05, 0.05))

	percentile = np.percentile(df["sims"], [25, 50, 75])

	textstr = "amount = " + str(len(df.index)) + \
	 "\nmean = " + str(np.mean(df["sims"])) + \
	 "\nQ1 = " + str(percentile[0]) + \
	 "\nQ2 = " + str(percentile[1]) + \
	 "\nQ3 = " + str(percentile[2])

	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

	plt.text(0.05, 0.95, textstr, fontsize=14, verticalalignment='top', bbox=props, transform=plt.gcf().transFigure)

	plt.subplots_adjust(left=0.3)

	plt.savefig(os.path.join(base_path, export_dir + "/" + filename + ".png"))



if __name__ == '__main__':
	lock = Lock()
	writelock = Lock()
	tfidf_queue = Queue()
	articles_queue = Queue()
	manager = Manager()

	num = Value("i", 0)
	finish = Value("i", 0)
	segementations = Value("i", 0)

	dbutils = DBUtility()

	jieba.load_userdict(os.path.join(base_path, "user_dict.txt"))

	print ("Loading Stopwords...")

	with open(os.path.join(base_path, 'stop_word_all.txt'),'r', encoding='utf-8-sig') as stopword:
		for word in stopword:
			STOPWORDS.append(word.replace("\n", ""))

	if not os.path.exists(os.path.join(base_path, export_dir)):
		os.mkdir(os.path.join(base_path, export_dir))


	days = (end - start).days


	articles = dbutils.GetArticles({"segs": None})

	for article in articles :
		articles_queue.put(article)

	total = articles_queue.qsize()

	sys.stdout.write('\r')
	sys.stdout.write("Doing Segmentation... 0%")
	sys.stdout.flush()

	for _ in range(WORKERS) :
		t = Process(target = Segmentation, args = (articles_queue, segementations, lock, dbutils))
		t.daemon = True
		t.start()

	while True :
		if total == 0:
			sys.stdout.write('\r')
			sys.stdout.write("Doing Segmentation... 100%")
			sys.stdout.flush()
			break
		percent = round(segementations.value/total*100, 2)
		sys.stdout.write('\r')
		sys.stdout.write("Doing Segmentation... {}%".format(str(percent)))
		sys.stdout.flush()
		time.sleep(0.1)
		if total == segementations.value:
			break

	contents = list()

	sys.stdout.write('\n')
	sys.stdout.write('\r')
	sys.stdout.write("Calculating Similarity... 0%")
	sys.stdout.flush()

	for _ in range(WORKERS) :
		t = Process(target = Calculate_Sim, args = (num, lock, writelock, finish, dbutils))
		t.daemon = True
		t.start()

	while True :
		percent = round(num.value/(days+1)*100, 2)
		sys.stdout.write('\r')
		sys.stdout.write("Calculating Similarity... {}%".format(percent))
		sys.stdout.flush()
		time.sleep(0.1)
		if finish.value == WORKERS and percent >= 100:
			break

	df = pd.read_csv(os.path.join(base_path, "output.csv"), names = ["sims", "date", "article1", "article2"])

	Statistic(df, str(start) + "~" + str(end) + "_statistic")

	if GET_KEYWORDS:

		df_keyword = pd.read_csv(os.path.join(base_path, "keywords_output.csv"), names = ["sims", "date", "article1", "article2"])

		Statistic(df_keyword, str(start) + "~" + str(end) + "_statistic_keyword")

	get_sentiment(start, end, wanted_word, dbutils)

	os.remove(os.path.join(base_path, "output.csv"))
	os.remove(os.path.join(base_path, "keywords_output.csv"))

	Send_Mail(start, end)
