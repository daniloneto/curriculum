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
import re

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

# Função para extrair palavras-chave do resumo profissional
def extract_keywords_from_resume(resume_text, min_length=4):
    # Remover pontuação e converter para minúsculas
    cleaned_text = re.sub(r'[^\w\s]', ' ', resume_text.lower())
    
    # Dividir em palavras
    words = cleaned_text.split()
    
    # Filtrar palavras curtas e palavras comuns (stopwords em português)
    stopwords = ["de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com", 
                "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", 
                "mas", "foi", "ao", "ele", "das", "tem", "seu", "sua", "ou", "ser", "quando",
                "muito", "nos", "já", "está", "eu", "também", "só", "pelo", "pela", "até",
                "isso", "ela", "entre", "era", "depois", "sem", "mesmo", "aos", "ter", "seus",
                "quem", "nas", "me", "esse", "eles", "estão", "você", "tinha", "foram", "essa",
                "num", "nem", "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas",
                "havia", "seja", "qual", "será", "nós", "tenho", "lhe", "deles", "essas",
                "esses", "pelas", "este", "fosse", "dele", "tu", "te", "vocês", "vos", "lhes",
                "meus", "minhas", "teu", "tua", "teus", "tuas", "nosso", "nossa", "nossos",
                "nossas", "dela", "delas", "esta", "estes", "estas", "aquele", "aquela",
                "aqueles", "aquelas", "isto", "aquilo", "estou", "está", "estamos", "estão",
                "estive", "esteve", "estivemos", "estiveram", "estava", "estávamos", "estavam",
                "estivera", "estivéramos", "esteja", "estejamos", "estejam", "estivesse",
                "estivéssemos", "estivessem", "estiver", "estivermos", "estiverem", "hei",
                "há", "havemos", "hão", "houve", "houvemos", "houveram", "houvera",
                "houvéramos", "haja", "hajamos", "hajam", "houvesse", "houvéssemos",
                "houvessem", "houver", "houvermos", "houverem", "houverei", "houverá",
                "houveremos", "houverão", "houveria", "houveríamos", "houveriam", "sou",
                "somos", "são", "era", "éramos", "eram", "fui", "foi", "fomos", "foram",
                "fora", "fôramos", "seja", "sejamos", "sejam", "fosse", "fôssemos", "fossem",
                "for", "formos", "forem", "serei", "será", "seremos", "serão", "seria",
                "seríamos", "seriam", "tenho", "tem", "temos", "tém", "tinha", "tínhamos",
                "tinham", "tive", "teve", "tivemos", "tiveram", "tivera", "tivéramos", "tenha",
                "tenhamos", "tenham", "tivesse", "tivéssemos", "tivessem", "tiver", "tivermos",
                "tiverem", "terei", "terá", "teremos", "terão", "teria", "teríamos", "teriam"]
    
    filtered_words = [word for word in words if len(word) >= min_length and word not in stopwords]
    
    # Contar frequência das palavras
    word_freq = {}
    for word in filtered_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Ordenar por frequência e retornar as top palavras
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, freq in sorted_words[:20]]
    
    return top_words

# Configurar os argumentos de linha de comando
parser = argparse.ArgumentParser(description='Gerar currículo em formato PDF otimizado para ATS.')
parser.add_argument('language', nargs='?', help='Código do idioma (ex: pt, en, es)')
parser.add_argument('--template', '-t', help='Nome do template a ser usado', default='pdf_ats')
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
if not selected_lang:
    print("Erro: Não foram encontrados arquivos de idioma válidos.")
    sys.exit(1)

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
    print("Usando o template padrão 'pdf_ats'.")
    template = template_manager.get_template('pdf_ats')

# Obter nome do arquivo para saída PDF
output_filename = get_field(data, 'nomeArquivoSaida', 'outputFileName')
if not output_filename:    # Se nenhum nome de arquivo for especificado, criar um a partir do nome e idioma
    if nome:
        output_filename = f"Curriculo_ATS_{nome.replace(' ', '_')}_{selected_lang}.pdf"
    else:
        output_filename = f"Curriculo_ATS_{selected_lang}.pdf"
else:
    # Adicionar sufixo ATS ao nome do arquivo e garantir extensão .pdf
    base_name, ext = os.path.splitext(output_filename)
    output_filename = f"{base_name}_ATS.pdf"

# Criar documento PDF
doc = template.create_document(output_filename)

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

