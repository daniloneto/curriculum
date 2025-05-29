"""
Modern PDF CV Template Module using ReportLab.

This module provides functions and styles for creating a CV with a modern
aesthetic in PDF format. It utilizes ReportLab for document generation and
defines specific color schemes, font choices, and layout elements to achieve
a contemporary look and feel.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.units import inch
from typing import List, Dict, Any, Optional

# Type aliases for ReportLab objects
Flowable = Any
RLSimpleDocTemplate = SimpleDocTemplate
RLParagraphStyle = ParagraphStyle

# Modern color palette
COLOR_PRIMARY_DARK = colors.Color(0.1, 0.2, 0.4)  # Dark Blue/Navy
COLOR_ACCENT_LIGHT = colors.Color(0.6, 0.8, 0.9)  # Light Blue/Teal
COLOR_BACKGROUND_GREY = colors.Color(0.9, 0.9, 0.9) # Light Grey for backgrounds
COLOR_TEXT_NORMAL = colors.darkslategray
COLOR_TEXT_SUBTLE = colors.dimgray

# Standard font names for a modern look (ensure they are available or use defaults)
FONT_HELVETICA = 'Helvetica'
FONT_HELVETICA_BOLD = 'Helvetica-Bold'


def get_styles() -> Dict[str, RLParagraphStyle]:
    """
    Defines and returns a dictionary of ParagraphStyle objects for the modern PDF template.

    These styles use Helvetica as the base font and incorporate the modern
    color palette for titles, headers, and text.

    Returns:
        Dict[str, ParagraphStyle]: A dictionary of style names to ParagraphStyle objects.
    """
    styles = getSampleStyleSheet()

    nome_style = ParagraphStyle(
        'NomeModerno',
        parent=styles['Title'],
        fontSize=26,
        fontName=FONT_HELVETICA_BOLD,
        textColor=COLOR_PRIMARY_DARK,
        spaceAfter=0.1 * inch,
        alignment=0  # Left aligned
    )

    contato_style = ParagraphStyle(
        'ContatoModerno',
        parent=styles['Normal'],
        fontSize=10,
        fontName=FONT_HELVETICA,
        textColor=COLOR_TEXT_SUBTLE, # Subtle color for contact details
        spaceAfter=0.05 * inch,
        alignment=0
    )

    secao_style = ParagraphStyle(
        'SecaoModerno',
        parent=styles['Heading2'],
        fontSize=14,
        fontName=FONT_HELVETICA_BOLD,
        textColor=COLOR_PRIMARY_DARK,
        spaceBefore=0.2 * inch,
        spaceAfter=0.1 * inch,
        # Modern templates might use bottom borders or background colors for sections
        # For this example, keeping it relatively simple, but could add:
        # borderColor=COLOR_ACCENT_LIGHT,
        # borderWidth=1,
        # borderPadding=(5, 2, 5, 2), # Left, top, right, bottom
        # backColor=COLOR_BACKGROUND_GREY, # Light background for section title
        alignment=0
    )

    normal_style = ParagraphStyle(
        'NormalModerno',
        parent=styles['Normal'],
        fontSize=11,
        fontName=FONT_HELVETICA,
        textColor=COLOR_TEXT_NORMAL,
        leading=15, # Slightly more leading for modern look
        alignment=0
    )

    bullet_style = ParagraphStyle(
        'BulletModerno',
        parent=normal_style,
        leftIndent=0.25 * inch,
        bulletIndent=0.1 * inch,
        firstLineIndent=0,
        spaceBefore=2,
        spaceAfter=2
    )

    return {
        'nome': nome_style,
        'contato': contato_style,
        'secao': secao_style,
        'normal': normal_style,
        'bullet': bullet_style,
        'base_normal': styles['Normal']
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
    Adds a modern-styled title section to the PDF elements list.

    Includes a colored header bar, name, and contact information.

    Args:
        elements (List[Flowable]): The list of ReportLab Flowables.
        name (Optional[str]): The full name.
        email (Optional[str]): Email address.
        phone (Optional[str]): Phone number.
        linkedin (Optional[str]): LinkedIn profile URL/vanity name.
        styles (Dict[str, ParagraphStyle]): Predefined styles.
    """
    if not name: name = "Nome Não Especificado"

    # Optional: Colored header bar for visual appeal
    header_bar_data = [['']] # Empty cell to apply background color
    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ACCENT_LIGHT),
        # Remove grid lines for a cleaner look
        ('LINEABOVE', (0,0), (-1,0), 0, colors.transparent),
        ('LINEBELOW', (0,0), (-1,0), 0, colors.transparent),
        ('LINEBEFORE', (0,0), (0,-1), 0, colors.transparent),
        ('LINEAFTER', (0,0), (0,-1), 0, colors.transparent),
    ])
    header_table = Table(header_bar_data, colWidths=[7.5 * inch], rowHeights=[0.4 * inch])
    header_table.setStyle(header_style)
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch)) # Space after the bar

    elements.append(Paragraph(name, styles['nome']))

    contact_items: List[str] = []
    if email: contact_items.append(f"📧 {email}") # Using emojis for modern feel
    if phone: contact_items.append(f"📱 {phone}")
    if linkedin: contact_items.append(f"🌐 {linkedin}")

    if contact_items:
        contact_text = "  |  ".join(contact_items) # Separator for contact info
        elements.append(Paragraph(contact_text, styles['contato']))

    # Simple line separator below contact info
    line_data = [['']]
    line_table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY_DARK),
        ('LINEABOVE', (0,0), (-1,0), 0, colors.transparent),
         # ... (remove other lines if needed)
    ])
    line_table_obj = Table(line_data, colWidths=[7.5 * inch], rowHeights=[0.02 * inch])
    line_table_obj.setStyle(line_table_style)
    elements.append(Spacer(1, 0.05 * inch)) # Space before line
    elements.append(line_table_obj)
    elements.append(Spacer(1, 0.2 * inch)) # Space after line


