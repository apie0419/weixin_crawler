from bs4 import BeautifulSoup
import re
import os
import time
import configparser
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


filepath = os.path.join("test.txt")

try :
	with open(filepath, 'r', encoding="utf-8-sig") as f :
		content = f.read()
	if len(content) == 1 :
		print ("[PARSER] " + file + " No Content")
except :
	print ("[PARSER] " + file + " Does not Exist")

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

	print (account)
	print (category[account])

except Exception as e:
	traceback.print_exc()