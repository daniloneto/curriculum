from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, PageBreak, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
import sys
import glob

# Função para listar idiomas disponíveis
def get_available_languages():
    # Procurar todos os arquivos JSON que seguem o padrão curriculo_XX.json
    json_files = glob.glob('curriculo_*.json')
    languages = {}
    
    for file in json_files:
        # Extrair o código do idioma do nome do arquivo (curriculo_XX.json -> XX)
        lang_code = file.replace('curriculo_', '').replace('.json', '')
        
        # Carregar o arquivo para obter o nome do idioma na própria língua
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Verificar se o arquivo tem a estrutura esperada
                if 'languageName' in data:
                    lang_name = data['languageName']
                else:
                    # Fallback para casos onde o nome do idioma não está definido
                    lang_name = lang_code.upper()
                
                languages[lang_code] = {
                    'name': lang_name,
                    'file': file
                }
        except:
            # Se houver erro ao carregar ou analisar, pular este arquivo
            pass
    
    return languages

# Determinar o idioma a ser usado
available_languages = get_available_languages()

# Default para português se disponível, caso contrário usa o primeiro idioma disponível
default_lang = 'pt' if 'pt' in available_languages else list(available_languages.keys())[0] if available_languages else None

# Verificar qual idioma usar com base nos argumentos de linha de comando
selected_lang = default_lang
if len(sys.argv) > 1:
    lang_arg = sys.argv[1].lower()
    if lang_arg in available_languages:
        selected_lang = lang_arg

# Se não houver idiomas disponíveis, terminar o programa
if not selected_lang:
    print("Erro: Não foram encontrados arquivos de idioma válidos.")
    sys.exit(1)

# Carregar o arquivo JSON do idioma selecionado
json_file = available_languages[selected_lang]['file']
with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Função genérica para obter valores do JSON de maneira padronizada
def get_field(data, primary_key, fallback_key=None):
    if primary_key in data:
        return data[primary_key]
    elif fallback_key and fallback_key in data:
        return data[fallback_key]
    return None

# Extrair dados básicos do JSON
# Estrutura padronizada para todas as línguas
nome = get_field(data, 'nome', 'name')
email = data['email']  # Email geralmente é o mesmo em qualquer idioma
telefone = get_field(data, 'telefone', 'phone')
linkedin = data['linkedin']  # LinkedIn geralmente é o mesmo em qualquer idioma

# Determinar qual é a chave principal para seções
secoes_key = None
for key in ['secoes', 'sections', 'secciones', 'sektionen']:
    if key in data:
        secoes_key = key
        break

# Se não encontrarmos a chave das seções, não podemos continuar
if not secoes_key:
    print("Erro: Formato de arquivo JSON inválido. A chave de seções não foi encontrada.")
    sys.exit(1)

secoes = data[secoes_key]

# Obter nome do arquivo para saída PDF
output_filename = get_field(data, 'nomeArquivoSaida', 'outputFileName')
if not output_filename:
    # Se nenhum nome de arquivo for especificado, criar um a partir do nome e idioma
    output_filename = f"Curriculo_{nome.replace(' ', '_')}_{selected_lang}.docx"

# Converter para PDF (substituindo .docx por .pdf se necessário)
pdf_filename = os.path.splitext(output_filename)[0] + ".pdf"

# Criar documento PDF
doc = SimpleDocTemplate(pdf_filename, pagesize=A4, 
                        leftMargin=inch, rightMargin=inch,
                        topMargin=inch, bottomMargin=inch)

# Configuração de fontes

# Estilos
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

# Lista para elementos do PDF
elements = []

# Função para adicionar título
def add_title(nome, email, telefone, linkedin):
    elements.append(Paragraph(nome, nome_style))
    
    contato_text = f"📧 {email}   📱 {telefone}   🌐 {linkedin}"
    elements.append(Paragraph(contato_text, contato_style))
    
    # Linha horizontal
    elements.append(Paragraph("_" * 70, ParagraphStyle(
        'Linha',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8,
    )))
    elements.append(Spacer(1, 0.1*inch))

