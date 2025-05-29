"""
Main command-line interface (CLI) script for generating ATS-optimized PDF CVs.

This script facilitates the creation of CVs in PDF format, specifically tailored
for Applicant Tracking Systems (ATS). It parses command-line arguments to
determine the language, CV data source (either a language code for a
`curriculo_<lang>.json` file or a direct path to a JSON file), and the
template to be used for PDF generation.

The script leverages:
- `DataLoader` to load and structure the CV data.
- `TemplateManager` to load the specified ATS-specific PDF template module.
- `PdfAtsGenerator` to perform the actual CV generation, including keyword
  extraction and layout optimization for ATS parsing.
"""
import sys
import argparse
import os

# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from templates import TemplateManager
from data_loader import DataLoader
from cv_generators.pdf_ats_generator import PdfAtsGenerator


def main():
    """
    Parses CLI arguments, loads data and template, then generates the ATS PDF CV.
    """
    parser = argparse.ArgumentParser(
        description='Gerar currículo em formato PDF otimizado para ATS.'
    )
    parser.add_argument(
        'language',
        nargs='?',
        default=None,
        help=('Código do idioma (ex: pt, en, es). '
              'Se não fornecido e --json-file não for usado, tenta "pt".')
    )
    parser.add_argument(
        '--template', '-t',
        help='Nome do template PDF ATS a ser usado (ex: pdf_ats).',
        default='pdf_ats'  # Default template for this script
    )
    parser.add_argument(
        '--json-file',
        help='Caminho para um arquivo JSON de dados do currículo personalizado.',
        default=None
    )
    args = parser.parse_args()

    selected_lang_code = args.language
    if not selected_lang_code and not args.json_file:
        print("Nenhum idioma ou arquivo JSON especificado. "
              "Tentando 'pt' como padrão para ATS PDF.")
        selected_lang_code = 'pt'
    elif not selected_lang_code and args.json_file:
        print(f"Arquivo JSON especificado ({args.json_file}) sem código de idioma explícito. "
              "Usando 'custom' como placeholder para o código de idioma para ATS PDF.")
        selected_lang_code = 'custom'

    # Load data using DataLoader
    try:
        if not selected_lang_code and not args.json_file: # Should be caught by above
             print("Erro: É necessário especificar um idioma ou um arquivo JSON.")
             sys.exit(1)

        data_loader = DataLoader(
            language_code=selected_lang_code,
            json_file_path=args.json_file,
            root_dir='.'  # Assumes script is run from project root
        )
    except FileNotFoundError as e:
        print(f"Erro ao carregar dados (ATS PDF): {e}")
        if not args.json_file:
            try:
                from utils import get_available_languages
                available = get_available_languages(root_dir='.')
                print("Idiomas disponíveis:", list(available.keys()))
            except Exception as lang_e:
                print(f"Não foi possível listar os idiomas disponíveis: {lang_e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado ao inicializar DataLoader (ATS PDF): {type(e).__name__} - {e}")
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
        # Fallback to default 'pdf_ats' template if the selected one fails
        if template_module_name != 'pdf_ats':
            print("Tentando usar o template padrão 'pdf_ats'.")
            try:
                loaded_template_module = template_manager.get_template('pdf_ats')
                template_module_name = 'pdf_ats'  # Update actual template name
            except ValueError as e_default:
                print(f"Erro ao carregar template padrão 'pdf_ats': {e_default}. Saindo.")
                sys.exit(1)
        else:  # If default 'pdf_ats' itself failed
            sys.exit(1)

    # Instantiate and use the PdfAtsGenerator
    try:
        generator = PdfAtsGenerator(
            data_loader=data_loader,
            template_module=loaded_template_module
        )
        output_filepath = generator.generate_cv()
        # output_filepath is an absolute path to the generated_cvs directory
        print(f"Arquivo gerado: {output_filepath}")
        print("\nDicas para aumentar a compatibilidade com ATS:")
        print("1. Use termos-chave específicos da sua área em seu resumo profissional.")
        print("2. Liste habilidades técnicas relevantes para a vaga desejada.")
        print("3. Mantenha um formato limpo e direto, evitando tabelas complexas.")
        print("4. Certifique-se de incluir datas completas nas experiências (mm/aaaa - mm/aaaa).")
    except Exception as e:
        print(f"Erro durante a geração do PDF ATS: {type(e).__name__} - {e}")
        # import traceback # Uncomment for detailed debugging
        # traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
