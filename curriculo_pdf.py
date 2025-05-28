from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
import sys
import glob
import argparse
from templates import TemplateManager
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
import sys
import glob
from templates import TemplateManager

# Função genérica para obter valores do JSON de maneira padronizada
def get_field(data, primary_key, fallback_key=None, additional_fallbacks=None):
    if primary_key in data:
        return data[primary_key]
    elif fallback_key and fallback_key in data:
        return data[fallback_key]
    
    # Verificar chaves adicionais específicas para alguns campos
    if additional_fallbacks:
        for key in additional_fallbacks:
            if key in data:
                return data[key]
    
    return None

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

# Configurar os argumentos de linha de comando
parser = argparse.ArgumentParser(description='Gerar currículo em formato PDF.')
parser.add_argument('language', nargs='?', help='Código do idioma (ex: pt, en, es)')
parser.add_argument('--template', '-t', help='Nome do template a ser usado', default='pdf')
parser.add_argument('--json-file', help='Caminho para um arquivo JSON personalizado', default=None)
args = parser.parse_args()

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
if args.language:
    lang_arg = args.language.lower()
    if lang_arg in available_languages:
        selected_lang = lang_arg

# Se não houver idiomas disponíveis, terminar o programa
if not selected_lang and not args.json_file:
    print("Erro: Não foram encontrados arquivos de idioma válidos.")
    sys.exit(1)

