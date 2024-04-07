from flask import Flask, jsonify, request, abort
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'restaurant.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    with app.open_resource('schema.sql', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()

# Routes
@app.route('/products', methods=['GET'])
def get_all_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if product is None:
        abort(404)
    return jsonify(dict(product))

@app.route('/products', methods=['POST'])
def create_product():
    if not request.json or 'name' not in request.json or 'price' not in request.json:
        abort(400)
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, price) VALUES (?, ?)', (request.json['name'], request.json['price']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product created successfully'}), 201

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if product is None:
        abort(404)
    if not request.json:
        abort(400)
    updated_product = {
        'name': request.json.get('name', product['name']),
        'price': request.json.get('price', product['price'])
    }
    conn.execute('UPDATE products SET name = ?, price = ? WHERE id = ?', (updated_product['name'], updated_product['price'], product_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product deleted successfully'})

# Order routes
@app.route('/orders', methods=['GET'])
def get_all_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

@app.route('/orders', methods=['POST'])
def place_order():
    if not request.json or 'product_id' not in request.json or 'quantity' not in request.json:
        abort(400)
    product_id = request.json['product_id']
    quantity = request.json['quantity']
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if product is None:
        abort(404)
    conn.execute('INSERT INTO orders (product_id, quantity) VALUES (?, ?)', (product_id, quantity))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Order placed successfully'}), 201

# Initialize database
if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
