"""
Database Utilities
Tools for managing and maintaining the budget analysis database
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from database_models import db, BudgetAnalysis, BudgetLineItem, BudgetComparison, UserActivity, get_database_stats

def create_app():
    """Create minimal Flask app for utilities"""
    app = Flask(__name__)
    # Use instance folder path (same as Flask app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_analysis.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def backup_database(backup_dir='backups'):
    """
    Create a backup of the database
    
    Args:
        backup_dir: Directory to store backups
    """
    import shutil
    
    # Check both possible locations
    db_path = None
    if os.path.exists('instance/budget_analysis.db'):
        db_path = 'instance/budget_analysis.db'
    elif os.path.exists('budget_analysis.db'):
        db_path = 'budget_analysis.db'
    
    if not db_path:
        print("❌ Database not found!")
        print("   Checked:")
        print("   - instance/budget_analysis.db")
        print("   - budget_analysis.db")
        return False
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'budget_analysis_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_file)
        size = os.path.getsize(backup_file) / 1024 / 1024  # Size in MB
        print(f"✅ Backup created: {backup_file}")
        print(f"   Source: {db_path}")
        print(f"   Size: {size:.2f} MB")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def show_stats():
    """Display database statistics"""
    app = create_app()
    
    with app.app_context():
        stats = get_database_stats()
        
        print("\n" + "=" * 80)
        print("DATABASE STATISTICS")
        print("=" * 80)
        print()
        print(f"📊 Total Analyses: {stats['total_analyses']}")
        print(f"📋 Total Line Items: {stats['total_line_items']}")
        print(f"🔄 Total Comparisons: {stats['total_comparisons']}")
        print(f"💰 Total Budget Tracked: ${stats['total_budget_tracked']:,.2f}")
        print(f"📈 Average Budget: ${stats['avg_budget']:,.2f}")
        print()
        print("🎯 Risk Distribution:")
        for risk_level, count in stats['risk_distribution']:
            print(f"   {risk_level}: {count}")
        print()
        
        # Recent activity
        recent = BudgetAnalysis.query.order_by(
            BudgetAnalysis.upload_date.desc()
        ).limit(5).all()
        
        print("📅 Recent Analyses:")
        for analysis in recent:
            print(f"   • {analysis.filename} - ${analysis.total_budget:,.2f} ({analysis.upload_date.strftime('%Y-%m-%d')})")
        print()

def cleanup_old_data(days_old=90, dry_run=True):
    """
    Remove analyses older than specified days
    
    Args:
        days_old: Delete data older than this many days
        dry_run: If True, only show what would be deleted
    """
    app = create_app()
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        old_analyses = BudgetAnalysis.query.filter(
            BudgetAnalysis.upload_date < cutoff_date
        ).all()
        
        if not old_analyses:
            print(f"✅ No analyses older than {days_old} days found")
            return
        
        print(f"\n{'DRY RUN - ' if dry_run else ''}Found {len(old_analyses)} analyses older than {days_old} days:")
        print()
        
        total_budget = 0
        for analysis in old_analyses:
            print(f"   • {analysis.filename} - {analysis.upload_date.strftime('%Y-%m-%d')} - ${analysis.total_budget:,.2f}")
            total_budget += analysis.total_budget
        
        print()
        print(f"   Total budget in old data: ${total_budget:,.2f}")
        print()
        
        if dry_run:
            print("💡 This was a DRY RUN. No data was deleted.")
            print("   Run with --execute to actually delete this data")
        else:
            response = input("⚠️  Are you sure you want to delete this data? (yes/no): ")
            if response.lower() == 'yes':
                for analysis in old_analyses:
                    db.session.delete(analysis)
                db.session.commit()
                print(f"✅ Deleted {len(old_analyses)} old analyses")
            else:
                print("❌ Deletion cancelled")

def search_budgets(query):
    """Search for budgets by filename"""
    app = create_app()
    
    with app.app_context():
        results = BudgetAnalysis.query.filter(
            BudgetAnalysis.filename.contains(query)
        ).all()
        
        if not results:
            print(f"❌ No budgets found matching: {query}")
            return
        
        print(f"\n📁 Found {len(results)} budget(s) matching '{query}':")
        print()
        
        for analysis in results:
            print(f"   ID: {analysis.id}")
            print(f"   File: {analysis.filename}")
            print(f"   Budget: ${analysis.total_budget:,.2f}")
            print(f"   Date: {analysis.upload_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Risk: {analysis.risk_level}")
            print()

def export_to_csv(output_file='budget_export.csv'):
    """Export all analyses to CSV"""
    import pandas as pd
    
    app = create_app()
    
    with app.app_context():
        analyses = BudgetAnalysis.query.all()
        
        if not analyses:
            print("❌ No data to export")
            return
        
        # Create DataFrame
        data = []
        for analysis in analyses:
            data.append({
                'ID': analysis.id,
                'Filename': analysis.filename,
                'Upload Date': analysis.upload_date,
                'Total Budget': analysis.total_budget,
                'Line Items': analysis.line_items,
                'Departments': analysis.num_departments,
                'Risk Level': analysis.risk_level,
                'Risk Score': analysis.risk_score
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        
        print(f"✅ Exported {len(data)} analyses to {output_file}")

def vacuum_database():
    """Optimize database (reclaim space, rebuild indexes)"""
    # Find database location
    db_path = None
    if os.path.exists('instance/budget_analysis.db'):
        db_path = 'instance/budget_analysis.db'
    elif os.path.exists('budget_analysis.db'):
        db_path = 'budget_analysis.db'
    
    if not db_path:
        print("❌ Database not found!")
        return
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get size before
            size_before = os.path.getsize(db_path) / 1024 / 1024
            
            db.session.execute('VACUUM')
            db.session.commit()
            
            # Get size after
            size_after = os.path.getsize(db_path) / 1024 / 1024
            saved = size_before - size_after
            
            print(f"✅ Database optimized")
            print(f"   Location: {db_path}")
            print(f"   Size before: {size_before:.2f} MB")
            print(f"   Size after: {size_after:.2f} MB")
            print(f"   Space saved: {saved:.2f} MB")
        except Exception as e:
            print(f"❌ Optimization failed: {e}")

def list_backups(backup_dir='backups'):
    """List all available backups"""
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
    
    if not backups:
        print(f"❌ No backups found in {backup_dir}")
        return
    
    print(f"\n📦 Found {len(backups)} backup(s) in {backup_dir}:")
    print()
    
    for backup in sorted(backups, reverse=True):
        path = os.path.join(backup_dir, backup)
        size = os.path.getsize(path) / 1024 / 1024
        modified = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"   • {backup}")
        print(f"     Size: {size:.2f} MB")
        print(f"     Date: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def restore_backup(backup_file):
    """Restore database from backup"""
    import shutil
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    # Determine where to restore (check if instance folder exists)
    if os.path.exists('instance'):
        restore_path = 'instance/budget_analysis.db'
    else:
        restore_path = 'budget_analysis.db'
    
    # Backup current database first if it exists
    if os.path.exists(restore_path):
        backup_database()
    
    try:
        # Create instance folder if needed
        if 'instance' in restore_path:
            os.makedirs('instance', exist_ok=True)
        
        shutil.copy2(backup_file, restore_path)
        print(f"✅ Database restored from: {backup_file}")
        print(f"   Restored to: {restore_path}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def show_help():
    """Show usage instructions"""
    print("""
    ============================================================================
    DATABASE UTILITIES
    ============================================================================
    
    Tools for managing the budget analysis database.
    
    USAGE:
        python database_utils.py <command> [options]
    
    COMMANDS:
        stats               Show database statistics
        backup              Create database backup
        cleanup DAYS        Delete data older than DAYS (dry run)
        cleanup DAYS --execute   Actually delete old data
        search QUERY        Search budgets by filename
        export [FILE]       Export all data to CSV
        vacuum              Optimize database
        list-backups        List all backups
        restore FILE        Restore from backup
    
    EXAMPLES:
        # View statistics
        python database_utils.py stats
        
        # Create backup
        python database_utils.py backup
        
        # See what would be deleted (90+ days old)
        python database_utils.py cleanup 90
        
        # Actually delete old data
        python database_utils.py cleanup 90 --execute
        
        # Search for budgets
        python database_utils.py search "2024"
        
        # Export to CSV
        python database_utils.py export budget_data.csv
        
        # Optimize database
        python database_utils.py vacuum
        
        # List backups
        python database_utils.py list-backups
        
        # Restore backup
        python database_utils.py restore backups/budget_analysis_20240101_120000.db
    
    ============================================================================
    """)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'stats':
            show_stats()
        
        elif command == 'backup':
            backup_database()
        
        elif command == 'cleanup':
            if len(sys.argv) < 3:
                print("❌ Error: Please specify days")
                print("   Usage: python database_utils.py cleanup DAYS [--execute]")
                sys.exit(1)
            
            days = int(sys.argv[2])
            execute = '--execute' in sys.argv
            cleanup_old_data(days, dry_run=not execute)
        
        elif command == 'search':
            if len(sys.argv) < 3:
                print("❌ Error: Please specify search query")
                sys.exit(1)
            
            query = sys.argv[2]
            search_budgets(query)
        
        elif command == 'export':
            output_file = sys.argv[2] if len(sys.argv) > 2 else 'budget_export.csv'
            export_to_csv(output_file)
        
        elif command == 'vacuum':
            vacuum_database()
        
        elif command == 'list-backups':
            list_backups()
        
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("❌ Error: Please specify backup file")
                sys.exit(1)
            
            backup_file = sys.argv[2]
            restore_backup(backup_file)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("   Run with --help to see available commands")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
