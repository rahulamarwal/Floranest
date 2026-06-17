import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Category, Product, Order, OrderItem

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'floranest-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///floranest.db').replace("postgres://", "postgresql://")
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

db.init_app(app)
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context Processor to provide categories and cart count to all templates
@app.context_processor
def inject_globals():
    categories = Category.query.all()
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return dict(categories=categories, cart_count=cart_count)

# --- USER ROUTES ---

@app.route('/')
def index():
    products = Product.query.order_by(Product.id.desc()).limit(8).all()
    return render_template('user/index.html', products=products)

@app.route('/category/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('user/category.html', category=category, products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('user/product_detail.html', product=product)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username, 
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('user/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('user/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash('Product added to cart!')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
    return render_template('user/cart.html', cart_items=cart_items, total=total)

# --- ADMIN ROUTES ---

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html', products=products, orders=orders)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category_id = int(request.form.get('category_id'))
        
        file = request.files.get('image')
        image_url = ''
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = filename
            
        new_product = Product(name=name, description=description, price=price, 
                              stock=stock, category_id=category_id, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        print(f"DEBUG: Created new product {new_product.id}: {name}")
        flash('Product added successfully!')
        return redirect(url_for('admin_dashboard'))
    
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category_id = int(request.form.get('category_id'))
        
        file = request.files.get('image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image_url = filename
            
        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('admin_dashboard'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin/product/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    print("Floranest is starting on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
