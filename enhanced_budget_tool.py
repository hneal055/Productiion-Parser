"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: enhanced_budget_tool.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Enhanced Budget Analysis Tool with Risk Scoring
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
    
    # Calculate risk score
    risk_score = calculate_risk_score(risks, total)
    print(f"\nOverall Risk Score: {risk_score['score']:.1f}/100 ({risk_score['level']} Risk)")
    
    # Create visualizations
    vis_paths = create_visualizations(df, output_dir)
    
    # Generate reports
    json_path = generate_json_report(df, risks, risk_score, vis_paths, output_dir)
    html_path = generate_html_report(df, risks, risk_score, vis_paths, output_dir)
    
    print(f"\nReports saved to:")
    print(f"  - JSON: {json_path}")
    print(f"  - HTML: {html_path}")
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

def calculate_risk_score(risks, total_budget):
    """Calculate an overall risk score for the production"""
    # Assign risk weights by category
    risk_weights = {
        "weather_dependent": 2.5,
        "talent_related": 2.0,
        "special_equipment": 1.5,
        "location_risks": 2.0,
        "vfx_heavy": 1.7
    }
    
    # Calculate weighted risk score
    score = 0
    for category, items in risks.items():
        if items:
            # Get the risk amount
            risk_amount = sum(item["amount"] for item in items)
            # Calculate percentage of budget at risk
            risk_pct = risk_amount / total_budget * 100
            # Apply weight
            weight = risk_weights.get(category, 1.0)
            score += risk_pct * weight
    
    # Normalize to 0-100 scale
    normalized_score = min(100, score / 5)
    
    # Determine risk level
    if normalized_score < 20:
        risk_level = "Low"
    elif normalized_score < 40:
        risk_level = "Moderate"
    elif normalized_score < 70:
        risk_level = "High"
    else:
        risk_level = "Critical"
    
    return {
        "score": normalized_score,
        "level": risk_level
    }

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
    
    # 3. Risk visualization
    try:
        # This would require the risks data, which we don't have here
        # We'll add this in the future
        pass
    except Exception as e:
        print(f"Note: Could not create risk visualization: {str(e)}")
    
    return vis_paths

def generate_json_report(budget_df, risks, risk_score, visualizations, output_dir="data/output"):
    """Generate a comprehensive JSON analysis report"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_budget = budget_df["Amount"].sum()
    
    # Create report data structure
    report = {
        "timestamp": datetime.now().isoformat(),
        "budget_summary": {
            "total_budget": float(total_budget),
            "line_items": int(len(budget_df)),
            "risk_score": float(risk_score["score"]),
            "risk_level": risk_score["level"]
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

def generate_html_report(budget_df, risks, risk_score, vis_paths, output_dir="data/output"):
    """Generate an HTML report for the budget analysis"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_budget = budget_df["Amount"].sum()
    
    # Create HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Production Budget Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #2c3e50; }}
            .section {{ margin-bottom: 30px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .chart {{ margin: 20px 0; max-width: 100%; }}
            .risk-low {{ background-color: #d4edda; }}
            .risk-moderate {{ background-color: #fff3cd; }}
            .risk-high {{ background-color: #f8d7da; }}
            .risk-critical {{ background-color: #dc3545; color: white; }}
        </style>
    </head>
    <body>
        <h1>Production Budget Analysis</h1>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Budget Summary</h2>
            <p>Total Budget: <strong>${total_budget:,.2f}</strong></p>
            <p>Number of Line Items: <strong>{len(budget_df)}</strong></p>
            <p>Risk Score: <strong>{risk_score['score']:.1f}/100</strong> (<span class="risk-{risk_score['level'].lower()}">{risk_score['level']} Risk</span>)</p>
        </div>
    """
    
    # Add department breakdown
    if "Department" in budget_df.columns:
        dept_data = budget_df.groupby("Department")["Amount"].agg(["sum", "count"])
        dept_data["percentage"] = dept_data["sum"] / total_budget * 100
        dept_data = dept_data.sort_values("sum", ascending=False)
        
        html += """
        <div class="section">
            <h2>Department Breakdown</h2>
            <table>
                <tr>
                    <th>Department</th>
                    <th>Amount</th>
                    <th>Percentage</th>
                    <th>Items</th>
                </tr>
        """
        
        for dept, data in dept_data.iterrows():
            html += f"""
                <tr>
                    <td>{dept}</td>
                    <td>${data['sum']:,.2f}</td>
                    <td>{data['percentage']:.1f}%</td>
                    <td>{data['count']}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
    
    # Add risk analysis
    html += """
    <div class="section">
        <h2>Risk Analysis</h2>
        <table>
            <tr>
                <th>Risk Category</th>
                <th>Items</th>
                <th>Amount at Risk</th>
                <th>Percentage of Budget</th>
            </tr>
    """
    
    for category, items in risks.items():
        if items:
            risk_amount = sum(item["amount"] for item in items)
            risk_pct = risk_amount / total_budget * 100
            
            html += f"""
                <tr>
                    <td>{category.replace('_', ' ').title()}</td>
                    <td>{len(items)}</td>
                    <td>${risk_amount:,.2f}</td>
                    <td>{risk_pct:.1f}%</td>
                </tr>
            """
    
    html += """
        </table>
    </div>
    """
    
    # Add high-cost items
    threshold = total_budget * 0.05
    high_cost = budget_df[budget_df["Amount"] >= threshold].sort_values("Amount", ascending=False)
    
    html += """
    <div class="section">
        <h2>High-Cost Items (>5% of budget)</h2>
        <table>
            <tr>
                <th>Description</th>
                <th>Department</th>
                <th>Amount</th>
                <th>Percentage</th>
            </tr>
    """
    
    for _, row in high_cost.iterrows():
        pct = row["Amount"] / total_budget * 100
        html += f"""
            <tr>
                <td>{row['Description']}</td>
                <td>{row.get('Department', 'N/A')}</td>
                <td>${row['Amount']:,.2f}</td>
                <td>{pct:.1f}%</td>
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
        if os.path.exists(path):
            img_name = os.path.basename(path)
            html += f"""
        <div>
            <h3>{desc.replace('_', ' ').title().replace('Pie', 'Chart').replace('Bar', 'Chart')}</h3>
            <img src="{img_name}" alt="{desc}" class="chart">
        </div>
            """
    
    html += """
    </div>
    </body>
    </html>
    """
    
    # Save the HTML report
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, f"budget_report_{timestamp}.html")
    with open(html_path, "w") as f:
        f.write(html)
    
    # Copy images to the same directory for relative linking
    import shutil
    for _, path in vis_paths.items():
        if os.path.exists(path):
            shutil.copy2(path, output_dir)
    
    return html_path

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
        print("Usage: python enhanced_budget_tool.py path/to/budget.xlsx")
        sys.exit(1)

