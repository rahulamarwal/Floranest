import os
from app import app, db
from models import User, Category, Product
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Use try-except to handle cases where tables already exist
        try:
            db.create_all()
            
            # Add Admin User
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', password_hash=generate_password_hash('admin123'), is_admin=True)
                db.session.add(admin)
                
            # Add Categories
            categories_data = [
                ('Seeds', 'Quality organic seeds for various crops.'),
                ('Fertilizers', 'Natural and chemical fertilizers to boost yield.'),
                ('Tools', 'Durable farming and gardening tools.'),
                ('Mushrooms', 'Fresh and dried gourmet mushrooms.'),
                ('Live Plants', 'Healthy saplings and decorative plants.')
            ]
            category_objects = {}
            for name, desc in categories_data:
                cat = Category.query.filter_by(name=name).first()
                if not cat:
                    cat = Category(name=name, description=desc)
                    db.session.add(cat)
                category_objects[name] = cat
            db.session.commit()

            # Add Sample Products
            products_data = [
                ('Organic Red Mustard Microgreen', 'High-yield organic tomato seeds.', 150.0, 100, 'Seeds'),
                ('Organic Moong Dal Microgreen', 'Pure organic compost for soil health.', 500.0, 50, 'Fertilizers'),
                ('Organic Sunflower Microgreen', 'Rust-resistant steel trowel with wooden handle.', 250.0, 30, 'Tools'),
                ('Fresh Shiitake Mushrooms', 'Premium quality fresh shiitake mushrooms.', 800.0, 20, 'Mushrooms'),
                ('Aloe Vera Sapling', 'Easy-to-grow aloe vera plant in a small pot.', 120.0, 40, 'Live Plants')
            ]
            for name, desc, price, stock, cat_name in products_data:
                if not Product.query.filter_by(name=name).first():
                    prod = Product(name=name, description=desc, price=price, stock=stock, 
                                   category_id=category_objects[cat_name].id)
                    db.session.add(prod)
            
            db.session.commit()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Database already initialized or error occurred: {e}")

if __name__ == '__main__':
    init_db()
