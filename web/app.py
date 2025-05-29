"""
Flask Web Application for the CV Generator.

This module implements a Flask web application that provides a user interface
for creating, editing, and generating CVs in various formats (DOCX, PDF, ATS-PDF).
It handles routing, request processing, interaction with the CV generation logic
(DataLoader, TemplateManager, and specific CV generators), and file downloads.

Endpoints:
    /: Redirects to the CV creation page.
    /schemas/<language>: Serves JSON schema for CV data validation.
    /edit: Page for editing existing CV data (loads data into form).
    /cadastrar: Page for creating new CV data using a dynamic form.
    /generate: Page for selecting options to generate a CV.
    /create_json: API endpoint to create a new language JSON file.
    /get_json_content: API endpoint to fetch content of a language JSON file.
    /save_json: API endpoint to save CV data to a language JSON file.
    /generate_cv: API endpoint to trigger CV generation.
    /download_cached/<file_id>: Serves a generated file from cache (production).
    /download_dev/<filename>: Serves a generated file directly (development).
    /debug/file_exists/<filename>: Debug endpoint to check file existence.
"""
import os
import sys
import json
import tempfile
import uuid
import logging
from logging import FileHandler
from flask import (
    Flask, render_template, request, jsonify,
    send_file, redirect, url_for
)
from typing import Dict, Any, Optional, List, Tuple # For type hinting

# Ensure project root is in path to allow imports of other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from templates import TemplateManager
from utils import get_available_languages
from data_loader import DataLoader
from cv_generators.docx_generator import DocxGenerator
from cv_generators.pdf_generator import PdfGenerator
from cv_generators.pdf_ats_generator import PdfAtsGenerator

# --- Application Setup & Configuration ---

app = Flask(__name__)
app.config['PROJECT_ROOT'] = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)


def is_production() -> bool:
    """
    Detects if the application is running in a production-like environment.
    Checks common environment variables used by hosting platforms like Render.

    Returns:
        bool: True if in a production environment, False otherwise.
    """
    return (os.environ.get('RENDER') == 'true' or
            os.environ.get('FLASK_ENV') == 'production')


# --- File Cache Manager ---
class FileCacheManager:
    """
    Manages temporary storage of generated file paths for download.

    This simple cache uses a dictionary to map unique IDs to file paths,
    facilitating file downloads, especially in serverless or ephemeral
    filesystem environments where direct path access might be complex.

    Attributes:
        cache (Dict[str, str]): A dictionary storing file_id: file_path pairs.
    """
    def __init__(self):
        """Initializes the FileCacheManager with an empty cache."""
        self.cache: Dict[str, str] = {}

    def add_file(self, file_path: str) -> str:
        """
        Adds a file path to the cache and returns a unique ID for retrieval.

        Args:
            file_path (str): The absolute path to the file to be cached.

        Returns:
            str: A unique string ID that can be used to retrieve the file path.
        """
        file_id = str(uuid.uuid4())
        self.cache[file_id] = file_path
        app.logger.info(f"File added to cache: ID {file_id} -> Path {file_path}")
        return file_id

    def get_file_path(self, file_id: str) -> Optional[str]:
        """
        Retrieves a file path from the cache using its unique ID.

        Args:
            file_id (str): The unique ID of the file.

        Returns:
            Optional[str]: The file path if found, otherwise None.
        """
        path = self.cache.get(file_id)
        if path:
            app.logger.info(f"File path retrieved from cache: ID {file_id} -> Path {path}")
        else:
            app.logger.warning(f"File ID not found in cache: {file_id}")
        return path

    def remove_file(self, file_id: str) -> Optional[str]:
        """
        Removes a file path from the cache using its ID (e.g., after download).

        Args:
            file_id (str): The unique ID of the file to remove.

        Returns:
            Optional[str]: The file path that was removed, or None if ID not found.
        """
        path = self.cache.pop(file_id, None)
        if path:
            app.logger.info(f"File removed from cache: ID {file_id}, Path {path}")
        return path

file_cache_manager = FileCacheManager()


