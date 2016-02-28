__author__ = 'ngcha_000'

from flask import Flask, render_template
from pymongo import MongoClient


client = MongoClient()
collection = client.GD.postsdaihocfpt


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/10posts')
def render_10posts():
    retrieve_documents = collection.find()

    document_list = []
    for document in retrieve_documents:
        print (document)
        document_list.append(document)
# print (document_list)
    return render_template("ForinJinja.html", content_list = document_list)

if __name__ == '__main__':
    app.run()