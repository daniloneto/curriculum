"""
Main command-line interface (CLI) script for the CV Generator.

This script provides an interactive menu for users to choose the language,
format (DOCX, PDF, ATS-optimized PDF), and template for their CV.
It then calls the appropriate generation script (`curriculo_docx.py`,
`curriculo_pdf.py`, or `curriculo_pdf_ats.py`) to create the CV.
"""
import os
import sys
import json
import subprocess
from typing import Dict, Optional, List, Any

# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from templates import TemplateManager
from utils import get_available_languages


def display_menu() -> Optional[Dict[str, str]]:
    """
    Displays an interactive menu for the user to select CV options.

    Presents options for language, output format (PDF, DOCX, ATS PDF),
    and template (if multiple are available for the chosen format).

    Returns:
        Optional[Dict[str, str]]: A dictionary containing the user's choices:
                                  - 'language' (str): Selected language code (e.g., 'pt').
                                  - 'format' (str): Selected format (e.g., 'pdf', 'docx', 'pdf_ats').
                                  - 'template' (Optional[str]): Selected template name if applicable.
                                  Returns None if the user makes an invalid choice or
                                  if no language files are found.
    """
    print("\n== GERADOR DE CURRÍCULO MULTILÍNGUE ==")

    # Assumes get_available_languages searches from the current directory (project root)
    languages = get_available_languages(root_dir='.')

    if not languages:
        print("Nenhum arquivo de idioma (curriculo_XX.json) encontrado na pasta raiz.")
        return None

    # TemplateManager also assumes it's being run from project root context
    # or paths are relative to project root.
    template_manager = TemplateManager(root_dir='.')
    all_templates = template_manager.list_templates()

    print("\nIdiomas disponíveis:")
    lang_map = list(languages.items()) # For indexed selection
    for i, (code, lang_details) in enumerate(lang_map, 1):
        print(f"{i}. {lang_details['name']} ({code})")

    print("\nFormatos disponíveis:")
    print("a. PDF")
    print("b. DOCX")
    print("c. PDF otimizado para ATS (Applicant Tracking Systems)")

    try:
        lang_choice_idx = int(input("\nEscolha o número do idioma: "))
        if not 1 <= lang_choice_idx <= len(lang_map):
            print("Escolha de idioma inválida.")
            return None
        selected_lang_code = lang_map[lang_choice_idx - 1][0]

        format_key = input("Escolha o formato (a/b/c): ").lower()
        if format_key not in ['a', 'b', 'c']:
            print("Formato inválido.")
            return None

        chosen_format_type: str
        if format_key == 'a': # PDF
            chosen_format_type = 'pdf'
            ats_choice = input("Deseja otimizar o PDF para sistemas ATS? (s/n): ").lower()
            if ats_choice == 's':
                return {'language': selected_lang_code, 'format': 'pdf_ats'}
        elif format_key == 'b': # DOCX
            chosen_format_type = 'docx'
        elif format_key == 'c': # ATS PDF directly
            return {'language': selected_lang_code, 'format': 'pdf_ats'}
        else: # Should be caught by previous check, but as safeguard
            print("Seleção de formato desconhecida.")
            return None


        # Template selection for chosen_format_type (pdf or docx)
        # Filter available templates: e.g., for 'pdf', find 'pdf', 'pdf_moderno', etc.
        # Exclude 'pdf_ats' here as it's a distinct format choice.
        relevant_templates = [
            t for t in all_templates
            if t.startswith(chosen_format_type) and t != 'pdf_ats'
        ]

        if not relevant_templates:
            # If no specific templates like 'pdf_moderno', but base 'pdf' template exists.
            if chosen_format_type in all_templates:
                 return {'language': selected_lang_code, 'format': chosen_format_type, 'template': chosen_format_type}
            print(f"Nenhum template encontrado para o formato {chosen_format_type}.")
            return {'language': selected_lang_code, 'format': chosen_format_type}


        if len(relevant_templates) == 1:
            return {
                'language': selected_lang_code,
                'format': chosen_format_type,
                'template': relevant_templates[0]
            }

        print(f"\nTemplates disponíveis para {chosen_format_type.upper()}:")
        template_map: List[str] = []
        for i, template_name in enumerate(relevant_templates, 1):
            display_name = template_name
            # If template is 'pdf' and chosen_format_type is 'pdf', it's the base/default
            if template_name == chosen_format_type:
                display_name = f"Padrão ({template_name})"
            # If template is 'pdf_moderno' for chosen_format_type 'pdf'
            elif template_name.startswith(f"{chosen_format_type}_"):
                style_name = template_name.replace(f"{chosen_format_type}_", "")
                display_name = style_name.capitalize()
            template_map.append(template_name)
            print(f"{i}. {display_name}")

        template_choice_idx = int(input("\nEscolha o número do template: "))
        if not 1 <= template_choice_idx <= len(template_map):
            print("Escolha de template inválida.")
            return None
        selected_template_name = template_map[template_choice_idx - 1]

        return {
            'language': selected_lang_code,
            'format': chosen_format_type, # This is base format like 'pdf' or 'docx'
            'template': selected_template_name # This is full template name like 'pdf_moderno'
        }

    except ValueError:
        print("Entrada inválida. Por favor, digite um número para as opções.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado no menu: {e}")
        return None


