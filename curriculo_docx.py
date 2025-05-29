"""
Main command-line interface (CLI) script for generating CVs in DOCX format.

This script parses command-line arguments to determine the language,
CV data source (either a language code to find a `curriculo_<lang>.json` file
or a direct path to a JSON file), and the template to use for generation.
It utilizes `DataLoader` to load and structure the CV data, `TemplateManager`
to load the specified DOCX template module, and `DocxGenerator` to perform
the actual CV generation.
"""
import sys
import argparse
import os

# Ensure project root is in sys.path to allow importing project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from templates import TemplateManager
from data_loader import DataLoader
from cv_generators.docx_generator import DocxGenerator


def main():
    """
    Parses arguments, loads data and template, and generates the DOCX CV.
    """
    parser = argparse.ArgumentParser(description='Gerar currículo em formato DOCX.')
    parser.add_argument(
        'language',
        nargs='?',
        default=None,
        help=('Código do idioma (ex: pt, en, es). '
              'Se não fornecido e --json-file não for usado, tenta "pt".')
    )
    parser.add_argument(
        '--template', '-t',
        help='Nome do template a ser usado (ex: docx, docx_moderno).',
        default='docx'
    )
    parser.add_argument(
        '--json-file',
        help='Caminho para um arquivo JSON de dados do currículo personalizado.',
        default=None
    )
    args = parser.parse_args()

    selected_lang_code = args.language
    if not selected_lang_code and not args.json_file:
        print("Nenhum idioma ou arquivo JSON especificado. Tentando 'pt' como padrão.")
        selected_lang_code = 'pt'
    elif not selected_lang_code and args.json_file:
        # Use a placeholder if only a JSON file is provided.
        # DataLoader primarily uses json_file_path if available.
        print(f"Arquivo JSON especificado ({args.json_file}) sem código de idioma explícito. "
              "Usando 'custom' como placeholder para o código de idioma.")
        selected_lang_code = 'custom'

    # Load data using DataLoader
    # The root_dir for DataLoader is assumed to be the current directory ('.')
    # as CLI scripts are typically run from the project root.
    try:
        if not selected_lang_code and not args.json_file: # Should be caught by above logic
             print("Erro: É necessário especificar um idioma ou um arquivo JSON.")
             sys.exit(1)

        data_loader = DataLoader(
            language_code=selected_lang_code,
            json_file_path=args.json_file,
            root_dir='.'
        )
    except FileNotFoundError as e:
        print(f"Erro ao carregar dados: {e}")
        if not args.json_file: # Suggest available languages if not using a specific file
            try:
                # utils.py should be in the same directory or Python path
                from utils import get_available_languages
                # Assuming get_available_languages searches from '.' (project root)
                available = get_available_languages(root_dir='.')
                print("Idiomas disponíveis:", list(available.keys()))
            except Exception as lang_e:
                print(f"Não foi possível listar os idiomas disponíveis: {lang_e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado ao inicializar DataLoader: {type(e).__name__} - {e}")
        sys.exit(1)

    # Load the template module
    # TemplateManager root_dir should also be project root for consistency.
    template_manager = TemplateManager(root_dir='.')
    template_module_name = args.template

    try:
        loaded_template_module = template_manager.get_template(template_module_name)
        print(f"Usando template: {template_module_name}")
    except ValueError as e:
        print(f"Erro ao carregar template '{template_module_name}': {e}")
        print(f"Templates disponíveis: {', '.join(template_manager.list_templates())}")
        # Fallback to default 'docx' template if the selected one fails
        if template_module_name != 'docx':
            print("Tentando usar o template padrão 'docx'.")
            try:
                loaded_template_module = template_manager.get_template('docx')
                template_module_name = 'docx' # Update actual template name
            except ValueError as e_default:
                print(f"Erro ao carregar template padrão 'docx': {e_default}. Saindo.")
                sys.exit(1)
        else: # If default 'docx' itself failed
            sys.exit(1)

    # Instantiate and use the DocxGenerator
    try:
        generator = DocxGenerator(
            data_loader=data_loader,
            template_module=loaded_template_module
        )
        output_filepath = generator.generate_cv()
        # The output_filepath is now an absolute path to the generated_cvs directory
        print(f"Arquivo gerado: {output_filepath}")
    except Exception as e:
        print(f"Erro durante a geração do DOCX: {type(e).__name__} - {e}")
        # For more detailed debugging, you might want to print the traceback
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
