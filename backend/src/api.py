import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    try:
        drinks = Drink.query.all()
        if not drinks:
            abort(404)

        formatted_drinks = [drink.short() for drink in drinks]

        if len(drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        }), 200
    except Exception:
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def retrieve_drinks_detail():
    try:
        drinks = Drink.query.all()
        if not drinks:
            abort(404)
    
        formatted_drinks = [drink.long() for drink in drinks]

        if len(drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        }), 200
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def add_drink():
    try:
        body = request.get_json()
        if not body:
            abort(403)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        formatted_recipe = json.dumps(new_recipe)
        drink = Drink(title = new_title, recipe = formatted_recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception:
        abort(400)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        drink.title = body.get('title')
        drink.recipe = json.dumps(body.get('recipe'))
        formatted_drink = [drink.long()]

        drink.update()
        return jsonify({
            'success': True,
            'drinks': formatted_drink
        }), 200

    except Exception:
        abort(400)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def purge_drink(drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except Exception:
        abort(500)

# Error Handling


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):

@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def return_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response