import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.connection import SessionLocal
from app.models.db_models import Product, create_tables

def upload_products(csv_file: str):
    print(f"Loading products from {csv_file}")
    try:
        df = pd.read_csv(csv_file).fillna("")
        print(f"Found {len(df)} products in CSV")
        
        # Print column names to debug
        print(f"CSV columns: {df.columns.tolist()}")
        
        db = SessionLocal()
        try:
            # Clear existing products
            db.query(Product).delete()
            db.commit()
            print("Cleared existing products")
            
            # Add new products
            for _, row in df.iterrows():
                product = Product(
                    title=row['title'],
                    price=str(row['Price']).replace("PKR", "").strip(),
                    manufacturer=row.get('manufacturer', ''),
                    details=row.get('details', ''),
                    url=row.get('url', '')
                )
                db.add(product)
                print(f"Added: {product.title}")
            
            db.commit()
            print(f"✅ Added {len(df)} products to database")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"❌ Database error: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return False

if __name__ == "__main__":
    # Create tables if they don't exist
    create_tables()
    
    # Upload products from sample data
    upload_products("data/sample_products.csv")
