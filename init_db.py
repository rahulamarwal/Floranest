import os
from app import app, db
from models import User, Category, Product
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

def init_db():
    with app.app_context():
        # Clean slate: Recreate database to ensure only new categories exist
        print("Resetting database...")
        db.drop_all()
        db.create_all()
        print("Database tables created.")

        try:
            # Add Admin User
            print("Creating admin user...")
            admin = User(username='admin', email='admin@floranest.com', password_hash=generate_password_hash('admin123'), is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")

            # Add New Categories in specific order
            categories_data = [
                ('Microgreens', 'Nutrient-rich young vegetable greens.'),
                ('Exotic Vegetables', 'Rare and specialty vegetables from around the world.'),
                ('Mushrooms', 'Premium gourmet and medicinal mushrooms.'),
                ('Tools', 'Durable and professional-grade agricultural tools.')
            ]

            category_map = {}
            for name, desc in categories_data:
                print(f"Creating category: {name}")
                cat = Category(name=name, description=desc)
                db.session.add(cat)
                category_map[name] = cat
            db.session.commit()

            # Add Sample Products
            print("Adding sample products...")
            products_data = [
                ('Radish Microgreens', 'Zesty and colorful radish microgreens.', 350.0, 50, 'Microgreens'),
                ('Purple Bok Choy', 'Stunning and crunchy exotic bok choy.', 450.0, 25, 'Exotic Vegetables'),
                ('Fresh Shiitake', 'Premium quality fresh shiitake mushrooms.', 800.0, 20, 'Mushrooms'),
                ('Oyster Mushroom', 'Delicate and flavorful oyster mushrooms.', 600.0, 15, 'Mushrooms'),
                ('Precision Pruner', 'High-quality pruner for delicate plants.', 950.0, 10, 'Tools')
            ]

            for name, desc, price, stock, cat_name in products_data:
                cat = category_map.get(cat_name)
                if cat:
                    prod = Product(name=name, description=desc, price=price, stock=stock, category_id=cat.id)
                    db.session.add(prod)
            db.session.commit()

            print("Database initialization complete.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during initialization: {e}")

if __name__ == '__main__':
    init_db()

