from utility.DBUtility import DBUtility
import csv
import sys
from datetime import date

dbutils = DBUtility()

aus_accounts = ["今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]
articles = list()


for account in aus_accounts :
	aus_articles = dbutils.GetArticles({"account": account})
	for article in aus_articles :
		dt_list = article["time"].split("-")
		dt = date(int(dt_list[0]), int(dt_list[1]), int(dt_list[2]))
		if dt <= date(2019, 3, 31):
			articles.append(article)


csvfile2 = open("output_taiwan.csv", "w+", newline="", encoding = "utf-8-sig")
writer2 = csv.writer(csvfile2)

total = 0

with open("output_all.csv", "w+", newline="", encoding = "utf-8-sig") as csvfile :
	writer = csv.writer(csvfile)
	writer.writerow(["標題", "來源", "發文作者", "文章內容", "發文時間", "Top10關鍵字", "NER"])
	writer2.writerow(["標題", "來源", "發文作者", "文章內容", "發文時間", "Top10關鍵字", "NER"])
	for article in articles :
		row = [article["title"], article["author"], article["account"], article["content"], article["time"], article["tfidf"], article["NER"]]
		writer.writerow(row)
		if "台湾" in row[3] :
			writer2.writerow(row)
		total += 1
		sys.stdout.write('\r')
		sys.stdout.write(" Writing File... {}%".format(str(round(total/len(articles)*100))))
		sys.stdout.flush()
