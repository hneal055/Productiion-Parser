"""
Initialize Fresh Database
Creates empty SQLite database with all tables
"""

from flask import Flask
from database_models import db, init_db, get_database_stats

def create_database():
    """Create fresh database with all tables"""
    print("=" * 80)
    print("CREATING FRESH DATABASE")
    print("=" * 80)
    print()
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_analysis.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print("🗄️  Initializing database...")
    init_db(app)
    
    # Verify
    with app.app_context():
        stats = get_database_stats()
        
        print()
        print("=" * 80)
        print("✅ DATABASE CREATED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("📊 Initial Statistics:")
        print(f"   Total Analyses: {stats['total_analyses']}")
        print(f"   Total Line Items: {stats['total_line_items']}")
        print(f"   Total Comparisons: {stats['total_comparisons']}")
        print()
        print("Database file: budget_analysis.db")
        print()
        print("Tables created:")
        print("  ✅ budget_analyses")
        print("  ✅ budget_line_items")
        print("  ✅ budget_comparisons")
        print("  ✅ user_activity")
        print("  ✅ app_settings")
        print()
        print("=" * 80)
        print("Ready to use!")
        print("=" * 80)

if __name__ == '__main__':
    create_database()