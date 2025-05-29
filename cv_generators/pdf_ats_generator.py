"""
ATS-Optimized PDF CV Generator.

This module provides the `PdfAtsGenerator` class, which is responsible for
creating CVs in PDF format, specifically optimized for Applicant Tracking Systems (ATS).
It leverages data loaded by `DataLoader` and an ATS-specific PDF template module.
Key features include keyword extraction and a simplified, parseable layout.
"""
import os
import re
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
    from reportlab.platypus.doctemplate import SimpleDocTemplate
    from reportlab.lib.styles import StyleSheet1
    from typing import Any as TemplateModuleType


class PdfAtsGenerator(BaseCvGenerator):
    """
    Generates CVs in PDF format, optimized for Applicant Tracking Systems (ATS).

    Inherits from `BaseCvGenerator` and implements PDF generation logic
    tailored for ATS compatibility. This includes keyword extraction and
    a clean, easily parsable structure.

    Attributes:
        elements (List[Any]): ReportLab Flowables for the PDF.
        doc (Optional[SimpleDocTemplate]): ReportLab document template.
        styles (Optional[StyleSheet1]): ReportLab StyleSheet object.
        pdf_filename (Optional[str]): Absolute path to the output PDF.
        keywords (List[str]): List of keywords extracted from the CV content.
    """

    def __init__(self, data_loader: 'DataLoader', template_module: 'TemplateModuleType'):
        """
        Initializes the PdfAtsGenerator.

        Args:
            data_loader (DataLoader): Instance providing CV data.
            template_module (TemplateModuleType): Loaded ATS-specific PDF template module.
        """
        super().__init__(data_loader, template_module)
        self.expected_extension: str = ".pdf"
        self.elements: List[Any] = []
        self.doc: Optional['SimpleDocTemplate'] = None
        self.styles: Optional['StyleSheet1'] = None
        self.pdf_filename: Optional[str] = None
        self.keywords: List[str] = []

    def _extract_keywords_from_resume(
        self,
        resume_text: Optional[str],
        min_length: int = 4
    ) -> None:
        """
        Extracts keywords from resume text and populates `self.keywords`.

        Keywords are typically nouns and verbs relevant to job descriptions.
        This implementation uses a generic stopword list; for better results,
        language-specific stopwords from `self.loader.language_code` could be used.

        Args:
            resume_text (Optional[str]): The text of the professional summary/resume.
            min_length (int): Minimum length for a word to be considered a keyword.
                              Defaults to 4.
        """
        if not resume_text:
            self.keywords = []
            return

        cleaned_text = re.sub(r'[^\w\s]', ' ', resume_text.lower())
        words = cleaned_text.split()

        # Generic stopwords. Consider enhancing with language-specific lists.
        stopwords = [
            "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com",
            "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como",
            "mas", "foi", "ao", "ele", "das", "tem", "seu", "sua", "ou", "ser", "quando",
            "muito", "nos", "já", "está", "eu", "também", "só", "pelo", "pela", "até",
            "isso", "ela", "entre", "era", "depois", "sem", "mesmo", "aos", "ter", "seus",
            "quem", "nas", "me", "esse", "eles", "estão", "você", "tinha", "foram", "essa",
            "num", "nem", "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas",
            "havia", "seja", "qual", "será", "nós", "tenho", "lhe", "deles", "essas",
            "esses", "pelas", "este", "fosse", "dele", "tu", "te", "vocês", "vos", "lhes",
            "meus", "minhas", "teu", "tua", "teus", "tuas", "nosso", "nossa", "nossos",
            "nossas", "dela", "delas", "esta", "estes", "estas", "the", "is", "in", "and",
            "to", "of", "it", "for", "with", "an", "are", "on", "that", "this", "was"
        ] # Expanded slightly

        filtered_words = [
            word for word in words if len(word) >= min_length and word not in stopwords
        ]

        word_freq: Dict[str, int] = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and take top N (e.g., 20)
        sorted_words = sorted(word_freq.items(), key=lambda item: item[1], reverse=True)
        self.keywords = [word for word, freq in sorted_words[:20]]

    def _setup_document(self) -> None:
        """
        Initializes the PDF document, styles, and determines the output path for ATS.
        Ensures the filename includes an "_ATS" suffix.
        """
        self.pdf_filename = self._get_full_output_path(
            default_prefix="Curriculo_ATS",  # Specific prefix for ATS
            extension=self.expected_extension
        )
        
        # Ensure "_ATS" suffix is correctly placed if not handled by get_output_filename
        base_name, ext = os.path.splitext(os.path.basename(self.pdf_filename))
        if not base_name.endswith("_ATS"):
            # This logic might be too aggressive if get_output_filename already appends language code.
            # Example: Curriculo_ATS_JohnDoe_en_ATS.pdf vs Curriculo_JohnDoe_en_ATS.pdf
            # The _get_full_output_path should ideally handle prefixing correctly.
            # For now, let's assume get_output_filename with "Curriculo_ATS" as prefix is primary.
            # If the loader's `get_output_filename` with "Curriculo_ATS" prefix
            # doesn't result in a name ending with _ATS (e.g. if outputFileName was in json)
            # then we ensure it here.
            if not self.loader.get_output_filename(default_prefix="").endswith("_ATS"): # Check if specific json name had it
                 output_dir = os.path.dirname(self.pdf_filename)
                 self.pdf_filename = os.path.join(output_dir, f"{base_name}_ATS{ext}")


        self.doc = self.template.create_document(self.pdf_filename)
        self.styles = self.template.get_styles()
        self.elements = []

    def _add_personal_info(self) -> None:
        """Adds personal information to the PDF elements list."""
        if not self.styles:
            raise Exception("Styles not initialized. Call _setup_document first.")
        pi = self.loader.get_personal_info()
        self.template.add_title(
            self.elements, pi.get('name'), pi.get('email'),
            pi.get('phone'), pi.get('linkedin'), self.styles
        )

    def _add_section(
        self,
        section_key_variants: List[str],
        content_handler_func: Callable[[Dict[str, Any]], None],
        *handler_args: Any
    ) -> bool:
        """
        Adds a generic section to the PDF elements list.

        Args:
            section_key_variants: Possible keys for the section.
            content_handler_func: Method to render the section's content.
            *handler_args: Additional arguments for the content_handler_func.

        Returns:
            True if section added, False otherwise.
        """
        if not self.styles or self.elements is None:
             raise Exception("Document or styles not initialized.")

        section_data = self.loader.get_section(section_key_variants)
        if section_data:
            self.template.add_section_title(
                self.elements, self.loader.get_section_title(section_data), self.styles
            )
            content_handler_func(section_data, *handler_args)
            self.elements.append(Spacer(1, 0.1 * inch))
            return True
        return False

    def _handle_resume_section(self, section_data: Dict[str, Any]) -> None:
        """Handles the resume/summary section and extracts keywords."""
        if not self.styles: return
        resume_text = self.loader.get_section_content(section_data)
        self._extract_keywords_from_resume(resume_text) # Populates self.keywords
        self.elements.append(Paragraph(resume_text, self.styles['normal']))

    def _handle_experience_section(self, section_data: Dict[str, Any]) -> None:
        """Handles the professional experience section for ATS PDF."""
        if not self.styles: return
        jobs = self.loader.get_jobs(section_data)
        current_lang = self.loader.language_code

        for job in jobs:
            position_raw = get_field(job, 'cargo', 'position')
            period = get_field(job, 'periodo', 'period')
            position = str(position_raw) if position_raw else ""
            company = str(get_field(job, 'empresa', 'company'))

            if not company and position_raw and ' - ' in position:
                parts = position.split(' - ', 1)
                position, company = parts[0].strip(), parts[1].strip()
            elif not company:
                company = ""

            desc_content = get_field(job, 'descricao', 'description', ['descripcion'])
            
            # Attempt to get localized labels from the template
            labels = {}
            if hasattr(self.template, 'get_default_labels'):
                labels = self.template.get_default_labels(current_lang)


            if hasattr(self.template, 'add_job_experience'):
                self.template.add_job_experience(
                    self.elements, position, company, period, desc_content, self.styles, labels
                )
            else:  # Fallback rendering if template method is missing
                if position:
                    self.elements.append(Paragraph(
                        f"<b>{labels.get('position', 'Position')}:</b> {position}", self.styles['bullet']
                    ))
                if company:
                    self.elements.append(Paragraph(
                        f"<b>{labels.get('company', 'Company')}:</b> {company}", self.styles['normal']
                    ))
                if period:
                    self.elements.append(Paragraph(
                        f"<b>{labels.get('period', 'Period')}:</b> {str(period)}", self.styles['normal']
                    ))
                if desc_content:
                    self.elements.append(Paragraph(
                        f"<b>{labels.get('description_heading', 'Responsibilities')}:</b>", self.styles['normal']
                    ))
                    items = []
                    if isinstance(desc_content, str):
                        items = [s.strip() for s in desc_content.splitlines() if s.strip()]
                    elif isinstance(desc_content, list):
                        items = [str(i).strip() for i in desc_content if str(i).strip()]
                    for item in items:
                        self.elements.append(Paragraph(f"- {item}", self.styles['bullet']))
            self.elements.append(Spacer(1, 0.05 * inch))

    def _handle_skills_section(self, section_data: Dict[str, Any]) -> None:
        """Handles the skills section, adding skill names to keywords."""
        if not self.styles: return
        skills = self.loader.get_skills(section_data) # Expects list of dicts
        for skill_item in skills:
            # Prioritize 'nombre' or 'name' for ATS keyword extraction
            skill_name = str(get_field(skill_item, 'nombre', 'name', ['skillName']))
            skill_level_str = str(get_field(skill_item, 'nivel', 'level'))

            if skill_name:
                if skill_name not in self.keywords:
                    self.keywords.append(skill_name)
                
                if hasattr(self.template, 'add_skill'):
                    try:
                        skill_level = int(skill_level_str) if skill_level_str and skill_level_str.isdigit() else 0
                        self.template.add_skill(
                            self.elements, skill_name, self.styles, skill_level, lang=self.loader.language_code
                        )
                    except ValueError: # If skill_level_str is not a valid int string
                        self.template.add_skill(
                             self.elements, skill_name, self.styles, 0, lang=self.loader.language_code
                        )
                else: # Basic fallback if template doesn't have add_skill
                    level_display = f" ({skill_level_str})" if skill_level_str else ""
                    self.elements.append(Paragraph(f"{skill_name}{level_display}", self.styles['normal']))


    def _handle_list_section(
        self,
        section_data: Dict[str, Any],
        list_keys: List[str],
        item_prefix: Optional[str] = None # item_prefix is ignored for ATS for cleaner parsing
    ) -> None:
        """Handles generic list sections, adding items to keywords."""
        if not self.styles: return
        items = self.loader.get_section_list(section_data, list_keys=list_keys)
        for item_raw in items:
            item = str(item_raw) # Ensure string
            self.elements.append(Paragraph(item, self.styles['normal']))
            if item not in self.keywords:
                self.keywords.append(item)

    def _add_keywords_to_document(self) -> None:
        """Adds a consolidated, sorted list of keywords to the document if template supports it."""
        if self.keywords and hasattr(self.template, 'add_keywords_section'):
            final_keywords = sorted(list(set(self.keywords))) # Deduplicate and sort
            self.template.add_keywords_section(self.elements, final_keywords, self.styles)

    def _build_pdf(self) -> str:
        """
        Builds the PDF document and returns the absolute path.
        Handles existing file renaming.
        """
        if not self.doc or not self.pdf_filename:
            raise Exception("Document not setup. Call _setup_document first.")
        try:
            if os.path.exists(self.pdf_filename):
                try:
                    temp_name = self.pdf_filename + ".old"
                    if os.path.exists(temp_name): os.remove(temp_name)
                    os.rename(self.pdf_filename, temp_name)
                    self.doc.build(self.elements)
                    if os.path.exists(temp_name): os.remove(temp_name)
                except OSError as e_os:
                    base, ext = os.path.splitext(self.pdf_filename)
                    alternative_filename = base + "_new_ats" + ext # Ensure unique alternate name
                    self.doc = self.template.create_document(alternative_filename)
                    self.doc.build(self.elements)
                    self.pdf_filename = alternative_filename
                except Exception as e_build:
                    if 'temp_name' in locals() and os.path.exists(temp_name) and \
                       not os.path.exists(self.pdf_filename):
                        os.rename(temp_name, self.pdf_filename) # Restore if build failed
                    raise
            else:
                self.doc.build(self.elements)
            return self.pdf_filename # Absolute path
        except Exception as e:
            print(f"Final error generating ATS PDF: {str(e)}")
            raise

    def generate_cv(self) -> str:
        """
        Generates the ATS-optimized PDF CV.

        Orchestrates document setup, content addition (including keyword extraction),
        and final PDF build. Saves the file to the `generated_cvs` directory.

        Returns:
            str: The absolute path to the generated ATS PDF file.
        """
        self._setup_document() # Sets self.pdf_filename (absolute path)
        self._add_personal_info()

        # Order of sections can be important for ATS parsing effectiveness
        self._add_section(
            ['resumoProfissional', 'professionalSummary', 'resumenProfesional', 'resumo'],
            self._handle_resume_section
        )
        
        # Optional: Page break after summary or before skills, if template supports
        if self.elements and hasattr(self.template, 'add_page_break'):
            self.template.add_page_break(self.elements)
        
        self._add_section(
            ['habilidadesTecnicas', 'technicalSkills', 'competencias', 'habilidades'],
            self._handle_skills_section # Adds skill names to self.keywords
        )
        self._add_section(
            ['experienciaProfissional', 'workExperience', 'experienciaLaboral'],
            self._handle_experience_section
        )
        self._add_section(
            ['educacao', 'education', 'educacion'],
            self._handle_list_section, ['formacao', 'degrees', 'diplomes', 'items']
        )
        self._add_section(
            ['certificacoes', 'certifications', 'certificaciones'],
            self._handle_list_section, ['lista', 'list', 'items']
        )
        self._add_section(
            ['emAndamento', 'inProgress', 'enProgreso', 'enCours'],
            self._handle_list_section, ['cursos', 'courses', 'items']
        )
        
        self._add_keywords_to_document() # Add the compiled keywords section at the end
        
        return self._build_pdf()


