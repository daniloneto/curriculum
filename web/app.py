import os
import sys
import glob
import json
import subprocess
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from templates import TemplateManager

# Detectar se está em ambiente de produção (Render) ou local
def is_production():
    """Detecta se o aplicativo está rodando em ambiente de produção (Render)."""
    return os.environ.get('RENDER') == 'true' or os.environ.get('FLASK_ENV') == 'production'

app = Flask(__name__)

# Cache de arquivos temporários
file_cache = {}

# Função para listar idiomas disponíveis (adaptado do cv-generator.py)
def get_available_languages():
    # Procurar todos os arquivos JSON que seguem o padrão curriculo_XX.json na pasta raiz
    root_dir = os.path.dirname(os.path.dirname(__file__))
    json_files = glob.glob(os.path.join(root_dir, 'curriculo_*.json'))
    languages = {}
    
    print(f"Diretório raiz: {root_dir}")
    print(f"Arquivos JSON encontrados: {json_files}")
    
    for file in json_files:
        # Extrair o código do idioma do nome do arquivo (curriculo_XX.json -> XX)
        base_name = os.path.basename(file)
        lang_code = base_name.replace('curriculo_', '').replace('.json', '')
        
        print(f"Processando arquivo: {file}, código de idioma: {lang_code}")
        
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
                print(f"Idioma adicionado: {lang_code} -> {lang_name}")
        except Exception as e:
            # Se houver erro ao carregar ou analisar, pular este arquivo
            print(f"Erro ao carregar {file}: {str(e)}")
            pass
    
    # Se nenhum idioma foi encontrado, adicionar pelo menos o português como fallback
    if not languages:
        print("Nenhum idioma encontrado, adicionando fallbacks manuais...")
        languages = {
            'pt': {'name': 'Português', 'file': os.path.join(root_dir, 'curriculo_pt.json')},
            'en': {'name': 'English', 'file': os.path.join(root_dir, 'curriculo_en.json')},
            'es': {'name': 'Español', 'file': os.path.join(root_dir, 'curriculo_es.json')}
        }
    
    print(f"Lista final de idiomas: {languages}")
    return languages

# Obter templates disponíveis
def get_available_templates():
    # Lista fixa de templates disponíveis
    # Isso garante que os templates serão exibidos mesmo que a descoberta automática falhe
    default_templates = [
        'pdf',
        'docx',
        'pdf_moderno',
        'pdf_ats'
    ]
    
    # Tentar obter os templates usando o TemplateManager
    try:
        template_manager = TemplateManager()
        discovered_templates = template_manager.list_templates()
        
        # Se encontrou templates, usar eles
        if discovered_templates:
            print("Templates descobertos:", discovered_templates)
            return discovered_templates
    except Exception as e:
        print(f"Erro ao descobrir templates: {str(e)}")
    
    # Fallback para a lista fixa de templates
    print("Usando lista de templates padrão:", default_templates)
    return default_templates

@app.route('/')
def index():
    # Redirecionar para a página de edição
    return redirect(url_for('edit'))

@app.route('/schemas/<language>')
def get_schema(language):
    """Rota para servir os schemas JSON de validação."""
    # Caminho absoluto para o diretório de schemas
    schema_path = os.path.join(os.path.dirname(__file__), 'static', 'schemas', f'schema_{language}.json')
    
    print(f"Procurando schema em: {schema_path}")
    
    # Verificar se o diretório existe e criar se não existir
    schemas_dir = os.path.join(os.path.dirname(__file__), 'static', 'schemas')
    if not os.path.exists(schemas_dir):
        try:
            os.makedirs(schemas_dir)
            print(f"Criado diretório de schemas: {schemas_dir}")
        except Exception as e:
            print(f"Erro ao criar diretório de schemas: {str(e)}")
            return jsonify({'error': f'Erro ao criar diretório de schemas: {str(e)}'}), 500
    
    # Se o schema não existir, criar um básico
    if not os.path.exists(schema_path):
        print(f"Schema não encontrado, criando novo schema para {language}")
        
        # Criar um schema básico para o idioma
        basic_schema = create_basic_schema(language)
        
        # Salvar o schema básico
        try:
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(basic_schema, f, indent=2, ensure_ascii=False)
            print(f"Schema básico criado em: {schema_path}")
        except Exception as e:
            print(f"Erro ao criar schema básico: {str(e)}")
            return jsonify({'error': f'Erro ao criar schema para o idioma {language}: {str(e)}'}), 500
    else:
        print(f"Schema encontrado em: {schema_path}")
    
    # Ler o schema existente
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        print(f"Schema carregado com sucesso")
        return jsonify(schema)
    except Exception as e:
        print(f"Erro ao ler schema: {str(e)}")
        return jsonify({'error': f'Erro ao ler schema para o idioma {language}: {str(e)}'}), 500

