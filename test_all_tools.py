"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: test_all_tools.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Test Script for All Budget Tools
-------------------------------
Tests all the updated budget tools with the sample budget.
"""
import os
import time
import subprocess
import sys

def print_section(title):
    """Print a section title"""
    print("\n" + "=" * 70)
    print(f" {title} ".center(70, "="))
    print("=" * 70 + "\n")

def run_command(command, description):
    """Run a command and print its output"""
    print_section(description)
    print(f"Running: {' '.join(command)}\n")
    
    try:
        process = subprocess.run(command, check=True)
        print(f"\nCommand completed with exit code {process.returncode}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\nError running command: {str(e)}")
        return False

def ensure_sample_budget_exists():
    """Make sure we have a sample budget file to work with"""
    sample_path = "data/input/sample_budget.xlsx"
    if not os.path.exists(sample_path):
        print("Sample budget file not found! Please make sure it exists at:", sample_path)
        sys.exit(1)
    return sample_path

def create_variant_budget():
    """Create a variant budget file for comparison testing"""
    import pandas as pd
    import numpy as np
    
    # Load the original budget
    df = pd.read_excel('data/input/sample_budget.xlsx')

    # Make some modifications to create a different budget
    df2 = df.copy()
    # Add some random variation to amounts (±20%)
    np.random.seed(42)  # For reproducible results
    df2['Amount'] = df2['Amount'].apply(lambda x: x * np.random.uniform(0.8, 1.2))
    # Change a few departments
    df2.loc[df2['Description'] == 'Visual Effects', 'Amount'] *= 1.5  # Increase VFX budget
    df2.loc[df2['Description'] == 'Cast - Lead Actor', 'Amount'] *= 0.8  # Reduce lead actor cost

    # Save as a new budget
    variant_path = 'data/input/sample_budget_variant.xlsx'
    df2.to_excel(variant_path, index=False)
    print(f"Created variant budget file: {variant_path}")
    return variant_path

def main():
    """Main test function"""
    print_section("PRODUCTION BUDGET ANALYSIS TOOLS TEST")
    print("This script will test all the fixed budget analysis tools.")
    
    # Ensure output directory exists
    os.makedirs("data/output", exist_ok=True)
    
    # Make sure we have a sample budget
    sample_budget = ensure_sample_budget_exists()
    
    # Test enhanced budget tool
    run_command(
        ["python", "enhanced_budget_tool_fixed.py", sample_budget],
        "TESTING ENHANCED BUDGET ANALYSIS TOOL"
    )
    
    # Create variant budget and test comparison tool
    variant_budget = create_variant_budget()
    run_command(
        ["python", "budget_comparison_fixed.py", sample_budget, variant_budget],
        "TESTING BUDGET COMPARISON TOOL"
    )
    
    # Test budget optimizer
    run_command(
        ["python", "budget_optimizer_fixed.py", sample_budget],
        "TESTING BUDGET OPTIMIZER TOOL"
    )
    
    print_section("ALL TESTS COMPLETED")
    print("Check the data/output directory for generated reports.\n")
    print("To run the integrated menu system, use:")
    print("python production_budget_tools.py")

if __name__ == "__main__":
    main()