if __name__ == '__main__':
    # This block is for illustrative purposes.
    # Direct execution requires careful setup of paths, DataLoader, template modules.
    print(
        "PdfAtsGenerator class defined. For testing, run the main CLI script "
        "(e.g., curriculo_pdf_ats.py) or create dedicated unit/integration tests."
    )

    # Example of a more complete direct test (requires careful setup):
    # import json
    # from data_loader import DataLoader # Adjust path if necessary
    # from templates import TemplateManager # Adjust path
    #
    # print("\n--- Running PdfAtsGenerator Direct Test Example ---")
    # test_output_base_dir = os.path.abspath(
    #    os.path.join(os.path.dirname(__file__), '..', '..', '_test_direct_run_output')
    # )
    # os.makedirs(test_output_base_dir, exist_ok=True)
    #
    # dummy_json_filename = "curriculo_test_direct_ats.json"
    # dummy_json_path = os.path.join(test_output_base_dir, dummy_json_filename)
    # with open(dummy_json_path, "w", encoding="utf-8") as f:
    #     json.dump({
    #         "languageName": "TestishDirectATS", "nome": "Direct ATS Tester",
    #         "email": "direct_ats@test.com", "outputFileName": "MyCustomATS.pdf",
    #         "secoes": {
    #             "resumoProfissional": {"titulo": "ATS Summary", "texto": "Relevant keyword1 and keyword2."},
    #             "habilidadesTecnicas": {"titulo": "ATS Skills", "habilidades": [{"nome": "Parsing", "nivel": "5"}]}
    #         }
    #     }, f)
    #
    # try:
    #     loader = DataLoader(
    #         language_code="test_direct_ats",
    #         json_file_path=dummy_json_path,
    #         root_dir=test_output_base_dir
    #     )
    #
    #     project_true_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    #     tm = TemplateManager(root_dir=project_true_root)
    #     pdf_ats_template_module = tm.get_template('pdf_ats') # Standard ATS PDF template
    #
    #     generator = PdfAtsGenerator(data_loader=loader, template_module=pdf_ats_template_module)
    #     generated_file = generator.generate_cv()
    #     print(f"Generated test ATS PDF at: {generated_file}")
    #
    #     assert os.path.exists(generated_file), "Generated ATS PDF file not found."
    #     assert "_ATS" in os.path.basename(generated_file), "Filename does not contain '_ATS'."
    #     assert "generated_cvs" in generated_file, "File not in generated_cvs subdir."
    #     print("Direct test for PdfAtsGenerator seems successful.")
    #
    # except Exception as e_test:
    #     print(f"Error during PdfAtsGenerator direct test: {e_test}")
    #     import traceback
    #     traceback.print_exc()
    #
    # finally:
    #     if os.path.exists(dummy_json_path):
    #         os.remove(dummy_json_path)
    #     # Clean up generated_cvs for this specific test run
    #     generated_cvs_path = os.path.join(test_output_base_dir, "generated_cvs")
    #     # Be cautious with recursive delete; ensure it's the correct, temporary path
    #     # For safety, only remove if it's empty or remove specific file
    #     if os.path.exists(generated_file) : os.remove(generated_file)
    #     if os.path.exists(generated_cvs_path) and not os.listdir(generated_cvs_path):
    #         os.rmdir(generated_cvs_path)
    #     if os.path.exists(test_output_base_dir) and not os.listdir(test_output_base_dir):
    #          os.rmdir(test_output_base_dir)
    # print("--- PdfAtsGenerator Direct Test Example Finished ---")
