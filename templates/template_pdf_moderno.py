"""
Template moderno para geração de currículos em formato PDF.
Este arquivo define as funções e estilos usados para criar um layout moderno de currículo em PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch, cm
from io import BytesIO

# Definir cores do template moderno
AZUL_ESCURO = colors.Color(0.1, 0.2, 0.4)
AZUL_CLARO = colors.Color(0.6, 0.8, 0.9)
CINZA = colors.Color(0.9, 0.9, 0.9)

# Configuração de estilos
def get_styles():
    styles = getSampleStyleSheet()
    
    # Adicionar estilos personalizados
    nome_style = ParagraphStyle(
        'Nome',
        parent=styles['Title'],
        fontSize=26,
        fontName='Helvetica-Bold',  
        textColor=AZUL_ESCURO,
        spaceAfter=0.1*inch,
    )
    
    contato_style = ParagraphStyle(
        'Contato',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.gray,
        spaceAfter=0.05*inch,
    )
    
    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=AZUL_ESCURO,
        spaceBefore=0.2*inch,
        spaceAfter=0.1*inch,
        borderColor=AZUL_CLARO,
        borderWidth=1,
        borderPadding=5,
        borderRadius=5,
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
    )
    
    return {
        'base': styles,
        'nome': nome_style,
        'contato': contato_style,
        'secao': secao_style,
        'normal': normal_style,
        'bullet': bullet_style
    }

# Função para adicionar título
def add_title(elements, nome, email, telefone, linkedin, styles):
    # Cabeçalho com cores modernas
    data = [['']]
    
    # Define a cor de fundo
    header_style = TableStyle([
        ('BACKGROUND', (0,0), (0,0), AZUL_CLARO),
        ('GRID', (0,0), (-1,-1), 0, colors.white),
    ])
    
    header_table = Table(data, colWidths=[7.5*inch], rowHeights=[0.5*inch])
    header_table.setStyle(header_style)
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Nome com estilo moderno
    elements.append(Paragraph(nome, styles['nome']))
    
    # Informações de contato com ícones
    elements.append(Paragraph(f"📧 {email} | 📱 {telefone} | 🌐 {linkedin}", styles['contato']))
    
    # Linha divisória
    elements.append(Spacer(1, 0.1*inch))
    data = [['']]
    line_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, AZUL_ESCURO),
        ('BACKGROUND', (0,0), (-1,-1), AZUL_ESCURO),
    ])
    line_table = Table(data, colWidths=[7.5*inch], rowHeights=[0.03*inch])
    line_table.setStyle(line_style)
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))

# Função para adicionar seção
def add_section_title(elements, title, styles):
    # Título da seção com estilo moderno
    elements.append(Paragraph(title, styles['secao']))

# Função para adicionar barra de skill
def add_skill_bar(elements, skill, styles, level=5, max_level=5):
    # Criar tabela para a barra de habilidade com o nome da habilidade
    data = [[skill, '']]
    skill_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0, colors.white),  # Sem grade
        ('FONTNAME', (0,0), (0,0), 'Helvetica'),
        ('FONTSIZE', (0,0), (0,0), 11),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
    ])
    
    skill_table = Table(data, colWidths=[3*inch, 4.5*inch], rowHeights=[0.3*inch])
    skill_table.setStyle(skill_style)
    elements.append(skill_table)
    
    # Espaço para colocar os quadradinhos na mesma linha
    elements.append(Spacer(1, -0.25*inch))
    
    # Adicionar espaços em branco antes dos quadrados para posicioná-los à direita
    elements.append(Paragraph("&nbsp;" * 50, styles['normal']))
    elements.append(Spacer(1, -0.2*inch))
    
    # Definir o tamanho e espaçamento dos quadrados
    square_size = 0.2*inch
    
    # Criar uma tabela para os quadrados
    squares_data = [['' for i in range(max_level)]]
    squares_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0, colors.white),  # Sem grade na tabela
    ])
    
    # Aplicar estilo a cada quadrado
    for i in range(max_level):
        if i < level:
            # Quadrado preenchido
            squares_style.add('BACKGROUND', (i,0), (i,0), AZUL_ESCURO)
            squares_style.add('BOX', (i,0), (i,0), 1, AZUL_ESCURO)
        else:
            # Quadrado vazio
            squares_style.add('BOX', (i,0), (i,0), 0.5, AZUL_CLARO)
            squares_style.add('BACKGROUND', (i,0), (i,0), CINZA)
    
    squares_table = Table(squares_data, colWidths=[square_size] * max_level, rowHeights=[square_size])
    squares_table.setStyle(squares_style)
    elements.append(squares_table)
    
    # Espaço após a barra de habilidade
    elements.append(Spacer(1, 0.15*inch))

# Função para adicionar quebra de página
def add_page_break(elements):
    elements.append(PageBreak())

# Cria o documento PDF
def create_document(filename):
    return SimpleDocTemplate(filename, pagesize=A4, 
                      leftMargin=inch/2, rightMargin=inch/2,
                      topMargin=inch/2, bottomMargin=inch/2)