def generate_cv(options: Dict[str, str]) -> None:
    """
    Calls the appropriate CV generation script based on user options.

    Args:
        options (Dict[str, str]): A dictionary containing 'language', 'format',
                                  and optionally 'template'.
    """
    script_name: str
    if options['format'] == 'pdf_ats':
        script_name = 'curriculo_pdf_ats.py'
    elif options['format'] == 'pdf':
        script_name = 'curriculo_pdf.py'
    elif options['format'] == 'docx':
        script_name = 'curriculo_docx.py'
    else:
        print(f"Formato desconhecido: {options['format']}")
        return

    # Command to execute: python <script_name> <language_code> [--template <template_name>]
    cmd = [sys.executable, script_name, options['language']]
    if 'template' in options and options['template']:
        cmd.extend(['--template', options['template']])

    print(f"\nExecutando comando: {' '.join(cmd)}")
    try:
        # Ensure that the scripts are found in the current directory
        # Or use absolute paths if they are located elsewhere.
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        print("\n--- Saída do Script ---")
        print(result.stdout)
        if result.stderr:
            print("--- Erros do Script ---")
            print(result.stderr)
        print("-----------------------")

        if result.returncode == 0:
            print(f"Currículo gerado com sucesso usando {script_name}.")
        else:
            print(f"Falha ao gerar currículo com {script_name}.")

    except FileNotFoundError:
        print(f"Erro: O script {script_name} não foi encontrado. "
              "Verifique se ele está no diretório correto.")
    except Exception as e:
        print(f"Erro ao executar o script {script_name}: {e}")


def main_flow():
    """
    Main execution flow for the CV generator CLI.
    Displays menu and triggers CV generation.
    """
    user_options = display_menu()
    if user_options:
        generate_cv(user_options)
    else:
        print("Nenhuma opção válida selecionada. Saindo.")


if __name__ == "__main__":
    # Ensure the script is run from the project root for correct path resolution
    # for language files and templates.
    # Alternatively, make all paths within the project absolute.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    if os.getcwd() != project_root:
        # This check might be too restrictive if script is called from elsewhere
        # but utils.py and TemplateManager now use root_dir='.' which implies
        # they expect to be run from where they are, or paths are relative to it.
        # For CLI, running from project root is a common assumption.
        # print(f"Aviso: O script está sendo executado de {os.getcwd()}, "
        #       f"mas o ideal é executá-lo da raiz do projeto: {project_root}")
        pass # Allowing execution from other dirs, assuming paths are handled.

    main_flow()
