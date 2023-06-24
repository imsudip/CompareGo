from flask import Flask, render_template, request, jsonify, send_from_directory
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from scrape import scrapeCompareRaja, scrapeDetailPage
from predict import predictReview

load_dotenv()

# connect to mongo db
client = MongoClient(os.getenv('MONGO_URI'))
db = client['comparego']
productsCollection = db['productreviews']

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    results = scrapeCompareRaja(query)
    return render_template('search.html', results=results)

# /details/id


@app.route('/details/<id>')
def details(id):
    url = 'https://www.compareraja.in/' + id + '.html'
    print(url)
    results = scrapeDetailPage(url)
    results['id'] = id
    # get product reviews , and overall rating
    productDetail = productsCollection.find_one({'id': id})
    if productDetail:
        productDetail['reviews'].reverse()
    else:
        productDetail = {
            'reviews': [],
            'overallRating': 0,
            'reviewsCount': 0
        }
    return render_template('details.html', results=results, productDetail=productDetail)


# review structure
# {
    # id: '123', # product id
    # reviews: [
    # {
    # comment: 'good product',
    # rating: 4,
    # }
    # ],
    # overallRating: 4.5
    # reviewsCount: 1
# }


@app.route('/api/review', methods=['POST'])
def addReview():
    data = request.get_json()
    id = data['id']
    review = data['review']
    # check if product exists
    product = productsCollection.find_one({'id': id})
    if product:
        # update the product
        updated_rating = (product['overallRating'] + review['rating']) / 2
        productsCollection.update_one({'id': id}, {'$push': {
                                      'reviews': review},
            '$set': {
            'overallRating': updated_rating},
            '$inc': {
            'reviewsCount': 1}
        },
        )
    else:
        # create the product
        productsCollection.insert_one({
            'id': id,
            'reviews': [review],
            'overallRating': review['rating'],
            'reviewsCount': 1
        })
    return jsonify({'message': 'success'})


@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    stars = predictReview(data['comment'])
    return jsonify({'stars': stars})

# ---------------------logos---------------------


@app.route('/logo/fpk')
def fkp():
    return send_from_directory('static', 'fpk.png')


@app.route('/logo/amzn')
def amzn():
    return send_from_directory('static', 'amzn.png')


@app.route('/logo/tclck')
def tclck():
    return send_from_directory('static', 'tclck.png')

# wildcard route for other than these


@app.route('/logo/<path:path>')
def send_logo(path):
    return send_from_directory('static', "shopping.png")


if __name__ == '__main__':
    app.run(debug=True)
