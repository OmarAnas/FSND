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
after_request() Allows CORS in the application

'''


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PATCH,POST,DELETE,OPTIONS')
    return response

# ROUTES


'''
GET /drinks endpoint
privacy: public endpoint
function: gets all drinks from database without their
          details (title and recipe only)
returns: status code 200 and json {"success": True, "drinks": drinks}
         where drinks is the list of drinks or 404 code if not found
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    short_drinks = [drink.short() for drink in drinks]

    if len(short_drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": short_drinks,
        "status_code": 200
    })


'''
GET /drinks-detail endpoint
privacy: only manager and barista
function: gets all drinks from database with their details
returns: status code 200 and json {"success": True, "drinks": drinks}
         where drinks is the list of drinks or 404 code if not found
'''


@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def get_details(payload):
    drinks = Drink.query.order_by(Drink.id).all()
    long_drinks = [drink.long() for drink in drinks]

    if len(long_drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": long_drinks,
        "status_code": 200
    })


'''
POST /drinks endpoint
privacy: only manager
function: creates new drink
returns: status code 200 and json {"success": True, "drinks": drink}
         where drink an array containing only
         the newly created drink or 422 if unprocessable
'''


@app.route('/drinks', methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):

    body = request.get_json()
    drinkTitle = body.get("title")
    recipe = body.get("recipe")

    if not isinstance(recipe, list):
        recipe = [recipe]

    recipe = str(recipe).replace("'", "\"")

    try:
        insertDrink = Drink(title=drinkTitle, recipe=recipe)
        insertDrink.insert()

        return jsonify({
            "success": True,
            "drinks": insertDrink.long(),
            "status_code": 200
        })
    except BaseException:
        abort(422)


'''
PATCH /drinks/drink_id endpoint
privacy: only manager
function: updates a drink and its details
returns: status code 200 and json {"success": True, "drinks": drink}
         where drink an array containing only the updated drink
         or 422 if unprocessable
'''


@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drink(payload, drink_id):
    body = request.get_json()
    drinkTitle = body.get("title")
    recipe = body.get("recipe")

    if not isinstance(recipe, list):
        recipe = [recipe]
    recipe = str(recipe).replace("'", "\"")

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if(drink is None):
            abort(404)

        drink.title = drinkTitle
        drink.recipe = recipe
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()],
            "status_code": 200
        })

    except BaseException:
        abort(422)


'''
DELETE /drinks/drink_id endpoint
privacy: only manager
function: Deletes a drink
returns: status code 200 and json {"success": True, "delete": id}
         where id is the id of the deleted record
         or 404 if id is not found or 400 if bad request
'''


@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if(drink is None):
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink.id,
            "status_code": 200
        })

    except BaseException:
        abort(400)


# Error Handling

# Error handler for 422 unprocessable errors

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# Error handler for 404 not found


@app.errorhandler(404)
def not_found_404(error):
    return jsonify({
        "success": False,
        "message": "Resource Not Found",
        "error": 404
    }), 404

# Error handler for 400 Bad request errors


@app.errorhandler(400)
def bad_request_400(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad Request"
    }), 400

# Error handler for 405 not allowed errors


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': "Method Not Allowed"
    }), 405

# Error handler for 500 server error


@app.errorhandler(500)
def server_error_500(error):
    return jsonify({
        'success': False,
        'error': 500,
        'Message': "Internal Server Error"
    }), 500

# custom error handler authentication errors


@app.errorhandler(AuthError)
def Auth_Error(error):
    return jsonify({
        'success': False,
        'status_code': error.to_dict()["status_code"],
        'Message': error.to_dict()["code"],
        'Description': error.to_dict()["description"]
    }), error.to_dict()["status_code"]
