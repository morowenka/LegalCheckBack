#!/usr/bin/env python
import os

from flask import Flask, request, send_file
from pymongo import MongoClient
from bson.json_util import dumps
from  Model import Model


app = Flask(__name__)

client = MongoClient("mongo:27017")
db = client.ArticleDB
model = Model()
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


@app.route('/', methods = ['GET'])
def todo():
    try:
        client.admin.command('ismaster')
    except:
        return "Server not available"
    return "Hello from the MongoDB client!\n"


@app.route("/insert_article",methods=['POST'])
def insert():
    import uuid
    article = request.files['article']
    name = request.form['name']
    filename = str(uuid.uuid4())
    article.save(os.path.join('files', f'{filename}.docx'))
    # try:
    db.articles.insert_one(
          {
                'name': name,
                'filename':filename,
          }
    )
    result = model.process_text(os.path.join('files', f'{filename}.docx'))
    return json.dumps(result, cls=NumpyEncoder)
    # except Exception as e:
    #    return dumps([{'error': str(e)}])


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
        return send_file(os.path.join(os.getcwd(), 'files', f'{x["filename"]}.docx'))
        # return dumps(x)
    except Exception as e:
        return dumps({'error' : str(e)})

@app.route("/get_one_article_result/<name>", methods = ['GET'])
def get_one_article_result(name):
    try:
        x = db['articles'].find_one({"name": name})
        result = model.process_text(os.path.join('files', f'{x["filename"]}.docx'))
        return json.dumps(result, cls=NumpyEncoder)
        # return dumps(x)
    except Exception as e:
        return dumps({'error' : str(e)})


@app.route("/get_all_articles_result", methods = ['GET'])
def get_all_articles_result():
    try:
        articles = db['articles'].find()
        r = []
        for article in articles:
            result = model.process_text(os.path.join('files', f'{article["filename"]}.docx'))
            r.append(result)
        return json.dumps(result, cls=NumpyEncoder)
    except Exception as e:
        return dumps({'error' : str(e)})

@app.route("/clean_bd", methods = ['DELETE'])
def clean():
    try:
        db.articles.drop()
        return dumps({'message' : 'succes'})
    except Exception as e:
        return dumps({'error' : str(e)})


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9090), debug=True)

