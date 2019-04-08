import csv
from utility.DBUtility import DBUtility

dbutils = DBUtility()

with open("output_aus.csv", "r", encoding = "utf-8-sig") as csvfile :
	rows = csv.reader(csvfile)
	for row in rows :
		sn = row[0]
		keywords = row[1]
		data = {
			"tfidf": keywords
		}

		dbutils.UpdateArticle(sn, data)