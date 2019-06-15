import csv
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter


results = list()
ids = list()

with open("output.csv", "r", encoding = "utf-8-sig", newline = "") as f:
	rows = csv.reader(f)
	for row in rows:
		ids.append(row[2])
		ids.append(row[3])

ids = list(set(ids))

df = pd.read_csv("output.csv", names = ["sims", "date", "article1", "article2"])

top10_res = list()

for id in ids:
	sims = list()
	chosen_article = df.loc[(df["article1"] == id) | (df["article2"] == id)]
	
	chosen_article = chosen_article.sort_values(by=["sims"], ascending = False)
	top10 = chosen_article.head(10)
	for i in range(len(top10.index)):
		if top10.iloc[i]["article1"] == id:
			sims.append(top10.iloc[i]["article2"])
		elif top10.iloc[i]["article2"] == id:
			sims.append(top10.iloc[i]["article1"])
	top10_res.append([id, sims])

with open("top10_sims.csv", "a+", encoding = "utf-8-sig", newline = "") as f:
	writer = csv.writer(f)
	for res in top10_res:
		writer.writerow(res)

df["date"] = pd.to_datetime(df["date"])

bound1 = date(2019, 5, 1)
bound2 = date(2019, 5, 31)

chosen_article = df.loc[(df["date"] >= bound1) & (df["date"] <= bound2)]
x = [i for i in np.arange(0.0, 1.05, 0.05)]
y = list()


# now = 0
# for i in np.arange(0.5, 1.0, 0.05):
# 	if now == 0:
# 		size = (chosen_article.loc[(df["sims"] >= now) & (df["sims"] < i)]).size
# 	else :
# 		size = (chosen_article.loc[(df["sims"] > now) & (df["sims"] < i)]).size
# 	y.append(size/total_size*100)
# 	now += 0.05

plt.hist(chosen_article["sims"], bins = x, weights = [1. / len(chosen_article.index)] * len(chosen_article.index))

plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

plt.xticks(np.arange(0.0, 1.05, 0.05))

percentile = np.percentile(chosen_article["sims"], [25, 50, 75])

textstr = "amount = " + str(len(chosen_article.index)) + \
 "\nmean = " + str(np.mean(chosen_article["sims"])) + \
 "\nQ1 = " + str(percentile[0]) + \
 "\nQ2 = " + str(percentile[1]) + \
 "\nQ3 = " + str(percentile[2])

props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

plt.text(0.05, 0.95, textstr, fontsize=14, verticalalignment='top', bbox=props, transform=plt.gcf().transFigure)

plt.subplots_adjust(left=0.3)

plt.show()