"""
Default PDF CV Template Module using ReportLab.

This module provides functions to create and structure a CV in PDF format
using the ReportLab library. It defines default styles for various elements
like titles, paragraphs, and sections, and provides functions to add these
elements to a ReportLab document.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.units import inch
from typing import List, Dict, Any, Tuple, Optional

# ReportLab SimpleDocTemplate and Flowable elements for type hinting
Flowable = Any # Base class for ReportLab flowables
RLSimpleDocTemplate = SimpleDocTemplate
RLParagraphStyle = ParagraphStyle


def get_styles() -> Dict[str, RLParagraphStyle]:
    """
    Defines and returns a dictionary of ParagraphStyle objects for the PDF.

    These styles include defaults for titles, contact information, section headers,
    normal text, and bullet points. Styles are based on ReportLab's
    `getSampleStyleSheet` with Times-Roman font as the base.

    Returns:
        Dict[str, ParagraphStyle]: A dictionary where keys are style names
                                   (e.g., 'nome', 'contato', 'secao') and
                                   values are the corresponding ParagraphStyle objects.
    """
    styles = getSampleStyleSheet()
    base_font_name = 'Times-Roman'  # Using a standard PDF font

    # Custom styles
    nome_style = ParagraphStyle(
        'Nome',
        parent=styles['Title'],
        fontSize=22,
        fontName=base_font_name,
        textColor=colors.black,
        spaceAfter=0.1 * inch,
        alignment=0  # Left aligned (TA_LEFT = 0)
    )

    contato_style = ParagraphStyle(
        'Contato',
        parent=styles['Normal'],
        fontSize=11,
        fontName=base_font_name,
        spaceAfter=0.1 * inch,
        alignment=0
    )

    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=14,
        fontName=base_font_name,
        textColor=colors.black, # Default, can be overridden with <font> tags
        spaceBefore=0.2 * inch,
        spaceAfter=0.1 * inch,
        alignment=0
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        fontName=base_font_name,
        leading=14,  # Line spacing
        alignment=0
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=normal_style, # Inherit from normal_style for consistency
        leftIndent=20,
        bulletIndent=10, # Space between bullet and text
        # firstLineIndent=0, # Not needed with bulletIndent usually
        # spaceBefore=2,
        # spaceAfter=2
    )
    
    # Store the base stylesheet as well if needed for other default styles
    # For this structure, only custom styles are returned.
    return {
        'nome': nome_style,
        'contato': contato_style,
        'secao': secao_style,
        'normal': normal_style,
        'bullet': bullet_style,
        'base_normal': styles['Normal'] # Exposing base Normal for general use like line
    }


def add_title(
    elements: List[Flowable],
    name: Optional[str],
    email: Optional[str],
    phone: Optional[str],
    linkedin: Optional[str],
    styles: Dict[str, RLParagraphStyle]
) -> None:
    """
    Adds the main title section (name, contact info, separator line) to the PDF elements list.

    Args:
        elements (List[Flowable]): The list of ReportLab Flowables to append to.
        name (Optional[str]): The full name.
        email (Optional[str]): The email address.
        phone (Optional[str]): The phone number.
        linkedin (Optional[str]): The LinkedIn profile URL/vanity name.
        styles (Dict[str, ParagraphStyle]): A dictionary of predefined styles.
    """
    if not name: name = "Nome Não Especificado" # Fallback
    elements.append(Paragraph(name, styles['nome']))

    contact_parts: List[str] = []
    if email:
        contact_parts.append(f"📧 {email}")
    if phone:
        contact_parts.append(f"📱 {phone}")
    if linkedin:
        contact_parts.append(f"🌐 {linkedin}")
    
    if contact_parts:
        contact_text = "   ".join(contact_parts) # Add space between contact items
        elements.append(Paragraph(contact_text, styles['contato']))

    # Horizontal line separator
    # Using a Paragraph with a bottom border or a graphic line could be more robust
    # For simplicity, a string of underscores is used here.
    line_style = ParagraphStyle(
        'LinhaSeparadora',
        parent=styles['base_normal'], # Use base_normal for this
        fontName='Times-Roman', # Must match for consistent underscore width
        fontSize=8, # Small font for a dense line
        textColor=colors.darkgrey, # Subtle color
        alignment=0, # Left
        spaceBefore=0.05*inch,
        spaceAfter=0.05*inch
    )
    elements.append(Paragraph("_" * 80, line_style)) # Adjust number of underscores for width
    elements.append(Spacer(1, 0.1 * inch))


def add_section_title(elements: List[Flowable], title: str, styles: Dict[str, RLParagraphStyle]) -> None:
    """
    Adds a formatted section title to the PDF elements list.

    The title uses HTML-like tags for simple inline styling (e.g., font color).

    Args:
        elements (List[Flowable]): The list of ReportLab Flowables.
        title (str): The text of the section title.
        styles (Dict[str, ParagraphStyle]): Dictionary of predefined styles.
    """
    # Hex color for the square marker, matching DEFAULT_ACCENT_COLOR from docx template if desired
    marker_color_hex = '#2F75B5' # (47, 117, 181)
    section_title_text = f"<font color='{marker_color_hex}'>■</font> {title}"
    elements.append(Paragraph(section_title_text, styles['secao']))


def add_skill_bar(
    elements: List[Flowable],
    skill_name: str,
    styles: Dict[str, RLParagraphStyle],
    level: int,
    max_level: int = 5
) -> None:
    """
    Adds a skill with a visual proficiency bar to the PDF elements list.

    The skill bar is created using a ReportLab Table with colored cells.

    Args:
        elements (List[Flowable]): The list of ReportLab Flowables.
        skill_name (str): The name of the skill.
        styles (Dict[str, ParagraphStyle]): Dictionary of predefined styles.
        level (int): The proficiency level of the skill.
        max_level (int): Maximum proficiency level. Defaults to 5.
    """
    if not isinstance(level, int) or not isinstance(max_level, int) or level < 0 or max_level <= 0:
        level = 0
        max_level = 5
    level = min(level, max_level)

    accent_color = colors.Color(47 / 255, 117 / 255, 181 / 255) # Default blue

    # Skill name and bar are in a single table to control alignment better
    # Column widths: [Skill Name | Spacer | Bar Cells]
    # Adjust colWidths as needed.
    bar_cell_width = 0.2 * inch
    skill_name_width = 2.0 * inch # Approximate width for skill name
    spacer_width = 0.1 * inch
    
    table_data: List[List[Any]] = [
        [Paragraph(f"{skill_name}:", styles['normal']), ""] # Add empty string for spacer cell
    ]
    
    # Add cells for the bar itself
    for i in range(max_level):
        table_data[0].append("") # Placeholder for a bar cell

    col_widths: List[float] = [skill_name_width, spacer_width] + [bar_cell_width] * max_level
    
    skill_table = Table(table_data, colWidths=col_widths, rowHeights=[0.2 * inch])

    table_styles: List[Tuple[Any, ...]] = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 0), # Skill name padding
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
    ]

    # Style for the bar cells (index starts from 2 due to name and spacer)
    for i in range(max_level):
        cell_pos = (i + 2, 0) # Column index for bar cells
        if i < level:
            table_styles.append(('BACKGROUND', cell_pos, cell_pos, accent_color))
            table_styles.append(('BOX', cell_pos, cell_pos, 0.5, accent_color))
        else:
            table_styles.append(('BOX', cell_pos, cell_pos, 0.5, colors.darkgrey)) # Empty box border

    skill_table.setStyle(TableStyle(table_styles))
    elements.append(skill_table)
    elements.append(Spacer(1, 0.05 * inch)) # Small spacer after each skill


def add_page_break(elements: List[Flowable]) -> None:
    """
    Adds a page break to the PDF elements list.

    Args:
        elements (List[Flowable]): The list of ReportLab Flowables.
    """
    elements.append(PageBreak())


def create_document(filename: str) -> RLSimpleDocTemplate:
    """
    Creates a new `SimpleDocTemplate` instance for the PDF.

    Sets page size to A4 and default margins.

    Args:
        filename (str): The name (including path) for the output PDF file.

    Returns:
        SimpleDocTemplate: A ReportLab `SimpleDocTemplate` object.
    """
    return SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )


if __name__ == '__main__':
    # Example usage: Create a dummy PDF file using this template's functions
    print("--- Testing template_pdf.py ---")
    
    # Use a temporary filename for testing
    output_filename = "_test_template_pdf_output.pdf"
    doc = create_document(output_filename)
    story: List[Flowable] = [] # 'story' is the conventional name for ReportLab elements list
    
    # Get styles
    current_styles = get_styles()

    # Add content
    add_title(story, "Seu Nome Completo (PDF)", "email.pdf@example.com",
              "(22) 91234-5678", "linkedin.com/in/seunomepdf", current_styles)
    
    add_section_title(story, "Resumo Profissional", current_styles)
    story.append(Paragraph("Este é um resumo profissional de exemplo em PDF...", current_styles['normal']))
    story.append(Spacer(1, 0.1 * inch))
    
    add_section_title(story, "Habilidades", current_styles)
    add_skill_bar(story, "ReportLab", current_styles, 4)
    add_skill_bar(story, "Python", current_styles, 5)
    add_skill_bar(story, "Criatividade", current_styles, 3, max_level=6)
    story.append(Spacer(1, 0.1 * inch))

    add_page_break(story)
    add_section_title(story, "Experiência", current_styles)
    story.append(Paragraph("Outra seção de exemplo após uma quebra de página.", current_styles['normal']))

    try:
        doc.build(story)
        print(f"Documento de teste PDF salvo como: {output_filename}")
        assert os.path.exists(output_filename), "Test PDF file was not created."
        print("Test PDF file created successfully.")
        # os.remove(output_filename) # Clean up
        # print(f"Test file {output_filename} removed.")
    except Exception as e:
        print(f"Erro ao salvar documento de teste PDF: {e}")
    
    print("--- template_pdf.py test finished ---")
