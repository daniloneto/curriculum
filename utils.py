"""
Utility functions for the CV Generator project.

This module provides helper functions for common tasks such as listing
available languages, and safely extracting data from dictionaries which
represent CV sections or fields. These utilities are used by various
components of the CV generation process, including data loading and
CV document generation.
"""
import os
import glob
import json
from typing import List, Dict, Any, Optional

def get_available_languages(root_dir: str = '.') -> Dict[str, Dict[str, str]]:
    """
    Lists available languages by finding curriculo_XX.json files.

    Scans the specified root directory for JSON files matching the pattern
    'curriculo_XX.json', where XX is the language code.

    Args:
        root_dir (str): The root directory to search for language files.
                        Defaults to the current directory.

    Returns:
        Dict[str, Dict[str, str]]: A dictionary where keys are language codes (e.g., 'pt', 'en')
                                   and values are dictionaries containing:
                                   - 'name' (str): The language name as specified in the JSON file,
                                                   or the uppercase language code as a fallback.
                                   - 'file' (str): The absolute path to the language JSON file.
    """
    json_files_path = os.path.join(root_dir, 'curriculo_*.json')
    json_files = glob.glob(json_files_path)
    languages = {}

    for file_path in json_files:
        lang_code = os.path.basename(file_path).replace('curriculo_', '').replace('.json', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang_name = data.get('languageName', lang_code.upper())
                languages[lang_code] = {
                    'name': lang_name,
                    'file': os.path.abspath(file_path) # Ensure consistent absolute path
                }
        except (json.JSONDecodeError, IOError) as e:
            # It's better to log errors or handle them more visibly if this were a library.
            # For this application, printing to console might be sufficient for CLI usage.
            print(f"Warning: Error loading or parsing language file {file_path}: {e}")
            # Optionally, skip this language or add it with default values
            # languages[lang_code] = {'name': lang_code.upper(), 'file': os.path.abspath(file_path), 'error': str(e)}

    return languages

def get_field(
    data: Dict[str, Any],
    primary_key: str,
    fallback_key: Optional[str] = None,
    additional_fallbacks: Optional[List[str]] = None
) -> Optional[Any]:
    """
    Retrieves a field from a dictionary using a primary key and optional fallback keys.

    Args:
        data (Dict[str, Any]): The dictionary to search.
        primary_key (str): The main key to try first.
        fallback_key (Optional[str]): A secondary key to try if the primary key is not found.
                                     Defaults to None.
        additional_fallbacks (Optional[List[str]]): A list of additional keys to try in order.
                                                   Defaults to None.

    Returns:
        Optional[Any]: The value associated with the first key found that has a non-empty value.
                       Returns None if no key is found or all found keys have empty values.
    """
    if primary_key in data and data[primary_key]:
        return data[primary_key]
    if fallback_key and fallback_key in data and data[fallback_key]:
        return data[fallback_key]
    if additional_fallbacks:
        for key in additional_fallbacks:
            if key in data and data[key]:
                return data[key]
    return None

def get_section_title(
    section_data: Dict[str, Any],
    title_keys: List[str] = None
) -> str:
    """
    Gets the title of a section using a list of possible keys.

    Args:
        section_data (Dict[str, Any]): The dictionary representing the section.
        title_keys (List[str], optional): A list of keys to try for the title.
                                          Defaults to ['titulo', 'title', 'titre', 'titel'].

    Returns:
        str: The found title, or "Untitled Section" as a fallback.
    """
    if title_keys is None:
        title_keys = ['titulo', 'title', 'titre', 'titel'] # Default keys
    
    for key in title_keys:
        if key in section_data and section_data[key]:
            return str(section_data[key])
    return "Untitled Section"

def get_section_content(
    section_data: Dict[str, Any],
    content_keys: List[str] = None
) -> str:
    """
    Gets the textual content of a section using a list of possible keys.

    Args:
        section_data (Dict[str, Any]): The dictionary representing the section.
        content_keys (List[str], optional): A list of keys to try for the content.
                                           Defaults to ['conteudo', 'content', 'contenido', 'inhalt', 'texto', 'text'].

    Returns:
        str: The found content as a string, or an empty string if not found.
    """
    if content_keys is None:
        content_keys = ['conteudo', 'content', 'contenido', 'inhalt', 'texto', 'text']
        
    for key in content_keys:
        if key in section_data and section_data[key]:
            return str(section_data[key])
    return ""

def get_section_list(
    section_data: Dict[str, Any],
    list_keys: List[str] = None
) -> List[Any]:
    """
    Gets a list of items from a section using a list of possible keys.

    Args:
        section_data (Dict[str, Any]): The dictionary representing the section.
        list_keys (List[str], optional): A list of keys to try for the list.
                                        Defaults to ['lista', 'list', 'items'].
                                        Note: 'lista' was duplicated in original, kept one.

    Returns:
        List[Any]: The found list, or an empty list if not found or not a list.
    """
    if list_keys is None:
        list_keys = ['lista', 'list', 'items'] # Default keys, removed duplicate 'lista'
        
    for key in list_keys:
        if key in section_data and isinstance(section_data[key], list):
            return section_data[key]
    return []

def get_jobs(
    section_data: Dict[str, Any],
    jobs_keys: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Gets job experiences (a list of dictionaries) from a section using a list of possible keys.

    Args:
        section_data (Dict[str, Any]): The dictionary representing the experience section.
        jobs_keys (List[str], optional): A list of keys to try for the jobs list.
                                        Defaults to ['empregos', 'jobs', 'empleos', 'emplois', 
                                                     'experiencias', 'experience'].

    Returns:
        List[Dict[str, Any]]: The found list of jobs, or an empty list if not found or not a list.
                              Each job is expected to be a dictionary.
    """
    if jobs_keys is None:
        jobs_keys = ['empregos', 'jobs', 'empleos', 'emplois', 'experiencias', 'experience']
        
    for key in jobs_keys:
        if key in section_data and isinstance(section_data[key], list):
            # Basic check if items are dictionaries, can be enhanced
            return [job for job in section_data[key] if isinstance(job, dict)]
    return []

if __name__ == '__main__':
    # Example usage for testing (can be expanded)
    print("--- Testing utils.py ---")

    # Create dummy project structure for testing get_available_languages
    test_root = "_test_lang_dir"
    os.makedirs(test_root, exist_ok=True)
    with open(os.path.join(test_root, "curriculo_en.json"), "w", encoding='utf-8') as f:
        json.dump({"languageName": "English", "name": "Test User"}, f)
    with open(os.path.join(test_root, "curriculo_pt.json"), "w", encoding='utf-8') as f:
        json.dump({"languageName": "Português", "nome": "Usuário Teste"}, f)
    with open(os.path.join(test_root, "curriculo_es.json"), "w", encoding='utf-8') as f: # No languageName
        json.dump({"nombre": "Usuario Prueba"}, f)

    print("\nTesting get_available_languages():")
    languages = get_available_languages(root_dir=test_root)
    assert "en" in languages and languages["en"]["name"] == "English"
    assert "pt" in languages and languages["pt"]["name"] == "Português"
    assert "es" in languages and languages["es"]["name"] == "ES" # Fallback to uppercase code
    print(f"Found languages: {languages}")

    # Clean up dummy files and directory
    os.remove(os.path.join(test_root, "curriculo_en.json"))
    os.remove(os.path.join(test_root, "curriculo_pt.json"))
    os.remove(os.path.join(test_root, "curriculo_es.json"))
    os.rmdir(test_root)

    print("\nTesting get_field():")
    sample_data = {"name_en": "John Doe", "name_pt": "João Ninguém", "email": "john@example.com"}
    assert get_field(sample_data, "name_en") == "John Doe"
    assert get_field(sample_data, "name_fr", "name_pt") == "João Ninguém"
    assert get_field(sample_data, "name_de", "name_it", ["email"]) == "john@example.com"
    assert get_field(sample_data, "phone") is None
    print("get_field tests passed.")

    print("\nTesting section functions:")
    section = {
        "titulo": "Summary", 
        "conteudo": "This is a summary.", 
        "lista": ["item1", "item2"],
        "experiencias": [{"cargo": "Dev"}, {"cargo": "Tester"}]
    }
    assert get_section_title(section) == "Summary"
    assert get_section_content(section) == "This is a summary."
    assert get_section_list(section) == ["item1", "item2"]
    assert len(get_jobs(section)) == 2
    print("Section function tests passed.")
    print("\n--- utils.py testing finished ---")
