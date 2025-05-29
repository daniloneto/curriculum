"""
PDF CV Generator.

This module provides the PdfGenerator class, responsible for creating CVs
in PDF format. It uses data loaded by DataLoader and a specific PDF template
module to structure and style the document using ReportLab.
"""
import os
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch
from typing import List, Dict, Any, Callable, Optional, TYPE_CHECKING

from .base_generator import BaseCvGenerator

# Ensure parent directory is in path for utils import.
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import get_field  # Used for accessing specific fields in nested job items

if TYPE_CHECKING:
    from data_loader import DataLoader # For type hinting
    from reportlab.platypus.doctemplate import SimpleDocTemplate # For type hinting
    from reportlab.lib.styles import StyleSheet1 # For type hinting
    # Using 'Any' for template_module, can be replaced by a Protocol.
    from typing import Any as TemplateModuleType


class PdfGenerator(BaseCvGenerator):
    """
    Generates CVs in standard PDF format.

    Inherits from BaseCvGenerator and implements PDF-specific generation
    logic using ReportLab and a corresponding template module.

    Attributes:
        elements (List[Any]): A list to hold ReportLab Flowables for the PDF.
        doc (Optional[SimpleDocTemplate]): The ReportLab document template instance.
        styles (Optional[StyleSheet1]): StyleSheet object from ReportLab.
        pdf_filename (Optional[str]): Absolute path to the output PDF file.
                                      Set by `_setup_document`.
    """

    def __init__(self, data_loader: 'DataLoader', template_module: 'TemplateModuleType'):
        """
        Initializes the PdfGenerator.

        Args:
            data_loader (DataLoader): Instance providing CV data.
            template_module (TemplateModuleType): Loaded PDF template module with methods like
                                                  `create_document`, `get_styles`, `add_title`, etc.
        """
        super().__init__(data_loader, template_module)
        self.expected_extension: str = ".pdf"
        self.elements: List[Any] = []
        self.doc: Optional['SimpleDocTemplate'] = None
        self.styles: Optional['StyleSheet1'] = None
        self.pdf_filename: Optional[str] = None

    def _setup_document(self) -> None:
        """
        Initializes the PDF document, styles, and determines the output path.

        Uses the `_get_full_output_path` method from `BaseCvGenerator` to define
        `self.pdf_filename`. It then calls the template module's `create_document`
        and `get_styles` methods.
        """
        self.pdf_filename = self._get_full_output_path(
            default_prefix="Curriculo",
            extension=self.expected_extension
        )
        if not self.pdf_filename: # Should not happen if _get_full_output_path is correct
            raise ValueError("Output PDF filename could not be determined.")

        self.doc = self.template.create_document(self.pdf_filename)
        self.styles = self.template.get_styles()
        self.elements = []  # Reset elements for each generation call

    def _add_personal_info(self) -> None:
        """Adds personal information to the PDF elements list using the template."""
        if not self.styles:
            raise Exception("Styles not initialized. Call _setup_document first.")
        personal_info = self.loader.get_personal_info()
        self.template.add_title(
            self.elements,
            personal_info.get('name'),
            personal_info.get('email'),
            personal_info.get('phone'),
            personal_info.get('linkedin'),
            self.styles
        )

    def _add_section(
        self,
        section_key_variants: List[str],
        content_handler_func: Callable[[Dict[str, Any]], None],
        *handler_args: Any
    ) -> bool:
        """
        Adds a generic section to the PDF elements list if data for it exists.

        Args:
            section_key_variants (List[str]): Possible keys for the section in CV data.
            content_handler_func (Callable): Method to render the section's content
                                             (e.g., `_handle_resume_section`).
            *handler_args: Additional arguments for the content_handler_func.

        Returns:
            bool: True if the section was found and added, False otherwise.
        
        Raises:
            Exception: If styles or document are not initialized.
        """
        if not self.styles or not self.elements is not None: # self.elements can be empty list
             raise Exception("Document or styles not initialized. Call _setup_document first.")

        section_data = self.loader.get_section(section_key_variants)
        if section_data:
            self.template.add_section_title(
                self.elements, self.loader.get_section_title(section_data), self.styles
            )
            content_handler_func(section_data, *handler_args)
            self.elements.append(Spacer(1, 0.1 * inch))  # Spacer after each section
            return True
        return False

    def _handle_resume_section(self, section_data: Dict[str, Any]) -> None:
        """Handles content for the resume/summary section."""
        if not self.styles: return
        content = self.loader.get_section_content(section_data)
        self.elements.append(Paragraph(content, self.styles['normal']))

    def _handle_experience_section(self, section_data: Dict[str, Any]) -> None:
        """Handles content for the professional experience section."""
        if not self.styles: return
        jobs = self.loader.get_jobs(section_data)
        for job in jobs:
            position = get_field(job, 'cargo', 'position')
            if position:
                self.elements.append(Paragraph(f"• {str(position)}", self.styles['bullet']))

            period = get_field(job, 'periodo', 'period')
            if period:
                self.elements.append(Paragraph(str(period), self.styles['normal']))

            raw_desc = get_field(job, 'descricao', 'description', ['descripcion'])
            processed_items: List[str] = []
            if isinstance(raw_desc, str):
                processed_items = [s.strip() for s in raw_desc.splitlines() if s.strip()]
            elif isinstance(raw_desc, list):
                processed_items = [str(item).strip() for item in raw_desc if str(item).strip()]

            for item_text in processed_items:
                self.elements.append(Paragraph(f"- {item_text}", self.styles['bullet']))
            if jobs: # Add spacer only if there were jobs
                 self.elements.append(Spacer(1, 0.05 * inch))


    def _handle_skills_section(self, section_data: Dict[str, Any]) -> None:
        """Handles content for the skills section."""
        if not self.styles: return
        skills = self.loader.get_skills(section_data)  # Expects list of dicts
        for skill in skills:
            skill_name = get_field(skill, 'name', 'nome', ['nombre'])
            skill_level_str = get_field(skill, 'level', 'nivel')
            if skill_name and skill_level_str:
                try:
                    skill_level = int(str(skill_level_str))
                    self.template.add_skill_bar(
                        self.elements, str(skill_name), self.styles, skill_level
                    )
                except ValueError:
                    print(
                        f"Warning (PDF Gen): Invalid skill level for '{skill_name}'. "
                        f"Received '{skill_level_str}', expected an integer."
                    )
            elif skill_name: # Handle skills with name but no level (e.g. just list them)
                 self.elements.append(Paragraph(str(skill_name), self.styles.get('skill_item', self.styles['normal'])))


    def _handle_list_section(
        self,
        section_data: Dict[str, Any],
        list_keys: List[str],
        item_prefix: Optional[str] = None
    ) -> None:
        """Handles content for generic list-based sections."""
        if not self.styles: return
        items = self.loader.get_section_list(section_data, list_keys=list_keys)
        for item in items:
            text = f"{item_prefix}{str(item)}" if item_prefix else str(item)
            self.elements.append(Paragraph(text, self.styles['normal']))

    def _build_pdf(self) -> str:
        """
        Builds the PDF document from accumulated elements.

        Handles existing file renaming to prevent errors if the output file
        is locked or open.

        Returns:
            str: The absolute path to the generated PDF file.

        Raises:
            Exception: If `_setup_document` was not called, or if ReportLab's
                       `doc.build` fails.
        """
        if not self.doc or not self.pdf_filename:
            raise Exception("Document not setup. Call _setup_document first.")

        try:
            if os.path.exists(self.pdf_filename):
                try:
                    temp_name = self.pdf_filename + ".old"
                    if os.path.exists(temp_name):
                        os.remove(temp_name)
                    os.rename(self.pdf_filename, temp_name)
                    self.doc.build(self.elements)
                    if os.path.exists(temp_name):
                        os.remove(temp_name)
                except OSError as e_os:
                    print(
                        f"OS Error renaming/removing existing PDF (PDF Gen): {e_os}. "
                        "Attempting alternative filename."
                    )
                    base, ext = os.path.splitext(self.pdf_filename)
                    alternative_filename = base + "_new" + ext
                    # Re-initialize doc with new filename
                    self.doc = self.template.create_document(alternative_filename)
                    self.doc.build(self.elements)
                    self.pdf_filename = alternative_filename  # Update path
                except Exception as e_build:
                    print(f"Error during PDF build (after rename attempt): {e_build}")
                    # Try to restore original if rename was successful but build failed
                    if 'temp_name' in locals() and os.path.exists(temp_name) and \
                       not os.path.exists(self.pdf_filename):
                        os.rename(temp_name, self.pdf_filename)
                    raise
            else:
                self.doc.build(self.elements)
            return self.pdf_filename
        except Exception as e:
            # Catch-all for other ReportLab errors or unexpected issues
            print(f"Final error generating PDF: {str(e)}")
            raise

    def generate_cv(self) -> str:
        """
        Generates the PDF CV document.

        This orchestrates the CV generation: sets up the document, adds personal info,
        adds all standard sections, and then builds the PDF. The resulting file
        is saved in the `generated_cvs` directory.

        Returns:
            str: The absolute path to the generated PDF file.
        """
        self._setup_document()  # Sets self.pdf_filename (absolute path)
        self._add_personal_info()

        section_map = [
            (['resumoProfissional', 'professionalSummary', 'resumenProfesional', 'resumo'], self._handle_resume_section, []),
            (['experienciaProfissional', 'workExperience', 'experienciaLaboral'], self._handle_experience_section, []),
            # Page break is handled by template or explicitly called if needed
            (['habilidadesTecnicas', 'technicalSkills', 'competencesTechniques', 'habilidades'], self._handle_skills_section, []),
            (['certificacoes', 'certifications', 'certificaciones'], self._handle_list_section, [['lista', 'list', 'items'], "🏅 "]),
            (['educacao', 'education', 'educacion'], self._handle_list_section, [['formacao', 'degrees', 'formacion', 'diplomes', 'items']]),
            (['emAndamento', 'inProgress', 'enProgreso', 'enCours'], self._handle_list_section, [['cursos', 'courses', 'items']])
        ]

        has_added_major_section = False
        for keys, handler, args in section_map:
            if self._add_section(keys, handler, *args):
                has_added_major_section = True
            # Add page break before skills if experience was added and template supports it
            if keys[0].startswith('experiencia') and has_added_major_section and hasattr(self.template, 'add_page_break'):
                 self.template.add_page_break(self.elements)


        return self._build_pdf()


