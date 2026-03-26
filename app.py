from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    cursor.execute("""
        create table if not exists events (
            id integer primary key autoincrement,
            event text not null,
            product_id integer not null,
            product_name text not null,
            timestamp text not null
        )
    """)

    conn.commit()
    conn.close()


init_db()

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

    if product is None:
        return "Product not found", 404

    return render_template("product.html", product=product)


@app.route("/track", methods=["POST"])
def track_event():
    data = request.get_json()
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    cursor.execute("""
        insert into events (event, product_id, product_name, timestamp)
        values (?, ?, ?, ?)
    """, (data["event"], data["product_id"], data["product_name"], timestamp))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "timestamp": timestamp
    })


@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    cursor.execute("""
        select product_name, count(*) as views
        from events
        where event = 'view_product'
        group by product_name
        order by views desc
    """)

    results = cursor.fetchall()
    conn.close()

    analytics_data = []
    for row in results:
        analytics_data.append({
            "product_name": row[0],
            "views": row[1]
        })

    return jsonify(analytics_data)

@app.route("/analytics-page")
def analytics_page():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    # product view counts
    cursor.execute("""
        select product_name, count(*) as views
        from events
        where event = 'view_product'
        group by product_name
        order by views desc
    """)
    results = cursor.fetchall()

    # total views
    cursor.execute("""
        select count(*) from events where event = 'view_product'
    """)
    total_views = cursor.fetchone()[0]

    # recent activity
    cursor.execute("""
        select product_name, timestamp
        from events
        where event = 'view_product'
        order by timestamp desc
        limit 5
    """)
    recent_results = cursor.fetchall()

    conn.close()

    analytics_data = []
    for row in results:
        analytics_data.append({
            "product_name": row[0],
            "views": row[1]
        })

    recent_activity = []
    for row in recent_results:
        recent_activity.append({
            "product_name": row[0],
            "timestamp": row[1]
        })

    top_product = analytics_data[0] if analytics_data else None

    return render_template(
    "analytics.html",
    analytics=analytics_data,
    total_views=total_views,
    top_product=top_product,
    recent_activity=recent_activity
)


@app.route("/events")
def get_events():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    cursor.execute("""
        select id, event, product_id, product_name, timestamp
        from events
        order by id desc
    """)

    results = cursor.fetchall()
    conn.close()

    events_data = []
    for row in results:
        events_data.append({
            "id": row[0],
            "event": row[1],
            "product_id": row[2],
            "product_name": row[3],
            "timestamp": row[4]
        })

    return jsonify(events_data)

@app.route("/products")
def products_page():
    return render_template("products.html", products=products)

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)
