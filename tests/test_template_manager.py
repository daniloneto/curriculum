import unittest
from unittest import mock
import os
import sys
import shutil
import importlib

# Adjust path to import TemplateManager from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from templates import TemplateManager

class TestTemplateManager(unittest.TestCase):
    """Test suite for the TemplateManager class."""

    @classmethod
    def setUpClass(cls):
        """Set up a temporary template directory and dummy template files."""
        cls.test_project_root = "_test_template_manager_project_root"
        cls.templates_dir_name = "test_templates_for_manager" # Custom name for test
        cls.actual_templates_path = os.path.join(cls.test_project_root, cls.templates_dir_name)
        os.makedirs(cls.actual_templates_path, exist_ok=True)

        # Create dummy template files
        cls.template_files_info = {
            "template_docx_default.py": "def create_document(): return 'docx_default_doc'",
            "template_pdf_simple.py": "def get_styles(): return {'style': 'simple_pdf_style'}",
            "template_pdf_ats_custom.py": "SOME_ATS_SETTING = True",
            "not_a_template.txt": "This is not a template.",
            "script_template_but_no_prefix.py": "def func(): pass" # Should not be picked up
        }
        for filename, content in cls.template_files_info.items():
            with open(os.path.join(cls.actual_templates_path, filename), 'w', encoding='utf-8') as f:
                f.write(content)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary template directory and files."""
        if os.path.exists(cls.test_project_root):
            shutil.rmtree(cls.test_project_root)

    def test_discover_templates(self):
        """Test the discovery of template files."""
        # Initialize TemplateManager pointing to our test templates directory
        manager = TemplateManager(template_dir=self.templates_dir_name, root_dir=self.test_project_root)
        
        discovered = manager.list_templates()
        self.assertIn("docx_default", discovered)
        self.assertIn("pdf_simple", discovered)
        self.assertIn("pdf_ats_custom", discovered)
        self.assertNotIn("not_a_template", discovered) # Based on .txt extension
        self.assertNotIn("script_template_but_no_prefix", discovered) # Based on filename prefix

        self.assertEqual(len(discovered), 3)

    def test_get_template_valid(self):
        """Test loading a valid template module."""
        manager = TemplateManager(template_dir=self.templates_dir_name, root_dir=self.test_project_root)
        
        template_module = manager.get_template("docx_default")
        self.assertIsNotNone(template_module)
        self.assertTrue(hasattr(template_module, 'create_document'))
        self.assertEqual(template_module.create_document(), 'docx_default_doc')

        template_module_pdf = manager.get_template("pdf_simple")
        self.assertIsNotNone(template_module_pdf)
        self.assertTrue(hasattr(template_module_pdf, 'get_styles'))
        self.assertEqual(template_module_pdf.get_styles(), {'style': 'simple_pdf_style'})
        
        template_module_ats = manager.get_template("pdf_ats_custom")
        self.assertIsNotNone(template_module_ats)
        self.assertTrue(hasattr(template_module_ats, 'SOME_ATS_SETTING'))
        self.assertTrue(template_module_ats.SOME_ATS_SETTING)


    def test_get_template_invalid(self):
        """Test attempting to load a non-existent template."""
        manager = TemplateManager(template_dir=self.templates_dir_name, root_dir=self.test_project_root)
        with self.assertRaises(ValueError) as context:
            manager.get_template("non_existent_template")
        self.assertIn("Template 'non_existent_template' not found.", str(context.exception))

    def test_get_template_import_error(self):
        """Test loading a template file that causes an import error (e.g., syntax error)."""
        # Create a temporary template file with a syntax error
        error_template_name = "template_syntax_error.py"
        error_template_path = os.path.join(self.actual_templates_path, error_template_name)
        with open(error_template_path, 'w', encoding='utf-8') as f:
            f.write("def some_func():\n  print 'this is python 2 syntax in python 3'") # Syntax error

        manager = TemplateManager(template_dir=self.templates_dir_name, root_dir=self.test_project_root)
        
        # The error during exec_module might be a SyntaxError or other ImportError subclass
        with self.assertRaises(ImportError) as context: # spec.loader.exec_module will raise
            manager.get_template("syntax_error")
        
        self.assertTrue("Failed to load template module 'syntax_error'" in str(context.exception) or
                        "invalid syntax" in str(context.exception).lower())

        os.remove(error_template_path) # Clean up

    def test_init_template_dir_not_found(self):
        """Test TemplateManager initialization with a non-existent template directory."""
        # Expect a warning print, but not necessarily an exception during init.
        # The available_templates list will be empty.
        with mock.patch('sys.stdout', new_callable=unittest.mock.StringIO) as mock_stdout:
            manager = TemplateManager(template_dir="non_existent_templates_dir", root_dir=self.test_project_root)
            self.assertEqual(manager.list_templates(), [])
            self.assertIn("Template directory 'non_existent_templates_dir' not found.", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main(verbosity=2)
