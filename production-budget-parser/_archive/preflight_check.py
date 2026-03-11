"""
Pre-Flight Check Script
Run this before starting your Flask app to verify all files are in place
"""

import os
import sys

print("=" * 80)
print("🔍 PRE-FLIGHT CHECK - Verifying Files")
print("=" * 80)
print()

# Files that must exist
required_files = {
    'Flask App': 'web_app_COMPLETE_WITH_COMPARISON.py',
    'Risk Manager': 'risk_manager.py',
    'Charts Data': 'charts_data.py',
    'Excel Exporter': 'excel_exporter.py',
    'PDF Generator': 'pdf_report_generator.py',
    'Budget Comparison': 'budget_comparison.py',
    'Comparison Charts': 'comparison_charts.py',
}

css_files = {
    'Modern Styles': 'static/css/modern-styles.css',
    'Comparison Styles': 'static/css/comparison-styles.css',
}

js_files = {
    'Charts JS': 'static/js/charts.js',
    'Chart.js Library': 'static/js/chart.umd.js',
}

all_good = True

# Check Python files
print("📄 Checking Python Files:")
print("-" * 80)
for name, filename in required_files.items():
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"  ✅ {name:20s} {filename:40s} ({size:,} bytes)")
    else:
        print(f"  ❌ {name:20s} {filename:40s} MISSING!")
        all_good = False
print()

# Check CSS files
print("🎨 Checking CSS Files:")
print("-" * 80)
for name, filepath in css_files.items():
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✅ {name:20s} {filepath:40s} ({size:,} bytes)")
    else:
        print(f"  ❌ {name:20s} {filepath:40s} MISSING!")
        all_good = False
print()

# Check JS files
print("📜 Checking JavaScript Files:")
print("-" * 80)
for name, filepath in js_files.items():
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✅ {name:20s} {filepath:40s} ({size:,} bytes)")
    else:
        print(f"  ❌ {name:20s} {filepath:40s} MISSING!")
        all_good = False
print()

# Check folders
print("📁 Checking Folders:")
print("-" * 80)
folders = ['uploads', 'outputs', 'static', 'static/css', 'static/js']
for folder in folders:
    if os.path.exists(folder):
        print(f"  ✅ {folder}")
    else:
        print(f"  ⚠️  {folder} (will be auto-created)")
print()

# Check imports
print("🔬 Testing Imports:")
print("-" * 80)

try:
    import flask
    print(f"  ✅ Flask installed (version {flask.__version__})")
except ImportError:
    print(f"  ❌ Flask NOT installed - Run: pip install flask")
    all_good = False

try:
    import pandas
    print(f"  ✅ Pandas installed (version {pandas.__version__})")
except ImportError:
    print(f"  ❌ Pandas NOT installed - Run: pip install pandas")
    all_good = False

try:
    import openpyxl
    print(f"  ✅ openpyxl installed (version {openpyxl.__version__})")
except ImportError:
    print(f"  ❌ openpyxl NOT installed - Run: pip install openpyxl")
    all_good = False

try:
    from reportlab import Version
    print(f"  ✅ ReportLab installed (version {Version})")
except ImportError:
    print(f"  ❌ ReportLab NOT installed - Run: pip install reportlab")
    all_good = False

print()
print("=" * 80)

if all_good:
    print("✅ ALL CHECKS PASSED! You're ready to run the app!")
    print()
    print("🚀 Run this command:")
    print("   python web_app_COMPLETE_WITH_COMPARISON.py")
    print()
    print("   Then open: http://localhost:8080")
else:
    print("❌ SOME CHECKS FAILED!")
    print()
    print("📝 Missing files:")
    print("   Download from the links provided")
    print()
    print("📦 Missing packages:")
    print("   Install with: pip install flask pandas openpyxl reportlab")

print("=" * 80)