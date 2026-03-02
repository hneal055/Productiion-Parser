"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: budget_comparison_fixed.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Budget Comparison Tool (Fixed Version)
---------------------
Compare multiple production budgets side by side.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
import time
from datetime import datetime

def compare_budgets(file_paths, output_dir="data/output"):
    """
    Compare multiple budget files
    
    Args:
        file_paths: List of paths to budget Excel files
        output_dir: Directory for output reports
    """
    print(f"Comparing {len(file_paths)} budget files...")
    
    # Load all budgets
    budgets = []
    for path in file_paths:
        try:
            df = pd.read_excel(path)
            filename = os.path.basename(path)
            budget_name = os.path.splitext(filename)[0]
            
            budgets.append({
                "name": budget_name,
                "data": df,
                "total": df["Amount"].sum(),
                "path": path
            })
            print(f"Loaded budget: {budget_name} (${df['Amount'].sum():,.2f})")
        except Exception as e:
            print(f"Error loading {path}: {str(e)}")
    
    if len(budgets) < 2:
        print("Need at least 2 valid budget files for comparison")
        return False
    
    # Create comparison report
    comparison = compare_departments(budgets)
    
    # Create visualizations
    vis_paths = create_comparison_charts(budgets, comparison, output_dir)
    
    # Close all plots to release file handles
    plt.close('all')
    
    # Small delay to ensure files are released
    time.sleep(1)
    
    # Generate HTML report
    html_path = generate_html_comparison(budgets, comparison, vis_paths, output_dir)
    
    print(f"\nComparison report generated: {html_path}")
    return True

def compare_departments(budgets):
    """Compare departments across budgets"""
    # Initialize comparison data
    comparison = {
        "departments": {},
        "totals": {}
    }
    
    # Get all unique departments across all budgets
    all_departments = set()
    for budget in budgets:
        if "Department" in budget["data"].columns:
            dept_totals = budget["data"].groupby("Department")["Amount"].sum()
            for dept in dept_totals.index:
                all_departments.add(dept)
    
    # Compare department totals and percentages
    for dept in all_departments:
        comparison["departments"][dept] = {}
        
        for budget in budgets:
            if "Department" in budget["data"].columns:
                dept_data = budget["data"][budget["data"]["Department"] == dept]
                
                if not dept_data.empty:
                    dept_total = dept_data["Amount"].sum()
                    dept_pct = (dept_total / budget["total"]) * 100
                    
                    comparison["departments"][dept][budget["name"]] = {
                        "amount": float(dept_total),
                        "percentage": float(dept_pct),
                        "item_count": len(dept_data)
                    }
                else:
                    # Department doesn't exist in this budget
                    comparison["departments"][dept][budget["name"]] = {
                        "amount": 0.0,
                        "percentage": 0.0,
                        "item_count": 0
                    }
    
    # Prepare total comparisons
    for budget in budgets:
        comparison["totals"][budget["name"]] = {
            "total": float(budget["total"]),
            "items": len(budget["data"])
        }
    
    return comparison