def add_section_title(elements: List[Flowable], title: str, styles: Dict[str, RLParagraphStyle]) -> None:
    """
    Adds a modern-styled section title to the PDF elements list.

    Args:
        elements (List[Flowable]): List of ReportLab Flowables.
        title (str): Text of the section title.
        styles (Dict[str, ParagraphStyle]): Predefined styles.
    """
    # Example: Section title with a bottom border or different background
    # For this version, using the 'secao' style which might have border/padding
    elements.append(Paragraph(title.upper(), styles['secao']))


def add_skill_bar(
    elements: List[Flowable],
    skill_name: str,
    styles: Dict[str, RLParagraphStyle],
    level: int,
    max_level: int = 5
) -> None:
    """
    Adds a modern-styled skill bar to the PDF elements list.

    Uses a table to create a visual representation of skill proficiency.

    Args:
        elements (List[Flowable]): List of ReportLab Flowables.
        skill_name (str): Name of the skill.
        styles (Dict[str, ParagraphStyle]): Predefined styles.
        level (int): Proficiency level.
        max_level (int): Maximum proficiency level. Defaults to 5.
    """
    if not isinstance(level, int) or not isinstance(max_level, int) or level < 0 or max_level <= 0:
        level = 0
        max_level = 5
    level = min(level, max_level)

    # Skill name on one side, bar on the other, in a single table row
    skill_text = Paragraph(skill_name, styles['normal'])
    
    # Create the bar as a list of small tables (one cell each) or a single table with multiple cells
    bar_cells_data: List[List[Any]] = [[]] # Single row for all bar squares
    bar_cell_width = 0.25 * inch
    bar_cell_height = 0.15 * inch

    for i in range(max_level):
        # Each cell is a tiny table to control its background and border precisely
        cell_content = "" # No text in the bar cells
        cell_style_ops: List[Tuple[str, Tuple[int,int], Tuple[int,int], Any]] = [
            ('BOX', (0,0), (0,0), 0.5, COLOR_PRIMARY_DARK), # Border for all cells
        ]
        if i < level:
            cell_style_ops.append(('BACKGROUND', (0,0), (0,0), COLOR_PRIMARY_DARK)) # Filled cell
        else:
            cell_style_ops.append(('BACKGROUND', (0,0), (0,0), COLOR_BACKGROUND_GREY)) # Empty cell

        cell_table = Table([[cell_content]], colWidths=[bar_cell_width], rowHeights=[bar_cell_height])
        cell_table.setStyle(TableStyle(cell_style_ops))
        bar_cells_data[0].append(cell_table)

    # Main table for skill name + bar
    # Adjust colWidths: skill name takes more space, bar takes sum of its cell widths
    # This approach (nested tables for bar cells) is complex.
    # A simpler approach might be drawing rectangles directly on canvas if precise control is needed,
    # or using a single table with styled cells if ReportLab handles it well.
    # For now, let's use a simpler text-based bar for the "modern" template too,
    # or revert to the standard PDF template's bar logic for simplicity if this becomes too complex.

    # Reverting to a simpler bar for robustness, similar to template_pdf.py's skill bar,
    # but can be styled with modern colors.
    skill_paragraph_text = f"{skill_name}: "
    bar_filled_char = "●" # Filled circle
    bar_empty_char = "○"  # Empty circle
    
    bar_representation = (bar_filled_char * level) + (bar_empty_char * (max_level - level))
    
    # Create a paragraph with the skill name and the bar.
    # The bar part can be colored.
    full_skill_text = f"{skill_paragraph_text}<font color='{COLOR_PRIMARY_DARK.hexval()}'>{bar_representation}</font>"
    elements.append(Paragraph(full_skill_text, styles['normal']))
    elements.append(Spacer(1, 0.05 * inch))