def create_basic_schema(language):
    """Cria um schema básico de validação para um idioma."""
    # Estrutura básica do schema JSON para validação
    schema = {
        "type": "object",
        "required": ["languageName"],
        "properties": {
            "languageName": {"type": "string"},
            "name": {"type": "string"},
            "nome": {"type": "string"},
            "nombre": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "phone": {"type": "string"},
            "telefone": {"type": "string"},
            "teléfono": {"type": "string"},
            "linkedin": {"type": "string"},
            "outputFileName": {"type": "string"},
            "secoes": {
                "type": "object",
                "properties": {
                    "resumo": {
                        "type": "object",
                        "properties": {
                            "titulo": {"type": "string"},
                            "texto": {"type": "string"}
                        }
                    },
                    "experienciaProfissional": {
                        "type": "object",
                        "properties": {
                            "titulo": {"type": "string"},
                            "empregos": {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "educacao": {
                        "type": "object",
                        "properties": {
                            "titulo": {"type": "string"},
                            "formacao": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            },
            "sections": {
                "type": "object"
            }
        }
    }
    
    return schema

@app.route('/edit')
def edit():
    languages = get_available_languages()
    return render_template('edit.html', languages=languages)

@app.route('/generate')
def generate():
    languages = get_available_languages()
    templates = get_available_templates()
    
    # Organizar templates por tipo
    template_groups = {}
    for template_name in templates:
        parts = template_name.split('_', 1)
        format_type = parts[0]  # pdf, docx, etc
        
        if format_type not in template_groups:
            template_groups[format_type] = []
        
        # Somente adicionar o modificador ao grupo, não o formato completo
        if len(parts) > 1:
            modifier = parts[1]
            # Se for um formato especial como pdf_ats, tratá-lo como um grupo separado
            if format_type == 'pdf' and modifier == 'ats':
                if 'pdf_ats' not in template_groups:
                    template_groups['pdf_ats'] = []
                template_groups['pdf_ats'].append(modifier)
            else:
                template_groups[format_type].append(modifier)
    
    # Preparar nomes de exibição para os formatos
    format_display_names = {
        'pdf': 'PDF',
        'docx': 'Word (DOCX)',
        'pdf_ats': 'PDF otimizado para ATS'
    }
    
    return render_template('generate.html', 
                           languages=languages, 
                           template_groups=template_groups,
                           format_display_names=format_display_names)

@app.route('/create_json', methods=['POST'])
def create_json():
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados JSON não recebidos'}), 400
            
        language = data.get('language')
        
        if not language:
            return jsonify({'error': 'Idioma não especificado'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500
        
    # Verificar se o arquivo já existe
    root_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(root_dir, f'curriculo_{language}.json')
    
    if os.path.exists(file_path):
        return jsonify({'error': f'Arquivo para o idioma {language} já existe'}), 400
    
    # Criar um template básico para o novo arquivo
    template = {
        "languageName": "",
        "nome": "",
        "email": "",
        "telefone": "",
        "linkedin": "",
        "secoes": {
            "resumo": {
                "titulo": "",
                "texto": ""
            },
            "experienciaProfissional": {
                "titulo": "",
                "empregos": []
            },
            "educacao": {
                "titulo": "",
                "formacao": []
            },
            "habilidades": {
                "titulo": "",
                "categorias": []
            },
            "idiomas": {
                "titulo": "",
                "lista": []
            },
            "certificacoes": {
                "titulo": "",
                "lista": []
            }
        }
    }
    
    # Definir nomes específicos do idioma
    if language == "pt":
        template["languageName"] = "Português"
        template["secoes"]["resumo"]["titulo"] = "Resumo Profissional"
        template["secoes"]["experienciaProfissional"]["titulo"] = "Experiência Profissional"
        template["secoes"]["educacao"]["titulo"] = "Educação"
        template["secoes"]["habilidades"]["titulo"] = "Habilidades"
        template["secoes"]["idiomas"]["titulo"] = "Idiomas"
        template["secoes"]["certificacoes"]["titulo"] = "Certificações"
    elif language == "en":
        template["languageName"] = "English"
        template["secoes"]["resumo"]["titulo"] = "Professional Summary"
        template["secoes"]["experienciaProfissional"]["titulo"] = "Work Experience"
        template["secoes"]["educacao"]["titulo"] = "Education"
        template["secoes"]["habilidades"]["titulo"] = "Skills"
        template["secoes"]["idiomas"]["titulo"] = "Languages"
        template["secoes"]["certificacoes"]["titulo"] = "Certifications"
    elif language == "es":
        template["languageName"] = "Español"
        template["secoes"]["resumo"]["titulo"] = "Resumen Profesional"
        template["secoes"]["experienciaProfissional"]["titulo"] = "Experiencia Profesional"
        template["secoes"]["educacao"]["titulo"] = "Educación"
        template["secoes"]["habilidades"]["titulo"] = "Habilidades"
        template["secoes"]["idiomas"]["titulo"] = "Idiomas"
        template["secoes"]["certificacoes"]["titulo"] = "Certificaciones"
    
    # Salvar o template no arquivo
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': f'Arquivo JSON para {template["languageName"]} criado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao criar arquivo: {str(e)}'}), 500

@app.route('/get_json_content', methods=['POST'])
def get_json_content():
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados JSON não recebidos'}), 400
            
        language = data.get('language')
        
        if not language:
            return jsonify({'error': 'Idioma não especificado'}), 400
        
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'curriculo_{language}.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return jsonify({'content': content})
        except FileNotFoundError:
            return jsonify({'error': f'Arquivo para o idioma {language} não encontrado'}), 404
        except Exception as e:
            return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500

@app.route('/save_json', methods=['POST'])
def save_json():
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados JSON não recebidos'}), 400
            
        language = data.get('language')
        content = data.get('content')
        
        if not language or not content:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'curriculo_{language}.json')
        
        try:
            # Verificar se o conteúdo é JSON válido
            parsed_content = json.loads(content) if isinstance(content, str) else content
            
            # Salvar o arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                    
            return jsonify({'success': True, 'message': 'Arquivo salvo com sucesso!'})
        except json.JSONDecodeError:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            return jsonify({'error': f'Erro ao salvar arquivo: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Dados JSON não recebidos'}), 400
            
        language = data.get('language')
        format_type = data.get('format')
        template = data.get('template', None)
        
        if not language or not format_type:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        try:
            # Determinar qual script usar com base no formato escolhido
            root_dir = os.path.dirname(os.path.dirname(__file__))
            print(f"Diretório raiz: {root_dir}")
            
            if format_type == 'pdf_ats':
                script = os.path.join(root_dir, 'curriculo_pdf_ats.py')
            elif format_type.startswith('pdf'):
                script = os.path.join(root_dir, 'curriculo_pdf.py')
            else:  # docx e outros
                script = os.path.join(root_dir, 'curriculo_docx.py')
                
            print(f"Script selecionado: {script}")
            
            # Preparar os argumentos
            cmd = [sys.executable, script, language]
            
            # Se um template específico foi selecionado, adicioná-lo aos argumentos
            if template and template != format_type:
                if '_' in template:
                    # O nome do template já inclui o formato, usar como está
                    cmd.extend(['--template', template])
                else:
                    # Adicionar o formato como prefixo
                    cmd.extend(['--template', f"{format_type}_{template}"])
            elif format_type and '_' in format_type:
                # Se o formato já é um template composto (como pdf_ats), passá-lo como template
                cmd.extend(['--template', format_type])
                
            print(f"Comando: {' '.join(cmd)}")
            
            # Executar o script Python
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Erro ao gerar currículo: {result.stderr}")
                return jsonify({'error': result.stderr}), 500
                
            # Localizar o arquivo gerado
            output_dir = os.path.join(root_dir)
            
            # Procurar o arquivo gerado (suponha que termina com o código do idioma e a extensão apropriada)
            file_extension = '.pdf' if format_type.startswith('pdf') else '.docx'
              # Ler a saída para encontrar o nome do arquivo gerado
            output = result.stdout
            filename = None
            
            for line in output.splitlines():
                if 'Arquivo gerado:' in line:
                    filename = line.split('Arquivo gerado:')[-1].strip()
                    break
                    
            if not filename:
                # Tentar encontrar qualquer arquivo recém-criado
                files = glob.glob(os.path.join(output_dir, f"*{file_extension}"))
                if files:
                    # Ordenar por data de modificação e pegar o mais recente
                    filename = sorted(files, key=os.path.getmtime)[-1]
                    filename = os.path.basename(filename)
            
            if not filename:
                return jsonify({'error': 'Não foi possível encontrar o arquivo gerado'}), 500
                
            print(f"Arquivo gerado: {filename}")
            file_path = os.path.join(root_dir, filename)
            
            # Verificar se o arquivo realmente existe
            if not os.path.exists(file_path):
                print(f"ERRO: Arquivo gerado não encontrado: {file_path}")
                return jsonify({'error': 'Arquivo gerado não encontrado no servidor'}), 500
                
            # Comportamento diferente baseado no ambiente
            if is_production():
                # Em produção (Render), usar sistema temporário
                import uuid
                file_id = str(uuid.uuid4())
                  # Armazenar o caminho completo no cache global
                global file_cache
                file_cache[file_id] = file_path
                
                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'file_id': file_id,
                    'download_url': url_for('download_file', file_id=file_id)
                })
            else:
                # Em ambiente local, usar sistema de arquivos normal
                # Garantir que a URL tenha o nome do arquivo correto
                download_url = url_for('download_file_local', filename=filename)
                print(f"URL de download local gerada: {download_url}")
                print(f"Caminho completo do arquivo: {file_path}")
                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'download_url': download_url,
                    'file_path': file_path  # Adicionar o caminho completo para depuração
                })
            
        except Exception as e:
            print(f"Erro ao gerar currículo: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    """Download de um arquivo usando file_id temporário (para ambiente de produção)."""
    # Verificar se o ID do arquivo existe no cache
    global file_cache
    if file_id not in file_cache:
        return jsonify({'error': 'Arquivo não encontrado ou expirado'}), 404
        
    file_path = file_cache[file_id]
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Arquivo não encontrado no servidor'}), 404
    
    # Determinar o tipo MIME com base na extensão
    filename = os.path.basename(file_path)
    mimetype = 'application/pdf' if filename.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    # Ler o conteúdo do arquivo
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Usar serve_temporary_file para enviar o arquivo
    return serve_temporary_file(content, filename, mimetype)

@app.route('/download_local/<filename>')
def download_file_local(filename):
    """Download de um arquivo usando o sistema de arquivos local."""
    root_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(root_dir, filename)
    
    print(f"Tentando baixar o arquivo: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"ERRO: Arquivo não encontrado: {file_path}")
        return jsonify({'error': 'Arquivo não encontrado no servidor'}), 404
    
    try:
        # Determinar o tipo MIME com base na extensão
        mimetype = 'application/pdf' if filename.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Usar o método mais robusto para enviar o arquivo
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        print(f"ERRO ao enviar arquivo: {str(e)}")
        return jsonify({'error': f'Erro ao baixar arquivo: {str(e)}'}), 500

# Adicionar função para servir arquivos temporários

def serve_temporary_file(content, filename, mimetype):
    """Serve um arquivo gerado sem salvá-lo permanentemente no servidor."""
    from io import BytesIO
    from flask import send_file
    
    print(f"Servindo arquivo temporário: {filename} ({len(content)} bytes)")
    print(f"Tipo MIME: {mimetype}")
    
    buffer = BytesIO()
    buffer.write(content)
    buffer.seek(0)
    
    try:
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,  # 'download_name' em versões recentes do Flask
            mimetype=mimetype
        )
    except Exception as e:
        print(f"ERRO ao servir arquivo temporário: {str(e)}")
        return jsonify({'error': f'Erro ao servir arquivo temporário: {str(e)}'}), 500

@app.route('/debug/file_exists/<filename>')
def debug_file_exists(filename):
    """Rota de depuração para verificar se um arquivo existe."""
    root_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(root_dir, filename)
    
    if os.path.exists(file_path):
        file_info = {
            'exists': True,
            'path': file_path,
            'size': os.path.getsize(file_path),
            'modified': os.path.getmtime(file_path),
            'is_file': os.path.isfile(file_path)
        }
        return jsonify(file_info)
    else:
        return jsonify({
            'exists': False,
            'path': file_path,
            'message': 'Arquivo não encontrado'
        }), 404

if __name__ == '__main__':
    # Desenvolvimento local
    app.run(debug=True)
else:
    # Em produção, debug deve ser False
    app.config['DEBUG'] = False
