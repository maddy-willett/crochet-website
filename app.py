from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

events = []

products = [
    {"id": 1, "name": "Crochet Bear", "price": 18},
    {"id": 2, "name": "Crochet Hat", "price": 20},
    {"id": 3, "name": "Crochet Purse", "price": 24}
]

@app.route("/")
def home():
    return render_template("index.html", products=products)

@app.route("/product/<int:product_id>")
def product_page(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    return render_template("product.html", product=product)

    if product is None:
        return "Product not found", 404
    
    return render_template("product.html", product=products)

@app.route("/track", methods=["POST"])
def track_event():
    data = request.get_json()
    events.append(data)

    print("Tracked event:", data)
    print("All events:", events)

    return jsonify({"status": "success"})

@app.route("/analytics")
def analytics():
    product_views = {}

    for event in events:
        if event["event"] == "view_product":
            product_id = event["product_id"]

            if product_id not in product_views:
                product_views[product_id] = 0

            product_views[product_id] += 1

    return jsonify(product_views)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)
