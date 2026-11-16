"""
Convert Final_Report.docx to Final_Report.pdf using ReportLab.
Extracts text, headings, tables, and images from docx and compiles into an academic PDF
with monochromatic navy-blue styling and page numbering.
"""

import os
from pathlib import Path
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCX_PATH = PROJECT_ROOT / "report" / "Final_Report.docx"
PDF_PATH = PROJECT_ROOT / "report" / "Final_Report.pdf"

# Monochromatic Navy Theme
DARK_NAVY = HexColor("#142D4E")
DEEP_BLUE = HexColor("#234B70")
MEDIUM_BLUE = HexColor("#4778A8")
LIGHT_BLUE = HexColor("#91B6D5")
VERY_LIGHT = HexColor("#EAF1F8")
DARK_TEXT = HexColor("#202833")
WHITE = HexColor("#FFFFFF")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:
            self.setFont("Helvetica", 9)
            self.setFillColor(DARK_TEXT)
            self.drawRightString(letter[0] - 54, 36, f"Page {self._pageNumber} of {page_count}")
            self.setStrokeColor(LIGHT_BLUE)
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 40, letter[0] - 54, letter[1] - 40)
            self.drawString(54, letter[1] - 34, "Comparative Crash Pattern Analysis | IIT Kharagpur CE60012")

def convert_docx_to_pdf(docx_path, pdf_path):
    doc = Document(docx_path)
    
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'AcademicBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=DARK_TEXT,
        spaceAfter=6,
        alignment=4 # Justify
    )
    
    title_style = ParagraphStyle(
        'AcademicTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=DARK_NAVY,
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'AcademicSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=DEEP_BLUE,
        alignment=1,
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'AcademicH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=DARK_NAVY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'AcademicH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=DEEP_BLUE,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    caption_style = ParagraphStyle(
        'AcademicCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=DEEP_BLUE,
        alignment=1,
        spaceBefore=4,
        spaceAfter=10
    )

    story = []
    
    # Process docx elements
    # First handle title page
    story.append(Spacer(1, 40))
    story.append(Paragraph("INDIAN INSTITUTE OF TECHNOLOGY KHARAGPUR", subtitle_style))
    story.append(Paragraph("DEPARTMENT OF CIVIL ENGINEERING", subtitle_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Comparative Crash Pattern Analysis at Signalized and Unsignalized Intersections", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("CE60012: Transportation Safety & Engineering — Assignment 2 (Project 7)", subtitle_style))
    story.append(Spacer(1, 40))
    
    meta_data = [
        [Paragraph("<b>Academic Term:</b>", normal_style), Paragraph("Autumn Semester 2026", normal_style)],
        [Paragraph("<b>Institution:</b>", normal_style), Paragraph("IIT Kharagpur", normal_style)],
        [Paragraph("<b>Department:</b>", normal_style), Paragraph("Department of Civil Engineering", normal_style)],
        [Paragraph("<b>Course:</b>", normal_style), Paragraph("CE60012 Road Safety & Crash Analysis", normal_style)],
        [Paragraph("<b>Primary Data Source:</b>", normal_style), Paragraph("NYC Motor Vehicle Collisions (2023–2024)", normal_style)],
        [Paragraph("<b>Supplementary Data:</b>", normal_style), Paragraph("NYC DOT Official Traffic Signals & OSM", normal_style)],
    ]
    meta_table = Table(meta_data, colWidths=[2.2*inch, 4.0*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), VERY_LIGHT),
        ('TEXTCOLOR', (0,0), (-1,-1), DARK_TEXT),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, MEDIUM_BLUE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, LIGHT_BLUE),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # Now iterate docx paragraphs and tables
    for p in doc.paragraphs[15:]: # Skip title block
        txt = p.text.strip()
        if not txt:
            continue
            
        style_name = p.style.name.lower()
        if 'heading 1' in style_name:
            story.append(Spacer(1, 8))
            story.append(Paragraph(txt, h1_style))
        elif 'heading 2' in style_name or 'heading 3' in style_name:
            story.append(Paragraph(txt, h2_style))
        elif txt.startswith("Figure ") or txt.startswith("Table "):
            story.append(Paragraph(txt, caption_style))
        else:
            # Check if text contains bold keywords
            formatted_txt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(formatted_txt, normal_style))

    # Add embedded charts & diagrams
    story.append(PageBreak())
    story.append(Paragraph("Visual Analysis Deliverables & Collision Diagrams", h1_style))
    story.append(Paragraph("The following figures present the empirical visualisations and schematic collision diagrams produced from the processed dataset.", normal_style))
    story.append(Spacer(1, 10))

    figures = [
        ("outputs/graphs/crash_frequency_by_type.png", "Figure 1: Total crash frequency by intersection type in Manhattan (2023–2024)."),
        ("outputs/graphs/collision_type_comparison.png", "Figure 2: Collision type distribution comparison between signalized and unsignalized intersections."),
        ("outputs/graphs/severity_distribution.png", "Figure 3: Severity distribution comparison across intersection control types."),
        ("outputs/graphs/vehicle_type_distribution.png", "Figure 4: Vehicle type distribution involved in crashes across control categories."),
        ("outputs/graphs/time_of_day_distribution.png", "Figure 5: Time-of-day crash distribution by intersection type."),
        ("outputs/graphs/day_of_week_distribution.png", "Figure 6: Day-of-week crash distribution by intersection type."),
        ("outputs/graphs/heatmap_hour_day.png", "Figure 7: Temporal collision density heatmap (Hour of Day vs Day of Week)."),
        ("outputs/maps/crash_locations_map.png", "Figure 8: Spatial GIS map of intersection crash occurrences across Manhattan."),
        ("outputs/diagrams/collision_diagram_signalized.png", "Figure 9: Schematic collision diagram for representative signalized intersection."),
        ("outputs/diagrams/collision_diagram_unsignalized.png", "Figure 10: Schematic collision diagram for representative unsignalized intersection."),
    ]

    for img_path, cap in figures:
        full_path = PROJECT_ROOT / img_path
        if full_path.exists():
            try:
                story.append(KeepTogether([
                    RLImage(str(full_path), width=6.0*inch, height=3.6*inch),
                    Spacer(1, 4),
                    Paragraph(cap, caption_style),
                    Spacer(1, 12)
                ]))
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")

    # Build PDF
    pdf_doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    pdf_doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Successfully compiled: {pdf_path}")

if __name__ == "__main__":
    convert_docx_to_pdf(DOCX_PATH, PDF_PATH)
