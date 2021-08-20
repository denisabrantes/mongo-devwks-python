# mongo.py

import config
from flask import Flask, Blueprint, render_template, jsonify,  request
from home import home_bp
from propertyView import prop_bp


app = Flask(__name__)
app.register_blueprint(home_bp)
app.register_blueprint(prop_bp)


if __name__ == '__main__':
    app.run(debug=True)