# Extrair palavras-chave do resumo profissional para uso posterior
keywords = []
if resume_section:
    resume_text = get_section_content(resume_section)
    if resume_text:
        keywords = extract_keywords_from_resume(resume_text)
    
    template.add_section_title(elements, get_section_title(resume_section), styles)
    elements.append(Paragraph(resume_text, styles['normal']))
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
    
    # Adicionar empregos no formato otimizado para ATS
    for job in jobs:
        position = get_field(job, 'cargo', 'position')
        company = ""  # Na estrutura atual não há empresa separada do cargo
        period = get_field(job, 'periodo', 'period')
        
        # Obter descrição - procurar por várias possíveis chaves
        description_items = []
        for key in ['descricao', 'description', 'descripcion']:
            if key in job:
                description_items = job[key]
                break
        
        # Usar a função especializada do template ATS
        if hasattr(template, 'add_job_experience'):
            template.add_job_experience(elements, position, company, period, description_items, styles)
        else:
            # Fallback caso o template não tenha a função especializada
            if position:
                elements.append(Paragraph(f"<b>{position}</b>", styles['bullet']))
            
            if period:
                elements.append(Paragraph(period, styles['normal']))
            
            for item in description_items:
                elements.append(Paragraph(f"- {item}", styles['bullet']))
                
            elements.append(Spacer(1, 0.1*inch))

# Adicionar palavras-chave extraídas para melhorar a compatibilidade ATS
if keywords and hasattr(template, 'add_keywords_section'):
    # Adicionar palavras-chave do resumo e habilidades técnicas
    skills_section = None
    for key in ['habilidadesTecnicas', 'technicalSkills', 'habilidadesTecnicas', 'competencesTechniques']:
        if key in secoes:
            skills_section = secoes[key]
            break
    
    if skills_section:
        # Obter lista de habilidades
        skills = []
        for key in ['habilidades', 'skills', 'habilidades', 'competences']:
            if key in skills_section:
                skills = skills_section[key]
                break
        
        # Adicionar nomes das habilidades à lista de palavras-chave
        for skill in skills:
            skill_name = get_field(skill, 'nome', 'name')
            if skill_name:
                keywords.append(skill_name)
    
    # Remover duplicatas e ordenar
    keywords = list(set(keywords))
    keywords.sort()
    

# Adicionar quebra de página antes das habilidades técnicas
template.add_page_break(elements)

# Habilidades Técnicas - procurar por várias possíveis chaves
skills_section = None
for key in ['habilidadesTecnicas', 'technicalSkills', 'habilidadesTecnicas', 'competencesTechniques']:
    if key in secoes:
        skills_section = secoes[key]
        break

if skills_section:
    template.add_section_title(elements, get_section_title(skills_section), styles)
    
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
            # Use add_skill para o template ATS, que será redirecionado para add_skill_bar na interface comum
            if hasattr(template, 'add_skill'):
                template.add_skill(elements, skill_name, styles, skill_level)
            else:
                template.add_skill_bar(elements, skill_name, styles, skill_level)
    
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
        # Usar texto simples para certificações (sem emojis) para melhor compatibilidade ATS
        elements.append(Paragraph(cert, styles['normal']))
    
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

template.add_keywords_section(elements, keywords, styles)

# Gerar o PDF
try:   
    if os.path.exists(output_filename):
        try:
            # Tentar renomear temporariamente o arquivo existente
            temp_name = output_filename + ".old"
            if os.path.exists(temp_name):
                os.remove(temp_name)
            os.rename(output_filename, temp_name)
            
        # Gerar o novo PDF
            doc.build(elements)
            
            # Se deu certo, remover o arquivo antigo
            if os.path.exists(temp_name):
                os.remove(temp_name)
                
        except Exception as e:
            # Se falhar em renomear, tentar outro nome de arquivo
            alternative_filename = os.path.splitext(output_filename)[0] + "_new.pdf"
            doc = template.create_document(alternative_filename)
            doc.build(elements)
            output_filename = alternative_filename
    else:
        # Se não existir, simplesmente criar o arquivo
        doc.build(elements)
        
    print(f"Arquivo PDF otimizado para ATS salvo como: {output_filename}")
    print("\nDicas para aumentar a compatibilidade com ATS:")
    print("1. Use termos-chave específicos da sua área em seu resumo profissional")
    print("2. Liste habilidades técnicas relevantes para a vaga desejada")
    print("3. Mantenha um formato limpo e direto, evitando tabelas complexas")
    print("4. Certifique-se de incluir datas completas nas experiências (mm/aaaa - mm/aaaa)")
    
except Exception as e:
    print(f"Erro ao gerar o PDF: {str(e)}")
    print("Tente fechar o arquivo PDF se ele estiver aberto em outro programa.")
