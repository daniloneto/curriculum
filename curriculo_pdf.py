"""
Main command-line interface (CLI) script for generating CVs in PDF format.

This script parses command-line arguments to determine the language,
CV data source (either a language code for a `curriculo_<lang>.json` file
or a direct path to a JSON file), and the template for PDF generation.
It uses `DataLoader` to load CV data, `TemplateManager` to load the
specified PDF template module, and `PdfGenerator` for CV creation.
"""
import sys
import argparse
import os

# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from templates import TemplateManager
from data_loader import DataLoader
from cv_generators.pdf_generator import PdfGenerator


def main():
    """
    Parses CLI arguments, loads data and template, then generates the PDF CV.
    """
    parser = argparse.ArgumentParser(description='Gerar currículo em formato PDF.')
    parser.add_argument(
        'language',
        nargs='?',
        default=None,
        help=('Código do idioma (ex: pt, en, es). '
              'Se não fornecido e --json-file não for usado, tenta "pt".')
    )
    parser.add_argument(
        '--template', '-t',
        help='Nome do template PDF a ser usado (ex: pdf, pdf_moderno).',
        default='pdf'
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
        print(f"Arquivo JSON especificado ({args.json_file}) sem código de idioma explícito. "
              "Usando 'custom' como placeholder para o código de idioma.")
        selected_lang_code = 'custom'

    # Load data using DataLoader
    try:
        if not selected_lang_code and not args.json_file:
             print("Erro: É necessário especificar um idioma ou um arquivo JSON.")
             sys.exit(1)

        data_loader = DataLoader(
            language_code=selected_lang_code,
            json_file_path=args.json_file,
            root_dir='.'  # Assumes script is run from project root
        )
    except FileNotFoundError as e:
        print(f"Erro ao carregar dados: {e}")
        if not args.json_file:
            try:
                from utils import get_available_languages
                available = get_available_languages(root_dir='.')
                print("Idiomas disponíveis:", list(available.keys()))
            except Exception as lang_e:
                print(f"Não foi possível listar os idiomas disponíveis: {lang_e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado ao inicializar DataLoader: {type(e).__name__} - {e}")
        sys.exit(1)

    # Load the template module
    template_manager = TemplateManager(root_dir='.')
    template_module_name = args.template

    try:
        loaded_template_module = template_manager.get_template(template_module_name)
        print(f"Usando template: {template_module_name}")
    except ValueError as e:
        print(f"Erro ao carregar template '{template_module_name}': {e}")
        print(f"Templates disponíveis: {', '.join(template_manager.list_templates())}")
        # Fallback to default 'pdf' template if the selected one fails
        if template_module_name != 'pdf':
            print("Tentando usar o template padrão 'pdf'.")
            try:
                loaded_template_module = template_manager.get_template('pdf')
                template_module_name = 'pdf'  # Update actual template name
            except ValueError as e_default:
                print(f"Erro ao carregar template padrão 'pdf': {e_default}. Saindo.")
                sys.exit(1)
        else:  # If default 'pdf' itself failed
            sys.exit(1)

    # Instantiate and use the PdfGenerator
    try:
        generator = PdfGenerator(
            data_loader=data_loader,
            template_module=loaded_template_module
        )
        output_filepath = generator.generate_cv()
        # output_filepath is an absolute path to the generated_cvs directory
        print(f"Arquivo gerado: {output_filepath}")
    except Exception as e:
        print(f"Erro durante a geração do PDF: {type(e).__name__} - {e}")
        # import traceback # Uncomment for detailed debugging
        # traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
