#report_gen.py
from fpdf import FPDF
import re

def create_pdf_report(report_text):
    # A4 size (210mm x 297mm)
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Header
    pdf.set_font("Arial", 'B', 16)
    # Width fix: 0 means full width until right margin
    pdf.cell(0, 10, txt="Compliance Audit Report", ln=1, align='C') # type: ignore
    pdf.ln(10)
    
    # 2. Body Text
    pdf.set_font("Arial", size=11)
    
    # Text Cleaning: Sirf readable English characters rakhein taake crash na ho
    # Ye step emojis aur symbols ko hata dega jo PDF ko break karte hain
    clean_text = re.sub(r'[^\x00-\x7f]', r'', report_text)
    
    for line in clean_text.split('\n'):
        if not line.strip():
            pdf.ln(4)
        else:
            # multi_cell(width, height, text)
            # Width = 0 is safe, but let's try a fixed width 180 to be sure
            pdf.multi_cell(180, 8, txt=line, align='L') # type: ignore
            
    report_path = "audit_report.pdf"
    pdf.output(report_path)
    return report_path
