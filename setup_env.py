"""
Environment Variable Setup Script
Creates .env file for secure configuration
"""

import os
import secrets

def generate_secret_key():
    """Generate a secure secret key for Flask"""
    return secrets.token_hex(32)

def create_env_file():
    """Create .env file with secure defaults"""
    
    env_content = f"""# Budget Analysis App Configuration
# Generated: {__import__('datetime').datetime.now().isoformat()}
# IMPORTANT: Do not commit this file to git!

# Flask Configuration
FLASK_SECRET_KEY={generate_secret_key()}
FLASK_ENV=development
FLASK_DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8080

# API Keys (add your generated API keys here)
# API_KEY=your_api_key_here
# ADMIN_API_KEY=your_admin_key_here

# Database (if you add one later)
# DATABASE_URL=sqlite:///budget_analysis.db

# External APIs (if needed)
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key

# Email Configuration (for notifications)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USERNAME=your_email@gmail.com
# MAIL_PASSWORD=your_app_password

# Security
# MAX_CONTENT_LENGTH=16777216  # 16MB
# RATE_LIMIT=100  # requests per hour

# Features
ENABLE_API_AUTH=False  # Set to True to require API keys
ENABLE_RATE_LIMITING=False
ENABLE_LOGGING=True
"""
    
    filename = '.env'
    
    if os.path.exists(filename):
        print(f"⚠️  {filename} already exists!")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return
    
    with open(filename, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {filename}")
    print()
    print("=" * 80)
    print("IMPORTANT NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Add .env to your .gitignore:")
    print("   echo '.env' >> .gitignore")
    print()
    print("2. Install python-dotenv:")
    print("   pip install python-dotenv")
    print()
    print("3. Load in your Flask app:")
    print("   from dotenv import load_dotenv")
    print("   load_dotenv()")
    print()
    print("4. Generate API keys:")
    print("   python api_key_manager.py create 'Production'")
    print()
    print("5. Add generated keys to .env file")
    print()

def create_gitignore():
    """Create or update .gitignore"""
    gitignore_content = """# Environment variables
.env
.env.local
.env.*.local

# API Keys
api_keys.json
*.key
*.pem

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
outputs/
temp/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/

# Backups
*.bak
*_backup.py
*_old.py
"""
    
    filename = '.gitignore'
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing = f.read()
        
        if '.env' in existing:
            print(f"✅ {filename} already contains .env")
            return
        
        with open(filename, 'a') as f:
            f.write('\n' + gitignore_content)
        print(f"✅ Updated {filename}")
    else:
        with open(filename, 'w') as f:
            f.write(gitignore_content)
        print(f"✅ Created {filename}")

def load_env_example():
    """Show example of loading environment variables"""
    example = """
# Example: Loading environment variables in Flask app

from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Use environment variables
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

API_KEY = os.getenv('API_KEY')
PORT = int(os.getenv('PORT', 8080))

if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=PORT,
        debug=app.config['DEBUG']
    )
"""
    print(example)

# ============================================================================
# MAIN SCRIPT
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 80)
    print("🔧 ENVIRONMENT SETUP")
    print("=" * 80)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup_env.py create    - Create .env file")
        print("  python setup_env.py gitignore - Create/update .gitignore")
        print("  python setup_env.py example   - Show usage example")
        print("  python setup_env.py all       - Do everything")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        create_env_file()
    
    elif command == 'gitignore':
        create_gitignore()
    
    elif command == 'example':
        load_env_example()
    
    elif command == 'all':
        create_env_file()
        print()
        create_gitignore()
        print()
        print("✅ Environment setup complete!")
        print()
        print("Next steps:")
        print("1. Install python-dotenv: pip install python-dotenv")
        print("2. Generate API keys: python api_key_manager.py create 'Production'")
        print("3. Add keys to .env file")
        print("4. Update Flask app to load .env")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)