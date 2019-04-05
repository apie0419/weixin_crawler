from pymongo import MongoClient
import configparser
import urllib



config = configparser.ConfigParser()
config.optionxform = str
config.read('setting.conf', encoding='utf-8')

ip          = config.get("MONGO", "IP")
port        = config.get("MONGO", "PORT")
user        = config.get("MONGO", "USER")
password    = urllib.parse.quote(config.get("MONGO", "PASSWORD"))
database    = config.get("MONGO", "DB")
collections = config.get("MONGO", "COLLECTION")


client = MongoClient("mongodb://{}:{}@{}:{}/{}".format(user, password, ip, port, database), connect = False, maxPoolSize = 200)
db = client[database]
articles = db[collections]

class DBUtility():

	def GetOneArticleById(self, query) :
		try :
			res = articles.find_one(query)
		except :
			res = None
		return res

	def GetArticles(self, query) :
		res = []
		try :
			cursor = articles.find(query)
		except :
			cursor = None

		for c in cursor :
			res.append(c)

		return res

	def InsertArticle(self, data) :
		try :
			id = articles.insert_one(data).inserted_id
		except :
			id = None
		return id

	def UpdateArticle(self, id, data) :
		try :
			id = articles.update_one({'_id': id}, {"$set": data}, upsert = False).inserted_id
		except :
			id = None

		return id

