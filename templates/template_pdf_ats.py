"""
Template otimizado para ATS (Applicant Tracking Systems) brasileiros.
Este arquivo define as funções e estilos usados para criar um layout de currículo em PDF que 
maximiza a compatibilidade com sistemas ATS comuns no Brasil.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch, cm
from io import BytesIO

# Definir cores do template - cores sóbrias para melhor reconhecimento ATS
PRETO = colors.black
CINZA_ESCURO = colors.Color(0.2, 0.2, 0.2)
CINZA_MEDIO = colors.Color(0.5, 0.5, 0.5)
CINZA_CLARO = colors.Color(0.9, 0.9, 0.9)

# Configuração de estilos otimizados para ATS
def get_styles():
    styles = getSampleStyleSheet()
    
    # Adicionar estilos personalizados com fontes e formatações simples para melhor leitura ATS
    nome_style = ParagraphStyle(
        'Nome',
        parent=styles['Title'],
        fontSize=18,
        fontName='Helvetica-Bold',  
        textColor=PRETO,
        spaceAfter=0.1*inch,
        alignment=1,  # Centralizado
    )
    
    contato_style = ParagraphStyle(
        'Contato',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        textColor=CINZA_ESCURO,
        spaceAfter=0.05*inch,
        alignment=1,  # Centralizado
    )
    
    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=PRETO,
        spaceBefore=0.2*inch,
        spaceAfter=0.1*inch,
        # Sem decorações complexas para facilitar leitura ATS
    )
    
    subsecao_style = ParagraphStyle(
        'SubSecao',
        parent=styles['Heading3'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=CINZA_ESCURO,
        spaceBefore=0.1*inch,
        spaceAfter=0.05*inch,
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        leading=14,
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        leftIndent=20,
        leading=14,
        # Bullets simples para melhor reconhecimento ATS
    )
    
    # Estilo para palavras-chave/competências com formato mais simples
    keyword_style = ParagraphStyle(
        'Keyword',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        leading=14,
    )
    
    return {
        'base': styles,
        'nome': nome_style,
        'contato': contato_style,
        'secao': secao_style,
        'subsecao': subsecao_style,
        'normal': normal_style,
        'bullet': bullet_style,
        'keyword': keyword_style
    }

# Função para adicionar título - simplificado para melhor compatibilidade ATS
def add_title(elements, nome, email, telefone, linkedin, styles):
    # Nome com estilo claro para ATS
    elements.append(Paragraph(nome, styles['nome']))
    
    # Contato formatado com rótulos explícitos para melhor reconhecimento ATS
    contact_info = f"E-mail: {email} | Telefone: {telefone} | LinkedIn: {linkedin}"
    elements.append(Paragraph(contact_info, styles['contato']))
    
    # Linha divisória simples
    elements.append(Spacer(1, 0.1*inch))
    data = [['']]
    line_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, CINZA_MEDIO),
        ('BACKGROUND', (0,0), (-1,-1), CINZA_MEDIO),
    ])
    line_table = Table(data, colWidths=[7.5*inch], rowHeights=[0.01*inch])
    line_table.setStyle(line_style)
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))

# Função para adicionar seção
def add_section_title(elements, title, styles):
    # Título da seção com estilo claro para ATS
    elements.append(Paragraph(title, styles['secao']))

# Função para adicionar habilidade como barra (compatível com a interface do template_pdf_moderno)
def add_skill_bar(elements, skill, styles, level=5, max_level=5):
    # Usar o método add_skill em vez disso
    add_skill(elements, skill, styles, level, max_level)

# Função para adicionar competência - formato de texto plano com nível explícito para ATS
def add_skill(elements, skill, styles, level=5, max_level=5, lang='pt'): # Add lang parameter
    # Representação textual do nível para melhor reconhecimento ATS
    level_text = ""
    
    # Convert level to int if it's a string, with error handling
    try:
        current_level = int(level)
    except ValueError:
        # Fallback or error message if level is not a valid number string
        print(f"Warning: Invalid skill level '{level}' for skill '{skill}'. Using default.")
        current_level = 3 # Default to Intermediate

    if lang == 'en':
        if current_level == 1:
            level_text = "Basic"
        elif current_level == 2:
            level_text = "Lower Intermediate"
        elif current_level == 3:
            level_text = "Intermediate"
        elif current_level == 4:
            level_text = "Advanced"
        elif current_level == 5:
            level_text = "Expert"
        else:
            level_text = "Intermediate" # Default for unknown levels
    elif lang == 'es':
        if current_level == 1:
            level_text = "Básico"
        elif current_level == 2:
            level_text = "Intermedio Bajo"
        elif current_level == 3:
            level_text = "Intermedio"
        elif current_level == 4:
            level_text = "Avanzado"
        elif current_level == 5:
            level_text = "Experto"
        else:
            level_text = "Intermedio" # Default for unknown levels
    else: # Default to Portuguese (pt)
        if current_level == 1:
            level_text = "Básico"
        elif current_level == 2:
            level_text = "Intermediário Baixo"
        elif current_level == 3:
            level_text = "Intermediário"
        elif current_level == 4:
            level_text = "Avançado"
        elif current_level == 5:
            level_text = "Especialista"
        else:
            level_text = "Intermediário" # Default for unknown levels
    
    # Formatar competência com nível para melhor leitura do ATS
    skill_text = f"{skill}: {level_text}"
    elements.append(Paragraph(skill_text, styles['normal']))
    elements.append(Spacer(1, 0.05*inch))

# Função para adicionar experiência profissional formatada para ATS
def add_job_experience(elements, cargo, empresa, periodo, descricao, styles, labels):
    # Formatar cargo e empresa com palavras-chave claras para ATS
    job_title = f"<b>{labels.get('position', 'Cargo')}:</b> {cargo}"
    elements.append(Paragraph(job_title, styles['subsecao']))
    
    if empresa:
        company_text = f"<b>{labels.get('company', 'Empresa')}:</b> {empresa}"
        elements.append(Paragraph(company_text, styles['normal']))
    
    if periodo:
        period_text = f"<b>{labels.get('period', 'Período')}:</b> {periodo}"
        elements.append(Paragraph(period_text, styles['normal']))
    
    elements.append(Spacer(1, 0.05*inch))
    
    # Adicionar descrição como lista de bullets com formatação clara para ATS
    processed_description_items = []
    if isinstance(descricao, str):
        processed_description_items = [s.strip() for s in descricao.split('\n') if s.strip()]
        if not processed_description_items and descricao.strip(): # Handle single-line non-empty strings
            processed_description_items = [descricao.strip()]
    elif isinstance(descricao, list):
        processed_description_items = [str(item).strip() for item in descricao if str(item).strip()]

    if processed_description_items:
        elements.append(Paragraph(f"<b>{labels.get('description_heading', 'Responsabilidades e Realizações')}:</b>", styles['normal']))
        for item in processed_description_items:
            bullet_item = f"• {item}"
            elements.append(Paragraph(bullet_item, styles['bullet']))
    
    elements.append(Spacer(1, 0.1*inch))

# Função para adicionar palavras-chave/competências para ATS
def add_keywords_section(elements, keywords, styles, title="Outras Competências"):
    # Seção específica para palavras-chave e competências (útil para ATS)
    add_section_title(elements, title, styles)
    
    if keywords and isinstance(keywords, list):
        # Formatar como texto simples separado por vírgulas para melhor reconhecimento ATS
        keywords_text = ", ".join(keywords)
        elements.append(Paragraph(keywords_text, styles['keyword']))
    
    elements.append(Spacer(1, 0.2*inch))

# Função para adicionar quebra de página
def add_page_break(elements):
    elements.append(PageBreak())

# Cria o documento PDF
def create_document(filename):
    return SimpleDocTemplate(filename, pagesize=A4, 
                      leftMargin=inch/2, rightMargin=inch/2,
                      topMargin=inch/2, bottomMargin=inch/2)
