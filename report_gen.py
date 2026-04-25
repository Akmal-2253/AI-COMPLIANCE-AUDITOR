from fpdf import FPDF
import re
def create_pdf_report(report_text):
    # Standard A4 Setup
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 1. Header
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, txt="Compliance Audit Report", ln=True, align='C')
    pdf.set_draw_color(200, 200, 200) # Light gray line
    pdf.line(10, 25, 200, 25) 
    pdf.ln(10)

    # 2. Text Cleaning (Essential for Latin-1 compatibility)
    clean_text = re.sub(r'[^\x00-\x7f]', r'', report_text)

    # 3. Body Text Processing
    for line in clean_text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3) # Space for empty lines
            continue

        # Check if line is a Heading (e.g., "1. PERCENTAGE ALIGNMENT:")
        if any(h in line.upper() for h in [":", "STEP", "RISK"]):
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 0, 100) # Dark Blue for headers
        else:
            pdf.set_font("Arial", '', 11)
            pdf.set_text_color(0, 0, 0) # Black for body text

        # THE FIX: Use 0 for full width and h=7 for compact, readable lines
        pdf.multi_cell(0, 7, txt=line, align='L')
        # Add a tiny gap after each block
        pdf.ln(1)

    report_path = "audit_report.pdf"
    pdf.output(report_path)
    return report_path
