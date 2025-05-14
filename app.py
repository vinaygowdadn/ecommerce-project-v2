from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from db_config import db_config

app = Flask(__name__)
CORS(app)

# MySQL config
app.config.update(db_config)
mysql = MySQL(app)

# Routes
@app.route('/api/items', methods=['GET'])
def get_items():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    cur.close()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.get_json()
    name = data['name']
    desc = data['description']
    price = data['price']
    img = data['image_url']
    stock = data['stock']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO items (name, description, price, image_url, stock) VALUES (%s, %s, %s, %s, %s)", 
                (name, desc, price, img, stock))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Item added'}), 201

@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    user_id = data['user_id']
    items = data['items']  # [{item_id: 1, quantity: 2}, ...]

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO orders (user_id) VALUES (%s)", (user_id,))
    order_id = cur.lastrowid

    for item in items:
        cur.execute("INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)", 
                    (order_id, item['item_id'], item['quantity']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Order placed', 'order_id': order_id})

@app.route('/api/orders/history/<int:user_id>', methods=['GET'])
def order_history(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.id, o.created_at, i.name, i.price, oi.quantity
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN items i ON oi.item_id = i.id
        WHERE o.user_id = %s
        ORDER BY o.created_at DESC
    """, (user_id,))
    history = cur.fetchall()
    cur.close()
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True)
