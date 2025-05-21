import os
import sys
import glob
import json
import subprocess

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
    
    # Exibir opções
    print("\nIdiomas disponíveis:")
    for i, (code, lang) in enumerate(languages.items(), 1):
        print(f"{i}. {lang['name']} ({code})")
    
    print("\nFormatos disponíveis:")
    print("a. PDF")
    print("b. DOCX")
    
    # Obter escolha do usuário
    try:
        lang_choice = int(input("\nEscolha o número do idioma: "))
        if lang_choice < 1 or lang_choice > len(languages):
            print("Escolha inválida.")
            return None
        
        format_choice = input("Escolha o formato (a/b): ").lower()
        if format_choice not in ['a', 'b']:
            print("Formato inválido.")
            return None
        
        # Obter código do idioma escolhido
        lang_code = list(languages.keys())[lang_choice - 1]
        
        return {
            'language': lang_code,
            'format': 'pdf' if format_choice == 'a' else 'docx'
        }
        
    except ValueError:
        print("Entrada inválida. Digite um número.")
        return None

def gerar_curriculo(opcoes):
    if opcoes['format'] == 'pdf':
        script = 'curriculo_pdf.py'
    else:
        script = 'curriculo_docx.py'
    
    # Executar o script com o idioma escolhido
    cmd = [sys.executable, script, opcoes['language']]
    
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
