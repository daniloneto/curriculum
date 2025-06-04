"""Utility functions for JSON-based resume generation."""
import glob
import json
import os
from typing import Any, Dict, Iterable, Optional


def get_available_languages(directory: str = '.', pattern: str = 'curriculo_*.json') -> Dict[str, Dict[str, str]]:
    """Return mapping of language codes to metadata."""
    json_files = glob.glob(os.path.join(directory, pattern))
    languages: Dict[str, Dict[str, str]] = {}
    for file in json_files:
        lang_code = os.path.basename(file).replace('curriculo_', '').replace('.json', '')
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            lang_name = data.get('languageName', lang_code.upper())
            languages[lang_code] = {'name': lang_name, 'file': file}
        except Exception:
            # skip malformed files
            continue
    return languages


def get_field(data: Dict[str, Any], primary_key: str, fallback_key: Optional[str] = None, additional_fallbacks: Optional[Iterable[str]] = None) -> Optional[Any]:
    """Retrieve a value from a dictionary with optional fallbacks."""
    if primary_key in data:
        return data[primary_key]
    if fallback_key and fallback_key in data:
        return data[fallback_key]
    if additional_fallbacks:
        for key in additional_fallbacks:
            if key in data:
                return data[key]
    return None


def get_section_title(section_data: Dict[str, Any], title_keys: Iterable[str] = ('titulo', 'title', 'titre', 'titel')) -> str:
    for key in title_keys:
        if key in section_data:
            return section_data[key]
    return 'N/A'


def get_section_content(section_data: Dict[str, Any], content_keys: Iterable[str] = ('conteudo', 'content', 'contenido', 'inhalt')) -> str:
    for key in content_keys:
        if key in section_data:
            return section_data[key]
    return ''


def get_section_list(section_data: Dict[str, Any], list_keys: Iterable[str] = ('lista', 'list', 'liste', 'lista')) -> list:
    for key in list_keys:
        if key in section_data:
            return section_data[key]
    return []


def get_jobs(section_data: Dict[str, Any], jobs_keys: Iterable[str] = ('empregos', 'jobs', 'empleos', 'emplois')) -> list:
    for key in jobs_keys:
        if key in section_data:
            return section_data[key]
    return []

