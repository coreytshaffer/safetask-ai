import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import db

def add_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 60)
    canvas.setStrokeColorRGB(1, 0, 0, alpha=0.1)
    canvas.setFillColorRGB(1, 0, 0, alpha=0.1)
    # Translate and rotate to put diagonal watermark
    canvas.translate(doc.pagesize[0]/2, doc.pagesize[1]/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL - TGRA USE ONLY")
    canvas.restoreState()

def generate_incident_pdf(incident_id, output_path):
    incident = db.get_incident(incident_id)
    if not incident:
        return False

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        spaceAfter=14,
        textColor=colors.HexColor('#0A192F')
    )
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#333333')
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        spaceAfter=12,
        leading=16
    )

    story = []

    # Header
    story.append(Paragraph("OFFICIAL CASINO SURVEILLANCE REPORT", title_style))
    story.append(Paragraph(f"<b>Incident ID:</b> {incident['id']}", meta_style))
    story.append(Paragraph(f"<b>Timestamp:</b> {incident['date']}", meta_style))
    story.append(Paragraph(f"<b>Classification:</b> {incident['category']} | <b>Severity:</b> {incident['severity']}", meta_style))
    story.append(Paragraph(f"<b>Edge Hash:</b> {incident.get('hash', 'N/A')}", meta_style))
    story.append(Spacer(1, 0.25 * inch))

    # Narrative
    story.append(Paragraph("NARRATIVE", styles['Heading2']))
    narrative_text = incident.get('formatted_narrative', '').replace('\n', '<br/>')
    story.append(Paragraph(narrative_text, body_style))
    story.append(Spacer(1, 0.25 * inch))

    # Radio Script
    if incident.get('radio_script'):
        story.append(Paragraph("DISPATCH SCRIPT", styles['Heading2']))
        story.append(Paragraph(incident['radio_script'], body_style))
        story.append(Spacer(1, 0.25 * inch))

    # Contact Slate
    if incident.get('contact_slate'):
        story.append(Paragraph("ESCALATION CONTACTS", styles['Heading2']))
        contacts = ", ".join(incident['contact_slate'])
        story.append(Paragraph(contacts, body_style))

    # Build PDF with watermark
    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    return True
