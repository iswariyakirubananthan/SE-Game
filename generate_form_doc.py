"""
generate_form_doc.py
Creates the official CIS046-3 Week 8 Progress Review Form as a Microsoft Word Document (.docx).
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def create_progress_form():
    doc = docx.Document()

    # Set 0.75-inch page margins to comfortably fit one page
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # 1. Title Header
    title = doc.add_paragraph()
    title_run = title.add_run("CIS046-3 Software for Enterprise – AY 23/24")
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(13)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    title.paragraph_format.space_after = Pt(4)

    # 2. Student Meta Information (2x2 Table)
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    col_widths = [Inches(3.8), Inches(3.2)]
    for row in meta_table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = col_widths[i]

    # Row 0
    p00 = meta_table.cell(0, 0).paragraphs[0]
    p00.paragraph_format.space_after = Pt(2)
    r = p00.add_run("Student Name: ")
    r.bold = True
    p00.add_run("Iswariya Kirubananthan")

    p01 = meta_table.cell(0, 1).paragraphs[0]
    p01.paragraph_format.space_after = Pt(2)
    r = p01.add_run("Student Number: ")
    r.bold = True
    p01.add_run("2541869")

    # Row 1
    p10 = meta_table.cell(1, 0).paragraphs[0]
    p10.paragraph_format.space_after = Pt(2)
    r = p10.add_run("Student Signature: ")
    r.bold = True
    sig_run = p10.add_run("K. Iswariya")
    sig_run.italic = True
    sig_run.bold = True
    sig_run.font.color.rgb = RGBColor(30, 58, 138)

    p11 = meta_table.cell(1, 1).paragraphs[0]
    p11.paragraph_format.space_after = Pt(2)
    r = p11.add_run("Date: ")
    r.bold = True
    p11.add_run("November 2023 (Week 8)")

    # 3. Form Instructions
    inst = doc.add_paragraph()
    inst.paragraph_format.space_before = Pt(6)
    inst.paragraph_format.space_after = Pt(6)
    inst_run = inst.add_run(
        "Please answer the questions below, print this form and bring it to the presentation where it will be "
        "checked against reality and signed off by the tutor. Once signed off, scan this form and submit on BREO "
        "with all other deliverables (video, code). At this stage, Week 8, (at least) a working prototype should be "
        "presented plus some ideas on how to continue with the development."
    )
    inst_run.font.name = "Calibri"
    inst_run.font.size = Pt(8.5)
    inst_run.font.italic = True
    inst_run.font.color.rgb = RGBColor(71, 85, 105)

    # 4. Form Sections
    sections_data = [
        (
            "Version Control",
            "How did you develop your code (e.g., what features have ben added after first version)?",
            "I developed the project using a GitHub repository following a structured feature-branch workflow. "
            "Starting from an initial project setup on the main branch, I developed the SQLite database authentication, "
            "the Banana API game engine, and the frontend interface on dedicated feature branches (feature/database-auth, "
            "feature/game-engine, and feature/frontend-ui), subsequently adding Google Sign-In, UI animations, and automated "
            "unit tests before merging all branches back into main."
        ),
        (
            "Event Driven Architectures",
            "What in your code triggers events (e.g., GUI, buttons, timeout …)?",
            "Events are triggered by user GUI actions including submit button clicks, difficulty selections, Google login modal "
            "triggers, and pressing the Enter key on the answer input. In addition, a JavaScript setInterval countdown timer triggers "
            "periodic visual urgency ticks and dispatches an automatic timeout penalty event when time reaches zero, using asynchronous "
            "fetch() API calls to update the score, lives, and puzzle image without reloading the page."
        ),
        (
            "Interoperability",
            "Do you use the API https://marcconrad.com/uob/tomato/api.php? If no, where in your code do you demonstrate interoperability? What protocols do you use?",
            "No, I integrated the official University of Bedfordshire Banana Game API (http://marcconrad.com/uob/banana/api.php?out=json) "
            "located in services/banana_service.py. The service communicates over the HTTP GET protocol using Python requests to "
            "retrieve and parse dynamic JSON puzzle payloads, and includes a 6-second timeout with an automated offline fallback mechanism "
            "to ensure gameplay continues seamlessly if the external server becomes unavailable."
        ),
        (
            "Virtual Identity",
            "How did you implement virtual identity in your code? (e.g., Passwords, Cookies, IP Numbers …)",
            "Virtual identity is established through user registration and stored in an SQLite database, where passwords are cryptographically "
            "salted and hashed using Werkzeug rather than plaintext. Active player sessions are secured using signed HTTP-only cookies "
            "(session['user_id']), private routes like the dashboard and game arena are guarded by a @login_required decorator, and completed "
            "game scores are permanently linked to the user's account with optional Google Sign-In authentication."
        ),
        (
            "Any other interesting features:",
            "",
            "The architecture keeps correct puzzle solutions strictly on the Python backend so players cannot inspect frontend code to cheat. "
            "The game also enforces three distinct backend difficulty levels (Easy, Medium, Hard), delivers dynamic feedback through victory "
            "confetti and wrong-answer card shakes, and is verified by a 9-suite automated unit test framework in test_app.py."
        )
    ]

    for title, question, answer in sections_data:
        # Create a single-cell boxed table for each section
        box_table = doc.add_table(rows=1, cols=1)
        box_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        box_table.autofit = False
        cell = box_table.cell(0, 0)
        cell.width = Inches(7.0)

        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

        cp = cell.paragraphs[0]
        cp.paragraph_format.space_before = Pt(0)
        cp.paragraph_format.space_after = Pt(2)

        # Section Heading
        h_run = cp.add_run(title)
        h_run.font.name = "Calibri"
        h_run.font.size = Pt(10.5)
        h_run.font.bold = True
        h_run.font.color.rgb = RGBColor(30, 41, 59)

        # Section Question (if exists)
        if question:
            qp = cell.add_paragraph()
            qp.paragraph_format.space_before = Pt(0)
            qp.paragraph_format.space_after = Pt(3)
            q_run = qp.add_run(question)
            q_run.font.name = "Calibri"
            q_run.font.size = Pt(9)
            q_run.font.italic = True
            q_run.font.color.rgb = RGBColor(71, 85, 105)

        # Section Answer
        ap = cell.add_paragraph()
        ap.paragraph_format.space_before = Pt(2)
        ap.paragraph_format.space_after = Pt(2)
        a_run = ap.add_run(answer)
        a_run.font.name = "Calibri"
        a_run.font.size = Pt(9.5)
        a_run.font.color.rgb = RGBColor(15, 23, 42)

        # Spacing between boxes
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_before = Pt(0)
        spacer.paragraph_format.space_after = Pt(2)

    output_path = "CIS046-3_Progress_Form_Filled.docx"
    doc.save(output_path)
    print(f"Document saved successfully as: {output_path}")

if __name__ == '__main__':
    create_progress_form()
