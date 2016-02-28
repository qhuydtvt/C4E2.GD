__author__ = 'ngcha_000'

from flask import Flask, render_template
from pymongo import MongoClient


client = MongoClient()
db = client.db
collects = db.collection_names(include_system_collections=False)

# for each_collection in client.GD:
#         print (each_collection)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/10posts')
def render_10posts():
        retrieve_documents = db.get_collection(collects[0])
        document_list = []
        for document in retrieve_documents:
            print (document)
            document_list.append(document)
        return render_template("ForinJinja.html", content_list = document_list)

if __name__ == '__main__':
    app.run()