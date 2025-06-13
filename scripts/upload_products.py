import pandas as pd
from sqlalchemy.orm import Session
from db.connection import SessionLocal
from models.db_models import Product

def upload_products(csv_file: str):
    df = pd.read_csv(csv_file).fillna("")
    db: Session = SessionLocal()

    for _, row in df.iterrows():
        product = Product(
            title=row['title'],
            price=str(row['Price']).replace("PKR", "").strip(),
            manufacturer=row.get('manufacturer', ''),
            details=row.get('details', ''),
            url=row.get('url', '')
        )
        db.add(product)
        print("✅ Added:", product.title)

    db.commit()
    db.close()
    print("✅ Upload complete.")

# Run it
upload_products("data/pakwheels_products.csv")