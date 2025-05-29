"""
Manages the loading and access of CV data from JSON files.

This module provides the DataLoader class, which is responsible for
reading CV data from specified JSON files or by discovering them based on
language codes. It uses utility functions from `utils.py` to extract
structured information like personal details, sections, and specific fields
(e.g., job experiences, skills) from the loaded data.
"""
import json
import os
from typing import List, Dict, Any, Optional

# Assuming utils.py is in the parent directory or accessible via PYTHONPATH
from utils import (
    get_available_languages,
    get_field as utils_get_field,
    get_section_title as utils_get_section_title,
    get_section_content as utils_get_section_content,
    get_section_list as utils_get_section_list,
    get_jobs as utils_get_jobs
)

# Default list of keys to identify the main sections container in the JSON.
DEFAULT_SECTIONS_KEYS = ['secoes', 'sections', 'secciones', 'sektionen']


class DataLoader:
    """
    Loads and provides access to CV data from JSON files.

    The DataLoader can load data from a specific JSON file path or
    discover the appropriate language file within a root directory based on
    a language code. It then offers methods to retrieve various parts of
    the CV data in a structured manner.

    Attributes:
        language_code (str): The language code for the CV data (e.g., 'pt', 'en').
        root_dir (str): The root directory where language files or custom JSON might be located.
                        Defaults to the current directory.
        data (Optional[Dict[str, Any]]): The loaded JSON data as a dictionary.
                                         None if loading fails.
        _secoes_key (Optional[str]): The key used to access the main sections
                                     dictionary within the loaded data (e.g., 'secoes').
                                     None if not found.
    """

    def __init__(
        self,
        language_code: str,
        json_file_path: Optional[str] = None,
        root_dir: str = '.'
    ):
        """
        Initializes the DataLoader and loads CV data.

        Args:
            language_code (str): The language code (e.g., 'en', 'pt'). This is used
                                 to find the language file if `json_file_path` is not provided,
                                 and can also be used for language-specific defaults.
            json_file_path (Optional[str]): Direct path to a JSON CV data file.
                                            If provided, this file is loaded directly.
                                            Defaults to None.
            root_dir (str): The root directory for resolving relative paths,
                            especially for finding language files. Defaults to '.'.

        Raises:
            FileNotFoundError: If the specified language file or custom JSON file
                               cannot be found.
            json.JSONDecodeError: If the JSON file is improperly formatted.
            ValueError: If no data could be loaded.
            Exception: For other unexpected errors during initialization.
        """
        self.language_code = language_code.lower()
        self.root_dir = os.path.abspath(root_dir) # Ensure root_dir is absolute
        self.data: Optional[Dict[str, Any]] = None
        self._secoes_key: Optional[str] = None

        try:
            if json_file_path:
                abs_json_file_path = os.path.join(self.root_dir, json_file_path) \
                    if not os.path.isabs(json_file_path) else json_file_path
                print(f"DataLoader: Loading from custom JSON file: {abs_json_file_path}")
                if not os.path.exists(abs_json_file_path):
                    raise FileNotFoundError(f"Custom JSON file not found: {abs_json_file_path}")
                with open(abs_json_file_path, 'r', encoding='utf-8') as file:
                    self.data = json.load(file)
            else:
                print(f"DataLoader: Loading for language '{self.language_code}' from root_dir '{self.root_dir}'")
                available_langs = get_available_languages(root_dir=self.root_dir)
                if self.language_code not in available_langs:
                    raise FileNotFoundError(
                        f"Language code '{self.language_code}' not found. "
                        f"Available in '{self.root_dir}': {list(available_langs.keys())}"
                    )
                lang_file_path = available_langs[self.language_code]['file'] # Already absolute from get_available_languages
                print(f"DataLoader: Found language file: {lang_file_path}")
                with open(lang_file_path, 'r', encoding='utf-8') as file:
                    self.data = json.load(file)

            if not self.data: # Should be caught by earlier errors, but as a safeguard.
                raise ValueError("No data loaded from JSON file.")

            # Determine the main sections key
            for key in DEFAULT_SECTIONS_KEYS:
                if key in self.data:
                    self._secoes_key = key
                    break
            if not self._secoes_key:
                print(
                    f"Warning: Main sections key (e.g., {DEFAULT_SECTIONS_KEYS}) "
                    "not found in JSON data. Section retrieval might be limited."
                )
        except FileNotFoundError as e:
            print(f"DataLoader Error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"DataLoader Error: Could not decode JSON. Details: {e}")
            raise
        except Exception as e:
            print(f"DataLoader Error: An unexpected error occurred during initialization: {e}")
            raise

    def get_data(self) -> Optional[Dict[str, Any]]:
        """
        Returns all loaded CV data.

        Returns:
            Optional[Dict[str, Any]]: The entire CV data as a dictionary,
                                      or None if data loading failed.
        """
        return self.data

    def get_personal_info(self) -> Dict[str, Optional[str]]:
        """
        Retrieves common personal information fields from the CV data.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing personal info like
                                      'name', 'email', 'phone', 'linkedin'.
                                      Values are None if not found.
        """
        if not self.data:
            return {}
        return {
            'name': utils_get_field(self.data, 'nome', 'name', ['nombre']),
            'email': self.data.get('email'),
            'phone': utils_get_field(self.data, 'telefone', 'phone', ['teléfono']),
            'linkedin': self.data.get('linkedin')
        }

    def get_sections_container(self) -> Dict[str, Any]:
        """
        Returns the main dictionary that contains all CV sections.

        If a primary sections key (e.g., 'secoes') was identified, that sub-dictionary
        is returned. Otherwise, it assumes the entire loaded data might be the
        sections container (for flatter JSON structures).

        Returns:
            Dict[str, Any]: The dictionary holding CV sections, or an empty
                            dictionary if no suitable container is found.
        """
        if not self.data:
            return {}
        if self._secoes_key and self._secoes_key in self.data:
            return self.data.get(self._secoes_key, {})
        # Fallback: if no _secoes_key, or if key doesn't exist,
        # consider self.data itself as the container, if it's a dict.
        return self.data if isinstance(self.data, dict) else {}

    def get_section(self, section_key_variants: List[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific section by trying a list of possible keys.

        Args:
            section_key_variants (List[str]): A list of keys to try in order
                                              (e.g., ['resumoProfissional', 'professionalSummary']).

        Returns:
            Optional[Dict[str, Any]]: The section data (as a dictionary) if found,
                                      otherwise None.
        """
        sections_container = self.get_sections_container()
        if not sections_container:
            return None

        for key in section_key_variants:
            if key in sections_container:
                return sections_container[key]
        return None

    def get_section_title(
        self,
        section_data: Optional[Dict[str, Any]],
        title_keys: Optional[List[str]] = None
    ) -> str:
        """
        Gets the title from provided section data using `utils.get_section_title`.

        Args:
            section_data (Optional[Dict[str, Any]]): The dictionary for a specific section.
            title_keys (Optional[List[str]]): Specific keys to check for the title.
                                             If None, `utils.get_section_title` defaults are used.

        Returns:
            str: The section title, or a default "Untitled Section" if not found.
        """
        if not section_data:
            return "N/A" # Or "Untitled Section" as per utils.py
        return utils_get_section_title(section_data, title_keys or ['titulo', 'title'])

    def get_section_content(
        self,
        section_data: Optional[Dict[str, Any]],
        content_keys: Optional[List[str]] = None
    ) -> str:
        """
        Gets content from provided section data using `utils.get_section_content`.

        Args:
            section_data (Optional[Dict[str, Any]]): The dictionary for a specific section.
            content_keys (Optional[List[str]]): Specific keys for content.
                                               If None, `utils.get_section_content` defaults are used.

        Returns:
            str: The section content, or an empty string if not found.
        """
        if not section_data:
            return ""
        return utils_get_section_content(section_data, content_keys or ['conteudo', 'content', 'texto'])

    def get_section_list(
        self,
        section_data: Optional[Any], # Can be dict or list itself
        list_keys: Optional[List[str]] = None
    ) -> List[Any]:
        """
        Gets a list from section data using `utils.get_section_list`.
        Handles cases where section_data itself might be the list.

        Args:
            section_data (Optional[Any]): The section data, which could be a dictionary
                                          containing the list, or the list itself.
            list_keys (Optional[List[str]]): Specific keys if section_data is a dict.
                                            If None, `utils.get_section_list` defaults are used.

        Returns:
            List[Any]: The list of items, or an empty list if not found.
        """
        if not section_data:
            return []
        if isinstance(section_data, list): # If the passed data is already the list
            return section_data
        # If it's a dict, use the utility to find the list within it
        return utils_get_section_list(section_data, list_keys or ['lista', 'list', 'items'])

    def get_jobs(
        self,
        section_data: Optional[Dict[str, Any]],
        jobs_keys: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Gets job experiences from section data using `utils.get_jobs`.

        Args:
            section_data (Optional[Dict[str, Any]]): The experience section's dictionary.
            jobs_keys (Optional[List[str]]): Specific keys for the jobs list.
                                            If None, `utils.get_jobs` defaults are used.

        Returns:
            List[Dict[str, Any]]: A list of job dictionaries, or an empty list.
        """
        if not section_data:
            return []
        return utils_get_jobs(section_data, jobs_keys or ['empregos', 'jobs', 'experiencias'])

    def get_skills(
        self,
        section_data: Optional[Any], # Can be dict or list itself
        skills_keys: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]: # Assuming skills are list of dicts e.g. {"name": "Python", "level": "5"}
        """
        Retrieves skills from a skills section.
        Can handle if section_data is the list of skills itself or a dict containing it.

        Args:
            section_data (Optional[Any]): The skills section data.
            skills_keys (Optional[List[str]]): Keys to look for if section_data is a dict.
                                              Defaults to ['habilidades', 'skills', 'competencias'].

        Returns:
            List[Dict[str, Any]]: A list of skill dictionaries, or an empty list.
        """
        if not section_data:
            return []
        if isinstance(section_data, list):
            # Ensure items are dictionaries, as expected for skills
            return [s for s in section_data if isinstance(s, dict)]

        # If it's a dict, use a more generic list retrieval from utils
        # (get_section_list is more general, get_jobs is specific to list of dicts)
        raw_list = utils_get_section_list(section_data, skills_keys or ['habilidades', 'skills', 'competencias'])
        return [s for s in raw_list if isinstance(s, dict)]


    def get_output_filename(self, default_prefix: str = "Curriculo") -> str:
        """
        Retrieves the base output filename from JSON or generates a default one.
        The filename generated does NOT include the extension.

        Args:
            default_prefix (str): A prefix to use if generating a default filename
                                  (e.g., "Curriculo", "Curriculo_ATS").

        Returns:
            str: The base filename without extension.
        """
        if not self.data:
            # Fallback if data loading failed completely
            return f"{default_prefix}_{self.language_code}"

        output_path_from_json = utils_get_field(self.data, 'nomeArquivoSaida', 'outputFileName')
        if output_path_from_json:
            # Remove extension if present, as generators will add their own
            return os.path.splitext(str(output_path_from_json))[0]

        # Generate default based on name and language
        personal_info = self.get_personal_info()
        name_part = str(personal_info.get('name', '')).replace(' ', '_') if personal_info.get('name') else "Anonimo"

        return f"{default_prefix}_{name_part}_{self.language_code}"


if __name__ == '__main__':
    # This block is for basic testing when running the module directly.
    # It requires dummy JSON files (e.g., curriculo_en.json, curriculo_pt.json)
    # to be present in the project root or the specified `root_dir`.
    print("--- Testing DataLoader ---")

    # Create a temporary directory for test files
    test_project_root = "_test_project_root"
    os.makedirs(test_project_root, exist_ok=True)

    # Create dummy JSON files for testing
    dummy_en_cv_path = os.path.join(test_project_root, "curriculo_en.json")
    with open(dummy_en_cv_path, "w", encoding='utf-8') as f:
        json.dump({
            "languageName": "English",
            "name": "Test User",
            "email": "test@example.com",
            "secoes": {
                "professionalSummary": {"titulo": "Summary", "texto": "English summary."},
                "skills": {"titulo": "Technical Skills", "habilidades": [{"name": "Python", "level": "5"}]}
            },
            "nomeArquivoSaida": "CV_TestUser_EN" # No extension
        }, f)

    dummy_pt_cv_path = os.path.join(test_project_root, "curriculo_pt.json")
    with open(dummy_pt_cv_path, "w", encoding='utf-8') as f:
        json.dump({
            "languageName": "Português",
            "nome": "Usuário Teste",
            "email": "teste@exemplo.com",
            "secoes": {
                "resumoProfissional": {"titulo": "Resumo", "conteudo": "Resumo em Português."},
                "educacao": {"titulo": "Educação", "formacao": ["Curso A", "Curso B"]}
            }
            # No nomeArquivoSaida, will use default
        }, f)

    try:
        print("\n--- Test 1: Loading with language code 'en' ---")
        loader_en = DataLoader(language_code='en', root_dir=test_project_root)
        assert loader_en.get_data() is not None
        print(f"Loaded 'en' data: {json.dumps(loader_en.get_personal_info(), indent=2, ensure_ascii=False)}")
        output_fn_en = loader_en.get_output_filename(default_prefix="CV")
        assert output_fn_en == "CV_TestUser_EN" # From nomeArquivoSaida
        print(f"Output filename for 'en': {output_fn_en}")

        summary_en = loader_en.get_section(['professionalSummary'])
        assert summary_en is not None
        assert loader_en.get_section_title(summary_en) == "Summary"
        assert "English summary" in loader_en.get_section_content(summary_en)

        skills_section_en = loader_en.get_section(['skills'])
        assert skills_section_en is not None
        skills_list_en = loader_en.get_skills(skills_section_en) # Test get_skills
        assert len(skills_list_en) == 1 and skills_list_en[0]['name'] == "Python"
        print("English CV data and sections loaded and verified.")

        print("\n--- Test 2: Loading with language code 'pt' (default filename) ---")
        loader_pt = DataLoader(language_code='pt', root_dir=test_project_root)
        assert loader_pt.get_data() is not None
        print(f"Loaded 'pt' data: {json.dumps(loader_pt.get_personal_info(), indent=2, ensure_ascii=False)}")
        output_fn_pt = loader_pt.get_output_filename(default_prefix="Curriculo")
        # Default name generation: Curriculo_Usuário_Teste_pt
        expected_fn_pt = "Curriculo_Usuário_Teste_pt" # Name has space, gets replaced by _
        assert output_fn_pt == expected_fn_pt
        print(f"Output filename for 'pt' (default): {output_fn_pt}")

        education_pt = loader_pt.get_section(['educacao'])
        assert education_pt is not None
        assert loader_en.get_section_title(education_pt, title_keys=['titulo']) == "Educação"
        assert len(loader_pt.get_section_list(education_pt, list_keys=['formacao'])) == 2
        print("Portuguese CV data and sections loaded and verified.")


        print("\n--- Test 3: Loading with non-existent language 'xx' ---")
        try:
            DataLoader(language_code='xx', root_dir=test_project_root)
        except FileNotFoundError as e:
            print(f"Successfully caught error for 'xx': {e}")
            assert "Language code 'xx' not found" in str(e)

        print("\n--- Test 4: Loading with non-existent custom file ---")
        try:
            DataLoader(language_code='en', json_file_path='non_existent.json', root_dir=test_project_root)
        except FileNotFoundError as e:
            print(f"Successfully caught error for non_existent.json: {e}")
            assert "non_existent.json" in str(e)

    except Exception as e:
        print(f"An error occurred during DataLoader testing: {type(e).__name__} - {e}")
    finally:
        # Clean up dummy files and directory
        if os.path.exists(dummy_en_cv_path): os.remove(dummy_en_cv_path)
        if os.path.exists(dummy_pt_cv_path): os.remove(dummy_pt_cv_path)
        if os.path.exists(test_project_root): os.rmdir(test_project_root)
        print("\n--- DataLoader testing finished ---")
