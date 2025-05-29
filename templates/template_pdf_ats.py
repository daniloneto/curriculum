"""
ATS-Optimized PDF CV Template using ReportLab.

This module provides functions to create and structure a CV in PDF format,
specifically tailored for Applicant Tracking Systems (ATS). It emphasizes
simple, parseable layouts, standard fonts, and clear labeling of sections
and content to maximize compatibility with common ATS used in recruitment.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.units import inch
from typing import List, Dict, Any, Optional

# Type aliases for ReportLab objects for clarity
Flowable = Any  # Base class for ReportLab flowables
RLSimpleDocTemplate = SimpleDocTemplate
RLParagraphStyle = ParagraphStyle

# Define common colors (using ReportLab's Color objects)
COLOR_BLACK = colors.black
COLOR_DARK_GREY = colors.Color(0.2, 0.2, 0.2)
COLOR_MEDIUM_GREY = colors.Color(0.5, 0.5, 0.5)
# COLOR_LIGHT_GREY = colors.Color(0.9, 0.9, 0.9) # Not used in current version

# Standard font names for ATS compatibility
FONT_HELVETICA = 'Helvetica'
FONT_HELVETICA_BOLD = 'Helvetica-Bold'


def get_styles() -> Dict[str, RLParagraphStyle]:
    """
    Defines and returns a dictionary of ParagraphStyle objects optimized for ATS.

    Styles use Helvetica font, clear hierarchies, and minimal formatting
    to ensure maximum readability by Applicant Tracking Systems.

    Returns:
        Dict[str, ParagraphStyle]: A dictionary where keys are style names
                                   (e.g., 'nome_ats', 'contato_ats') and
                                   values are ParagraphStyle objects.
    """
    styles = getSampleStyleSheet()

    nome_style = ParagraphStyle(
        'NomeATS',  # Unique name to avoid clashes if other templates are merged
        parent=styles['Title'],
        fontSize=18,
        fontName=FONT_HELVETICA_BOLD,
        textColor=COLOR_BLACK,
        spaceAfter=0.1 * inch,
        alignment=1,  # Centered (TA_CENTER = 1)
    )

    contato_style = ParagraphStyle(
        'ContatoATS',
        parent=styles['Normal'],
        fontSize=10, # Slightly smaller for contact line
        fontName=FONT_HELVETICA,
        textColor=COLOR_DARK_GREY,
        spaceAfter=0.05 * inch,
        alignment=1,  # Centered
    )

    secao_style = ParagraphStyle(
        'SecaoATS',
        parent=styles['Heading2'],
        fontSize=14,
        fontName=FONT_HELVETICA_BOLD,
        textColor=COLOR_BLACK,
        spaceBefore=0.15 * inch, # Reduced space for ATS
        spaceAfter=0.08 * inch,
        alignment=0,  # Left aligned (TA_LEFT = 0)
    )

    subsecao_style = ParagraphStyle(
        'SubSecaoATS',
        parent=styles['Heading3'],
        fontSize=12,
        fontName=FONT_HELVETICA_BOLD,
        textColor=COLOR_DARK_GREY,
        spaceBefore=0.1 * inch,
        spaceAfter=0.04 * inch,
        alignment=0,
    )

    normal_style = ParagraphStyle(
        'NormalATS',
        parent=styles['Normal'],
        fontSize=11,
        fontName=FONT_HELVETICA,
        leading=14, # Standard line spacing
        alignment=0,
    )

    bullet_style = ParagraphStyle(
        'BulletATS',
        parent=normal_style,
        leftIndent=0.25 * inch, # Standard bullet indent
        bulletIndent=0.1 * inch,
        firstLineIndent=0, # Ensures bullet is to the left
        spaceBefore=1,
        spaceAfter=1,
    )

    keyword_style = ParagraphStyle(
        'KeywordATS',
        parent=normal_style,
        fontSize=10, # Keywords can be slightly smaller
        textColor=COLOR_MEDIUM_GREY,
    )

    return {
        'nome': nome_style,
        'contato': contato_style,
        'secao': secao_style,
        'subsecao': subsecao_style,
        'normal': normal_style,
        'bullet': bullet_style,
        'keyword': keyword_style,
        'base_normal': styles['Normal'] # For generic line drawing or fallbacks
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
    Adds the main title section (name, contact info) to the PDF elements.
    Simplified for ATS readability, with explicit labels for contact info.

    Args:
        elements (List[Flowable]): List of ReportLab Flowables.
        name (Optional[str]): The full name.
        email (Optional[str]): Email address.
        phone (Optional[str]): Phone number.
        linkedin (Optional[str]): LinkedIn profile URL/vanity name.
        styles (Dict[str, ParagraphStyle]): Predefined styles.
    """
    if not name: name = "Nome Não Especificado"
    elements.append(Paragraph(name, styles['nome']))

    contact_items: List[str] = []
    if email: contact_items.append(f"Email: {email}")
    if phone: contact_items.append(f"Telefone: {phone}")
    if linkedin: contact_items.append(f"LinkedIn: {linkedin}")
    
    if contact_items:
        contact_text = " | ".join(contact_items) # Use pipe for clear separation
        elements.append(Paragraph(contact_text, styles['contato']))

    # Simple spacer instead of a graphical line for ATS
    elements.append(Spacer(1, 0.15 * inch))


