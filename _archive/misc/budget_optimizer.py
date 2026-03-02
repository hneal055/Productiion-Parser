"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: budget_optimizer.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Production Budget Optimizer
--------------------------
Suggests optimizations for production budgets based on best practices.
"""
import os
import pandas as pd
import json
from datetime import datetime

def optimize_budget(file_path, output_dir="data/output"):
    """
    Analyze a budget file and suggest optimizations
    
    Args:
        file_path: Path to the budget Excel file
        output_dir: Output directory for reports
    """
    print(f"Analyzing budget for optimization: {file_path}")
    
    # Load the budget
    try:
        df = pd.read_excel(file_path)
        total_budget = df["Amount"].sum()
        
        print(f"Loaded budget with {len(df)} items, total: ${total_budget:,.2f}")
        
        # Find optimization opportunities
        optimizations = find_optimizations(df)
        
        # Generate report
        report_path = generate_optimization_report(df, optimizations, output_dir)
        
        print(f"Optimization report generated: {report_path}")
        return True
        
    except Exception as e:
        print(f"Error loading budget: {str(e)}")
        return False

def find_optimizations(budget_df):
    """Find potential cost optimization opportunities"""
    total_budget = budget_df["Amount"].sum()
    
    # Industry benchmarks (these would be refined with real data)
    benchmarks = {
        "departments": {
            "Cast": 0.25,  # Cast should be around 25% of total budget
            "Production": 0.30,  # Production around 30%
            "Post-Production": 0.15,  # Post around 15%
            "Art": 0.08,  # Art around 8%
            "Camera": 0.06,  # Camera around 6%
            "Wardrobe": 0.03,  # Wardrobe around 3%
            "Lighting": 0.04,  # Lighting around 4%
            "Transportation": 0.03,  # Transportation around 3%
            "Locations": 0.04  # Locations around 4%
        },
        "contingency": 0.10,  # Contingency should be around 10%
        "high_cost_threshold": 0.15  # No single item should exceed 15% of budget
    }
    
    optimizations = {
        "department_adjustments": [],
        "high_cost_items": [],
        "contingency_check": {},
        "potential_savings": 0.0
    }
    
    # 1. Check department allocations
    if "Department" in budget_df.columns:
        dept_totals = budget_df.groupby("Department")["Amount"].sum()
        dept_percentages = dept_totals / total_budget
        
        for dept, benchmark_pct in benchmarks["departments"].items():
            if dept in dept_percentages:
                actual_pct = dept_percentages[dept]
                difference = actual_pct - benchmark_pct
                
                # If more than 3% off benchmark, suggest adjustment
                if abs(difference) > 0.03:
                    direction = "reduce" if difference > 0 else "increase"
                    adjustment_amount = abs(difference) * total_budget
                    
                    optimizations["department_adjustments"].append({
                        "department": dept,
                        "current_percentage": float(actual_pct * 100),
                        "benchmark_percentage": float(benchmark_pct * 100),
                        "difference_percentage": float(difference * 100),
                        "adjustment_direction": direction,
                        "adjustment_amount": float(adjustment_amount),
                        "current_amount": float(dept_totals[dept]),
                        "suggested_amount": float(benchmark_pct * total_budget)
                    })
                    
                    if direction == "reduce":
                        optimizations["potential_savings"] += adjustment_amount
    
    # 2. Check for excessively high-cost items
    high_threshold = benchmarks["high_cost_threshold"] * total_budget
    high_cost_items = budget_df[budget_df["Amount"] > high_threshold]
    
    for _, row in high_cost_items.iterrows():
        excess = row["Amount"] - high_threshold
        optimizations["high_cost_items"].append({
            "description": row["Description"],
            "department": row.get("Department", "Unknown"),
            "current_amount": float(row["Amount"]),
            "percentage_of_budget": float(row["Amount"] / total_budget * 100),
            "suggested_max": float(high_threshold),
            "potential_savings": float(excess)
        })
        
        optimizations["potential_savings"] += excess
    
    # 3. Check contingency
    contingency_items = budget_df[budget_df["Description"].str.contains("Contingency", case=False)]
    
    if not contingency_items.empty:
        contingency_total = contingency_items["Amount"].sum()
        contingency_pct = contingency_total / total_budget
        benchmark_contingency = benchmarks["contingency"] * total_budget
        
        optimizations["contingency_check"] = {
            "current_amount": float(contingency_total),
            "current_percentage": float(contingency_pct * 100),
            "benchmark_percentage": float(benchmarks["contingency"] * 100),
            "benchmark_amount": float(benchmark_contingency),
            "status": "adequate" if abs(contingency_pct - benchmarks["contingency"]) < 0.02 else "inadequate"
        }
        
        if contingency_pct > benchmarks["contingency"] + 0.02:
            excess = contingency_total - benchmark_contingency
            optimizations["contingency_check"]["potential_savings"] = float(excess)
            optimizations["potential_savings"] += excess
        elif contingency_pct < benchmarks["contingency"] - 0.02:
            shortfall = benchmark_contingency - contingency_total
            optimizations["contingency_check"]["shortfall"] = float(shortfall)
    else:
        # No contingency found
        optimizations["contingency_check"] = {
            "current_amount": 0.0,
            "current_percentage": 0.0,
            "benchmark_percentage": float(benchmarks["contingency"] * 100),
            "benchmark_amount": float(benchmarks["contingency"] * total_budget),
            "status": "missing",
            "recommendation": "Add contingency line item"
        }
    
    return optimizations

def generate_optimization_report(budget_df, optimizations, output_dir):
    """Generate an optimization report"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_budget = budget_df["Amount"].sum()
    
    # Print summary to console
    potential_savings = optimizations["potential_savings"]
    print(f"\nOptimization Summary:")
    print(f"Total Budget: ${total_budget:,.2f}")
    print(f"Potential Savings: ${potential_savings:,.2f} ({potential_savings/total_budget*100:.1f}% of budget)")
    
    print("\nDepartment Adjustments:")
    for adj in optimizations["department_adjustments"]:
        print(f"  {adj['department']}: {adj['adjustment_direction']} by ${adj['adjustment_amount']:,.2f}")
    
    print("\nHigh Cost Items:")
    for item in optimizations["high_cost_items"]:
        print(f"  {item['description']}: ${item['current_amount']:,.2f} (suggested max: ${item['suggested_max']:,.2f})")
    
    print("\nContingency Check:")
    contingency = optimizations["contingency_check"]
    print(f"  Current: ${contingency['current_amount']:,.2f} ({contingency['current_percentage']:.1f}%)")
    print(f"  Benchmark: ${contingency['benchmark_amount']:,.2f} ({contingency['benchmark_percentage']:.1f}%)")
    print(f"  Status: {contingency['status']}")
    
    # Generate JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "budget_file": os.path.basename(file_path),
        "total_budget": float(total_budget),
        "potential_savings": float(potential_savings),
        "savings_percentage": float(potential_savings/total_budget*100),
        "optimizations": optimizations,
        "optimization_count": len(optimizations["department_adjustments"]) + len(optimizations["high_cost_items"]) + (1 if optimizations["contingency_check"]["status"] != "adequate" else 0)
    }
    
    # Save to file
    report_path = os.path.join(output_dir, f"budget_optimization_{timestamp}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Generate HTML report
    html_path = generate_html_report(budget_df, optimizations, output_dir, timestamp)
    
    return html_path

def generate_html_report(budget_df, optimizations, output_dir, timestamp):
    """Generate HTML optimization report"""
    total_budget = budget_df["Amount"].sum()
    potential_savings = optimizations["potential_savings"]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Budget Optimization Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .section {{ margin-bottom: 30px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .savings {{ color: green; font-weight: bold; }}
            .increase {{ color: blue; }}
            .reduce {{ color: red; }}
            .adequate {{ color: green; }}
            .inadequate {{ color: orange; }}
            .missing {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>Budget Optimization Report</h1>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Optimization Summary</h2>
            <p>Total Budget: <strong>${total_budget:,.2f}</strong></p>
            <p>Potential Savings: <span class="savings">${potential_savings:,.2f}</span> ({potential_savings/total_budget*100:.1f}% of budget)</p>
        </div>
    """
    
    # Department adjustments
    if optimizations["department_adjustments"]:
        html += """
        <div class="section">
            <h2>Department Adjustments</h2>
            <table>
                <tr>
                    <th>Department</th>
                    <th>Current Amount</th>
                    <th>Current %</th>
                    <th>Benchmark %</th>
                    <th>Suggested Amount</th>
                    <th>Adjustment</th>
                </tr>
        """
        
        for adj in sorted(optimizations["department_adjustments"], 
                          key=lambda x: abs(x["adjustment_amount"]),
                          reverse=True):
            direction_class = "reduce" if adj["adjustment_direction"] == "reduce" else "increase"
            adjustment_text = f"{adj['adjustment_direction']} by ${adj['adjustment_amount']:,.2f}"
            
            html += f"""
                <tr>
                    <td>{adj["department"]}</td>
                    <td>${adj["current_amount"]:,.2f}</td>
                    <td>{adj["current_percentage"]:.1f}%</td>
                    <td>{adj["benchmark_percentage"]:.1f}%</td>
                    <td>${adj["suggested_amount"]:,.2f}</td>
                    <td class="{direction_class}">{adjustment_text}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
    
    # High cost items
    if optimizations["high_cost_items"]:
        html += """
        <div class="section">
            <h2>High-Cost Items</h2>
            <p>These items exceed 15% of the total budget and could be reassessed.</p>
            <table>
                <tr>
                    <th>Description</th>
                    <th>Department</th>
                    <th>Current Amount</th>
                    <th>% of Budget</th>
                    <th>Suggested Max</th>
                    <th>Potential Savings</th>
                </tr>
        """
        
        for item in sorted(optimizations["high_cost_items"], 
                           key=lambda x: x["current_amount"],
                           reverse=True):
            html += f"""
                <tr>
                    <td>{item["description"]}</td>
                    <td>{item["department"]}</td>
                    <td>${item["current_amount"]:,.2f}</td>
                    <td>{item["percentage_of_budget"]:.1f}%</td>
                    <td>${item["suggested_max"]:,.2f}</td>
                    <td class="savings">${item["potential_savings"]:,.2f}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
    
    # Contingency check
    contingency = optimizations["contingency_check"]
    html += f"""
    <div class="section">
        <h2>Contingency Assessment</h2>
        <table>
            <tr>
                <th>Current Amount</th>
                <th>Current %</th>
                <th>Benchmark %</th>
                <th>Benchmark Amount</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>${contingency["current_amount"]:,.2f}</td>
                <td>{contingency["current_percentage"]:.1f}%</td>
                <td>{contingency["benchmark_percentage"]:.1f}%</td>
                <td>${contingency["benchmark_amount"]:,.2f}</td>
                <td class="{contingency["status"]}">{contingency["status"].title()}</td>
            </tr>
        </table>
    """
    
    if contingency["status"] == "inadequate" and "shortfall" in contingency:
        html += f"""
        <p class="increase">Recommendation: Increase contingency by ${contingency["shortfall"]:,.2f}</p>
        """
    elif contingency["status"] == "missing":
        html += f"""
        <p class="increase">Recommendation: Add contingency line item of ${contingency["benchmark_amount"]:,.2f}</p>
        """
    
    html += """
    </div>
    </body>
    </html>
    """
    
    # Save HTML report
    html_path = os.path.join(output_dir, f"budget_optimization_{timestamp}.html")
    with open(html_path, "w") as f:
        f.write(html)
    
    return html_path

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Budget Optimization Tool")
    parser.add_argument("budget_file", help="Path to the budget Excel file")
    parser.add_argument("--output", "-o", default="data/output", help="Output directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.budget_file):
        print(f"Error: File not found: {args.budget_file}")
        sys.exit(1)
    
    file_path = args.budget_file
    optimize_budget(file_path, args.output)

