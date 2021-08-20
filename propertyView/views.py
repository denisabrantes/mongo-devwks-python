import config
from flask import render_template, request
from pymongo import MongoClient
from . import prop_bp

@prop_bp.route('/')
def render_propView():

    # Variables for query filtering
    id = request.args.get('id', '')
    conn_string = 'mongodb+srv://' + config.MDB_USER + ':' + config.MDB_PASS + '@' + config.MDB_URL + '/sample_airbnb?retryWrites=true&w=majority'
    mongo = MongoClient(conn_string)
    db = mongo.sample_airbnb
    collection = db.listingsAndReviews

    searchCriteria = { '_id' : id }
    output = []

    #Run Query
    thisProperty = collection.find_one(searchCriteria)
    bathrooms = str(thisProperty['bathrooms']).replace(".0","")
    scores = thisProperty['review_scores']
    try:
        scoreLoc = scores['review_scores_location']
    except:
        scoreLoc = 0
    try:
      scoreVal = scores['review_scores_value']
    except:
      scoreVal = 0
    review_count = len(thisProperty['reviews'])
    output.append({'_id' : thisProperty['_id'], 'name' : thisProperty['name'], 'summary' : thisProperty['summary'], 'description' : thisProperty['description'],
    'notes' : thisProperty['notes'], 'property_type' : thisProperty['property_type'], 'accommodates' : thisProperty['accommodates'], 'bedrooms' : thisProperty['bedrooms'],
    'beds' : thisProperty['beds'], 'bathrooms' : bathrooms, 'amenities' : thisProperty['amenities'], 'price' : thisProperty['price'], 'room_type' : thisProperty['room_type'],
    'images' : thisProperty['images'], 'address' : thisProperty['address'], 'scoreLoc' : scoreLoc, 'scoreVal' : scoreVal, 'review_count' : review_count})

    # Run query to get 4 similar properties.
    # Similar is based on coordinates, with a 500 meters range
    newCoordinates = thisProperty['address']['location']['coordinates']
    newSearchCriteria = {'address.location' : { '$near': { '$geometry': { 'type': 'Point' , 'coordinates': newCoordinates }, '$maxDistance': 500 } }, '_id' : { '$ne' : id} }
    recProperties = collection.find(newSearchCriteria).limit(4)
    similarProperties = []
    for thisRecProperty in recProperties:
        try:
            scoreLoc = thisRecProperty['review_scores']['review_scores_location']
        except:
            scoreLoc = 0
        similarProperties.append({'_id' : thisRecProperty['_id'], 'name' : thisRecProperty['name'], 'property_type' : thisRecProperty['property_type'],
        'images' : thisRecProperty['images'], 'price' : thisRecProperty['price'], 'scoreLoc' : scoreLoc})

    print(similarProperties)
    return render_template('/viewProperty.html', propertyData = output, similarProperties = similarProperties)