# Carregar o arquivo JSON
if args.json_file:
    print(f"Usando arquivo JSON personalizado: {args.json_file}")
    # Usar o arquivo JSON personalizado
    try:
        with open(args.json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Erro ao carregar arquivo JSON personalizado: {str(e)}")
        sys.exit(1)
else:
    # Carregar o arquivo JSON do idioma selecionado
    json_file = available_languages[selected_lang]['file']
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

# Extrair dados básicos do JSON
# Estrutura padronizada para todas as línguas
nome = get_field(data, 'nome', 'name', ['nombre'])
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

# Carregar o template
template_manager = TemplateManager()
template_name = args.template

try:
    template = template_manager.get_template(template_name)
    print(f"Usando template: {template_name}")
except ValueError as e:
    print(f"Erro ao carregar template: {str(e)}")
    print(f"Templates disponíveis: {', '.join(template_manager.list_templates())}")
    print("Usando o template padrão 'pdf'.")
    template = template_manager.get_template('pdf')

# Obter nome do arquivo para saída PDF
output_filename = get_field(data, 'nomeArquivoSaida', 'outputFileName')
if not output_filename:    # Se nenhum nome de arquivo for especificado, criar um a partir do nome e idioma
    if nome:
        output_filename = f"Curriculo_{nome.replace(' ', '_')}_{selected_lang}.pdf"
    else:
        output_filename = f"Curriculo_{selected_lang}.pdf"

# Converter para PDF (substituindo .docx por .pdf se necessário)
pdf_filename = os.path.splitext(output_filename)[0]
if not pdf_filename.lower().endswith('.pdf'):
    pdf_filename += ".pdf"

# Criar documento PDF
doc = template.create_document(pdf_filename)

# Obter estilos definidos no template
styles = template.get_styles()

# Lista para elementos do PDF
elements = []

# Montar o currículo visual
template.add_title(elements, nome, email, telefone, linkedin, styles)

# Resumo Profissional - procurar por várias possíveis chaves
resume_section = None
for key in ['resumoProfissional', 'professionalSummary', 'resumenProfesional', 'resumentProfessionnel']:
    if key in secoes:
        resume_section = secoes[key]
        break

if resume_section:
    template.add_section_title(elements, get_section_title(resume_section), styles)
    elements.append(Paragraph(get_section_content(resume_section), styles['normal']))
    elements.append(Spacer(1, 0.1*inch))

# Experiência Profissional - procurar por várias possíveis chaves
experience_section = None
for key in ['experienciaProfissional', 'workExperience', 'experienciaLaboral', 'experienceProfessionnelle']:
    if key in secoes:
        experience_section = secoes[key]
        break

if experience_section:
    template.add_section_title(elements, get_section_title(experience_section), styles)
    
    # Obter lista de empregos
    jobs = get_jobs(experience_section)
    
    # Adicionar empregos
    for job in jobs:
        position = get_field(job, 'cargo', 'position')
        if position:
            elements.append(Paragraph(f"• {position}", styles['bullet']))
        
        period = get_field(job, 'periodo', 'period')
        if period:
            elements.append(Paragraph(period, styles['normal']))
        
        # Obter descrição - procurar por várias possíveis chaves
        description_content = None
        for key in ['descricao', 'description', 'descripcion']:
            if key in job:
                description_content = job[key]
                break
        
        processed_description_items = []
        if isinstance(description_content, str):
            # If it's a string, split by newlines to create multiple bullet points.
            # Filter out empty strings that might result from multiple newlines.
            processed_description_items = [s.strip() for s in description_content.split('\\n') if s.strip()]
            # If splitting by newline results in an empty list, but the original string was not empty,
            # treat the original string as a single item. This covers cases where the string has no newlines.
            if not processed_description_items and description_content.strip():
                 processed_description_items = [description_content.strip()]
        elif isinstance(description_content, list):
            # If it's already a list, assume each item is a bullet point
            # Ensure all items are strings and stripped of whitespace.
            processed_description_items = [str(item).strip() for item in description_content if str(item).strip()]

        # Create Paragraph objects for each processed description item
        item_paragraphs = []
        for item_text in processed_description_items:
            item_paragraphs.append(Paragraph(f"- {item_text}", styles['bullet']))
            
        for p in item_paragraphs:
            elements.append(p)
        
        elements.append(Spacer(1, 0.1*inch))

# Habilidades Técnicas - procurar por várias possíveis chaves
template.add_page_break(elements)
skills_section = None
# Ensure unique keys in a preferred order for lookup
for key in ['habilidadesTecnicas', 'technicalSkills', 'competencesTechniques']: # PT/ES, EN, FR
    if key in secoes:
        skills_section = secoes[key]
        break

if skills_section:
    template.add_section_title(elements, get_section_title(skills_section), styles)
      # Obter lista de habilidades
    skills = []
    # Ensure unique keys in a preferred order for lookup
    for key in ['habilidades', 'skills', 'competencias', 'competences']: # Added 'competencias' for robustness, ensure unique keys
        if key in skills_section:
            skills = skills_section[key]
            break
    
    for skill in skills:
        # Adjusted get_field calls to correctly find keys for different languages
        skill_name = get_field(skill, 'name', 'nome', ['nombre']) # Checks 'name', then 'nome', then 'nombre'
        skill_level_str = get_field(skill, 'level', 'nivel') # Checks 'level', then 'nivel'
        if skill_name and skill_level_str:
            try:
                skill_level = int(skill_level_str) # Convert to integer
                template.add_skill_bar(elements, skill_name, styles, skill_level)
            except ValueError:
                print(f"Aviso: Nível de habilidade inválido para '{skill_name}'. Esperado um número, recebido '{skill_level_str}'. Pulando esta habilidade.")
    
    elements.append(Spacer(1, 0.1*inch))

# Certificações - procurar por várias possíveis chaves
certifications_section = None
for key in ['certificacoes', 'certifications', 'certificaciones', 'certifications']:
    if key in secoes:
        certifications_section = secoes[key]
        break

if certifications_section:
    template.add_section_title(elements, get_section_title(certifications_section), styles)
    certifications = get_section_list(certifications_section)
    
    for cert in certifications:
        elements.append(Paragraph(f"🏅 {cert}", styles['normal']))
    
    elements.append(Spacer(1, 0.1*inch))

# Educação - procurar por várias possíveis chaves
education_section = None
for key in ['educacao', 'education', 'educacion', 'education']:
    if key in secoes:
        education_section = secoes[key]
        break

if education_section:
    template.add_section_title(elements, get_section_title(education_section), styles)
    
    # Obter lista de formações
    degrees = []
    for key in ['formacao', 'degrees', 'formacion', 'diplomes']:
        if key in education_section:
            degrees = education_section[key]
            break
    
    for degree in degrees:
        elements.append(Paragraph(degree, styles['normal']))
    
    elements.append(Spacer(1, 0.1*inch))

# Em Andamento - procurar por várias possíveis chaves
in_progress_section = None
for key in ['emAndamento', 'inProgress', 'enProgreso', 'enCours']:
    if key in secoes:
        in_progress_section = secoes[key]
        break

if in_progress_section:
    template.add_section_title(elements, get_section_title(in_progress_section), styles)
    
    # Obter lista de cursos
    courses = []
    for key in ['cursos', 'courses', 'cursos', 'cours']:
        if key in in_progress_section:
            courses = in_progress_section[key]
            break
    
    for course in courses:
        elements.append(Paragraph(course, styles['normal']))

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
            doc = template.create_document(alternative_filename)
            doc.build(elements)
            pdf_filename = alternative_filename
    else:
        # Se não existir, simplesmente criar o arquivo
        doc.build(elements)
        
    print(f"Arquivo PDF salvo como: {pdf_filename}")
    
except Exception as e:
    print(f"Erro ao gerar o PDF: {str(e)}")
    print("Tente fechar o arquivo PDF se ele estiver aberto em outro programa.")
