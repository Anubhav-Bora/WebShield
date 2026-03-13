"""
PDF export utilities for reports and logs.
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json


def generate_security_logs_pdf(logs: list, filename: str = "security_logs.pdf") -> BytesIO:
    """
    Generate a PDF report of security logs with details.
    
    Args:
        logs: List of security log dictionaries
        filename: Output filename
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.4*inch, bottomMargin=0.4*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8
    )
    
    # Content
    elements = []
    
    # Title
    elements.append(Paragraph("Security Logs Report", title_style))
    elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", heading_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Summary
    if logs:
        event_types = {}
        for log in logs:
            event_type = log.get('event_type', 'Unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        summary_text = f"<b>Total Events:</b> {len(logs)}<br/>"
        for event_type, count in sorted(event_types.items()):
            summary_text += f"<b>{event_type.replace('_', ' ').title()}:</b> {count}<br/>"
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
    
    # Table - simplified without details column
    if logs:
        table_data = [
            ['Event Type', 'Provider', 'IP Address', 'Request ID', 'Created At']
        ]
        
        for log in logs[:150]:  # Limit to 150 rows
            table_data.append([
                log.get('event_type', 'N/A').replace('_', ' ').title(),
                log.get('provider_name', 'N/A'),
                log.get('ip_address', 'N/A'),
                log.get('request_id', 'N/A')[:12] if log.get('request_id') else 'N/A',
                log.get('created_at', 'N/A')[:16] if log.get('created_at') else 'N/A'
            ])
        
        table = Table(table_data, colWidths=[1.3*inch, 1.1*inch, 1.2*inch, 1.3*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No security logs found.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_webhook_events_pdf(events: list, filename: str = "webhook_events.pdf") -> BytesIO:
    """
    Generate a PDF report of webhook events with payloads.
    
    Args:
        events: List of webhook event dictionaries
        filename: Output filename
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.4*inch, bottomMargin=0.4*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8
    )
    
    # Content
    elements = []
    
    # Title
    elements.append(Paragraph("Webhook Events Report", title_style))
    elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", heading_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Summary
    if events:
        successful = sum(1 for e in events if e.get('response_status') == 200)
        failed = sum(1 for e in events if e.get('response_status') and e.get('response_status') != 200)
        pending = sum(1 for e in events if not e.get('response_status'))
        
        summary_text = f"<b>Total Events:</b> {len(events)}<br/><b>Successful:</b> {successful}<br/><b>Failed:</b> {failed}<br/><b>Pending:</b> {pending}"
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
    
    # Table - simplified without payload column
    if events:
        table_data = [
            ['Request ID', 'Source', 'Signature', 'Status', 'Hash', 'Received At']
        ]
        
        for event in events[:150]:  # Limit to 150 rows
            table_data.append([
                event.get('request_id', 'N/A')[:12],
                event.get('source', 'N/A'),
                '✓' if event.get('signature_valid') else '✗',
                str(event.get('response_status', 'Pending')),
                event.get('payload_hash', 'N/A')[:14] if event.get('payload_hash') else 'N/A',
                event.get('received_at', 'N/A')[:16] if event.get('received_at') else 'N/A'
            ])
        
        table = Table(table_data, colWidths=[1.2*inch, 1.1*inch, 0.7*inch, 0.9*inch, 1.4*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No webhook events found.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer



def generate_dashboard_pdf(
    providers_count: int,
    webhooks_total: int,
    webhooks_successful: int,
    webhooks_failed: int,
    success_rate: float,
    security_events: int,
    webhook_events: list,
    security_logs: list,
    traffic_sources: dict
) -> BytesIO:
    """
    Generate a comprehensive dashboard PDF report.
    
    Args:
        providers_count: Number of providers
        webhooks_total: Total webhook events
        webhooks_successful: Successful webhooks
        webhooks_failed: Failed webhooks
        success_rate: Success rate percentage
        security_events: Total security events
        webhook_events: List of webhook event dictionaries
        security_logs: List of security log dictionaries
        traffic_sources: Dictionary of traffic sources with counts
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.4*inch, bottomMargin=0.4*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    # Content
    elements = []
    
    # Title
    elements.append(Paragraph("WebShield Dashboard Report", title_style))
    elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", heading_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Providers', str(providers_count)],
        ['Total Webhooks', str(webhooks_total)],
        ['Successful Webhooks', str(webhooks_successful)],
        ['Failed Webhooks', str(webhooks_failed)],
        ['Success Rate', f'{success_rate:.1f}%'],
        ['Security Events', str(security_events)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Traffic Sources
    if traffic_sources:
        elements.append(Paragraph("Traffic Sources", heading_style))
        traffic_data = [['Source', 'Count', 'Percentage']]
        total_traffic = sum(traffic_sources.values())
        
        for source, count in sorted(traffic_sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total_traffic * 100) if total_traffic > 0 else 0
            traffic_data.append([source, str(count), f'{percentage:.1f}%'])
        
        traffic_table = Table(traffic_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        traffic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(traffic_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Recent Webhook Events
    if webhook_events:
        elements.append(Paragraph("Recent Webhook Events", heading_style))
        webhook_data = [['Request ID', 'Source', 'Status', 'Received At']]
        
        for event in webhook_events[:15]:
            status = 'Success' if event.get('response_status') == 200 else 'Failed' if event.get('response_status') else 'Pending'
            webhook_data.append([
                event.get('request_id', 'N/A')[:12],
                event.get('source', 'N/A'),
                status,
                event.get('received_at', 'N/A')[:16] if event.get('received_at') else 'N/A'
            ])
        
        webhook_table = Table(webhook_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1.3*inch])
        webhook_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(webhook_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Page break before security logs
    elements.append(PageBreak())
    
    # Security Logs
    if security_logs:
        elements.append(Paragraph("Security Events Log", heading_style))
        security_data = [['Event Type', 'Provider', 'IP Address', 'Created At']]
        
        for log in security_logs[:25]:
            security_data.append([
                log.get('event_type', 'N/A').replace('_', ' ').title(),
                log.get('provider_name', 'N/A'),
                log.get('ip_address', 'N/A'),
                log.get('created_at', 'N/A')[:16] if log.get('created_at') else 'N/A'
            ])
        
        security_table = Table(security_data, colWidths=[1.5*inch, 1.2*inch, 1.3*inch, 1.5*inch])
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(security_table)
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        "This report was automatically generated by WebShield Gateway.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=colors.grey)
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
