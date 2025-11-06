"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, distribution, or use is strictly prohibited.

File: generate_sample_budgets.py
Module: Test Data Generator
Purpose: Generate realistic production budget samples
================================================================================
"""
"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: generate_sample_budgets.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Sample Budget Generator for Testing
-----------------------------------
Generates realistic film/TV production budgets for testing the analysis system.
"""
import pandas as pd
import random
import os

def generate_budget(budget_type="standard", total_target=250000):
    """Generate a realistic production budget"""
    
    if budget_type == "standard":
        # Standard indie film budget
        items = [
            # Cast
            {"Description": "Lead Actor", "Department": "Cast", "Amount": 45000, "Notes": "5-week shoot, principal talent"},
            {"Description": "Supporting Actor 1", "Department": "Cast", "Amount": 18000, "Notes": "3-week shoot"},
            {"Description": "Supporting Actor 2", "Department": "Cast", "Amount": 15000, "Notes": "3-week shoot"},
            {"Description": "Day Players", "Department": "Cast", "Amount": 12000, "Notes": "Multiple small roles"},
            {"Description": "Extras", "Department": "Cast", "Amount": 8000, "Notes": "Background performers"},
            
            # Camera
            {"Description": "Camera Package Rental", "Department": "Camera", "Amount": 15000, "Notes": "RED camera with lenses"},
            {"Description": "Camera Crew", "Department": "Camera", "Amount": 12000, "Notes": "DP, AC, 2nd AC"},
            {"Description": "Camera Expendables", "Department": "Camera", "Amount": 2000, "Notes": "Batteries, media, accessories"},
            
            # Lighting
            {"Description": "Lighting Package", "Department": "Lighting", "Amount": 10000, "Notes": "Standard grip & electric package"},
            {"Description": "Gaffer & Key Grip", "Department": "Lighting", "Amount": 8000, "Notes": "Lighting crew"},
            {"Description": "Additional Lighting", "Department": "Lighting", "Amount": 3500, "Notes": "Special lighting effects"},
            
            # Production
            {"Description": "Director Fee", "Department": "Production", "Amount": 30000, "Notes": "Flat fee"},
            {"Description": "Producer Fee", "Department": "Production", "Amount": 25000, "Notes": "Executive producer"},
            {"Description": "Production Manager", "Department": "Production", "Amount": 15000, "Notes": "5-week shoot"},
            {"Description": "1st AD", "Department": "Production", "Amount": 12000, "Notes": "Assistant director"},
            {"Description": "Script Supervisor", "Department": "Production", "Amount": 8000, "Notes": "Continuity"},
            {"Description": "Production Assistants", "Department": "Production", "Amount": 6000, "Notes": "4 PAs"},
            {"Description": "Catering", "Department": "Production", "Amount": 12000, "Notes": "25 crew, 20 days"},
            
            # Locations
            {"Description": "Location Permits", "Department": "Locations", "Amount": 5000, "Notes": "City permits for exterior locations"},
            {"Description": "Location Fees", "Department": "Locations", "Amount": 8000, "Notes": "Private property rentals"},
            {"Description": "Location Security", "Department": "Locations", "Amount": 3000, "Notes": "On-set security"},
            
            # Art Department
            {"Description": "Production Design", "Department": "Art", "Amount": 12000, "Notes": "Production designer fee"},
            {"Description": "Art Director", "Department": "Art", "Amount": 8000, "Notes": "Set design and decoration"},
            {"Description": "Set Construction", "Department": "Art", "Amount": 15000, "Notes": "Build 2 special sets"},
            {"Description": "Props", "Department": "Art", "Amount": 6000, "Notes": "Props rental and purchase"},
            {"Description": "Set Dressing", "Department": "Art", "Amount": 5000, "Notes": "Furniture and decoration"},
            
            # Wardrobe
            {"Description": "Costume Designer", "Department": "Wardrobe", "Amount": 7000, "Notes": "Costume design"},
            {"Description": "Costume Rental", "Department": "Wardrobe", "Amount": 5000, "Notes": "Period costumes for 8 characters"},
            {"Description": "Costume Purchase", "Department": "Wardrobe", "Amount": 3000, "Notes": "Custom pieces"},
            
            # Makeup & Hair
            {"Description": "Makeup Artist", "Department": "Makeup", "Amount": 6000, "Notes": "Key makeup"},
            {"Description": "Hair Stylist", "Department": "Makeup", "Amount": 5000, "Notes": "Key hair"},
            {"Description": "Makeup Supplies", "Department": "Makeup", "Amount": 2000, "Notes": "Products and supplies"},
            
            # Sound
            {"Description": "Sound Mixer", "Department": "Sound", "Amount": 10000, "Notes": "Production sound"},
            {"Description": "Boom Operator", "Department": "Sound", "Amount": 6000, "Notes": "Sound crew"},
            {"Description": "Sound Equipment", "Department": "Sound", "Amount": 4000, "Notes": "Mics and recorder rental"},
            
            # Transportation
            {"Description": "Production Vehicles", "Department": "Transportation", "Amount": 7500, "Notes": "2 passenger vans and fuel"},
            {"Description": "Equipment Truck", "Department": "Transportation", "Amount": 4000, "Notes": "Grip truck rental"},
            
            # Post-Production
            {"Description": "Editor", "Department": "Post-Production", "Amount": 18000, "Notes": "8 weeks of editing"},
            {"Description": "Editing Suite", "Department": "Post-Production", "Amount": 6000, "Notes": "Equipment rental"},
            {"Description": "Color Grading", "Department": "Post-Production", "Amount": 8000, "Notes": "Professional color"},
            {"Description": "Sound Design", "Department": "Post-Production", "Amount": 10000, "Notes": "Audio post"},
            {"Description": "Music Composer", "Department": "Post-Production", "Amount": 12000, "Notes": "Original score"},
            {"Description": "Visual Effects", "Department": "Post-Production", "Amount": 15000, "Notes": "VFX shots"},
            
            # Insurance & Contingency
            {"Description": "Production Insurance", "Department": "Insurance", "Amount": 8000, "Notes": "Comprehensive coverage"},
            {"Description": "Contingency", "Department": "Production", "Amount": 25000, "Notes": "10% contingency fund"},
        ]
    
    elif budget_type == "action":
        # Action-heavy production with stunts
        items = [
            {"Description": "Lead Action Star", "Department": "Cast", "Amount": 75000, "Notes": "A-list talent for stunts"},
            {"Description": "Supporting Cast", "Department": "Cast", "Amount": 35000, "Notes": "3 supporting roles"},
            {"Description": "Stunt Coordinator", "Department": "Stunts", "Amount": 25000, "Notes": "Professional stunt coordination"},
            {"Description": "Stunt Performers", "Department": "Stunts", "Amount": 40000, "Notes": "Multiple stunt doubles and performers"},
            {"Description": "Stunt Equipment", "Department": "Stunts", "Amount": 15000, "Notes": "Safety gear and rigging"},
            {"Description": "Practical Effects", "Department": "Stunts", "Amount": 30000, "Notes": "Explosions and fire effects"},
            {"Description": "Special Effects Supervisor", "Department": "Stunts", "Amount": 18000, "Notes": "SFX coordination"},
            {"Description": "Camera Package", "Department": "Camera", "Amount": 25000, "Notes": "High-speed cameras for action"},
            {"Description": "Crane & Dolly", "Department": "Camera", "Amount": 12000, "Notes": "Specialized camera equipment"},
            {"Description": "Director", "Department": "Production", "Amount": 40000, "Notes": "Action director"},
            {"Description": "2nd Unit Director", "Department": "Production", "Amount": 20000, "Notes": "Action unit"},
            {"Description": "Location Permits - Action", "Department": "Locations", "Amount": 15000, "Notes": "Permits for street closures and stunts"},
            {"Description": "Specialized Insurance", "Department": "Insurance", "Amount": 25000, "Notes": "Stunt and pyro coverage"},
            {"Description": "Medical Staff", "Department": "Production", "Amount": 8000, "Notes": "On-set medics for stunts"},
            {"Description": "Post-Production VFX Heavy", "Department": "Post-Production", "Amount": 45000, "Notes": "Extensive visual effects"},
            {"Description": "Sound Design - Action", "Department": "Post-Production", "Amount": 15000, "Notes": "Action sound effects"},
        ]
    
    elif budget_type == "vfx":
        # VFX-heavy sci-fi production
        items = [
            {"Description": "Cast - Principal", "Department": "Cast", "Amount": 60000, "Notes": "Lead actors"},
            {"Description": "Green Screen Studio", "Department": "Locations", "Amount": 35000, "Notes": "Studio rental with green screen"},
            {"Description": "Motion Capture Equipment", "Department": "Camera", "Amount": 40000, "Notes": "Mocap system rental"},
            {"Description": "VFX Supervisor", "Department": "Post-Production", "Amount": 35000, "Notes": "On-set VFX supervision"},
            {"Description": "CGI Character Animation", "Department": "Post-Production", "Amount": 50000, "Notes": "Digital character work"},
            {"Description": "Environment VFX", "Department": "Post-Production", "Amount": 45000, "Notes": "Digital environments"},
            {"Description": "Compositing", "Department": "Post-Production", "Amount": 30000, "Notes": "Green screen compositing"},
            {"Description": "VFX Rendering", "Department": "Post-Production", "Amount": 20000, "Notes": "Render farm time"},
            {"Description": "Special Makeup Effects", "Department": "Makeup", "Amount": 18000, "Notes": "Prosthetics and special effects makeup"},
            {"Description": "Specialized Lighting", "Department": "Lighting", "Amount": 15000, "Notes": "Lighting for VFX plates"},
        ]
    
    elif budget_type == "location_heavy":
        # Production with extensive location work
        items = [
            {"Description": "Cast", "Department": "Cast", "Amount": 50000, "Notes": "Principal cast"},
            {"Description": "International Location Permits", "Department": "Locations", "Amount": 25000, "Notes": "Foreign permits and fees"},
            {"Description": "Location Scouts", "Department": "Locations", "Amount": 10000, "Notes": "International scouting"},
            {"Description": "Travel & Accommodation", "Department": "Transportation", "Amount": 45000, "Notes": "Crew travel and hotels"},
            {"Description": "Equipment Shipping", "Department": "Transportation", "Amount": 15000, "Notes": "International shipping"},
            {"Description": "Local Crew Hires", "Department": "Production", "Amount": 30000, "Notes": "Local production crew"},
            {"Description": "Location Manager", "Department": "Locations", "Amount": 15000, "Notes": "Remote location management"},
            {"Description": "Remote Location Catering", "Department": "Production", "Amount": 18000, "Notes": "Food in remote areas"},
            {"Description": "Weather Contingency", "Department": "Production", "Amount": 20000, "Notes": "Weather delays for outdoor shoots"},
        ]
    
    # Add some random variation
    for item in items:
        variation = random.uniform(0.9, 1.1)
        item["Amount"] = int(item["Amount"] * variation)
    
    return pd.DataFrame(items)

