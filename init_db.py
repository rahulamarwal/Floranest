import os
from app import app, db
from models import User, Category, Product
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

def init_db():
    with app.app_context():
        # Check if tables already exist
        inspector = inspect(db.engine)
        if not inspector.has_table("user"):
            print("Creating database tables...")
            db.create_all()
        else:
            print("Tables already exist. Skipping creation.")

        # Use a nested block or individual commits to avoid autoflush issues
        try:
            # Add Admin User if it doesn't exist
            admin = db.session.query(User).filter_by(username='admin').first()
            if not admin:
                print("Creating admin user...")
                admin = User(username='admin', password_hash=generate_password_hash('admin123'), is_admin=True)
                db.session.add(admin)
                db.session.commit()

            # Add Categories if they don't exist
            categories_data = [
                ('Seeds', 'Quality organic seeds for various crops.'),
                ('Fertilizers', 'Natural and chemical fertilizers to boost yield.'),
                ('Tools', 'Durable farming and gardening tools.'),
                ('Mushrooms', 'Fresh and dried gourmet mushrooms.'),
                ('Live Plants', 'Healthy saplings and decorative plants.')
            ]

            for name, desc in categories_data:
                cat = db.session.query(Category).filter_by(name=name).first()
                if not cat:
                    print(f"Creating category: {name}")
                    cat = Category(name=name, description=desc)
                    db.session.add(cat)
            db.session.commit()

            # Add Sample Products if none exist
            if db.session.query(Product).count() == 0:
                print("Adding sample products...")
                seeds_cat = db.session.query(Category).filter_by(name='Seeds').first()
                fert_cat = db.session.query(Category).filter_by(name='Fertilizers').first()
                tools_cat = db.session.query(Category).filter_by(name='Tools').first()
                mush_cat = db.session.query(Category).filter_by(name='Mushrooms').first()
                live_cat = db.session.query(Category).filter_by(name='Live Plants').first()

                products_data = [
                    ('Organic Tomato Seeds', 'High-yield organic tomato seeds.', 150.0, 100, seeds_cat),
                    ('Natural Compost', 'Pure organic compost for soil health.', 500.0, 50, fert_cat),
                    ('Steel Garden Trowel', 'Rust-resistant steel trowel with wooden handle.', 250.0, 30, tools_cat),
                    ('Fresh Shiitake Mushrooms', 'Premium quality fresh shiitake mushrooms.', 800.0, 20, mush_cat),
                    ('Aloe Vera Sapling', 'Easy-to-grow aloe vera plant in a small pot.', 120.0, 40, live_cat)
                ]

                for name, desc, price, stock, cat in products_data:
                    if cat:
                        prod = Product(name=name, description=desc, price=price, stock=stock, category_id=cat.id)
                        db.session.add(prod)
                db.session.commit()

            print("Database initialization check complete.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during initialization: {e}")

if __name__ == '__main__':
    init_db()

