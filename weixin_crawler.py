from multiprocessing import Queue, Process, Manager, Value, Lock
import time
from tools.Fetcher import Fetcher
from tools.Parser import Parser
import os
import configparser

FETCER_WORKERS = 25
PARSER_WORKDER = 10
REPORT_INTERVAL = 5

config = configparser.ConfigParser()
config.optionxform = str
config.read('setting.conf', encoding='utf-8')


if __name__ == '__main__':
	lock = Lock()
	fetcher = Fetcher()
	parser = Parser()
	manager = Manager()
	articles_queue = Queue()
	articles_path_queue = Queue()
	proxies_list = manager.list()


	num = 0
	articles_path = config.get("SYSTEM", "ARTICLES_DIR")
	urls_path = config.get("SYSTEM", "URLS_DIR")

	if not os.path.exists(articles_path):
		os.mkdir(articles_path)

	if not os.path.exists(urls_path):
		os.mkdir(urls_path)

	for file in os.listdir(articles_path) :
		articles_path_queue.put(file[:-4])
		num += 1

	print ("Add " + str(num) + " Jobs")

	for _ in range(FETCER_WORKERS):
		p = Process(target=fetcher.fetch, args=(articles_queue, articles_path_queue, proxies_list, lock))
		p.daemon = True
		p.start()

	for _ in range(PARSER_WORKDER):
		p = Process(target=parser.parse, args=(articles_path_queue, ))
		p.daemon = True
		p.start()

	p = Process(target=parser.parseurls, args=(articles_queue, ))
	p.daemon = True
	p.start()
	p = Process(target=fetcher.add_detect_jobs, args=(articles_queue, ))
	p.daemon = True
	p.start()

	while True :
		time.sleep(REPORT_INTERVAL)
		print ('[FETCHER_QUEUE] Job Remaining: ' + str(articles_queue.qsize()))
		print ("[PARSER_QUEUE] Job Remaining: " + str(articles_path_queue.qsize()))


