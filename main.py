from flask import Flask
import requests
from flask_sqlalchemy import SQLAlchemy
import flask_restless
import googletrans
from googletrans import Translator
from datetime import datetime
from dateutil.tz import gettz

app= Flask(__name__)
app.secret_key = "IM<+2L#R~lgnPwjO6k@IF>zzUupVOPix>Xk,|/hDWk,U&xKL:i|L`fyWd`hJ"
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

class News(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title_en = db.Column(db.String)
    desc_en = db.Column(db.String)
    title_fr = db.Column(db.String)
    desc_fr = db.Column(db.String)
    timestamp = db.Column(db.DateTime,default=datetime.now(tz=gettz('Asia/Kolkata')))
    image_url = db.Column(db.String)


db.create_all()

# Fetching data from News api
url = "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=cae780e1b4bc4d7a9debcf61e6b1745e"
req = requests.get(url).json()
articles = req['articles']

# Translation from English to French Using Google translate
translator = Translator()

# Removal of 'page' key from result and Setting of 'Object' key to News using Postprocessors
def api_post_get_many(result=None, **kw):
    list_of_del_keys = []
    for key in result.keys():
        if key != 'objects':
            list_of_del_keys.append(key)
    for data in list_of_del_keys:
        del result[data]
    result['News'] = result.pop('objects')

# Sending data to database 
for news in articles:
    title_fr = translator.translate(text = news['title'], dest='fr' , src = 'en').text
    desc_fr = translator.translate(text = news['description'], dest='fr',src = 'en').text
    timenow = datetime.now(tz=gettz('Asia/Kolkata'))
    image_url = news['urlToImage']
    news_instance= News(title_en=news['title'],desc_en = news['description'],title_fr=title_fr,desc_fr=desc_fr ,timestamp = timenow, image_url = image_url)
    db.session.add(news_instance)
    db.session.commit()


# Creating api blueprint
manager = flask_restless.APIManager(app,flask_sqlalchemy_db=db)

blueprint = manager.create_api(News, methods=['GET'] ,exclude_columns = ['objects', 'id'],max_results_per_page=15 ,postprocessors = {'GET_MANY':[api_post_get_many]})



all_news = News.query.all()
if __name__== '__main__':
    app.run(debug=True)

# Deletion of all news when we shut our server
for news in all_news:
    db.session.delete(news)
    db.session.commit()