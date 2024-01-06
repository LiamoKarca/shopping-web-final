import secrets
from urllib import request
from random import randint

from flask import render_template, Flask, request, redirect, flash, session
from apps.database import Database

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 生成一个 16 字节的随机密钥


@app.route('/')
def index():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('index.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('index.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products)


@app.route('/login')
def login():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        error = ''
        if 'error' in session:
            error = session['error']
            session.pop('error')  # 从 session 中移除错误消息，避免再次显示

        return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    # 用户注销，清除会话中的登录信息
    session.pop('username', None)
    return redirect('/login')  # 注销后重定向到登录页面


@app.route('/checkLogin', methods=['POST'])
def checkLogin():
    db = Database()
    loginEmail = request.form['singin-email']
    loginPassword = request.form['singin-password']
    username = db.getUsername(loginEmail)
    # 調用登入驗證方法
    loginResult = db.login(loginEmail, loginPassword)
    # 在 checkLogin 路由中
    if loginResult == 'Login successful':
        session['username'] = username
        session.pop('error', None)
        return redirect('/dashboard')  # 重導向回登入頁面
    else:
        flash(loginResult, 'error')  # 將錯誤訊息放入 flash 中，並標記為 'error'
        return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    db = Database()
    con = db.connect()

    if request.method == 'POST':
        registerUserName = request.form['register-userName']
        registerPassword = request.form['register-password']
        registerFirstName = request.form['register-firstName']
        registerLastName = request.form['register-lastName']
        registerAddress = request.form['register-address']
        registerPhone = request.form['register-phone']
        registerEmail = request.form['register-email']

        registerResult = db.register(firstName=registerFirstName,
                                     lastName=registerLastName,
                                     displayName=registerUserName,
                                     email=registerEmail,
                                     password=registerPassword,
                                     address=registerAddress,
                                     phone=registerPhone)

        if registerResult == 'Registration successful':
            session['username'] = registerUserName
            return redirect('/dashboard')
        else:
            return render_template('login.html', error=registerResult)
    else:
        return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('dashboard.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        return render_template('login.html')


@app.route('/product')
def product():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('product.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('product.html',
                               username=username,
                               products=products,
                               productId=1)


@app.route('/product/<int:productId>')
def productPage(productId):
    db = Database()
    # 获取特定产品的信息
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('product.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products,
                               productId=productId)
    else:
        username = None
        return render_template('product.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products,
                               productId=productId)


@app.route('/shop')
def shop():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('shop.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('shop.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products)


# TODO 非用戶無法加入購物車邏輯
@app.route('/addToShoppingCart', methods=['GET', 'POST'])
def addToShoppingCart():
    if 'username' in session:
        if request.method == 'POST':
            db = Database()
            productId = request.form['productId']
            quantity = request.form['quantity']
            if productId != 0:
                username = session.get('username')
                added_to_cart = db.addToShoppingCart(username, productId, quantity)  # 调用向购物车添加商品的方法
                if added_to_cart != 0:
                    return redirect('/')  # 添加成功后重定向到首页或其他页面
                else:
                    flash('Failed to add product to cart. Please try again.', 'error')
                    return 'Failed to add product to cart.'  # 添加失败的消息
            else:
                flash('Invalid product ID or quantity.', 'error')
                return 'Product ID not provided.'  # 如果没有提供产品ID，则返回错误消息
    else:
        error = ''
        if 'error' in session:
            error = session['error']
            session.pop('error')  # 从 session 中移除错误消息，避免再次显示

        return render_template('login.html', error=error)


@app.route('/about')
def about():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('about.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('about.html', username=username, total_quantity=0, total_price=0, products=products)


@app.route('/contact')
def contact():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('contact.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('contact.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products)


@app.route('/faq')
def faq():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('faq.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('faq.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products)


@app.route('/checkout')
def checkout():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('checkout.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('checkout.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products)


@app.route('/cart')
def cart():
    db = Database()
    products = db.getAllProductsInfo()
    if 'username' in session:
        username = session['username']
        shopping_cart = db.getUserShoppingCart(username=username)
        total_quantity = sum(item[2] for item in shopping_cart)  # Calculate total quantity
        total_price = sum(item[1] * item[2] for item in shopping_cart)  # Calculate total price
        return render_template('cart.html',
                               username=username,
                               total_quantity=total_quantity,
                               total_price=total_price,
                               shopping_cart=shopping_cart,
                               products=products)
    else:
        username = None
        return render_template('cart.html',
                               username=username,
                               total_quantity=0,
                               total_price=0,
                               products=products)


@app.errorhandler(404)
def page_not_found(e):
    if 'username' in session:
        username = session['username']
        return render_template('404.html', username=username)
    else:
        return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=8787, host='0.0.0.0')
