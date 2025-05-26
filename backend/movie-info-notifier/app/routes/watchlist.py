from flask import Blueprint, request

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/watchlist')