if __name__ == '__main__':
    # This block is for illustrative purposes.
    # Direct execution requires specific setup for DataLoader, template modules,
    # and accessible utils.py / data_loader.py.
    print(
        "PdfGenerator class defined. For testing, run the main CLI script "
        "(e.g., curriculo_pdf.py) or create dedicated unit/integration tests."
    )

    # Example of a more complete direct test (requires careful setup):
    # import json
    # from data_loader import DataLoader # Adjust relative path if necessary
    # from templates import TemplateManager # Adjust relative path
    #
    # print("\n--- Running PdfGenerator Direct Test Example ---")
    # # Ensure the test output base directory exists
    # test_output_base_dir = os.path.abspath(
    #    os.path.join(os.path.dirname(__file__), '..', '..', '_test_direct_run_output')
    # )
    # os.makedirs(test_output_base_dir, exist_ok=True)
    #
    # dummy_json_filename = "curriculo_test_direct_pdf.json"
    # dummy_json_path = os.path.join(test_output_base_dir, dummy_json_filename)
    # with open(dummy_json_path, "w", encoding="utf-8") as f:
    #     json.dump({
    #         "languageName": "TestishDirectPDF",
    #         "nome": "Direct PDF Tester", "email": "direct_pdf@test.com",
    #         "secoes": {
    #             "resumo": {"titulo": "Direct PDF Summary", "texto": "This is a direct PDF test."}
    #         }
    #     }, f)
    #
    # try:
    #     loader = DataLoader(
    #         language_code="test_direct_pdf",
    #         json_file_path=dummy_json_path, # Absolute path to dummy JSON
    #         root_dir=test_output_base_dir # Where generated_cvs will be created
    #     )
    #
    #     project_true_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    #     tm = TemplateManager(root_dir=project_true_root)
    #     pdf_template_module = tm.get_template('pdf') # Standard PDF template
    #
    #     generator = PdfGenerator(data_loader=loader, template_module=pdf_template_module)
    #     generated_file = generator.generate_cv()
    #     print(f"Generated test PDF at: {generated_file}")
    #
    #     assert os.path.exists(generated_file), "Generated PDF file not found."
    #     assert "generated_cvs" in generated_file, "File not in generated_cvs subdir."
    #     print("Direct test for PdfGenerator seems successful.")
    #
    # except Exception as e_test:
    #     print(f"Error during PdfGenerator direct test: {e_test}")
    #     import traceback
    #     traceback.print_exc()
    #
    # finally:
    #     if os.path.exists(dummy_json_path):
    #         os.remove(dummy_json_path)
    #     # Clean up generated_cvs for this specific test run if desired
    #     generated_cvs_path = os.path.join(test_output_base_dir, "generated_cvs")
    #     if os.path.exists(generated_cvs_path) and not os.listdir(generated_cvs_path):
    #         os.rmdir(generated_cvs_path)
    #     if os.path.exists(test_output_base_dir) and not os.listdir(test_output_base_dir):
    #          os.rmdir(test_output_base_dir)
    # print("--- PdfGenerator Direct Test Example Finished ---")
