import os
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request
from pymongo import MongoClient
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)  # adds /metrics for Prometheus

# Database settings come from environment variables
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "productdb")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
PORT = int(os.getenv("PORT", "5002"))


def get_collection():
    # tests replace this client with a fake one
    if not hasattr(app, "mongo_client"):
        if MONGO_USER and MONGO_PASSWORD:
            uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
        else:
            uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
        app.mongo_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    return app.mongo_client[MONGO_DB]["products"]


def to_json(product):
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "price": product["price"],
        "stock": product.get("stock", 0),
        "description": product.get("description", ""),
    }


def find_by_id(product_id):
    try:
        return get_collection().find_one({"_id": ObjectId(product_id)})
    except InvalidId:
        return None


def check_fields(data, partial=False):
    # returns an error message, or None if the data is fine
    if not data:
        return "Request body must be JSON"
    if not partial:
        if not data.get("name"):
            return "name is required"
        if "price" not in data:
            return "price is required"
    if "price" in data:
        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            return "price must be a number that is 0 or more"
    if "stock" in data:
        if not isinstance(data["stock"], int) or data["stock"] < 0:
            return "stock must be a whole number that is 0 or more"
    return None


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "product-service"}), 200


@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json(silent=True)
    error = check_fields(data)
    if error:
        return jsonify({"error": error}), 400

    product = {
        "name": data["name"],
        "price": data["price"],
        "stock": data.get("stock", 0),
        "description": data.get("description", ""),
    }
    result = get_collection().insert_one(product)
    product["_id"] = result.inserted_id
    return jsonify(to_json(product)), 201


@app.route("/products", methods=["GET"])
def list_products():
    products = [to_json(p) for p in get_collection().find()]
    return jsonify(products), 200


@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    product = find_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(to_json(product)), 200


@app.route("/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    product = find_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True)
    error = check_fields(data, partial=True)
    if error:
        return jsonify({"error": error}), 400

    allowed = ["name", "price", "stock", "description"]
    changes = {k: v for k, v in data.items() if k in allowed}
    if changes:
        get_collection().update_one({"_id": product["_id"]}, {"$set": changes})
    return jsonify(to_json(find_by_id(product_id))), 200


@app.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = find_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    get_collection().delete_one({"_id": product["_id"]})
    return jsonify({"message": "Product deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
