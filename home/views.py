import config, json
from flask import Flask, render_template, jsonify, request, Response
from pymongo import MongoClient
from bson import json_util
from decimal import Decimal
from . import home_bp

conn_string = 'mongodb+srv://' + config.MDB_USER + ':' + config.MDB_PASS + '@' + config.MDB_URL + '/sample_airbnb?retryWrites=true&w=majority'
mongo = MongoClient(conn_string)
db = mongo.sample_airbnb
collection = db.listingsAndReviews

@home_bp.route('/', methods=['GET'])
def render_home():

    # Variables for query filtering
    # city refers to the address.market field
    city = request.args.get('city', 'New York').replace('%20',' ')
    print(city)
    pricefrom = float(request.args.get('pricefrom', 1))
    priceto = float(request.args.get('priceto', 1000))
    amenities = request.args.get('amenities', '')

    # On Initial Load, Render Properties in New York: [40.7280785,-73.994592]
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

    # New Search strategy: run 2 searches. One to return name and coordinates, to feed the map (max 100)
    # and a second search to return only the first 10 properties, to feed the list. Pagination will
    # need to skip records based on the page number

    searchCriteria = {
        'address.location' : { '$near': { '$geometry': { 'type': 'Point' , 'coordinates': coordinates }, '$maxDistance': 3000 } },
        'price' : { '$gte' : pricefrom, '$lte' : priceto }
    }
    if amenities != '':
        searchCriteria['amenities'] = amenities
    #print(searchCriteria)
    searchProjection = { '_id' : 1, 'name' : 1, 'summary' : 1, 'description' : 1, 'notes' : 1, 'property_type' : 1, 'accommodates' : 1, 
                        'bedrooms' : 1, 'beds' : 1, 'bathrooms' : 1, 'amenities' : 1, 'price' : 1, 'images' : 1, 'address' : 1}
    coordProjection = { '_id' : 1, 'address.location' : 1, 'name' : 1}
    allCoordinates = []
    output = []
    searchMetadata = []
    returnPayload = []

    #Get Coordinate List
    allCoordinates = collection.find(searchCriteria, coordProjection).limit(100)

    #Query with Pagination
    allProperties = collection.find(searchCriteria, searchProjection).limit(10)

    #print(output)
    totalRecords = allCoordinates.count(True)
    totalPages = ((totalRecords + 10 // 2) // 10)
    if totalPages < totalRecords / 10:
        totalPages = totalPages + 1
    searchMetadata.append({'coordinates' : coordinates, 'city' : city, 'pricefrom' : pricefrom, 'priceto' : priceto, 'amenities' : amenities,
    'totalRecords' : totalRecords, 'totalPages' : totalPages})
    
    returnPayload.append({'coordinates' : allCoordinates})
    returnPayload.append({'properties' : allProperties})
    return render_template('/home.html', searchMetadata = searchMetadata, propertyList = returnPayload)
 


@home_bp.route('/loadPage', methods=['GET'])
def loadPage():

    #Search Criteria
    pagenum = request.args.get('pagenum', type=int)
    end = pagenum * 10
    initial = (end - 10)

    coords = request.args.get('coordinates').split(',')
    coordinates = []
    coordinates.append(float(coords[0]))
    coordinates.append(float(coords[1]))
    pricefrom = request.args.get('pricefrom', type=int)
    priceto = request.args.get('priceto', type=int)
    amenities = request.args.get('amenities', type=str)
    
    searchCriteria = {
        'address.location' : { '$near': { '$geometry': { 'type': 'Point' , 'coordinates': coordinates }, '$maxDistance': 3000 } },
        'price' : { '$gte' : pricefrom, '$lte' : priceto }
    }
    if amenities != '':
        searchCriteria['amenities'] = amenities

    #print(searchCriteria)
    searchProjection = { '_id' : 1, 'name' : 1, 'summary' : 1, 'description' : 1, 'notes' : 1, 'property_type' : 1, 'accommodates' : 1, 
                        'bedrooms' : 1, 'beds' : 1, 'bathrooms' : 1, 'amenities' : 1, 'price' : 1, 'images' : 1, 'address' : 1}

    #Query with Pagination
    allProperties = collection.find(searchCriteria, searchProjection).limit(10).skip(initial)
    #returnPayload = [json.dumps(thisProperty, default=json_util.default) for thisProperty in allProperties]
    returnPayload = []
    for thisProperty in allProperties:
          try:
           bathrooms = float(str(thisProperty['bathrooms']).replace(".0",""))
           price = float(str(thisProperty['price']))
          except:
           bathrooms = 0
           price = 0
        
          returnPayload.append({ '_id' : thisProperty['_id'], 'name' : thisProperty['name'], 'summary' : thisProperty['summary'], 
            'description' : thisProperty['description'], 'notes' : thisProperty['notes'], 'property_type' : thisProperty['property_type'], 
            'accommodates' : thisProperty['accommodates'], 'bedrooms' : thisProperty['bedrooms'], 'beds' : thisProperty['beds'], 
            'bathrooms' : bathrooms, 'amenities' : thisProperty['amenities'], 'price' : price, 
            'images' : thisProperty['images'], 'address' : thisProperty['address']})

    #print('==> Pagenum: ', initial)
    #print('==> Returning ', len(returnPayload), ' documents')
    return {"data" : [returnPayload]}




