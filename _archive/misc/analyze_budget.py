"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: analyze_budget.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
import os
import pandas as pd
import json

def analyze_budget(file_path):
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
    
    return True

# Main execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            analyze_budget(file_path)
        else:
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
    else:
        print("Please provide a budget file path")
        print("Usage: python analyze_budget.py path/to/budget.xlsx")
        sys.exit(1)