def add_section_title(elements: List[Flowable], title: str, styles: Dict[str, RLParagraphStyle]) -> None:
    """
    Adds a section title to the PDF elements. Uses plain text for ATS.

    Args:
        elements (List[Flowable]): List of ReportLab Flowables.
        title (str): Text of the section title.
        styles (Dict[str, ParagraphStyle]): Predefined styles.
    """
    elements.append(Paragraph(title.upper(), styles['secao'])) # Uppercase for emphasis


def add_skill(
    elements: List[Flowable],
    skill_name: str,
    styles: Dict[str, RLParagraphStyle],
    level: int, # Keep level for potential textual representation
    max_level: int = 5, # Keep for consistency, though not visually used
    lang: str = 'pt'
) -> None:
    """
    Adds a skill entry, formatted as plain text for ATS.
    Optionally includes a textual representation of the skill level.

    Args:
        elements (List[Flowable]): List of ReportLab Flowables.
        skill_name (str): Name of the skill.
        styles (Dict[str, ParagraphStyle]): Predefined styles.
        level (int): Proficiency level (1-5).
        max_level (int): Maximum proficiency level (unused visually here).
        lang (str): Language code ('pt', 'en', 'es') for level text.
    """
    level_text_map: Dict[str, Dict[int, str]] = {
        'pt': {1: "Básico", 2: "Intermediário Baixo", 3: "Intermediário", 4: "Avançado", 5: "Especialista"},
        'en': {1: "Basic", 2: "Lower Intermediate", 3: "Intermediate", 4: "Advanced", 5: "Expert"},
        'es': {1: "Básico", 2: "Intermedio Bajo", 3: "Intermedio", 4: "Avanzado", 5: "Experto"},
    }
    default_level_text = "Intermediário" if lang == 'pt' else "Intermediate" # Fallback

    try:
        current_level = int(level)
    except ValueError:
        current_level = 3 # Default to Intermediate if level is invalid

    level_description = level_text_map.get(lang, {}).get(current_level, default_level_text)
    
    # For ATS, simply listing the skill might be better, or skill + textual level.
    # Example: "Python (Avançado)"
    skill_entry = f"{skill_name} ({level_description})"
    # Or, for even simpler parsing: just the skill name.
    # skill_entry = skill_name
    elements.append(Paragraph(skill_entry, styles['normal']))
    # elements.append(Spacer(1, 0.02 * inch)) # Minimal spacer


def add_skill_bar(*args, **kwargs) -> None:
    """
    Placeholder for `add_skill_bar`. For ATS, `add_skill` is preferred.
    This ensures compatibility if `add_skill_bar` is called by a generic process.
    """
    add_skill(*args, **kwargs)


def get_default_labels(lang: str) -> Dict[str, str]:
    """
    Provides default localized labels for job experience fields.
    This can be called by the PdfAtsGenerator.

    Args:
        lang (str): Language code ('pt', 'en', 'es').

    Returns:
        Dict[str, str]: A dictionary of localized labels.
    """
    if lang == 'en':
        return {
            "position": "Position", "company": "Company", "period": "Period",
            "description_heading": "Responsibilities and Achievements"
        }
    elif lang == 'es':
        return {
            "position": "Cargo", "company": "Empresa", "period": "Período", # Or "Puesto"
            "description_heading": "Responsabilidades y Logros"
        }
    # Default to Portuguese
    return {
        "position": "Cargo", "company": "Empresa", "period": "Período",
        "description_heading": "Responsabilidades e Realizações"
    }


