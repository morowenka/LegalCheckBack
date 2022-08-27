#!/usr/bin/env python
import os

from flask import Flask, request
from pymongo import MongoClient
from bson.json_util import dumps
from  Model import Model
import torch


app = Flask(__name__)

client = MongoClient("mongo:27017")
db = client.ArticleDB
model = Model()



@app.route('/', methods = ['GET'])
def todo():
    try:
        client.admin.command('ismaster')
    except:
        return "Server not available"
    return "Hello from the MongoDB client!\n"


@app.route("/insert_article",methods=['POST'])
def insert():
    article = request.form.get('article')
    try:
       # db.articles.insert_one(
       #        {
       #               'article': article,
       #        }
       # )
       # return dumps({'message': 'SUCCESS'})
       result = model.process_text(article)
       print(result)
       return dumps(result)
    except Exception as e:
       return dumps({'error': str(e)})


@app.route("/get_all_articles", methods = ['GET'])
def get_all_articles():
    try:
        articles = db['articles'].find()
        # print(contacts.name)
        return dumps(articles)
    except Exception as e:
        return dumps({'error' : str(e)})

@app.route("/get_one_article/<name>", methods = ['GET'])
def get_one_article(name):
    try:
        x = db['articles'].find_one({"name": name})
        return dumps(x)
    except Exception as e:
        return dumps({'error' : str(e)})


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9090), debug=True)

