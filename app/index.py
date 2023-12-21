import math
from flask import render_template, request, redirect, session, jsonify
import dao
import utils
from app import app, login
from flask_login import login_user


@app.route('/')
def index():
    kw = request.args.get('kw')
    cate_id = request.args.get('cate_id')
    page = request.args.get('page')
    cates = dao.load_categories()
    products = dao.load_products(kw, cate_id, page)

    num = dao.product_count()
    return render_template('index.html', categories=cates, products=products,
                           pages=math.ceil(num/app.config["PAGE_SIZE"]))


@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route("/api/cart", methods=['post'])
def add_to_cart():
    '''
    {
        "cart": {
            "1": {
                "id": "1",
                "name": "IPhone"
                "price": 123,
                "quantity": 1
            }, "2": {
                "id": "2",
                "name": "IPhone"
                "price": 123,
                "quantity": 1

        }
    '''

    data = request.json
    cart = session.get('cart')
    if cart is None:
        cart = {}

    id = str(data.get('id'))
    if id in cart:  # đã có sản phẩm trong giỏ hàng
        cart[id]['quantity'] += 1
    else:  # chưa có sản phẩm trong giỏ hàng
        cart[id] = {
                "id": id,
                "name": data.get('name'),
                "price": data.get("price"),
                "quantity": 1
            }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods =['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        quantity = request.json.get('quantity')
        cart[product_id]['quantity'] = int(quantity)

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods =['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/login')
def process_login_user():
    return render_template('login.html')


@login.user_loader  # mỗi lần login xong tự động nó sẽ get đối tượng user từ db và nó gắn cho cái biến current
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_response():
    return {
        'categories': dao.load_categories(),
        'cart': utils.count_cart(session.get('cart'))
    }


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