def add_job_experience(
    elements: List[Flowable],
    position: str,
    company: Optional[str],
    period: Optional[str],
    description: Optional[Any], # str or List[str]
    styles: Dict[str, RLParagraphStyle],
    labels: Dict[str, str] # Localized labels
) -> None:
    """
    Adds a job experience entry, formatted clearly for ATS.

    Args:
        elements: List of ReportLab Flowables.
        position: Job title/position.
        company: Company name.
        period: Employment period.
        description: Job description (string with newlines or list of strings).
        styles: Predefined styles.
        labels: Localized labels for fields (e.g., "Cargo:", "Empresa:").
    """
    elements.append(Paragraph(f"<b>{labels.get('position', 'Position')}:</b> {position}", styles['subsecao']))
    if company:
        elements.append(Paragraph(f"<b>{labels.get('company', 'Company')}:</b> {company}", styles['normal']))
    if period:
        elements.append(Paragraph(f"<b>{labels.get('period', 'Period')}:</b> {str(period)}", styles['normal']))
    
    elements.append(Spacer(1, 0.05 * inch))

    processed_desc_items: List[str] = []
    if isinstance(description, str):
        processed_desc_items = [s.strip() for s in description.splitlines() if s.strip()]
    elif isinstance(description, list):
        processed_desc_items = [str(item).strip() for item in description if str(item).strip()]

    if processed_desc_items:
        elements.append(Paragraph(
            f"<b>{labels.get('description_heading', 'Responsibilities')}:</b>", styles['normal']
        ))
        for item in processed_desc_items:
            # Using a standard bullet character for ATS compatibility
            elements.append(Paragraph(f"• {item}", styles['bullet']))
    elements.append(Spacer(1, 0.1 * inch))


def add_keywords_section(
    elements: List[Flowable],
    keywords: List[str],
    styles: Dict[str, RLParagraphStyle],
    title: str = "Palavras-chave e Competências Adicionais"
) -> None:
    """
    Adds a section for keywords, formatted as comma-separated text for ATS.

    Args:
        elements: List of ReportLab Flowables.
        keywords: List of keyword strings.
        styles: Predefined styles.
        title: Title for the keywords section.
    """
    if keywords:
        add_section_title(elements, title, styles)
        keywords_text = ", ".join(keywords)
        elements.append(Paragraph(keywords_text, styles['keyword']))
        elements.append(Spacer(1, 0.15 * inch))


def add_page_break(elements: List[Flowable]) -> None:
    """Adds a page break to the PDF elements list."""
    elements.append(PageBreak())


def create_document(filename: str) -> RLSimpleDocTemplate:
    """
    Creates a new `SimpleDocTemplate` for an ATS-optimized PDF.
    Uses slightly reduced margins for content packing if needed, but standard
    margins are generally fine.

    Args:
        filename (str): Name (including path) for the output PDF file.

    Returns:
        SimpleDocTemplate: A ReportLab `SimpleDocTemplate` object.
    """
    return SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=0.75 * inch, # Slightly reduced margins
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )


if __name__ == '__main__':
    # Example usage: Create a dummy ATS PDF file
    print("--- Testing template_pdf_ats.py ---")
    
    output_filename_ats = "_test_template_pdf_ats_output.pdf"
    doc_ats = create_document(output_filename_ats)
    story_ats: List[Flowable] = []
    
    current_styles_ats = get_styles()
    default_labels_ats = get_default_labels('pt')

    add_title(story_ats, "Nome Completo (ATS)", "email.ats@example.com",
              "00 99999-0000", "linkedin.com/in/ats", current_styles_ats)
    
    add_section_title(story_ats, "RESUMO PROFISSIONAL", current_styles_ats)
    story_ats.append(Paragraph("Resumo focado em palavras-chave como gestão, desenvolvimento e liderança.", current_styles_ats['normal']))
    story_ats.append(Spacer(1, 0.1 * inch))
    
    add_section_title(story_ats, "HABILIDADES TÉCNICAS", current_styles_ats)
    add_skill(story_ats, "Python", current_styles_ats, 5, lang='pt')
    add_skill(story_ats, "SQL", current_styles_ats, 4, lang='pt')
    story_ats.append(Spacer(1, 0.1 * inch))

    add_section_title(story_ats, "EXPERIÊNCIA PROFISSIONAL", current_styles_ats)
    add_job_experience(story_ats, "Desenvolvedor Sênior", "Empresa X", "01/2020 - Atual",
                       ["Liderança de projetos.", "Desenvolvimento backend.", "Otimização de SQL."],
                       current_styles_ats, default_labels_ats)
    
    add_keywords_section(story_ats, ["Gestão de Projetos", "Liderança Técnica", "SQL", "Python", "API Design"], current_styles_ats)

    try:
        doc_ats.build(story_ats)
        print(f"Documento ATS de teste PDF salvo como: {output_filename_ats}")
        assert os.path.exists(output_filename_ats), "Test ATS PDF file was not created."
        print("Test ATS PDF file created successfully.")
        # os.remove(output_filename_ats) # Clean up
        # print(f"Test file {output_filename_ats} removed.")
    except Exception as e:
        print(f"Erro ao salvar documento de teste ATS PDF: {e}")
    
    print("--- template_pdf_ats.py test finished ---")
