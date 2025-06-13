import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed successfully")

def install_spacy_model():
    print("Installing spaCy model...")
    try:
        import spacy
        spacy.cli.download("en_core_web_sm")
        print("✅ spaCy model installed successfully")
    except Exception as e:
        print(f"❌ Error installing spaCy model: {e}")
        print("Please run: python -m spacy download en_core_web_sm")

def create_directories():
    print("Creating necessary directories...")
    directories = ["app", "app/db", "app/models", "app/llm", "templates", "static", "static/js", "data"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully")

def create_init_files():
    print("Creating __init__.py files...")
    init_paths = ["app/__init__.py", "app/db/__init__.py", "app/models/__init__.py", "app/llm/__init__.py"]
    
    for path in init_paths:
        with open(path, "w") as f:
            f.write("# Init file\n")
    
    print("✅ Init files created successfully")

def create_env_file():
    print("Creating .env file...")
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("GROQ_API_KEY=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\n")
            f.write("DB_USER=postgres\n")
            f.write("DB_PASSWORD=admin\n")
            f.write("DB_HOST=localhost\n")
            f.write("DB_PORT=5432\n")
            f.write("DB_NAME=auto_chatbot_db\n")
        print("✅ .env file created successfully")
    else:
        print("⚠️ .env file already exists, skipping")

def create_sample_data():
    print("Creating sample product data...")
    sample_data_path = "data/sample_products.csv"
    
    if not os.path.exists(sample_data_path):
        with open(sample_data_path, "w") as f:
            f.write("title,Price,manufacturer,details,url\n")
            f.write("Car Battery,8500,Exide,12V Maintenance Free Battery,https://example.com/battery\n")
            f.write("Brake Pads,3500,Wagner,Front Brake Pads Set,https://example.com/brake-pads\n")
            f.write("Engine Oil,2800,Mobil,Synthetic 5W-30 1L,https://example.com/engine-oil\n")
            f.write("Starter Motor,12000,Bosch,Universal Fit Starter,https://example.com/starter\n")
            f.write("Radiator Coolant,950,Prestone,1L Coolant,https://example.com/coolant\n")
        print("✅ Sample data created successfully")
    else:
        print("⚠️ Sample data file already exists, skipping")

if __name__ == "__main__":
    create_directories()
    create_init_files()
    create_env_file()
    create_sample_data()
    install_dependencies()
    install_spacy_model()
    print("\n✅ Setup complete! You can now run the application with: python main.py")
