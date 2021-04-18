import flask
from flask import request, jsonify

from data import db_session
from data.products import Products

blueprint = flask.Blueprint('products_api', __name__, template_folder='templates')


@blueprint.route('/api/products')
def get_products():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).all()
    return jsonify(
        {'products': [item.to_dict(only=(
            'id', 'title', 'quantity', 'price', "description", "category", "user_id")) for
            item in products]})


@blueprint.route('/api/products/<int:product_id>', methods=['GET'])
def get_one_product(product_id):
    db_sess = db_session.create_session()
    products = db_sess.query(Products).get(product_id)
    if not products:
        return jsonify({'error': 'Not found'})
    return jsonify({'products': products.to_dict(
        only=('id', 'title', 'quantity', 'price', "description", "category", "user_id"))})


@blueprint.route('/api/products', methods=['POST'])
def create_product():
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'title', 'quantity', 'price', "description", "category", "user_id"]):
        return jsonify({'error': 'Bad request'})
    elif db_sess.query(Products).get(request.json["id"]):
        return jsonify({'error': 'Id already exists'})

    products = Products(
        id=request.json['id'],
        title=request.json['title'],
        quantity=request.json['quantity'],
        price=request.json['price'],
        description=request.json['description'],
        category=request.json['category'],
        user_id=request.json['user_id']
    )
    db_sess.add(products)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_job(product_id):
    db_sess = db_session.create_session()
    products = db_sess.query(Products).get(product_id)
    if not request.json:
        return jsonify({'error': 'Empty request'})
    if not products:
        return jsonify({'error': 'Not found'})
    db_sess.delete(products)
    db_sess.commit()
    return jsonify({'success': 'OK'})
