"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: test_comparison.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
import pandas as pd
import numpy as np
import os

# Ensure output directory exists
os.makedirs("data/output", exist_ok=True)

print("Creating variant budget file...")
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

print("\nRunning budget comparison...")
# Launch the comparison script as a subprocess
import subprocess
subprocess.run(["python", "budget_comparison_fixed.py", 
                "data/input/sample_budget.xlsx", 
                "data/input/sample_budget_variant.xlsx"])

print("\nComparison complete. Check the data/output directory for the report.")

