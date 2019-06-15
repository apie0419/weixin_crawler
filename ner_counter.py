# encoding=utf8

from utility.DBUtility import DBUtility
import tensorflow as tf
import numpy as np
from ner.model import Model
from ner.data_utils import load_word2vec, input_from_line
from ner.loader import load_sentences
from ner.utils import create_model, load_config

def evaluate_line():

    config = load_config(os.path.join(base_path, "ner/config_file"))
    logger = get_logger(os.path.join(base_path, "ner/train.log"))
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    dbutils = DBUtility()
    articles = dbutils.GetArticles({"NER": ""})
    jobs = list()

    for article in articles :
        dt_list = article["time"].split("-")
        dt = date(int(dt_list[0]), int(dt_list[1]), int(dt_list[2]))
        if dt >= date(2019, 3, 30) :
            jobs.append(article)

    print (str(len(jobs)) + " Jobs")

    with open(os.path.join(base_path, "ner/maps.pkl"), "rb") as f:
        char_to_id, id_to_char, tag_to_id, id_to_tag = pickle.load(f)
    with tf.Session(config=tf_config) as sess:
        model = create_model(sess, Model, os.path.join(base_path, "ner/ckpt_IDCNN"), load_word2vec, config, id_to_char, logger, False)
        num = 0
        error = 0
        for job in jobs:
            try :
                sn = job["_id"]
                line = job["content"]
                result = model.evaluate_line(sess, input_from_line(line, char_to_id), id_to_tag)
                res = list()
                for entity in result["entities"] :
                    res.append({
                        "word": entity["word"], 
                        "type": entity["type"]
                    })
                data = {
                    "NER": res
                }
                dbutils.UpdateArticle(sn, data)
                num += 1
                print ("Complete " + str(num))
                print ("Error: " + str(error))
            except Exception as e :
                error += 1


if __name__ == "__main__":
    evaluate_line()



