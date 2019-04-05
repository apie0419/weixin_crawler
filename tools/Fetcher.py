from multiprocessing import Process
from bs4 import BeautifulSoup
from datetime import date, timedelta
import time
import random
import requests
import os
import re
import traceback
import configparser
from utility.DBUtility import DBUtility

config = configparser.ConfigParser()
config.optionxform = str
config.read('setting.conf', encoding='utf-8')


dbutils = DBUtility()

class Fetcher() :
	headers = {
		"Connection" : "keep-alive",
		"Cache-Control" : "max-age=0",
		"User-Agent" : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
		"Upgrade-Insecure-Requests" : "1",
		"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"Accept-Encoding" : "gzip, deflate, br",
		"Accept-Language" : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6"	
	}
	articles_path = config.get("SYSTEM", "ARTICLES_DIR")
	ban = "你的访问过于频繁，需要从微信打开验证身份，是否需要继续访问当前页面？"
	ban2 = "该内容已被发布者删除"
	bad = "HTTP/1.1 400 Bad Request"
	
	def __init__(self) :
		pass

	def update_proxy(self, proxies_list) :
		total = 0
		print ("[FETCHER] Fetching New Proxy...")
		res = requests.get("https://free-proxy-list.net/", self.headers)
		soup = BeautifulSoup(res.text, "html.parser")
		table = soup.select("tbody")[0]
		for row in table.select("tr"):
			columns = row.select("td")
			try :
				ip = columns[0].text
				port = columns[1].text
				https = columns[6].text
				if https == "yes" :
					proxy = {
						"https" : "https://{}:{}".format(ip, port)
					}
				else :
					proxy = {
						"http" : "http://{}:{}".format(ip, port)
					}
				if proxy not in proxies_list :
					proxies_list.append(proxy)
					total += 1
			except Exception :
				pass
		print ("[FETCHER] Get " + str(total) + " New Proxies")

	def fetch(self, articles_queue, articles_path_queue, proxies_list, lock) :
		while True :
			lock.acquire()
			print ("[FETCHER] Left Proxies : " + str(len(proxies_list)))
			proxies_num = len(proxies_list)
			if proxies_num <= 30 :
				self.update_proxy(proxies_list)
			proxies_num = len(proxies_list)
			num = random.randint(0,len(proxies_list) - 1)
			proxies = proxies_list[num]
			lock.release()
			try :
				url, dt, detect = articles_queue.get()
			except Exception :
				time.sleep(5)
				continue
			while True :
				try :
					res = requests.get(url, proxies = proxies, headers = self.headers, timeout = 10)
				except Exception as e:
					lock.acquire()
					try :
						proxies_list.remove(proxies)
					except Exception :
						pass
					print ("[FETCHER] " + list(proxies.values())[0] + " Got Banned")
					num = random.randint(0,len(proxies_list) - 1)
					proxies = proxies_list[num]
					lock.release()
					continue

				pattern = re.compile(r"sn=([0-9 a-z]){32}")
				sn_res = re.search(pattern, url)
				sn = sn_res.group(0)[3:]
				pattern = re.compile(r"__biz=(.){16}")
				__biz_res = re.search(pattern, url)
				__biz = __biz_res.group(0)[6:]
				pattern = re.compile(r"idx=([0-9]){1}")
				idx_res = re.search(pattern, url)
				idx = idx_res.group(0)[4:]
				pattern = re.compile(r"mid=([0-9]){10}")
				mid_res = re.search(pattern, url)
				mid = mid_res.group(0)[4:]
				pattern = re.compile(r"chksm=([0-9 a-z]){76}")
				mid_res = re.search(pattern, url)
				chksm = mid_res.group(0)[6:]
				
				if res.status_code == 200 :
					html = res.text
					if self.ban in html :
						status = 1
					elif self.bad in html :
						status = 2
					elif self.ban2 in html :
						print ("[FETCHER] " + sn + " is Deleted")
						data = {
							"censor": 1
						}
						dbutils.UpdateArticle(sn, data)
						break
					else :
						status = 0

					if status != 0 :
						lock.acquire()
						try :
							proxies_list.remove(proxies)
						except Exception :
							pass
						print ("[FETCHER] " + list(proxies.values())[0] + " Got Banned: Status(" + str(status) + ")")
						num = random.randint(0,len(proxies_list) - 1)
						proxies = proxies_list[num]
						lock.release()
						continue
					if detect :
						break
					dt = dt.strftime("%Y-%m-%d")
					filename = dt + "_" + sn + "_" + __biz + "_" + idx + "_" + mid + "_" + chksm
					filepath = os.path.join(self.articles_path, filename + ".txt")
					with open(filepath, "w+", encoding = "utf-8-sig") as file :
						file.write(html)
					articles_path_queue.put(filename)
					print ("[FETCHER] " + list(proxies.values())[0] + " Get Article : " + sn)
					time.sleep(random.uniform(2, 4))
					break
				else :
					lock.acquire()
					try :
						proxies_list.remove(proxies)
					except Exception :
						pass
					print ("[FETCHER] " + list(proxies.values())[0] + " Got Banned: Status Code Error")
					num = random.randint(0,len(proxies_list) - 1)
					proxies = proxies_list[num]
					lock.release()
					continue

	def add_detect_jobs(self, articles_queue) :
		while True :
			dt = (date.today() - timedelta(2)).strftime("%Y-%m-%d")
			query = {
				"time" : dt
			}
			articles = dbutils.GetArticles(query)
			for article in articles :
				articles_queue.put((article["url"], dt, True))
			print ("[FETCHER] Add " + str(len(articles)) + " Detect Jobs")
			delay = 24 * 60 * 60
			time.sleep(delay)