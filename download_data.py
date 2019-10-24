from utility.DBUtility import DBUtility
from multiprocessing   import Queue, Process, Lock, Manager, Value, cpu_count
from datetime          import date, timedelta
from progressbar       import *
from argparse          import ArgumentParser
import pandas as pd
import csv, os, sys, time


parser = ArgumentParser()
parser.add_argument("--keywords", help="needed keywords Path", dest="keyword")
parser.add_argument("--start", help="start date: yyyy-mm-dd", dest="start", required=True)
parser.add_argument("--end", help="end date: yyyy-mm-dd", dest="end", required=True)

base_path = os.path.dirname(os.path.abspath(__file__))

WORKERS = cpu_count()

def Download(dt_queue, writelock, dbutil, finish, res, keywords):
    while True:
        try :
            dt = dt_queue.get()
        except Exception :
            break

        articles = dbutil.GetArticles({"time": str(dt), "state": "cn"})

        tmp = list()
        for article in articles:
            if len(keywords) == 0:
                fetch = True
            else:
                fetch = False
            for keyword in keywords:
                if keyword == "台湾":
                    if article["segs"].count(keyword) > 1:
                        fetch = True
                        break
                else:
                    if article["segs"].count(keyword) > 0:
                        fetch = True
                        break
            if fetch:
                tmp.append({
                    "_id": article["_id"],
                    "account": article["account"],
                    "author": article["author"],
                    "date": str(dt),
                    "segs": article["segs"],
                    "title": article["title"],
                    "official": article["official"],
                    "censor": article["censor"],
                    "license": article["license"],
                    "forprofit": article["forprofit"]
                })

        writelock.acquire()

        res.extend(tmp)

        finish.value += 1

        writelock.release()

if __name__ == '__main__':
    writelock = Lock()
    dt_queue = Queue()
    manager = Manager()
    finish = Value("i", 0)
    res = manager.list()
    args = parser.parse_args()
    keyword_path = args.keyword
    start_str = args.start.split("-")
    end_str = args.end.split("-")
    start = date(int(start_str[0]), int(start_str[1]), int(start_str[2]))
    end = date(int(end_str[0]), int(end_str[1]), int(end_str[2]))
    keywords = list()
    if keyword_path is not None:
        with open(keyword_path, "r", encoding="utf-8-sig") as keywds:
            for word in keywds:
                keywords.append(word.replace("\n", ""))
    now = start
    dbutil = DBUtility()

    while True:
        if now > end:
            break
        dt_queue.put(str(now))
        now += timedelta(days = 1)


    for _ in range(WORKERS):
        t = Process(target = Download, args = (dt_queue, writelock, dbutil, finish, res, keywords))
        t.daemon = True
        t.start()

    total = dt_queue.qsize()

    widgets = ['Downloading: ',Percentage(), ' ', Bar('#'),' ', Timer()]

    pbar = ProgressBar(widgets=widgets).start()

    while True :
        percent = int((total - dt_queue.qsize())/total*100)
        pbar.update(percent)
        time.sleep(0.1)
        if finish.value == total and percent >= 100:
            break
    pbar.finish()
    df = pd.DataFrame(list(res))
    df.to_csv(os.path.join(base_path, "Data.csv"))
