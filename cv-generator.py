import os
import sys
import glob
import json
import subprocess
from templates import TemplateManager

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
        except Exception as e:
            # Se houver erro ao carregar ou analisar, pular este arquivo
            print(f"Erro ao carregar {file}: {str(e)}")
            pass
    
    return languages

def exibir_menu():
    print("\n== GERADOR DE CURRÍCULO MULTILÍNGUE ==")
    
    # Obter idiomas disponíveis
    languages = get_available_languages()
    
    if not languages:
        print("Nenhum arquivo de idioma encontrado. Verifique se existem arquivos curriculo_XX.json na pasta.")
        return None
    
    # Obter templates disponíveis
    template_manager = TemplateManager()
    templates = template_manager.list_templates()
    
    # Exibir opções
    print("\nIdiomas disponíveis:")
    for i, (code, lang) in enumerate(languages.items(), 1):
        print(f"{i}. {lang['name']} ({code})")

    print("\nFormatos disponíveis:")
    print("a. PDF")
    print("b. DOCX")
    print("c. PDF otimizado para ATS (Applicant Tracking Systems)")
    
    # Obter escolha do usuário
    try:
        lang_choice = int(input("\nEscolha o número do idioma: "))
        if lang_choice < 1 or lang_choice > len(languages):
            print("Escolha inválida.")
            return None
        
        format_choice = input("Escolha o formato (a/b/c): ").lower()
        if format_choice not in ['a', 'b', 'c']:
            print("Formato inválido.")
            return None
            
        # Obter código do idioma escolhido
        lang_code = list(languages.keys())[lang_choice - 1]
        
        # Escolher formato
        if format_choice == 'a':
            chosen_format = 'pdf'
            
            # Perguntar se quer otimizar para ATS
            ats_choice = input("Deseja otimizar o PDF para sistemas ATS? (s/n): ").lower()
            if ats_choice == 's':
                # Para o formato ATS, usar diretamente o script dedicado
                return {
                    'language': lang_code,
                    'format': 'pdf_ats'
                }
        elif format_choice == 'b':
            chosen_format = 'docx'
        elif format_choice == 'c':
            # Para o formato ATS, usar diretamente o script dedicado
            return {
                'language': lang_code,
                'format': 'pdf_ats'
            }
        
        # Escolher template (caso exista mais de um para o formato selecionado)
        available_templates = [t for t in templates if t.startswith(chosen_format)]
        
        # Se não houver templates disponíveis para o formato, usar o padrão
        if not available_templates:
            return {
                'language': lang_code,
                'format': chosen_format
            }
        
        # Se houver apenas um template, usá-lo como padrão
        if len(available_templates) == 1:
            return {
                'language': lang_code,
                'format': chosen_format,
                'template': available_templates[0]
            }
        
        # Se houver múltiplos templates, permitir escolha
        print("\nTemplates disponíveis:")
        for i, template in enumerate(available_templates, 1):
            # Formatar nome do template para exibição
            display_name = template
            if template == chosen_format:
                display_name = f"Padrão ({template})"
            elif template.startswith(f"{chosen_format}_"):
                # Remover prefixo (ex: pdf_moderno -> Moderno)
                style_name = template.replace(f"{chosen_format}_", "")
                display_name = style_name.capitalize()
            
            print(f"{i}. {display_name}")
        
        template_choice = int(input("\nEscolha o número do template: "))
        if template_choice < 1 or template_choice > len(available_templates):
            print("Escolha de template inválida.")
            return None
        
        return {
            'language': lang_code,
            'format': chosen_format,
            'template': available_templates[template_choice - 1]
        }
        
    except ValueError:
        print("Entrada inválida. Digite um número.")
        return None

def gerar_curriculo(opcoes):
    if opcoes['format'] == 'pdf_ats':
        script = 'curriculo_pdf_ats.py'
    elif opcoes['format'] == 'pdf':
        script = 'curriculo_pdf.py'
    else:
        script = 'curriculo_docx.py'
    
    # Executar o script com o idioma escolhido
    cmd = [sys.executable, script, opcoes['language']]
    
    # Se houver template especificado, passar como argumento adicional
    if 'template' in opcoes:
        cmd.append('--template')
        cmd.append(opcoes['template'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Erros:", result.stderr)
    except Exception as e:
        print(f"Erro ao executar o script: {str(e)}")

def main():
    opcoes = exibir_menu()
    if opcoes:
        gerar_curriculo(opcoes)

if __name__ == "__main__":
    main()
