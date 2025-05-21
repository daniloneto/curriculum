"""
Template para geração de currículos em formato PDF.
Este arquivo define as funções e estilos usados para criar um layout de currículo em PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Configuração de estilos
def get_styles():
    styles = getSampleStyleSheet()
    
    # Adicionar estilos personalizados
    nome_style = ParagraphStyle(
        'Nome',
        parent=styles['Title'],
        fontSize=22,
        fontName='Times-Roman',  
        textColor=colors.black,
        spaceAfter=0.1*inch,
    )
    
    contato_style = ParagraphStyle(
        'Contato',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Times-Roman',
        spaceAfter=0.1*inch,
    )
    
    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Times-Roman',
        textColor=colors.black,
        spaceBefore=0.2*inch,
        spaceAfter=0.1*inch,
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Times-Roman',
        leading=14,
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Times-Roman',
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
    elements.append(Paragraph(nome, styles['nome']))
    
    contato_text = f"📧 {email}   📱 {telefone}   🌐 {linkedin}"
    elements.append(Paragraph(contato_text, styles['contato']))
    
    # Linha horizontal
    elements.append(Paragraph("_" * 70, ParagraphStyle(
        'Linha',
        parent=styles['base']['Normal'],
        fontName='Times-Roman',
        fontSize=8,
    )))
    elements.append(Spacer(1, 0.1*inch))

# Função para adicionar seção
def add_section_title(elements, title, styles):
    section_text = f"<font color='#2F75B5'>■</font> {title}"
    elements.append(Paragraph(section_text, styles['secao']))

# Função para adicionar barra de skill
def add_skill_bar(elements, skill, styles, level=5, max_level=5):
    # Definir a cor azul usada no documento
    azul = colors.Color(47/255, 117/255, 181/255)
    
    # Criar dados da tabela - uma célula para o texto e uma para cada quadrado da barra
    data = [[f"{skill}:"]]
    
    # Definir estilo da tabela principal
    style = TableStyle([
        ('FONTSIZE', (0,0), (0,0), 11),
        ('FONTNAME', (0,0), (0,0), 'Times-Roman'),
        ('VALIGN', (0,0), (0,0), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
    ])
    
    # Criar a tabela com o texto da habilidade
    table = Table(data, colWidths=[5.5*inch])
    table.setStyle(style)
    elements.append(table)
    
    # Tamanhos dos quadrados azuis
    square_size = 0.15*inch  
    
    # Criar a barra como uma nova tabela logo abaixo
    boxes_data = [['']*max_level] 
    boxes_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0, colors.white),  # Sem grade interna
    ])
    
    # Adicionar estilo para cada caixa na barra
    for i in range(max_level):
        if i < level:
            # Quadrado preenchido para níveis atingidos
            boxes_style.add('BACKGROUND', (i,0), (i,0), azul)
            boxes_style.add('BOX', (i,0), (i,0), 0.5, azul)  # Borda azul
        else:
            # Quadrado vazio para níveis não preenchidos
            boxes_style.add('BOX', (i,0), (i,0), 0.5, azul)  # Apenas borda
    
    # Deslocar para posicionar a barra ao lado do texto da habilidade
    elements.append(Spacer(1, -0.22*inch))  # Ajustando posição vertical
    
    # Adicionar espaço em branco para posicionar a barra à direita
    elements.append(Paragraph("&nbsp;" * 40, styles['normal']))
    
    # Deslocar verticalmente para alinhar com o texto
    elements.append(Spacer(1, -0.15*inch))  # Ajustando para os quadrados menores
    
    # Adicionar a barra de habilidade com quadrados menores
    boxes_table = Table(boxes_data, colWidths=[square_size]*max_level, rowHeights=[square_size])
    boxes_table.setStyle(boxes_style)
    elements.append(boxes_table)
    
    # Espaço após a barra completa
    elements.append(Spacer(1, 0.08*inch))

# Função para adicionar quebra de página
def add_page_break(elements):
    elements.append(PageBreak())

# Cria o documento PDF
def create_document(filename):
    return SimpleDocTemplate(filename, pagesize=A4, 
                      leftMargin=inch, rightMargin=inch,
                      topMargin=inch, bottomMargin=inch)