# Função para adicionar seção
def add_section_title(title):
    section_text = f"<font color='#2F75B5'>■</font> {title}"
    elements.append(Paragraph(section_text, secao_style))

# Função para adicionar barra de skill usando uma única tabela simplificada
def add_skill_bar(skill, level=5, max_level=5):
    # Definir a cor azul usada no documento
    azul = colors.Color(47/255, 117/255, 181/255)
    
    # Criar dados da tabela - uma célula para o texto e uma para cada quadrado da barra
    data = [[f"{skill}:"]]
    
    # Definir estilo da tabela principal
    style = TableStyle([
        ('FONTSIZE', (0,0), (0,0), 11),
        ('FONTNAME', (0,0), (0,0), 'Times-Roman'),  # Usando Times-Roman
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
    elements.append(Paragraph("&nbsp;" * 40, normal_style))
    
    # Deslocar verticalmente para alinhar com o texto
    elements.append(Spacer(1, -0.15*inch))  # Ajustando para os quadrados menores
    
    # Adicionar a barra de habilidade com quadrados menores
    boxes_table = Table(boxes_data, colWidths=[square_size]*max_level, rowHeights=[square_size])
    boxes_table.setStyle(boxes_style)
    elements.append(boxes_table)
    
    # Espaço após a barra completa
    elements.append(Spacer(1, 0.08*inch))

# Função para adicionar quebra de página
def add_page_break():
    elements.append(PageBreak())

# Função genérica para obter título de seção
def get_section_title(section_data, title_keys=['titulo', 'title', 'titre', 'titel']):
    for key in title_keys:
        if key in section_data:
            return section_data[key]
    return "N/A"  # Fallback

# Função genérica para obter conteúdo de seção
def get_section_content(section_data, content_keys=['conteudo', 'content', 'contenido', 'inhalt']):
    for key in content_keys:
        if key in section_data:
            return section_data[key]
    return ""  # Fallback

# Função genérica para obter lista de itens
def get_section_list(section_data, list_keys=['lista', 'list', 'liste', 'lista']):
    for key in list_keys:
        if key in section_data:
            return section_data[key]
    return []  # Fallback

# Função genérica para obter lista de empregos/experiências
def get_jobs(section_data, jobs_keys=['empregos', 'jobs', 'empleos', 'emplois']):
    for key in jobs_keys:
        if key in section_data:
            return section_data[key]
    return []  # Fallback

# Montar o currículo visual
add_title(nome, email, telefone, linkedin)

# Resumo Profissional - procurar por várias possíveis chaves
resume_section = None
for key in ['resumoProfissional', 'professionalSummary', 'resumenProfesional', 'resumentProfessionnel']:
    if key in secoes:
        resume_section = secoes[key]
        break

if resume_section:
    add_section_title(get_section_title(resume_section))
    elements.append(Paragraph(get_section_content(resume_section), normal_style))
    elements.append(Spacer(1, 0.1*inch))

# Experiência Profissional - procurar por várias possíveis chaves
experience_section = None
for key in ['experienciaProfissional', 'workExperience', 'experienciaLaboral', 'experienceProfessionnelle']:
    if key in secoes:
        experience_section = secoes[key]
        break

if experience_section:
    add_section_title(get_section_title(experience_section))
    
    # Obter lista de empregos
    jobs = get_jobs(experience_section)
    
    # Adicionar empregos
    for job in jobs:
        position = get_field(job, 'cargo', 'position')
        if position:
            elements.append(Paragraph(f"• {position}", bullet_style))
        
        period = get_field(job, 'periodo', 'period')
        if period:
            elements.append(Paragraph(period, normal_style))
        
        # Obter descrição - procurar por várias possíveis chaves
        description_items = []
        for key in ['descricao', 'description', 'descripcion']:
            if key in job:
                description_items = job[key]
                break
        
        items = []
        for item in description_items:
            items.append(Paragraph(f"- {item}", bullet_style))
            
        for item in items:
            elements.append(item)
        
        elements.append(Spacer(1, 0.1*inch))

# Habilidades Técnicas - procurar por várias possíveis chaves
add_page_break()
skills_section = None
for key in ['habilidadesTecnicas', 'technicalSkills', 'habilidadesTecnicas', 'competencesTechniques']:
    if key in secoes:
        skills_section = secoes[key]
        break

if skills_section:
    add_section_title(get_section_title(skills_section))
    
    # Obter lista de habilidades
    skills = []
    for key in ['habilidades', 'skills', 'habilidades', 'competences']:
        if key in skills_section:
            skills = skills_section[key]
            break
    
    for skill in skills:
        skill_name = get_field(skill, 'nome', 'name')
        skill_level = get_field(skill, 'nivel', 'level')
        if skill_name and skill_level:
            add_skill_bar(skill_name, skill_level)
    
    elements.append(Spacer(1, 0.1*inch))

# Certificações - procurar por várias possíveis chaves
certifications_section = None
for key in ['certificacoes', 'certifications', 'certificaciones', 'certifications']:
    if key in secoes:
        certifications_section = secoes[key]
        break

if certifications_section:
    add_section_title(get_section_title(certifications_section))
    certifications = get_section_list(certifications_section)
    
    for cert in certifications:
        elements.append(Paragraph(f"🏅 {cert}", normal_style))
    
    elements.append(Spacer(1, 0.1*inch))

# Educação - procurar por várias possíveis chaves
education_section = None
for key in ['educacao', 'education', 'educacion', 'education']:
    if key in secoes:
        education_section = secoes[key]
        break

if education_section:
    add_section_title(get_section_title(education_section))
    
    # Obter lista de formações
    degrees = []
    for key in ['formacao', 'degrees', 'formacion', 'diplomes']:
        if key in education_section:
            degrees = education_section[key]
            break
    
    for degree in degrees:
        elements.append(Paragraph(degree, normal_style))
    
    elements.append(Spacer(1, 0.1*inch))

# Em Andamento - procurar por várias possíveis chaves
in_progress_section = None
for key in ['emAndamento', 'inProgress', 'enProgreso', 'enCours']:
    if key in secoes:
        in_progress_section = secoes[key]
        break

if in_progress_section:
    add_section_title(get_section_title(in_progress_section))
    
    # Obter lista de cursos
    courses = []
    for key in ['cursos', 'courses', 'cursos', 'cours']:
        if key in in_progress_section:
            courses = in_progress_section[key]
            break
    
    for course in courses:
        elements.append(Paragraph(course, normal_style))

# Gerar o PDF
try:   
    if os.path.exists(pdf_filename):
        try:
            # Tentar renomear temporariamente o arquivo existente
            temp_name = pdf_filename + ".old"
            if os.path.exists(temp_name):
                os.remove(temp_name)
            os.rename(pdf_filename, temp_name)
            
            # Gerar o novo PDF
            doc.build(elements)
            
            # Se deu certo, remover o arquivo antigo
            if os.path.exists(temp_name):
                os.remove(temp_name)
                
        except Exception as e:
            # Se falhar em renomear, tentar outro nome de arquivo
            alternative_filename = os.path.splitext(pdf_filename)[0] + "_new.pdf"
            doc = SimpleDocTemplate(alternative_filename, pagesize=A4, 
                        leftMargin=inch, rightMargin=inch,
                        topMargin=inch, bottomMargin=inch)
            doc.build(elements)
            pdf_filename = alternative_filename
    else:
        # Se não existir, simplesmente criar o arquivo
        doc.build(elements)
        
    print(f"Arquivo PDF salvo como: {pdf_filename}")
    
except Exception as e:
    print(f"Erro ao gerar o PDF: {str(e)}")
    print("Tente fechar o arquivo PDF se ele estiver aberto em outro programa.")
