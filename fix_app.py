"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: fix_app.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
with open("src/app.py", "w") as f:
    f.write("""
"""
Production Budget Analysis Tool
----------------------------
Main application for the production budget analysis and risk management system.
"""
import os
import sys
import argparse
import pandas as pd
from datetime import datetime

# Import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from advanced_parser import BudgetParser
    from risk_manager import RiskManager
    import budget_visualizer
except ImportError:
    print("Warning: Some modules not found. Running in limited mode.")
    BudgetParser = None
    RiskManager = None

class ProductionBudgetApp:
    def __init__(self):
        """Initialize the Production Budget Analysis Tool"""
        self.parser = BudgetParser() if BudgetParser else None
        self.risk_manager = RiskManager() if RiskManager else None
    
    def analyze_budget(self, budget_file, output_dir="data/output"):
        """Run a full analysis on a budget file"""
        print(f"🎬 Starting analysis for: {budget_file}")
        
        # If advanced parser not available, use basic parsing
        if not self.parser:
            print("Using basic Excel parsing...")
            budget_df = pd.read_excel(budget_file)
            parse_result = {
                "status": "success",
                "data": budget_df,
                "line_items": len(budget_df),
                "total_amount": budget_df["Amount"].sum()
            }
        else:
            # 1. Parse the budget file
            print("\n🔍 Parsing budget file...")
            parse_result = self.parser.parse(budget_file)
            
        if parse_result["status"] != "success":
            print(f"❌ Error parsing budget: {parse_result.get('message', 'Unknown error')}")
            return False
        
        budget_df = parse_result["data"]
        print(f"✅ Successfully parsed {parse_result['line_items']} budget items.")
        print(f"   Total budget: ${parse_result['total_amount']:,.2f}")
        
        # 2. Analyze risks
        if self.risk_manager:
            print("\n⚠️ Analyzing production risks...")
            risk_analysis = self.risk_manager.analyze_risks(budget_df)
        else:
            # Simple risk identification
            risk_analysis = self.simple_risk_analysis(budget_df)
        
        # 3. Create visualizations
        print("\n📊 Generating visualizations...")
        if "budget_visualizer" in globals():
            vis_result = budget_visualizer.visualize_budget(budget_df, output_dir)
        else:
            vis_result = self.simple_visualize(budget_df, output_dir)
        
        # 4. Generate report
        print("\n📝 Generating comprehensive report...")
        report_path = self.generate_report(budget_df, risk_analysis, vis_result, output_dir)
        
        print(f"\n✅ Analysis complete! Full report available at: {report_path}")
        return True
    
    def simple_risk_analysis(self, budget_df):
        """Simple risk analysis when risk_manager is not available"""
        total_budget = budget_df["Amount"].sum()
        high_cost_threshold = total_budget * 0.05  # 5% of total
        
        high_cost_items = budget_df[budget_df["Amount"] >= high_cost_threshold]
        
        print(f"Identified {len(high_cost_items)} high-cost items (>5% of total budget)")
        
        return {
            "summary": {
                "overall_risk_score": len(high_cost_items) * 10,
                "risk_level": "Medium",
                "risk_categories": {
                    "high_cost": {
                        "count": len(high_cost_items),
                        "amount": float(high_cost_items["Amount"].sum()),
                        "percentage": float(high_cost_items["Amount"].sum() / total_budget * 100),
                        "description": "High cost budget items (>5% of total)"
                    }
                }
            }
        }
    
    def simple_visualize(self, budget_df, output_dir):
        """Simple visualization when budget_visualizer is not available"""
        import matplotlib.pyplot as plt
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a simple bar chart of top items
        plt.figure(figsize=(10, 6))
        top_items = budget_df.nlargest(10, "Amount")
        plt.barh(top_items["Description"], top_items["Amount"])
        plt.xlabel("Amount ($)")
        plt.title("Top 10 Budget Items")
        
        # Save the chart
        chart_path = os.path.join(output_dir, "top_items.png")
        plt.savefig(chart_path)
        plt.close()
        
        print(f"Created visualization: {chart_path}")
        return {"top_items": chart_path}
    
    def generate_report(self, budget_df, risk_analysis, visualizations, output_dir):
        """Generate a comprehensive analysis report"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create report data
        report = {
            "timestamp": datetime.now().isoformat(),
            "budget_summary": {
                "total_amount": float(budget_df["Amount"].sum()),
                "line_items": len(budget_df),
                "departments": budget_df["Department"].nunique() if "Department" in budget_df.columns else 0
            },
            "department_breakdown": {},
            "risk_analysis": risk_analysis["summary"],
            "visualizations": visualizations
        }
        
        # Add department data if available
        if "Department" in budget_df.columns:
            dept_data = budget_df.groupby("Department")["Amount"].agg(["sum", "count"])
            for dept, data in dept_data.iterrows():
                report["department_breakdown"][dept] = {
                    "amount": float(data["sum"]),
                    "percentage": float(data["sum"] / budget_df["Amount"].sum() * 100),
                    "item_count": int(data["count"])
                }
        
        # Save to JSON file
        report_path = os.path.join(output_dir, f"production_analysis_{timestamp}.json")
        import json
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report_path

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Production Budget Analysis Tool")
    parser.add_argument("budget_file", help="Path to the production budget file (Excel, CSV)")
    parser.add_argument("--output", "-o", default="data/output", help="Output directory for reports and visualizations")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.budget_file):
        print(f"Error: File not found: {args.budget_file}")
        return 1
    
    # Run the analysis
    app = ProductionBudgetApp()
    success = app.analyze_budget(args.budget_file, args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
""")
    print("Fixed app.py successfully!")

