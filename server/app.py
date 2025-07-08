#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict(rules=("-restaurant_pizzas",)) for r in restaurants], 200

api.add_resource(RestaurantsResource, "/restaurants")



class RestaurantByIDResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204
    
api.add_resource(RestaurantByIDResource, "/restaurants/<int:id>")



class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas], 200
    
api.add_resource(PizzasResource, "/pizzas")


class RestaurantPizzasResource(Resource):
    def get(self):
        relationships = RestaurantPizza.query.all()
        return [rp.to_dict() for rp in relationships], 200
    
    def post(self):
        data = request.get_json(force=True)

        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"]
            )
            db.session.add(new_rp)
            db.session.commit()

            return make_response(new_rp.to_dict(rules=(
                "-restaurant.restaurant_pizzas",
                "-pizza.restaurant_pizzas"
            )), 201)

        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400
    
        
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")



if __name__ == "__main__":
    app.run(port=5555, debug=True)