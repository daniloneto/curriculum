import unittest
from unittest import mock
import os
import json
import shutil # For cleaning up test directories
import sys

# Adjust path to import DataLoader and utils from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import DataLoader
from utils import get_available_languages # DataLoader uses this internally

class TestDataLoader(unittest.TestCase):
    """Test suite for the DataLoader class."""

    @classmethod
    def setUpClass(cls):
        """Create mock data directory and files for all tests in this class."""
        cls.test_root_dir = "_test_project_root_for_loader"
        cls.mock_data_dir = os.path.join(cls.test_root_dir, "tests", "mock_data") # Mimic structure if needed by utils
        
        # Recreate mock files in a temporary test-specific root to avoid interference
        # and ensure DataLoader's root_dir logic is tested.
        # DataLoader itself will look for curriculo_*.json in its root_dir.
        os.makedirs(cls.test_root_dir, exist_ok=True)

        cls.en_mock_path = os.path.join(cls.test_root_dir, "curriculo_en_mock.json")
        cls.pt_mock_path = os.path.join(cls.test_root_dir, "curriculo_pt_mock.json")
        cls.malformed_mock_path = os.path.join(cls.test_root_dir, "curriculo_malformed_mock.json")

        cls.en_data = {
            "languageName": "English (Mock)", "name": "John Doe", "email": "john.doe@example.com",
            "phone": "123-456-7890", "linkedin": "linkedin.com/in/johndoe",
            "outputFileName": "CV_JohnDoe_EN_mock", # No extension
            "secoes": {
                "professionalSummary": {"title": "Professional Summary", "content": "A brief summary."},
                "workExperience": {"title": "Work Experience", "jobs": [{"position": "Engineer", "descricao": ["Desc1"]}]},
                "technicalSkills": {"title": "Technical Skills", "habilidades": [{"nome": "Python", "nivel": "5"}]},
                "education": {"title": "Education", "degrees": ["BSc CS"]}
            }
        }
        with open(cls.en_mock_path, 'w', encoding='utf-8') as f:
            json.dump(cls.en_data, f)

        cls.pt_data = {
            "languageName": "Português (Mock)", "nome": "João Ninguém",
            "secoes": {"resumoProfissional": {"titulo": "Resumo", "conteudo": "Resumo PT."}}
        }
        with open(cls.pt_mock_path, 'w', encoding='utf-8') as f:
            json.dump(cls.pt_data, f)

        with open(cls.malformed_mock_path, 'w', encoding='utf-8') as f:
            f.write('{"languageName": "Malformed", "name": "Error Maker", "secoes": {') # Intentionally malformed

    @classmethod
    def tearDownClass(cls):
        """Remove mock data directory and files after all tests."""
        if os.path.exists(cls.test_root_dir):
            shutil.rmtree(cls.test_root_dir)

    def test_init_with_valid_language_code(self):
        """Test DataLoader initialization with a valid language code."""
        loader = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        self.assertIsNotNone(loader.data)
        self.assertEqual(loader.data['name'], 'John Doe')
        self.assertEqual(loader.language_code, 'en_mock')
        self.assertEqual(loader.root_dir, os.path.abspath(self.test_root_dir)) # Check abs path
        self.assertIsNotNone(loader._secoes_key) # Should find "secoes"

    def test_init_with_valid_json_file_path(self):
        """Test DataLoader initialization with a direct valid JSON file path."""
        # Pass relative path to DataLoader, it should resolve with root_dir
        relative_path = os.path.join(os.path.basename(self.test_root_dir), "curriculo_pt_mock.json")

        # Test with root_dir = '.' to simulate running from project root where test_root_dir is a subfolder
        # This requires the test_root_dir to be actually inside current working dir for this test path to work
        # For consistency, let's use an absolute path for json_file_path if we can
        # Or ensure root_dir for DataLoader is set correctly to find the file.

        # Let's test by providing an absolute path to the json_file_path
        loader = DataLoader(language_code='pt_mock_custom', json_file_path=self.pt_mock_path, root_dir=".")
        self.assertIsNotNone(loader.data)
        self.assertEqual(loader.data['nome'], 'João Ninguém')
        self.assertEqual(loader.language_code, 'pt_mock_custom') # lang_code is still set

        # Test with relative path and explicit root_dir for DataLoader
        loader_rel = DataLoader(language_code='pt_rel', json_file_path="curriculo_pt_mock.json", root_dir=self.test_root_dir)
        self.assertIsNotNone(loader_rel.data)
        self.assertEqual(loader_rel.data['nome'], 'João Ninguém')


    def test_init_with_invalid_language_code(self):
        """Test DataLoader initialization with an invalid language code."""
        with self.assertRaises(FileNotFoundError):
            DataLoader(language_code='xx_non_existent', root_dir=self.test_root_dir)

    def test_init_with_invalid_json_file_path(self):
        """Test DataLoader initialization with an invalid JSON file path."""
        with self.assertRaises(FileNotFoundError):
            DataLoader(language_code='any', json_file_path='non_existent.json', root_dir=self.test_root_dir)

    def test_init_with_malformed_json(self):
        """Test DataLoader initialization with a malformed JSON file."""
        with self.assertRaises(json.JSONDecodeError):
            DataLoader(language_code='malformed_mock', json_file_path=self.malformed_mock_path, root_dir=".")


    def test_get_data(self):
        """Test get_data method."""
        loader = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        self.assertEqual(loader.get_data(), self.en_data)

    def test_get_personal_info(self):
        """Test get_personal_info method."""
        loader = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        info = loader.get_personal_info()
        self.assertEqual(info['name'], 'John Doe')
        self.assertEqual(info['email'], 'john.doe@example.com')
        self.assertEqual(info['phone'], '123-456-7890')
        self.assertEqual(info['linkedin'], 'linkedin.com/in/johndoe')

    def test_get_sections_container(self):
        """Test get_sections_container method."""
        loader = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        sections = loader.get_sections_container()
        self.assertIn('professionalSummary', sections)
        self.assertEqual(sections, self.en_data['secoes'])

    def test_get_section(self):
        """Test get_section method."""
        loader = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        summary_section = loader.get_section(['professionalSummary', 'summary'])
        self.assertIsNotNone(summary_section)
        self.assertEqual(summary_section['title'], 'Professional Summary')
        
        non_existent_section = loader.get_section(['nonExistentSection', 'anotherMissing'])
        self.assertIsNone(non_existent_section)

    def test_get_section_title_content_list_jobs_skills(self):
        """Test various section data extraction methods."""
        loader = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        
        summary_data = loader.get_section(['professionalSummary'])
        self.assertEqual(loader.get_section_title(summary_data), "Professional Summary")
        self.assertEqual(loader.get_section_content(summary_data), "A brief summary.")
        
        experience_data = loader.get_section(['workExperience'])
        jobs = loader.get_jobs(experience_data)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['position'], "Engineer")
        # Test get_section_list on job description
        self.assertEqual(loader.get_section_list(jobs[0], list_keys=['descricao']), ["Desc1"])

        skills_data = loader.get_section(['technicalSkills'])
        skills = loader.get_skills(skills_data) # Uses get_section_list internally
        self.assertEqual(len(skills), 2)
        self.assertEqual(skills[0]['nome'], "Python")
        
        education_data = loader.get_section(['education'])
        # Test get_section_list with a different key
        degrees = loader.get_section_list(education_data, list_keys=['degrees', 'formacao'])
        self.assertEqual(len(degrees), 1)
        self.assertEqual(degrees[0], "BSc CS")


    def test_get_output_filename(self):
        """Test get_output_filename method."""
        # Case 1: outputFileName specified in JSON
        loader_en = DataLoader(language_code='en_mock', root_dir=self.test_root_dir)
        self.assertEqual(loader_en.get_output_filename(default_prefix="CV"), "CV_JohnDoe_EN_mock")

        # Case 2: outputFileName NOT specified in JSON, should use default prefix and name/lang
        loader_pt = DataLoader(language_code='pt_mock', root_dir=self.test_root_dir)
        # Expected: "Prefix_João Ninguém_pt_mock" -> "Prefix_João_Ninguém_pt_mock"
        self.assertEqual(loader_pt.get_output_filename(default_prefix="Curriculo"), "Curriculo_João_Ninguém_pt_mock")
        
        # Case 3: No name in data (should use "Anonimo")
        data_no_name = {"languageName": "NoNameLang"} # No 'nome' or 'name'
        no_name_path = os.path.join(self.test_root_dir, "curriculo_noname_mock.json")
        with open(no_name_path, 'w', encoding='utf-8') as f:
            json.dump(data_no_name, f)
        loader_no_name = DataLoader(language_code='noname_mock', root_dir=self.test_root_dir)
        self.assertEqual(loader_no_name.get_output_filename(default_prefix="CV"), "CV_Anonimo_noname_mock")
        os.remove(no_name_path) # Clean up

    def test_init_no_secoes_key(self):
        """Test DataLoader with JSON data that does not have a primary 'secoes' key."""
        flat_data = {
            "languageName": "Flat Mock", 
            "name": "Flat Stanley",
            "professionalSummary": {"title": "Flat Summary", "content": "I am flat."}
        }
        flat_json_path = os.path.join(self.test_root_dir, "curriculo_flat_mock.json")
        with open(flat_json_path, 'w', encoding='utf-8') as f:
            json.dump(flat_data, f)
        
        with mock.patch('sys.stdout', new_callable=unittest.mock.StringIO) as mock_stdout:
            loader = DataLoader(language_code='flat_mock', json_file_path=flat_json_path, root_dir=".")
            self.assertIsNotNone(loader.data)
            self.assertIsNone(loader._secoes_key) # No 'secoes', 'sections' etc.
            # Check for warning message
            self.assertIn("Warning: Main sections key", mock_stdout.getvalue())

            # Test that get_section can still find sections if they are at the root
            summary_section = loader.get_section(['professionalSummary'])
            self.assertIsNotNone(summary_section)
            self.assertEqual(summary_section['title'], "Flat Summary")
        
        os.remove(flat_json_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
