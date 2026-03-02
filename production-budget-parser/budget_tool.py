"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: budget_tool.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Comprehensive Budget Analysis Tool
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

def analyze_budget(file_path, output_dir="data/output"):
    """Analyze a budget Excel file"""
    print(f"Analyzing budget file: {file_path}")
    
    # Load the budget data
    df = pd.read_excel(file_path)
    total = df["Amount"].sum()
    
    print(f"Total budget: ${total:,.2f}")
    print(f"Line items: {len(df)}")
    
    # Department breakdown
    if "Department" in df.columns:
        print("\nDepartment breakdown:")
        for dept, amount in df.groupby("Department")["Amount"].sum().items():
            percentage = amount / total * 100
            print(f"  {dept}: ${amount:,.2f} ({percentage:.1f}%)")
    
    # High-cost items
    threshold = total * 0.05  # 5% of total
    high_cost = df[df["Amount"] >= threshold]
    
    print("\nHigh-cost items (>5% of budget):")
    for _, row in high_cost.iterrows():
        percentage = row["Amount"] / total * 100
        print(f"  {row['Description']}: ${row['Amount']:,.2f} ({percentage:.1f}%)")
    
    # Perform risk analysis
    risks = identify_risks(df)
    
    # Create visualizations
    vis_paths = create_visualizations(df, output_dir)
    
    # Generate report
    report_path = generate_report(df, risks, vis_paths, output_dir)
    
    print(f"\nFull report saved to: {report_path}")
    return True

def identify_risks(budget_df):
    """Identify production-specific risks in the budget"""
    total_budget = budget_df["Amount"].sum()
    
    # Define risk categories and keywords
    risk_categories = {
        "weather_dependent": ["exterior", "outdoor", "location"],
        "talent_related": ["cast", "actor", "talent"],
        "special_equipment": ["camera", "equipment", "gear", "rental"],
        "location_risks": ["location", "permit", "travel"],
        "vfx_heavy": ["vfx", "effects", "post-production"]
    }
    
    # Initialize results
    risks = {category: [] for category in risk_categories.keys()}
    
    # Scan each budget item for risks
    for _, row in budget_df.iterrows():
        description = str(row["Description"]).lower()
        notes = str(row.get("Notes", "")).lower()
        text = description + " " + notes
        
        # Check for each risk category
        for category, keywords in risk_categories.items():
            if any(keyword in text for keyword in keywords):
                risks[category].append({
                    "description": row["Description"],
                    "amount": float(row["Amount"]),
                    "percentage": float(row["Amount"] / total_budget * 100)
                })
    
    # Print risk summary
    print("\nRisk Analysis:")
    for category, items in risks.items():
        if items:
            risk_total = sum(item["amount"] for item in items)
            percentage = risk_total / total_budget * 100
            print(f"  {category.replace('_', ' ').title()}: {len(items)} items, ${risk_total:,.2f} ({percentage:.1f}% of budget)")
    
    return risks

def create_visualizations(budget_df, output_dir="data/output"):
    """Create visualizations of the budget data"""
    os.makedirs(output_dir, exist_ok=True)
    total_budget = budget_df["Amount"].sum()
    vis_paths = {}
    
    # 1. Department pie chart
    if "Department" in budget_df.columns:
        plt.figure(figsize=(10, 6))
        dept_data = budget_df.groupby("Department")["Amount"].sum()
        plt.pie(dept_data, labels=dept_data.index, autopct="%1.1f%%")
        plt.title("Budget by Department")
        plt.axis("equal")  # Equal aspect ratio ensures pie is circular
        
        pie_path = os.path.join(output_dir, "department_breakdown.png")
        plt.savefig(pie_path)
        plt.close()
        print(f"Created department breakdown chart: {pie_path}")
        vis_paths["department_pie"] = pie_path
    
    # 2. Top budget items bar chart
    plt.figure(figsize=(12, 8))
    top_items = budget_df.nlargest(10, "Amount").sort_values("Amount")
    plt.barh(top_items["Description"], top_items["Amount"])
    
    # Add percentage labels
    for i, (_, row) in enumerate(top_items.iterrows()):
        percentage = row["Amount"] / total_budget * 100
        plt.text(row["Amount"] + total_budget * 0.01, i, f"{percentage:.1f}%")
    
    plt.xlabel("Amount ($)")
    plt.title("Top 10 Budget Items")
    plt.tight_layout()
    
    bar_path = os.path.join(output_dir, "top_items.png")
    plt.savefig(bar_path)
    plt.close()
    print(f"Created top items chart: {bar_path}")
    vis_paths["top_items_bar"] = bar_path
    
    return vis_paths

def generate_report(budget_df, risks, visualizations, output_dir="data/output"):
    """Generate a comprehensive analysis report"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_budget = budget_df["Amount"].sum()
    
    # Create report data structure
    report = {
        "timestamp": datetime.now().isoformat(),
        "budget_summary": {
            "total_budget": float(total_budget),
            "line_items": int(len(budget_df))
        },
        "departments": {},
        "risk_categories": {},
        "visualizations": visualizations
    }
    
    # Add department data
    if "Department" in budget_df.columns:
        report["budget_summary"]["departments"] = budget_df["Department"].nunique()
        for dept, data in budget_df.groupby("Department")["Amount"].agg(["sum", "count"]).iterrows():
            report["departments"][dept] = {
                "amount": float(data["sum"]),
                "percentage": float(data["sum"] / total_budget * 100),
                "item_count": int(data["count"])
            }
    
    # Add risk data
    for category, items in risks.items():
        if items:
            risk_total = sum(item["amount"] for item in items)
            report["risk_categories"][category] = {
                "items": len(items),
                "amount": float(risk_total),
                "percentage": float(risk_total / total_budget * 100),
                "details": items[:5]  # Include top 5 items for brevity
            }
    
    # Add high-cost items
    threshold = total_budget * 0.05
    high_cost_items = budget_df[budget_df["Amount"] >= threshold]
    report["high_cost_items"] = [
        {
            "description": row["Description"],
            "amount": float(row["Amount"]),
            "percentage": float(row["Amount"] / total_budget * 100)
        }
        for _, row in high_cost_items.iterrows()
    ]
    
    # Save the report
    report_path = os.path.join(output_dir, f"budget_analysis_{timestamp}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    return report_path

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        budget_file = sys.argv[1]
        if os.path.exists(budget_file):
            analyze_budget(budget_file)
        else:
            print(f"Error: File not found: {budget_file}")
            sys.exit(1)
    else:
        print("Please provide a budget file path")
        print("Usage: python budget_tool.py path/to/budget.xlsx")
        sys.exit(1)

