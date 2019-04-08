from bs4 import BeautifulSoup
import re
import os
import time
import configparser
from utility.DBUtility import DBUtility
import xlrd
from datetime import date
import configparser
import traceback

myWorkbook = xlrd.open_workbook('wechatacc.xlsx')
mySheets = myWorkbook.sheets()
mySheet = mySheets[0]

nrows = mySheet.nrows
ncols = mySheet.ncols

category = dict()
for i in range(nrows) :
	temp = []
	for j in range(ncols) :
		myCell = mySheet.cell(i, j)
		myCellValue = myCell.value 
		if j == 1 :
			myCellValue = int(myCellValue)
		temp.append(myCellValue)
	category.update({temp[0] : temp[1]})

dbutils = DBUtility()

config = configparser.ConfigParser()
config.optionxform = str
config.read('setting.conf', encoding='utf-8')


class Parser() :
	articles_path = config.get("SYSTEM", "ARTICLES_DIR")
	urls_path = config.get("SYSTEM", "URLS_DIR")
	url_file = "urls.txt"
	saved_urls = []


	def __init__(self) :
		pass

	def parse(self, articles_path_queue) :
		while True:
			try :
				file = articles_path_queue.get()
			except Exception :
				traceback.print_exc()
				continue
			filepath = os.path.join(self.articles_path, file + ".txt")
			token = file.split("_")
			dt = token[0]
			sn = token[1]
			__biz = token[2]
			idx = token[3]
			mid = token[4]
			chksm = token[5]
			url = "http://mp.weixin.qq.com/s?__biz=" + __biz + "&amp;mid=" + mid + "&amp;idx=" + idx + "&amp;sn=" + sn + "&amp;chksm=" + chksm + "&amp;scene=38#wechat_redirect"
			
			try :
				with open(filepath, 'r', encoding="utf-8-sig") as f :
					content = f.read()
				if len(content) == 1 :
					print ("[PARSER] " + file + " No Content")
					os.remove(filepath)
					continue
			except :
				print ("[PARSER] " + file + " Does not Exist")
				continue
			soup = BeautifulSoup(content, "html.parser")
			isShare = False

			# 檢查是否為轉貼文章

			try :
				shareurl = soup.select("#js_share_source")[0]['href']
				time.sleep(4)
				res = requests.get(shareurl)
				soup2 = BeautifulSoup(res.text, "html.parser")
				isShare = True
			except Exception as e :
				pass
			try :

				# Title & Source

				if isShare :

					title = soup2.select("#activity-name")[0].text
					title = title.replace("\n", "")
					title = title.replace("\t", "")
					title = title.replace(" ", "")
					comefrom = soup2.select("#js_name")[0].text
					comefrom = comefrom.replace("\n", "")
					comefrom = comefrom.replace("\t", "")
					comefrom = comefrom.replace(" ", "")

				else : 

					title = soup.select("#activity-name")[0].text

					try :
						if "publish_time" == soup.select(".rich_media_meta.rich_media_meta_text")[0]['id'] or "copyright_logo" == soup.select(".rich_media_meta.rich_media_meta_text")[0]['id'] :
							comefrom = "原創"
						else :
							comefrom = soup.select(".rich_media_meta.rich_media_meta_text")[0].text
					except Exception :
						comefrom = soup.select(".rich_media_meta.rich_media_meta_text")[0].text

				# Content

				content = ""

				if isShare :
					for cont in soup2.select("#js_content") :
						try :
							for c in cont.find_all("p") :
								content += c.text				
						except Exception :
							pass
				else :
					for cont in soup.select("#js_content") :
						try :
							for c in cont.find_all("p") :
								content += c.text
						except Exception :
							pass
				
				if content == "" :
					print ("[PARSER] Article: " + str(sn) + " No Content")
					os.remove(filepath)
					continue

				# Account

				if isShare :
					account = soup.select(".account_nickname > .account_nickname_inner")[0].text
				else :
					account = soup.select("#js_name")[0].text

				# Save Data
				comefrom = comefrom.strip().rstrip()
				account = account.strip().rstrip()
				title = title.strip().rstrip()
				content = content.strip()
				data = {
					"_id": sn,
					"url": url,
					"time": dt,
					"author": comefrom,
					"account": account,
					"title": title,
					"content": content,
					"class": category[account],
					"tfidf": "",
					"NER": "",
					"censor": 0
				}

				dbutils.InsertArticle(data)

				print ("[PARSER] Insert Article: " + str(sn) + " To DB")

				os.remove(filepath)

			except Exception as e:
				# traceback.print_exc()
				os.remove(filepath)
				pass
	
	def parseurls(self, articles_queue) :
		while True :
			files = os.listdir(self.urls_path)
			if not files :
				time.sleep(10)
				continue
			for file in files :

				filepath = os.path.join(self.urls_path, file)
				while True :
					with open(filepath, "r", encoding="utf-8-sig") as f :
						content = f.read()
					if len(content) < 10 :
						time.sleep(5)
					else :
						break
				print ("[PARSER] Parse File: " + str(file))
				soup = BeautifulSoup(content, "html.parser")

				articles = soup.select(".weui_media_bd.js_media")
				num = 0
				for article in articles :
					try : 
						url = article.select("h4")[0]["hrefs"]
						articledate = article.select("p")[0].text
					except Exception :
						continue
					pattern = re.compile(r"sn=([0-9 a-z]){32}")
					res = re.search(pattern, url)
					sn = res.group(0)[3:]
					if dbutils.GetOneArticleById({"_id": sn}) is not None :
						continue
					date_pattern = re.compile(r"[0-9]+")
					d = re.findall(date_pattern, articledate)
					now = date(int(d[0]), int(d[1]), int(d[2]))
					wanted = date(2018, 11, 1)
					if now >= wanted :
						articles_queue.put((url, now, False))
						num += 1
				os.remove(filepath)
				print ("[PARSER] Add " + str(num) + " Jobs")