# --- Helper Functions ---
def get_project_root() -> str:
    """
    Returns the absolute path to the project root directory.
    Relies on `app.config['PROJECT_ROOT']`.

    Returns:
        str: Absolute path to the project root.
    """
    return app.config['PROJECT_ROOT']


# --- Routes ---
@app.route('/')
def index() -> Any:
    """Redirects the root URL to the CV creation page."""
    return redirect(url_for('cadastrar'))


@app.route('/schemas/<language>')
def get_schema(language: str) -> Any:
    """
    Serves JSON schema files for CV data validation for a given language.
    If a schema file doesn't exist, a basic one is created.

    Args:
        language (str): The language code for which to retrieve the schema.

    Returns:
        Response: A Flask JSON response containing the schema or an error message.
    """
    schema_dir = os.path.join(get_project_root(), 'web', 'static', 'schemas')
    schema_path = os.path.join(schema_dir, f'schema_{language}.json')

    if not os.path.isdir(schema_dir):
        try:
            os.makedirs(schema_dir)
            app.logger.info(f"Created schema directory: {schema_dir}")
        except OSError as e:
            app.logger.error(f"Error creating schema directory {schema_dir}: {e}")
            return jsonify({'error': f'Erro ao criar diretório de schemas: {str(e)}'}), 500

    if not os.path.exists(schema_path):
        app.logger.info(f"Schema not found for language '{language}', creating basic schema at {schema_path}.")
        # Simplified basic schema for brevity in this example
        basic_schema: Dict[str, Any] = {
            "type": "object",
            "properties": {
                "languageName": {"type": "string", "description": f"Name of the language ({language})"},
                "nome": {"type": "string", "description": "Full name"}
            },
            "required": ["languageName", "nome"]
        }
        try:
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(basic_schema, f, indent=2, ensure_ascii=False)
        except IOError as e:
            app.logger.error(f"Error creating basic schema file {schema_path}: {e}")
            return jsonify({'error': f'Erro ao criar schema básico para {language}: {str(e)}'}), 500

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_content = json.load(f)
        return jsonify(schema_content)
    except FileNotFoundError: # Should be caught by creation logic, but as safeguard
        app.logger.error(f"Schema file not found after attempting creation: {schema_path}")
        return jsonify({'error': f'Schema para o idioma {language} não encontrado.'}), 404
    except Exception as e:
        app.logger.error(f"Error reading schema file {schema_path}: {e}")
        return jsonify({'error': f'Erro ao ler schema para o idioma {language}: {str(e)}'}), 500


@app.route('/edit')
def edit_cv_page() -> str: # Renamed for clarity
    """Renders the CV editing page."""
    languages = get_available_languages(root_dir=get_project_root())
    return render_template('edit.html', languages=languages)


@app.route('/cadastrar')
def cadastrar_cv_page() -> str: # Renamed for clarity
    """Renders the CV creation/registration page."""
    languages = get_available_languages(root_dir=get_project_root())
    return render_template('cadastrar.html', languages=languages)


def get_available_templates_grouped() -> Dict[str, List[str]]:
    """
    Retrieves and groups available template names for the UI.

    Templates are grouped by their base format type (e.g., 'pdf', 'docx').
    Special templates like 'pdf_ats' are handled as a distinct group.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are format types/groups
                              and values are lists of template modifier names.
    """
    template_manager = TemplateManager(root_dir=get_project_root())
    templates_list = template_manager.list_templates()
    
    template_groups: Dict[str, List[str]] = {}
    for template_name in templates_list:
        parts = template_name.split('_', 1)
        format_type = parts[0]
        modifier = parts[1] if len(parts) > 1 else ""

        if format_type == 'pdf' and modifier == 'ats':
            # Treat 'pdf_ats' as its own top-level group for clarity in UI
            group_key = 'pdf_ats'
            # Store 'ats' as a "modifier" or an empty string if no further variants
            actual_modifier_for_ats = "" # Or 'ats' itself if it makes sense for UI
        else:
            group_key = format_type
        
        if group_key not in template_groups:
            template_groups[group_key] = []
        
        # For base templates (e.g. 'pdf' or 'docx' themselves), modifier is empty string
        # For variants (e.g. 'pdf_moderno'), modifier is 'moderno'
        if modifier and group_key != 'pdf_ats': # Don't add 'ats' as modifier to 'pdf_ats' group
            template_groups[group_key].append(modifier)
        elif not modifier and group_key != 'pdf_ats': # Base template, no modifier to add to list
            pass # Base template is implied by the group key
            
    # Ensure base format keys exist even if only variants were found (e.g. only 'pdf_moderno')
    for fmt in ['pdf', 'docx']:
        if fmt not in template_groups:
            template_groups[fmt] = []
            
    return template_groups