def save_budgets(output_dir="data/input"):
    """Generate and save multiple sample budgets"""
    os.makedirs(output_dir, exist_ok=True)
    
    budgets = {
        "sample_budget_standard.xlsx": ("standard", 250000),
        "sample_budget_action.xlsx": ("action", 400000),
        "sample_budget_vfx_heavy.xlsx": ("vfx", 350000),
        "sample_budget_location.xlsx": ("location_heavy", 300000),
        "sample_budget_small.xlsx": ("standard", 150000),
        "sample_budget_large.xlsx": ("standard", 500000),
    }
    
    print("=" * 60)
    print("🎬 GENERATING SAMPLE PRODUCTION BUDGETS")
    print("=" * 60)
    print()
    
    for filename, (budget_type, target) in budgets.items():
        df = generate_budget(budget_type, target)
        total = df["Amount"].sum()
        
        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False)
        
        print(f"✅ Created: {filename}")
        print(f"   Type: {budget_type.replace('_', ' ').title()}")
        print(f"   Total: ${total:,.2f}")
        print(f"   Items: {len(df)}")
        print()
    
    print("=" * 60)
    print(f"📁 All budgets saved to: {output_dir}")
    print("=" * 60)
    print()
    print("🚀 You can now:")
    print("   1. Upload these files to the web app")
    print("   2. Test risk analysis with different scenarios")
    print("   3. Compare budgets side-by-side")
    print()

if __name__ == "__main__":
    save_budgets()

