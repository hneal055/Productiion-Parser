"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: python create_sample.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
# Sample budget file creator
import pandas as pd
import os

# Ensure the directory exists
os.makedirs("data/input", exist_ok=True)

# Create sample budget data
data = {
    "Description": [
        "Camera Equipment Rental",
        "Lighting Package",
        "Cast - Lead Actor",
        "Cast - Supporting Roles",
        "Director Fee",
        "Location Permits",
        "Catering",
        "Transportation",
        "Costumes",
        "Production Design",
        "Post-Production Sound",
        "Visual Effects",
        "Insurance",
        "Contingency"
    ],
    "Department": [
        "Camera",
        "Lighting",
        "Cast",
        "Cast",
        "Production",
        "Locations",
        "Production",
        "Transportation",
        "Wardrobe",
        "Art",
        "Post-Production",
        "Post-Production",
        "Production",
        "Production"
    ],
    "Amount": [
        15000,
        8500,
        45000,
        25000,
        30000,
        5000,
        12000,
        7500,
        9000,
        18000,
        12000,
        22000,
        8500,
        20000
    ],
    "Notes": [
        "Includes specialized underwater housing",
        "Standard package plus effects",
        "5-week shoot",
        "3 supporting roles",
        "Flat fee",
        "City permits for exterior locations",
        "25 crew members for 20 days",
        "Includes 2 passenger vans and fuel",
        "Period costumes for 8 characters",
        "Includes special set builds",
        "Mix, edit, ADR",
        "20 VFX shots",
        "General liability and E&O",
        "10% of total budget"
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save as Excel file
output_path = "data/input/sample_budget.xlsx"
df.to_excel(output_path, index=False)

print(f"Sample budget file created at: {output_path}")
