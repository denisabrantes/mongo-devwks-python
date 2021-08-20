import config
from flask import render_template, request
from pymongo import MongoClient
from . import home_bp

@home_bp.route('/')
def render_home():

    # Variables for query filtering
    # city refers to the address.market field
    city = request.args.get('city', 'New York').replace('%20',' ')
    print(city)
    pricefrom = float(request.args.get('pricefrom', 1))
    priceto = float(request.args.get('priceto', 1000))
    amenities = request.args.get('amenities', '')

    # On Initial Load, Render Properties in New York: [40.7280785,-73.994592]
    conn_string = 'mongodb+srv://' + config.MDB_USER + ':' + config.MDB_PASS + '@' + config.MDB_URL + '/sample_airbnb?retryWrites=true&w=majority'
    mongo = MongoClient(conn_string)
    db = mongo.sample_airbnb
    collection = db.listingsAndReviews
    coordinates = [-73.9868103, 40.7620853]
    if city == 'Porto':
        coordinates = [-8.6182103, 41.1494736]
    if city == 'Maui':
        coordinates = [-156.45649, 20.76438]
    if city == 'Rio de Janeiro':
        coordinates = [-43.1882865, -22.9375275]
    if city == 'Sidney':
        city = 'Sydney'
    if city == 'Sydney':
        coordinates = [151.2025025, -33.8784914]
    if city == 'Barcelona':
        coordinates = [2.1620029, 41.3882004]

    searchCriteria = {
        'address.location' : { '$near': { '$geometry': { 'type': 'Point' , 'coordinates': coordinates }, '$maxDistance': 3000 } },
        'price' : { '$gte' : pricefrom, '$lte' : priceto },
    }
    if amenities != '':
        searchCriteria['amenities'] = amenities
    print(searchCriteria)
    output = []
    searchMetadata = []
    returnPayload = []

    #Query with Pagination
    allProperties = collection.find(searchCriteria).limit(100)
    for thisProperty in allProperties:
      try:
          bathrooms = str(thisProperty['bathrooms']).replace(".0","")
      except:
          bathrooms = 0
      output.append({'_id' : thisProperty['_id'], 'name' : thisProperty['name'], 'summary' : thisProperty['summary'], 'description' : thisProperty['description'],
    'notes' : thisProperty['notes'], 'property_type' : thisProperty['property_type'], 'accommodates' : thisProperty['accommodates'], 'bedrooms' : thisProperty['bedrooms'],
    'beds' : thisProperty['beds'], 'bathrooms' : bathrooms, 'amenities' : thisProperty['amenities'], 'price' : thisProperty['price'],
    'images' : thisProperty['images'], 'address' : thisProperty['address']})

    #print(output)
    totalRecords = allProperties.count(True)
    totalPages = ((totalRecords + 10 // 2) // 10)
    if totalPages < totalRecords / 10:
        totalPages = totalPages + 1
    searchMetadata.append({'coordinates' : coordinates, 'city' : city, 'pricefrom' : pricefrom, 'priceto' : priceto, 'amenities' : amenities,
    'totalRecords' : totalRecords, 'totalPages' : totalPages})
    returnPayload.append({'properties' : output})
    return render_template('/home.html', searchMetadata = searchMetadata, propertyList = returnPayload)
