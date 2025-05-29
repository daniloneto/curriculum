import unittest
import os
import shutil
import sys

# Adjust path to import project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_loader import DataLoader
from templates import TemplateManager
from cv_generators.docx_generator import DocxGenerator
from cv_generators.pdf_generator import PdfGenerator
from cv_generators.pdf_ats_generator import PdfAtsGenerator

class TestCvGenerators(unittest.TestCase):
    """
    Test suite for the CV generator classes (DocxGenerator, PdfGenerator, PdfAtsGenerator).
    These tests focus on the generation process: file creation, path, and extension.
    """
    test_root_dir = "_test_generator_output"
    mock_data_source_dir = "tests/mock_data" # Where initial mock files are
    
    # Specific mock files to copy into test_root_dir for DataLoader to use
    # DataLoader expects curriculo_*.json files directly in its root_dir
    mock_files_to_copy = {
        "curriculo_en_mock.json": None, # Content will be loaded later
        "curriculo_pt_mock.json": None
    }

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for generator tests."""
        os.makedirs(cls.test_root_dir, exist_ok=True)
        
        # Load content from actual mock files
        for mock_file in cls.mock_files_to_copy:
            source_path = os.path.join(cls.mock_data_source_dir, mock_file)
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    cls.mock_files_to_copy[mock_file] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load mock data from {source_path}: {e}")
                # Fallback to minimal data if loading fails
                if "en" in mock_file:
                    cls.mock_files_to_copy[mock_file] = {"languageName": "English", "name": "Fallback EN"}
                elif "pt" in mock_file:
                     cls.mock_files_to_copy[mock_file] = {"languageName": "Portugues", "nome": "Fallback PT"}


        # Write these contents into curriculo_*.json files in test_root_dir for DataLoader
        for lang_code, data_content in [("en", cls.mock_files_to_copy["curriculo_en_mock.json"]), 
                                        ("pt", cls.mock_files_to_copy["curriculo_pt_mock.json"])]:
            if data_content: # Only write if content was loaded/fallbacked
                dest_path = os.path.join(cls.test_root_dir, f"curriculo_{lang_code}.json")
                with open(dest_path, 'w', encoding='utf-8') as f:
                    json.dump(data_content, f)
            else:
                print(f"Warning: No data to write for {lang_code} mock file in setUpClass.")


        # Initialize TemplateManager - assumes templates are in ../templates relative to this test file's dir
        cls.template_manager = TemplateManager(root_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after generator tests."""
        if os.path.exists(cls.test_root_dir):
            shutil.rmtree(cls.test_root_dir)
        # Also clean up generated_cvs from project root if tests put anything there
        # (BaseGenerator saves into self.loader.root_dir/generated_cvs)
        # For these tests, self.loader.root_dir will be cls.test_root_dir.
        # So, generated_cvs will be inside cls.test_root_dir.

    def _common_generator_test(self, generator_class, lang_code, template_name, expected_extension, default_prefix):
        """Helper method to run common tests for a generator."""
        # DataLoader will use files from self.test_root_dir
        data_loader = DataLoader(language_code=lang_code, root_dir=self.test_root_dir)
        
        try:
            template_module = self.template_manager.get_template(template_name)
        except ValueError as e:
            self.skipTest(f"Template '{template_name}' not found, skipping test: {e}")
            return

        generator = generator_class(data_loader, template_module)
        
        output_filepath = None # Ensure it's defined for finally block
        try:
            output_filepath = generator.generate_cv()

            self.assertIsInstance(output_filepath, str)
            self.assertTrue(os.path.isabs(output_filepath), "Path returned should be absolute.")
            self.assertTrue(os.path.exists(output_filepath), f"Generated file does not exist: {output_filepath}")
            
            # Check if file is in 'generated_cvs' subdirectory of the DataLoader's root_dir
            expected_output_dir = os.path.join(os.path.abspath(self.test_root_dir), "generated_cvs")
            self.assertTrue(
                output_filepath.startswith(expected_output_dir),
                f"File not in expected dir. Got: {output_filepath}, Expected in: {expected_output_dir}"
            )
            
            self.assertTrue(output_filepath.endswith(expected_extension), f"File extension mismatch. Expected {expected_extension}, Got {output_filepath}")

            # Verify filename structure (e.g., Prefix_Name_Lang.ext)
            # DataLoader's get_output_filename creates the base name.
            # Example: CV_JohnDoe_EN_mock for english mock data.
            # The generator then adds the extension.
            # If outputFileName is in JSON, that's used.
            # self.mock_files_to_copy["curriculo_en_mock.json"]["outputFileName"] is "CV_JohnDoe_EN_mock"
            
            if lang_code == "en":
                expected_basename_part = self.mock_files_to_copy["curriculo_en_mock.json"].get("outputFileName", "CV_JohnDoe_EN_mock")
            elif lang_code == "pt":
                expected_basename_part = self.mock_files_to_copy["curriculo_pt_mock.json"].get("outputFileName", f"{default_prefix}_João_Ninguém_{lang_code}")
            else: # Fallback if more languages are tested
                expected_basename_part = f"{default_prefix}_Unknown_{lang_code}"

            # If it's ATS, ensure the _ATS suffix is present
            if "ats" in template_name.lower() and "_ATS" not in expected_basename_part :
                 if default_prefix.endswith("_ATS"): # if default_prefix already has it from ATS generator
                     pass
                 else: # if base name from JSON doesn't have it, ATS generator should add it
                     expected_basename_part += "_ATS"
            
            self.assertIn(expected_basename_part, os.path.basename(output_filepath))

        finally:
            # Clean up the specific generated file
            if output_filepath and os.path.exists(output_filepath):
                os.remove(output_filepath)

    # --- DocxGenerator Tests ---
    def test_docx_generator_en(self):
        """Test DocxGenerator with English mock data."""
        self._common_generator_test(DocxGenerator, "en", "docx", ".docx", default_prefix="Curriculo")

    def test_docx_generator_pt_modern_template(self):
        """Test DocxGenerator with Portuguese mock data and a specific docx template (if one exists)."""
        # Assuming a 'docx_moderno' template might exist. If not, this test will be skipped.
        self._common_generator_test(DocxGenerator, "pt", "docx_moderno", ".docx", default_prefix="Curriculo")

    # --- PdfGenerator Tests ---
    def test_pdf_generator_en(self):
        """Test PdfGenerator with English mock data and default PDF template."""
        self._common_generator_test(PdfGenerator, "en", "pdf", ".pdf", default_prefix="Curriculo")

    def test_pdf_generator_pt_modern_template(self):
        """Test PdfGenerator with Portuguese mock data and 'pdf_moderno' template."""
        self._common_generator_test(PdfGenerator, "pt", "pdf_moderno", ".pdf", default_prefix="Curriculo")

    # --- PdfAtsGenerator Tests ---
    def test_pdf_ats_generator_en(self):
        """Test PdfAtsGenerator with English mock data."""
        # The default_prefix for PdfAtsGenerator in its _setup_document is "Curriculo_ATS"
        self._common_generator_test(PdfAtsGenerator, "en", "pdf_ats", ".pdf", default_prefix="Curriculo_ATS")
    
    def test_pdf_ats_generator_pt(self):
        """Test PdfAtsGenerator with Portuguese mock data."""
        self._common_generator_test(PdfAtsGenerator, "pt", "pdf_ats", ".pdf", default_prefix="Curriculo_ATS")


if __name__ == '__main__':
    # Important: Ensure that the script is run from the project root directory
    # for TemplateManager and DataLoader to correctly resolve paths to templates and data.
    # Example: python -m unittest tests.test_generators
    unittest.main(verbosity=2)
