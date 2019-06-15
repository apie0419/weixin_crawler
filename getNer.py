from utility.DBUtility import DBUtility
import csv
import json
import codecs
import sys
from datetime import date, timedelta

dbutils = DBUtility()

aus_accounts = ["华人瞰世界", "今日悉尼", "微悉尼", "澳洲微报", "悉尼印象", "Australia News", "澳洲中文台"]
articles = list()


now = date(2018, 11, 1)
result = list()


def csvhandlerstr(str):
    if ',' in str:
        if '"' in str:
            str = str.replace('"','""')
        str = '"' + str + '"'
    return str


while True :
	words_feq = dict()
	if now >= date(2019, 4, 1) :
		break
	all_articles = dbutils.GetArticles({"time": str(now)})
	for article in all_articles :
		if article["account"] in aus_accounts :
			for word in article["NER"]:
				w = word["word"]
				if w in words_feq:
					words_feq[w] += 1
				else :
					words_feq[w] = 1
	result.append({str(now): words_feq})
	now += timedelta(1)

with codecs.open("output_freq.json", "w", encoding = "utf-8-sig") as f :
	json.dump(result, f, ensure_ascii=False)

with open("output_freq.csv", "w+", encoding = "utf-8-sig", newline='') as csvfile:
	writer = csv.writer(csvfile)
	for res in result:
		dt = res[0]
		feq = res[1]
		string = ""
		for key, value in feq.items() :
			string += key + ":" + str(value) + " "
		writer.writerow([dt, string])
