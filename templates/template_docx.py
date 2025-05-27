"""
Template para geração de currículos em formato DOCX.
Este arquivo define as funções e estilos usados para criar um layout de currículo em DOCX.
"""

from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.parser import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.shared import Inches

# Função para adicionar título visual
def add_title(doc, nome, email, telefone, linkedin):
    # Nome grande
    p = doc.add_paragraph()
    run = p.add_run(nome)
    run.font.size = Pt(22)
    run.font.bold = True
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT    # Linha de contato com ícones (texto)
    p = doc.add_paragraph()
    if email:
        p.add_run("📧 ").bold = True
        p.add_run(email + "   ")
    if telefone:
        p.add_run("📱 ").bold = True
        p.add_run(telefone + "   ")
    if linkedin:
        p.add_run("🌐 ").bold = True
        p.add_run(linkedin)
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # Linha
    doc.add_paragraph().add_run("―" * 50)

# Função para adicionar sessão com bloco colorido
def add_section_title(doc, title):
    p = doc.add_paragraph()
    run = p.add_run("■ ")
    run.font.color.rgb = RGBColor(47, 117, 181) # azul
    run.font.size = Pt(14)
    run.bold = True
    run = p.add_run(title)
    run.font.size = Pt(14)
    run.bold = True
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

# Função para adicionar barra de skill
def add_skill_bar(doc, skill, level=5, max_level=5):
    p = doc.add_paragraph()
    run = p.add_run(skill + ": ")
    run.font.size = Pt(11)
    # Barra de "progresso"
    bar = "■" * level + "□" * (max_level-level)
    run = p.add_run(bar)
    run.font.color.rgb = RGBColor(47, 117, 181)

# Função para adicionar quebra de página
def add_page_break(doc):
    run = doc.add_paragraph().add_run()
    run.add_break(WD_BREAK.PAGE)

# Criar um novo documento DOCX
def create_document():
    return Document()
