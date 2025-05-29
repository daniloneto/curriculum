import unittest
from unittest import mock
import os
import json
import sys

# Adjust path to import utils from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import (
    get_available_languages,
    get_field,
    get_section_title,
    get_section_content,
    get_section_list,
    get_jobs
)

class TestUtils(unittest.TestCase):
    """Test suite for utility functions in utils.py."""

    @mock.patch('utils.glob.glob')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_get_available_languages(self, mock_file_open, mock_glob):
        """Test get_available_languages function."""
        # --- Test Case 1: Standard operation with root_dir ---
        mock_glob.return_value = [
            '/test_project/curriculo_en.json',
            '/test_project/curriculo_pt.json',
            '/test_project/curriculo_es.json'
        ]
        
        # Mock file contents for each language
        mock_en_data = {'languageName': 'English', 'name': 'John'}
        mock_pt_data = {'languageName': 'Português', 'nome': 'João'}
        mock_es_data = {'languageName': 'Español', 'nombre': 'Juan'} # No explicit name, should fallback

        # Configure mock_open to return different content based on file path
        def side_effect_open(filepath, *args, **kwargs):
            if filepath == '/test_project/curriculo_en.json':
                return mock.mock_open(read_data=json.dumps(mock_en_data))()
            elif filepath == '/test_project/curriculo_pt.json':
                return mock.mock_open(read_data=json.dumps(mock_pt_data))()
            elif filepath == '/test_project/curriculo_es.json':
                 # Test fallback for languageName
                return mock.mock_open(read_data=json.dumps({"nombre": "Juan"}))()
            return mock.mock_open(read_data="{}")() # Default for any other file

        mock_file_open.side_effect = side_effect_open
        
        # os.path.abspath will be called by the function, ensure it's consistent
        with mock.patch('os.path.abspath', side_effect=lambda x: x): # Simple pass-through for abspath
            languages = get_available_languages(root_dir='/test_project')

        self.assertEqual(len(languages), 3)
        self.assertIn('en', languages)
        self.assertEqual(languages['en']['name'], 'English')
        self.assertEqual(languages['en']['file'], '/test_project/curriculo_en.json')
        self.assertIn('pt', languages)
        self.assertEqual(languages['pt']['name'], 'Português')
        self.assertEqual(languages['pt']['file'], '/test_project/curriculo_pt.json')
        self.assertIn('es', languages)
        self.assertEqual(languages['es']['name'], 'ES') # Fallback to uppercase code
        self.assertEqual(languages['es']['file'], '/test_project/curriculo_es.json')

        mock_glob.assert_called_with(os.path.join('/test_project', 'curriculo_*.json'))

        # --- Test Case 2: No files found ---
        mock_glob.return_value = []
        languages_empty = get_available_languages(root_dir='/empty_dir')
        self.assertEqual(len(languages_empty), 0)
        mock_glob.assert_called_with(os.path.join('/empty_dir', 'curriculo_*.json'))

        # --- Test Case 3: File read error (simulated by mock_open raising IOError) ---
        mock_glob.return_value = ['/test_project/curriculo_fr.json']
        mock_file_open.side_effect = IOError("File read error")
        # Redirect print to capture warning for error loading
        with mock.patch('sys.stdout', new_callable=unittest.mock.StringIO) as mock_stdout:
            languages_error = get_available_languages(root_dir='/test_project')
            self.assertEqual(len(languages_error), 0) # Should skip the file with error
            self.assertIn("Error loading or parsing language file", mock_stdout.getvalue())
        
        # --- Test Case 4: Malformed JSON ---
        mock_glob.return_value = ['/test_project/curriculo_de.json']
        mock_file_open.side_effect = json.JSONDecodeError("Syntax error", "{}", 0)
        with mock.patch('sys.stdout', new_callable=unittest.mock.StringIO) as mock_stdout:
            languages_json_error = get_available_languages(root_dir='/test_project')
            self.assertEqual(len(languages_json_error), 0)
            self.assertIn("Error loading or parsing language file", mock_stdout.getvalue())


    def test_get_field(self):
        """Test get_field function for various scenarios."""
        data = {
            "primary": "Primary Value",
            "fallback": "Fallback Value",
            "additional1": "Additional 1",
            "additional2": "Additional 2",
            "empty_primary": "",
            "empty_fallback": ""
        }
        self.assertEqual(get_field(data, "primary"), "Primary Value")
        self.assertEqual(get_field(data, "non_existent", "fallback"), "Fallback Value")
        self.assertEqual(get_field(data, "non_existent", "still_non_existent", ["additional1"]), "Additional 1")
        self.assertEqual(get_field(data, "non_existent", "still_non_existent", ["non1", "additional2"]), "Additional 2")
        self.assertIsNone(get_field(data, "non_existent"))
        self.assertIsNone(get_field(data, "non_existent", "still_non_existent", ["non1", "non2"]))
        
        # Test with empty values (should return None or the first non-empty fallback)
        self.assertIsNone(get_field(data, "empty_primary"))
        self.assertEqual(get_field(data, "empty_primary", "fallback"), "Fallback Value")
        self.assertEqual(get_field(data, "empty_primary", "empty_fallback", ["additional1"]), "Additional 1")

    def test_get_section_title(self):
        """Test get_section_title function."""
        section_data_en = {"title": "Summary", "content": "..."}
        section_data_pt = {"titulo": "Resumo", "conteudo": "..."}
        section_data_fr = {"titre": "Résumé", "contenu": "..."}
        section_data_de = {"titel": "Überblick", "inhalt": "..."}
        section_data_custom_key = {"sectionName": "My Section", "text": "..."}
        section_data_empty = {"content": "No title here"}
        section_data_none = {}

        self.assertEqual(get_section_title(section_data_en), "Summary")
        self.assertEqual(get_section_title(section_data_pt), "Resumo")
        self.assertEqual(get_section_title(section_data_fr), "Résumé")
        self.assertEqual(get_section_title(section_data_de), "Überblick")
        self.assertEqual(get_section_title(section_data_custom_key, title_keys=["sectionName"]), "My Section")
        self.assertEqual(get_section_title(section_data_empty), "Untitled Section")
        self.assertEqual(get_section_title(section_data_none), "Untitled Section")

    def test_get_section_content(self):
        """Test get_section_content function."""
        section_data_en = {"title": "Summary", "content": "English content."}
        section_data_pt = {"titulo": "Resumo", "conteudo": "Conteúdo em português."}
        section_data_custom_key = {"title": "Custom", "text_body": "Custom body."}
        section_data_empty = {"title": "No content"}
        section_data_none = {}

        self.assertEqual(get_section_content(section_data_en), "English content.")
        self.assertEqual(get_section_content(section_data_pt), "Conteúdo em português.")
        self.assertEqual(get_section_content(section_data_custom_key, content_keys=["text_body", "text"]), "Custom body.")
        self.assertEqual(get_section_content(section_data_empty), "")
        self.assertEqual(get_section_content(section_data_none), "")

    def test_get_section_list(self):
        """Test get_section_list function."""
        section_data_items = {"title": "Skills", "items": ["Python", "Java"]}
        section_data_lista = {"titulo": "Cursos", "lista": ["Curso A", "Curso B"]}
        section_data_list_direct = ["Direct Item 1", "Direct Item 2"] # Not how DataLoader passes, but util might be used
        section_data_not_list = {"title": "Invalid", "items": "Not a list"}
        section_data_empty = {"title": "Empty List"}
        section_data_none = {}

        self.assertEqual(get_section_list(section_data_items), ["Python", "Java"])
        self.assertEqual(get_section_list(section_data_lista), ["Curso A", "Curso B"])
        # self.assertEqual(get_section_list(section_data_list_direct), ["Direct Item 1", "Direct Item 2"]) # Util expects dict
        self.assertEqual(get_section_list(section_data_not_list), [])
        self.assertEqual(get_section_list(section_data_empty), [])
        self.assertEqual(get_section_list(section_data_none), [])

    def test_get_jobs(self):
        """Test get_jobs function."""
        job1 = {"position": "Dev", "company": "A"}
        job2 = {"cargo": "Tester", "empresa": "B"}
        section_data_jobs = {"title": "Experience", "jobs": [job1, job2]}
        section_data_empregos = {"titulo": "Experiência", "empregos": [job1]}
        section_data_not_list = {"title": "Experience", "jobs": "Not a list"}
        section_data_empty = {"title": "No Jobs"}
        section_data_none = {}

        self.assertEqual(get_jobs(section_data_jobs), [job1, job2])
        self.assertEqual(get_jobs(section_data_empregos), [job1])
        self.assertEqual(get_jobs(section_data_not_list), [])
        self.assertEqual(get_jobs(section_data_empty), [])
        self.assertEqual(get_jobs(section_data_none), [])
        
        # Test with items in list not being dictionaries
        section_data_mixed_jobs = {"title": "Experience", "jobs": [job1, "not_a_job_dict", job2]}
        self.assertEqual(get_jobs(section_data_mixed_jobs), [job1, job2])


if __name__ == '__main__':
    unittest.main(verbosity=2)
