import pandas as pd
import csv
from datetime import date, timedelta


df = pd.read_csv("output.csv", names = ["sims", "date", "article1", "article2"])
df["date"] = pd.to_datetime(df["date"])


start = date(2019, 5, 1)
end = date(2019, 5, 31)

days = (end - start).days

results = list()


for i in range(days+1):
	now = start + timedelta(days = i)
	chosen_article = df.loc[df["date"] == now]
	total = len(chosen_article.index)
	over_03 = chosen_article.loc[chosen_article["sims"] > 0.3]
	results.append([now, total, len(over_03.index), str(len(over_03.index)/total)])


with open("statistic.csv", "a+", encoding = "utf-8", newline = "") as f :
	writer = csv.writer(f)
	for res in results:
		writer.writerow(res)