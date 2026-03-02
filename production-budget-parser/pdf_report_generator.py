"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

File: pdf_report_generator.py
Module: Professional PDF Report Generator
Version: 1.0.0
================================================================================
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


def generate_pdf_report(budget_data, risk_data, optimizations, output_path, visualizations=None):
    """
    Generate a comprehensive PDF report for budget analysis
    
    Args:
        budget_data: Dict with budget information
        risk_data: Dict with risk analysis results
        optimizations: List of optimization recommendations
        output_path: Path where PDF should be saved
        visualizations: Dict with paths to chart images
    """
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # === PAGE 1: Cover & Executive Summary ===
    
    # Title
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("PRODUCTION BUDGET", title_style))
    elements.append(Paragraph("ANALYSIS REPORT", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Copyright notice
    copyright_style = ParagraphStyle(
        'Copyright',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("PROPRIETARY AND CONFIDENTIAL", copyright_style))
    elements.append(Paragraph("Copyright © 2024-2025. All Rights Reserved.", copyright_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Report metadata
    metadata = [
        ["Report Date:", datetime.now().strftime("%B %d, %Y")],
        ["File Analyzed:", budget_data.get('filename', 'N/A')],
        ["Total Budget:", f"${budget_data.get('total_budget', 0):,.2f}"],
        ["Line Items:", str(budget_data.get('line_items', 0))],
        ["Departments:", str(budget_data.get('num_departments', 0))],
        ["Risk Level:", budget_data.get('risk_level', 'N/A').upper()]
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 3*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    # Summary findings
    total_budget = budget_data.get('total_budget', 0)
    risk_level = budget_data.get('risk_level', 'unknown')
    risk_score = risk_data.get('overall_risk_score', 0)
    
    summary_text = f"""
    This report provides a comprehensive analysis of the production budget totaling 
    <b>${total_budget:,.2f}</b>. The budget has been assessed across 
    {budget_data.get('num_departments', 0)} departments with 
    {budget_data.get('line_items', 0)} individual line items.
    <br/><br/>
    The overall risk assessment indicates a <b>{risk_level.upper()}</b> risk level 
    with a risk score of <b>{risk_score:.1f}</b>. 
    """
    
    if optimizations and len(optimizations) > 0:
        total_savings = sum(opt.get('potential_savings', 0) for opt in optimizations)
        summary_text += f"""
        Our analysis has identified <b>{len(optimizations)}</b> optimization opportunities 
        with potential savings of <b>${total_savings:,.2f}</b>.
        """
    
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Budget Overview Table
    elements.append(Paragraph("BUDGET OVERVIEW", subheading_style))
    
    overview_data = [
        ["Metric", "Value"],
        ["Total Budget", f"${total_budget:,.2f}"],
        ["Number of Line Items", str(budget_data.get('line_items', 0))],
        ["Number of Departments", str(budget_data.get('num_departments', 0))],
        ["Average Item Cost", f"${total_budget / max(budget_data.get('line_items', 1), 1):,.2f}"],
        ["Risk Level", risk_level.upper()],
        ["Risk Score", f"{risk_score:.1f}/100"]
    ]
    
    overview_table = Table(overview_data, colWidths=[3*inch, 2*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#95a5a6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(overview_table)
    
    # Page break
    elements.append(PageBreak())
    
    # === PAGE 2: Department Breakdown ===
    
    elements.append(Paragraph("DEPARTMENT BREAKDOWN", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    departments = budget_data.get('departments', {})
    
    if departments:
        # Sort departments by amount
        sorted_depts = sorted(departments.items(), key=lambda x: x[1]['amount'], reverse=True)
        
        # Create department table
        dept_data = [["Department", "Amount", "% of Total", "Line Items"]]
        
        for dept_name, dept_info in sorted_depts:
            dept_data.append([
                dept_name,
                f"${dept_info['amount']:,.2f}",
                f"{dept_info['percentage']:.1f}%",
                str(dept_info['items'])
            ])
        
        # Add total row
        dept_data.append([
            "TOTAL",
            f"${total_budget:,.2f}",
            "100.0%",
            str(budget_data.get('line_items', 0))
        ])
        
        dept_table = Table(dept_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(dept_table)
    else:
        elements.append(Paragraph("No department data available.", body_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Top spending analysis
    if departments and len(sorted_depts) > 0:
        elements.append(Paragraph("KEY FINDINGS", subheading_style))
        
        top_dept = sorted_depts[0]
        findings_text = f"""
        • <b>{top_dept[0]}</b> represents the largest budget allocation at 
        <b>${top_dept[1]['amount']:,.2f}</b> ({top_dept[1]['percentage']:.1f}% of total budget)<br/>
        """
        
        if len(sorted_depts) >= 3:
            top_3_total = sum(dept[1]['amount'] for dept in sorted_depts[:3])
            top_3_pct = (top_3_total / total_budget * 100) if total_budget > 0 else 0
            findings_text += f"""
            • The top 3 departments account for <b>${top_3_total:,.2f}</b> 
            ({top_3_pct:.1f}% of total budget)<br/>
            """
        
        elements.append(Paragraph(findings_text, body_style))
    
    # Page break
    elements.append(PageBreak())
    
    # === PAGE 3: Risk Analysis ===
    
    elements.append(Paragraph("RISK ANALYSIS", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Overall risk
    risk_color = colors.green
    if risk_level.lower() == 'high':
        risk_color = colors.red
    elif risk_level.lower() == 'medium':
        risk_color = colors.orange
    
    risk_summary = [
        ["Overall Risk Level", risk_level.upper()],
        ["Risk Score", f"{risk_score:.1f}/100"]
    ]
    
    risk_summary_table = Table(risk_summary, colWidths=[3*inch, 2*inch])
    risk_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('BACKGROUND', (1, 1), (1, 1), risk_color),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(risk_summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Risk categories
    risk_categories = risk_data.get('risk_categories', {})
    
    if risk_categories:
        elements.append(Paragraph("RISK CATEGORIES", subheading_style))
        
        risk_cat_data = [["Risk Category", "Count", "Total Amount"]]
        
        for category, items in risk_categories.items():
            if items:
                total_amount = sum(item.get('amount', 0) for item in items)
                risk_cat_data.append([
                    category.replace('_', ' ').title(),
                    str(len(items)),
                    f"${total_amount:,.2f}"
                ])
        
        if len(risk_cat_data) > 1:
            risk_cat_table = Table(risk_cat_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
            risk_cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fadbd8')]),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(risk_cat_table)
    
    # Page break
    elements.append(PageBreak())
    
    # === PAGE 4: Visualizations ===
    
    if visualizations:
        elements.append(Paragraph("VISUAL ANALYSIS", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add charts if they exist
        chart_added = False
        
        if 'pie_chart' in visualizations and os.path.exists(visualizations['pie_chart']):
            elements.append(Paragraph("Department Allocation", subheading_style))
            try:
                img = Image(visualizations['pie_chart'], width=5*inch, height=3.5*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.3*inch))
                chart_added = True
            except:
                pass
        
        if 'bar_chart' in visualizations and os.path.exists(visualizations['bar_chart']):
            elements.append(Paragraph("Top Budget Items", subheading_style))
            try:
                img = Image(visualizations['bar_chart'], width=5*inch, height=3.5*inch)
                elements.append(img)
                chart_added = True
            except:
                pass
        
        if not chart_added:
            elements.append(Paragraph("No visualizations available.", body_style))
        
        # Page break
        elements.append(PageBreak())
    
    # === PAGE 5: Recommendations ===
    
    elements.append(Paragraph("OPTIMIZATION RECOMMENDATIONS", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if optimizations and len(optimizations) > 0:
        total_savings = sum(opt.get('potential_savings', 0) for opt in optimizations)
        
        elements.append(Paragraph(
            f"Our analysis has identified <b>{len(optimizations)}</b> optimization opportunities "
            f"with potential savings of <b>${total_savings:,.2f}</b>.",
            body_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        for i, opt in enumerate(optimizations, 1):
            opt_title = f"{i}. {opt.get('category', 'Optimization').upper()}"
            elements.append(Paragraph(opt_title, subheading_style))
            
            opt_text = f"""
            <b>Recommendation:</b> {opt.get('recommendation', 'N/A')}<br/>
            <b>Potential Savings:</b> ${opt.get('potential_savings', 0):,.2f}<br/>
            <b>Priority:</b> {opt.get('priority', 'Medium').upper()}
            """
            elements.append(Paragraph(opt_text, body_style))
            elements.append(Spacer(1, 0.15*inch))
    else:
        elements.append(Paragraph(
            "No specific optimization recommendations at this time. "
            "The budget appears to be well-structured.",
            body_style
        ))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("— END OF REPORT —", footer_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    return output_path


if __name__ == "__main__":
    print("PDF Report Generator Module")
    print("Import this module to generate professional PDF reports")