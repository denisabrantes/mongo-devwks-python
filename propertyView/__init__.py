from flask import Blueprint

prop_bp = Blueprint('prop_bp', __name__, template_folder='templates', static_folder='../static', static_url_path='assets', url_prefix='/viewProperty')

from . import views