@app.route('/generate')
def select_generation_options_page() -> str: # Renamed for clarity
    """Renders the page for selecting CV generation options."""
    languages = get_available_languages(root_dir=get_project_root())
    template_groups = get_available_templates_grouped()
    
    format_display_names = {
        'pdf': 'PDF',
        'docx': 'Word (DOCX)',
        'pdf_ats': 'PDF otimizado para ATS'
    }
    
    return render_template(
        'generate.html',
        languages=languages,
        template_groups=template_groups,
        format_display_names=format_display_names
    )


@app.route('/create_json', methods=['POST'])
def create_language_json_file() -> Any: # Renamed for clarity
    """
    API endpoint to create a new language JSON file with a basic template.
    Expects a JSON payload with a 'language' field (e.g., 'fr').
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Dados JSON não recebidos (payload vazio)'}), 400
        language = data.get('language')
        if not language or not isinstance(language, str) or len(language) > 10: # Basic validation
            return jsonify({'error': 'Parâmetro "language" ausente ou inválido'}), 400
    except Exception as e:
        app.logger.warning(f"Invalid request to /create_json: {e}")
        return jsonify({'error': f'Requisição JSON inválida: {str(e)}'}), 400

    file_path = os.path.join(get_project_root(), f'curriculo_{language}.json')
    if os.path.exists(file_path):
        return jsonify({'error': f'Arquivo para o idioma "{language}" já existe em {file_path}'}), 400

    # Basic CV template structure
    cv_template: Dict[str, Any] = {
        "languageName": language.capitalize(),
        "nome": "", "email": "", "telefone": "", "linkedin": "",
        "secoes": {
            "resumo": {"titulo": "Resumo"},
            "experienciaProfissional": {"titulo": "Experiência Profissional", "empregos": []},
            "educacao": {"titulo": "Educação", "formacao": []},
            "habilidades": {"titulo": "Habilidades", "items": []} # Using 'items' for generic list
        },
        "outputFileName": f"Curriculo_{language.capitalize()}" # Default output name suggestion
    }
    # Language-specific titles (can be expanded)
    if language == "pt": cv_template["secoes"]["resumo"]["titulo"] = "Resumo Profissional"
    elif language == "en": cv_template["secoes"]["resumo"]["titulo"] = "Professional Summary"
    elif language == "es": cv_template["secoes"]["resumo"]["titulo"] = "Resumen Profesional"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cv_template, f, indent=2, ensure_ascii=False)
        app.logger.info(f"Created new language file: {file_path}")
        return jsonify({'success': True, 'message': f'Arquivo JSON para "{language}" criado com sucesso.'})
    except IOError as e:
        app.logger.error(f"IOError creating language file {file_path}: {e}")
        return jsonify({'error': f'Erro de I/O ao criar arquivo: {str(e)}'}), 500


@app.route('/get_json_content', methods=['POST'])
def get_language_json_content() -> Any: # Renamed for clarity
    """
    API endpoint to fetch the content of a specific language JSON file.
    Expects a JSON payload with a 'language' field.
    """
    try:
        data = request.json
        if not data: return jsonify({'error': 'Dados JSON não recebidos'}), 400
        language = data.get('language')
        if not language: return jsonify({'error': 'Idioma não especificado'}), 400
    except Exception as e:
        return jsonify({'error': f'Requisição JSON inválida: {str(e)}'}), 400

    file_path = os.path.join(get_project_root(), f'curriculo_{language}.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        return jsonify({'content': content})
    except FileNotFoundError:
        return jsonify({'error': f'Arquivo para o idioma "{language}" não encontrado.'}), 404
    except Exception as e:
        app.logger.error(f"Error reading JSON file {file_path}: {e}")
        return jsonify({'error': f'Erro ao ler arquivo JSON: {str(e)}'}), 500


@app.route('/save_json', methods=['POST'])
def save_language_json_content() -> Any: # Renamed for clarity
    """
    API endpoint to save CV data to a specific language JSON file.
    Expects a JSON payload with 'language' and 'content' (the CV data object).
    """
    try:
        data = request.json
        if not data: return jsonify({'error': 'Dados JSON não recebidos'}), 400
        language = data.get('language')
        content_data = data.get('content')
        if not language or not isinstance(content_data, dict): # Basic validation for content
            return jsonify({'error': 'Dados incompletos (idioma ou conteúdo ausente/inválido)'}), 400
    except Exception as e:
        return jsonify({'error': f'Requisição JSON inválida: {str(e)}'}), 400

    file_path = os.path.join(get_project_root(), f'curriculo_{language}.json')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        app.logger.info(f"Saved content to language file: {file_path}")
        return jsonify({'success': True, 'message': 'Arquivo salvo com sucesso!'})
    except Exception as e:
        app.logger.error(f"Error saving JSON file {file_path}: {e}")
        return jsonify({'error': f'Erro ao salvar arquivo JSON: {str(e)}'}), 500


@app.route('/generate_cv', methods=['POST'])
def generate_cv_endpoint() -> Any:
    """
    API endpoint to generate a CV.
    Expects JSON payload with 'language', 'format_type' (e.g., 'pdf', 'docx'),
    'template' (modifier, e.g., 'moderno'), and optional 'content' (direct CV data).
    Uses the appropriate generator class directly.
    """
    try:
        data = request.json
        if not data: return jsonify({'error': 'Dados JSON não recebidos'}), 400
        
        language: Optional[str] = data.get('language')
        format_type: Optional[str] = data.get('format') # Base format: 'pdf', 'docx'
        # Template modifier from UI, e.g., 'moderno' for 'pdf_moderno', or 'ats' for 'pdf_ats'
        template_selection: Optional[str] = data.get('template')
        cv_content_json: Optional[Dict[Any, Any]] = data.get('content')

        if not language or not format_type:
            return jsonify({'error': 'Parâmetros "language" ou "format" ausentes.'}), 400
        
        root_dir = get_project_root()
        temp_json_file_path: Optional[str] = None
        
        if cv_content_json:
            try:
                # Save content to a temporary file for DataLoader
                # Ensure temp file is created in a writable directory, preferably within project for consistency
                temp_dir = os.path.join(root_dir, "temp_cv_data") # Create a specific temp dir
                os.makedirs(temp_dir, exist_ok=True)
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f'_{language}.json', mode='w',
                    encoding='utf-8', dir=temp_dir
                ) as temp_f:
                    json.dump(cv_content_json, temp_f)
                    temp_json_file_path = temp_f.name
                app.logger.info(f"Temporary CV data saved to: {temp_json_file_path}")
            except Exception as e:
                app.logger.error(f"Failed to save temporary CV data: {e}")
                return jsonify({'error': f'Falha ao processar dados do CV: {str(e)}'}), 500
        
        data_loader = DataLoader(
            language_code=language,
            json_file_path=temp_json_file_path, # Will be absolute path if created
            root_dir=root_dir # DataLoader uses this to find curriculo_XX.json if temp_json_file_path is None
        )
        
        template_manager = TemplateManager(root_dir=root_dir)
        
        # Determine actual template name to load (e.g., 'pdf_moderno', 'docx', 'pdf_ats')
        # format_type: 'pdf', 'docx'. template_selection: 'moderno', 'ats', or base format name
        actual_template_name = format_type
        if template_selection and template_selection != format_type:
            if format_type == 'pdf' and template_selection == 'ats':
                actual_template_name = 'pdf_ats'
            else:
                actual_template_name = f"{format_type}_{template_selection}"
        
        app.logger.info(f"Attempting to load template: '{actual_template_name}' "
                        f"(format: {format_type}, selection: {template_selection})")
        
        try:
            template_module = template_manager.get_template(actual_template_name)
        except ValueError: # Template not found, try base format as fallback
            app.logger.warning(f"Template '{actual_template_name}' not found. Trying base '{format_type}'.")
            try:
                template_module = template_manager.get_template(format_type)
                actual_template_name = format_type # Update to the one actually loaded
            except ValueError as e_base:
                app.logger.error(f"Base template '{format_type}' also not found: {e_base}")
                if temp_json_file_path and os.path.exists(temp_json_file_path):
                    os.unlink(temp_json_file_path)
                return jsonify({'error': f"Template '{actual_template_name}' ou base '{format_type}' não encontrado."}), 400
        
        app.logger.info(f"Using template module: {actual_template_name}")

        generator_instance: Optional[Any] = None # BaseCvGenerator type
        if actual_template_name == 'pdf_ats':
            generator_instance = PdfAtsGenerator(data_loader, template_module)
        elif format_type == 'pdf': # Covers 'pdf', 'pdf_moderno', etc.
            generator_instance = PdfGenerator(data_loader, template_module)
        elif format_type == 'docx': # Covers 'docx', 'docx_variant', etc.
            generator_instance = DocxGenerator(data_loader, template_module)
        
        if not generator_instance:
            if temp_json_file_path and os.path.exists(temp_json_file_path):
                os.unlink(temp_json_file_path)
            return jsonify({'error': f'Formato de CV não suportado: {format_type}'}), 400

        output_file_abs_path = generator_instance.generate_cv() # Returns absolute path
        
    except Exception as e: # Catch-all for unexpected errors during setup
        app.logger.error(f"Error during CV generation setup: {type(e).__name__} - {str(e)}", exc_info=True)
        if 'temp_json_file_path' in locals() and temp_json_file_path and os.path.exists(temp_json_file_path):
             try: os.unlink(temp_json_file_path)
             except OSError: app.logger.warning(f"Could not clean up temp file {temp_json_file_path} on error.")
        return jsonify({'error': f'Erro interno ao preparar geração do currículo: {str(e)}'}), 500
    finally: # Ensure temp file is cleaned up if created by this endpoint run
        if 'temp_json_file_path' in locals() and temp_json_file_path and os.path.exists(temp_json_file_path):
            try:
                os.unlink(temp_json_file_path)
                app.logger.info(f"Temporary JSON file '{temp_json_file_path}' deleted.")
            except OSError as e_del:
                app.logger.warning(f"Failed to delete temporary JSON file '{temp_json_file_path}': {e_del}")

    if not output_file_abs_path or not os.path.exists(output_file_abs_path):
         app.logger.error(f"CV generation failed or file not found at: {output_file_abs_path}")
         return jsonify({'error': 'Falha ao gerar o arquivo ou arquivo não encontrado no servidor.'}), 500

    filename = os.path.basename(output_file_abs_path)
    app.logger.info(f"CV generated successfully: {filename} at {output_file_abs_path}")

    if is_production():
        file_id = file_cache_manager.add_file(output_file_abs_path)
        return jsonify({
            'success': True, 'filename': filename, 'file_id': file_id,
            'download_url': url_for('download_cached_file', file_id=file_id)
        })
    else: # Local development
        # For local dev, files are in 'generated_cvs'.
        # We need a route to serve them from there, relative to project root.
        # `filename` here would be like "Curriculo_JohnDoe_en.pdf"
        # The actual file is at "PROJECT_ROOT/generated_cvs/Curriculo_JohnDoe_en.pdf"
        # So, the download URL should reflect this structure.
        relative_path_for_download = os.path.join("generated_cvs", filename)
        return jsonify({
            'success': True, 'filename': filename,
            'download_url': url_for('download_local_dev_file', structured_filename=relative_path_for_download)
        })


@app.route('/download_cached/<file_id>')
def download_cached_file(file_id: str) -> Any:
    """
    Serves a cached file for download (typically used in production).

    Args:
        file_id (str): The unique ID of the file in the cache.

    Returns:
        Response: Flask send_file response or JSON error.
    """
    file_path = file_cache_manager.get_file_path(file_id)
    if not file_path or not os.path.exists(file_path):
        app.logger.warning(f"Cached file ID '{file_id}' not found or file missing at '{file_path}'.")
        return jsonify({'error': 'Arquivo não encontrado ou expirado.'}), 404
    
    # Optional: Remove file from cache after download for single-use links
    # file_cache_manager.remove_file(file_id)
    
    app.logger.info(f"Serving cached file: {file_path}")
    return send_file(file_path, as_attachment=True)


@app.route('/download_dev/<path:structured_filename>')
def download_local_dev_file(structured_filename: str) -> Any:
    """
    Serves a file for download during local development.
    The filename can include subdirectories relative to project root (e.g., "generated_cvs/mycv.pdf").

    IMPORTANT: This route is intended for development only and is NOT safe for production
               if it allows arbitrary path traversal.

    Args:
        structured_filename (str): The filename, potentially including "generated_cvs/" prefix.

    Returns:
        Response: Flask send_file response or JSON error.
    """
    if is_production():
        app.logger.error("Attempt to access /download_dev in production.")
        return jsonify({'error': 'Acesso direto a arquivos desabilitado em produção.'}), 403
        
    # Construct path relative to project root.
    # os.path.normpath and os.path.join ensure path is safe and correct.
    # structured_filename is already like "generated_cvs/filename.pdf"
    file_path = os.path.join(get_project_root(), structured_filename)
    file_path = os.path.normpath(file_path)

    # Security check: Ensure the path is still within the project root (or a designated public dir)
    # This is a basic check. For true security, serve from a dedicated static folder if possible.
    if not file_path.startswith(os.path.normpath(get_project_root())):
        app.logger.error(f"Attempt to access file outside project root: {file_path}")
        return jsonify({'error': 'Acesso negado.'}), 403
        
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        app.logger.warning(f"Local dev file not found: {file_path}")
        return jsonify({'error': 'Arquivo não encontrado no servidor.'}), 404
    
    app.logger.info(f"Serving local dev file: {file_path}")
    return send_file(file_path, as_attachment=True)


@app.route('/debug/file_exists/<path:filename>')
def debug_file_exists_endpoint(filename: str) -> Any: # Renamed for clarity
    """
    Debug endpoint to check if a file exists relative to project root.
    The filename can include subdirectories (e.g., "generated_cvs/mycv.pdf").

    Args:
        filename (str): The filename (path relative to project root).

    Returns:
        Response: JSON response with file existence status and details.
    """
    file_path = os.path.join(get_project_root(), filename)
    file_path = os.path.normpath(file_path) # Normalize path
    exists = os.path.exists(file_path)
    is_file = os.path.isfile(file_path) if exists else False
    size = os.path.getsize(file_path) if is_file else None
    
    return jsonify({
        'requested_filename': filename,
        'absolute_path': file_path,
        'exists': exists,
        'is_file': is_file,
        'size_bytes': size
    })


if __name__ == '__main__':
    # Configuration for local development
    app.run(debug=True, host='0.0.0.0', port=5000) # Standard Flask dev port
else:
    # Production environment (e.g., Gunicorn)
    # Logging should be configured by the WSGI server or a dedicated logging setup.
    # This basic setup is a fallback if no other logging is configured.
    if not app.debug and not app.logger.handlers: # Avoid adding handlers if already configured
        # Example: Log to stdout for platforms like Render that collect stdout/stderr
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO if os.environ.get('FLASK_DEBUG') else logging.WARNING)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
        )
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO if os.environ.get('FLASK_DEBUG') else logging.WARNING)
        app.logger.info("Flask app logger configured for production (fallback).")