def add_page_break(elements: List[Flowable]) -> None:
    """Adds a page break to the PDF elements list."""
    elements.append(PageBreak())


def create_document(filename: str) -> RLSimpleDocTemplate:
    """
    Creates a new `SimpleDocTemplate` for the modern PDF.
    Uses slightly different margins for a modern layout.

    Args:
        filename (str): Name (including path) for the output PDF file.

    Returns:
        SimpleDocTemplate: A ReportLab `SimpleDocTemplate` object.
    """
    return SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=0.8 * inch, # Example: different margins for modern look
        rightMargin=0.8 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch
    )


if __name__ == '__main__':
    # Example usage: Create a dummy "modern" PDF file
    print("--- Testing template_pdf_moderno.py ---")
    
    output_filename_modern = "_test_template_pdf_moderno_output.pdf"
    doc_modern = create_document(output_filename_modern)
    story_modern: List[Flowable] = []
    
    current_styles_modern = get_styles()

    add_title(story_modern, "Nome Moderno & Estiloso", "moderno@example.com",
              "33 98877-6655", "linkedin.com/in/moderno", current_styles_modern)
    
    add_section_title(story_modern, "Perfil Criativo", current_styles_modern)
    story_modern.append(Paragraph("Um resumo profissional com um toque moderno e design arrojado.", current_styles_modern['normal']))
    story_modern.append(Spacer(1, 0.1 * inch))
    
    add_section_title(story_modern, "Super Habilidades", current_styles_modern)
    add_skill_bar(story_modern, "Design Thinking", current_styles_modern, 5)
    add_skill_bar(story_modern, "UI/UX Prototyping", current_styles_modern, 4)
    story_modern.append(Spacer(1, 0.1 * inch))

    add_page_break(story_modern)
    add_section_title(story_modern, "Projetos Inovadores", current_styles_modern)
    story_modern.append(Paragraph("Detalhes de projetos com impacto visual e funcional.", current_styles_modern['normal']))

    try:
        doc_modern.build(story_modern)
        print(f"Documento moderno de teste PDF salvo como: {output_filename_modern}")
        assert os.path.exists(output_filename_modern), "Test Modern PDF file was not created."
        print("Test Modern PDF file created successfully.")
        # os.remove(output_filename_modern) # Clean up
        # print(f"Test file {output_filename_modern} removed.")
    except Exception as e:
        print(f"Erro ao salvar documento de teste PDF moderno: {e}")
    
    print("--- template_pdf_moderno.py test finished ---")