def create_comparison_charts(budgets, comparison, output_dir):
    """Create comparison visualizations"""
    os.makedirs(output_dir, exist_ok=True)
    vis_paths = {}
    
    # Use a timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Total budget comparison
    plt.figure(figsize=(10, 6))
    budget_names = [b["name"] for b in budgets]
    budget_totals = [b["total"] for b in budgets]
    
    bars = plt.bar(budget_names, budget_totals)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 5000,
                f'${height:,.0f}',
                ha='center', va='bottom', rotation=0)
    
    plt.title("Total Budget Comparison")
    plt.ylabel("Amount ($)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    total_path = os.path.join(output_dir, f"budget_total_comparison_{timestamp}.png")
    plt.savefig(total_path)
    plt.close()  # Close the figure to release the file
    vis_paths["total_comparison"] = total_path
    
    # 2. Department comparison
    # Only include departments that exist in at least two budgets
    shared_depts = []
    for dept, budgets_data in comparison["departments"].items():
        active_budgets = sum(1 for budget_data in budgets_data.values() if budget_data["amount"] > 0)
        if active_budgets >= 2:
            shared_depts.append(dept)
    
    if shared_depts:
        # For each shared department, create a comparison
        plt.figure(figsize=(12, 8))
        
        # Set up the bar positions
        x = list(range(len(shared_depts)))
        width = 0.8 / len(budgets)
        
        # Plot bars for each budget
        for i, budget in enumerate(budgets):
            dept_values = []
            for dept in shared_depts:
                value = comparison["departments"][dept].get(budget["name"], {}).get("amount", 0)
                dept_values.append(value)
            
            offset = i * width - (len(budgets) - 1) * width / 2
            plt.bar([pos + offset for pos in x], dept_values, width, label=budget["name"])
        
        plt.xlabel("Department")
        plt.ylabel("Amount ($)")
        plt.title("Department Spending Comparison")
        plt.xticks(x, shared_depts, rotation=45, ha="right")
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        
        dept_path = os.path.join(output_dir, f"department_comparison_{timestamp}.png")
        plt.savefig(dept_path)
        plt.close()  # Close the figure to release the file
        vis_paths["department_comparison"] = dept_path
    
    # 3. Percentage comparison
    if shared_depts:
        plt.figure(figsize=(12, 8))
        
        # Create a stacked percentage bar for each budget
        budget_data = []
        for budget in budgets:
            dept_pcts = {}
            for dept, budgets_data in comparison["departments"].items():
                dept_pcts[dept] = budgets_data.get(budget["name"], {}).get("percentage", 0)
            
            # Sort by percentage, descending
            sorted_depts = sorted(dept_pcts.items(), key=lambda x: x[1], reverse=True)
            
            # Get top categories and an "Other" category
            top_depts = dict(sorted_depts[:5])
            other_pct = sum(dict(sorted_depts[5:]).values())
            if other_pct > 0:
                top_depts["Other"] = other_pct
            
            budget_data.append({
                "name": budget["name"],
                "departments": top_depts
            })
        
        # Create a figure with subplots for each budget
        fig, axs = plt.subplots(1, len(budgets), figsize=(5*len(budgets), 6))
        if len(budgets) == 1:
            axs = [axs]  # Make it iterable for the loop
        
        # Create a pie chart for each budget
        for i, (budget, ax) in enumerate(zip(budget_data, axs)):
            labels = list(budget["departments"].keys())
            sizes = list(budget["departments"].values())
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title(budget["name"])
            ax.axis('equal')
        
        plt.tight_layout()
        
        pct_path = os.path.join(output_dir, f"percentage_comparison_{timestamp}.png")
        plt.savefig(pct_path)
        plt.close()  # Close the figure to release the file
        vis_paths["percentage_comparison"] = pct_path
    
    return vis_paths

def generate_html_comparison(budgets, comparison, vis_paths, output_dir):
    """Generate HTML comparison report"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Start HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Production Budget Comparison</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .section {{ margin-bottom: 30px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .chart {{ margin: 20px 0; max-width: 100%; }}
            .budget-positive {{ color: green; }}
            .budget-negative {{ color: red; }}
            .budget-neutral {{ color: gray; }}
        </style>
    </head>
    <body>
        <h1>Production Budget Comparison</h1>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Total Budget Comparison</h2>
            <table>
                <tr>
                    <th>Budget</th>
                    <th>Total Amount</th>
                    <th>Line Items</th>
                </tr>
    """
    
    # Add totals for each budget
    lowest_total = min(budget["total"] for budget in budgets)
    highest_total = max(budget["total"] for budget in budgets)
    
    for budget in sorted(budgets, key=lambda x: x["total"], reverse=True):
        difference = ""
        if budget["total"] == highest_total and len(budgets) > 1:
            difference = '<span class="budget-negative"> (Highest)</span>'
        elif budget["total"] == lowest_total and len(budgets) > 1:
            difference = '<span class="budget-positive"> (Lowest)</span>'
        
        html += f"""
                <tr>
                    <td>{budget["name"]}</td>
                    <td>${budget["total"]:,.2f}{difference}</td>
                    <td>{len(budget["data"])}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
    """
    
    # Add department comparison
    html += """
        <div class="section">
            <h2>Department Comparison</h2>
            <table>
                <tr>
                    <th>Department</th>
    """
    
    # Add budget names as column headers
    for budget in budgets:
        html += f"""
                    <th>{budget["name"]} Amount</th>
                    <th>{budget["name"]} %</th>
        """
    
    html += """
                </tr>
    """
    
    # Add rows for each department
    for dept, budget_data in sorted(comparison["departments"].items(),
                                   key=lambda x: max(d.get("amount", 0) for d in x[1].values()),
                                   reverse=True):
        html += f"""
                <tr>
                    <td>{dept}</td>
        """
        
        for budget in budgets:
            dept_info = budget_data.get(budget["name"], {})
            amount = dept_info.get("amount", 0)
            percentage = dept_info.get("percentage", 0)
            
            html += f"""
                    <td>${amount:,.2f}</td>
                    <td>{percentage:.1f}%</td>
            """
        
        html += """
                </tr>
        """
    
    html += """
            </table>
        </div>
    """
    
    # Add visualizations
    html += """
        <div class="section">
            <h2>Visualizations</h2>
    """
    
    for desc, path in vis_paths.items():
        # Instead of copying the file, reference it directly
        img_name = os.path.basename(path)
        html += f"""
            <div>
                <h3>{desc.replace('_', ' ').title()}</h3>
                <img src="{img_name}" alt="{desc}" class="chart">
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    report_path = os.path.join(output_dir, f"budget_comparison_{timestamp}.html")
    with open(report_path, "w") as f:
        f.write(html)
    
    # Copy the images to the output directory - but only after all plots are closed
    import shutil
    try:
        for _, path in vis_paths.items():
            if os.path.exists(path):
                # Add exception handling for the copy
                try:
                    shutil.copy2(path, output_dir)
                except Exception as e:
                    print(f"Warning: Could not copy {path} to {output_dir}: {str(e)}")
    except Exception as e:
        print(f"Warning: Error copying visualization files: {str(e)}")
    
    return report_path

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare multiple production budgets")
    parser.add_argument("budgets", nargs="+", help="Paths to budget Excel files")
    parser.add_argument("--output", "-o", default="data/output", help="Output directory")
    
    args = parser.parse_args()
    
    if len(args.budgets) < 2:
        print("Please provide at least 2 budget files to compare")
        sys.exit(1)
    
    for path in args.budgets:
        if not os.path.exists(path):
            print(f"Error: File not found: {path}")
            sys.exit(1)
    
    compare_budgets(args.budgets, args.output)

