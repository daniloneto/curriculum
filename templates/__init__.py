"""
Template Management for CV Generation.

This module provides the `TemplateManager` class, responsible for discovering,
loading, and managing different CV template modules. Templates are expected
to be Python files located within a specified template directory (by default,
'templates/') and follow a naming convention (e.g., `template_docx.py`,
`template_pdf_moderno.py`). Each template module should define functions
and configurations necessary for generating a CV in a specific format and style.
"""
import os
import glob
import importlib.util
from typing import Dict, List, Optional, Any

# Using 'Any' for the return type of get_template, as it's a module object.
# A more specific Protocol could be defined if template modules adhere to a strict interface.
TemplateModuleType = Any


class TemplateManager:
    """
    Manages the discovery and loading of CV template modules.

    Scans a specified directory for template files (Python modules) and provides
    methods to list available templates and load a specific template module
    dynamically.

    Attributes:
        template_dir (str): The directory where template modules are stored.
        available_templates (Dict[str, Dict[str, str]]):
            A dictionary mapping template names to their details (name and file path).
    """

    def __init__(self, template_dir: str = 'templates', root_dir: Optional[str] = None):
        """
        Initializes the TemplateManager.

        Args:
            template_dir (str): The name of the directory containing template modules.
                                This path is considered relative to `root_dir`.
                                Defaults to 'templates'.
            root_dir (Optional[str]): The root directory of the project. If None,
                                      os.getcwd() is used. This is used to construct
                                      an absolute path to the template directory.
                                      Defaults to None.
        """
        if root_dir is None:
            # If no root_dir is provided, assume the templates directory is relative
            # to the current working directory, or adjust as per project structure.
            # For this project, templates are typically at 'project_root/templates'.
            # If this __init__.py is in 'project_root/templates', then template_dir
            # could be '.', or for 'project_root/templates', it's 'templates'.
            # Let's assume this class is instantiated from project root.
            effective_root_dir = os.getcwd()
        else:
            effective_root_dir = os.path.abspath(root_dir)

        self.template_dir: str = os.path.join(effective_root_dir, template_dir)
        self.available_templates: Dict[str, Dict[str, str]] = self._discover_templates()

    def _discover_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Discovers all available template modules in the template directory.

        Template modules are expected to be Python files named `template_*.py`.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary mapping template names
                                       (e.g., 'docx', 'pdf_moderno') to their details.
        """
        templates: Dict[str, Dict[str, str]] = {}

        if not os.path.isdir(self.template_dir):
            print(f"Warning: Template directory '{self.template_dir}' not found.")
            return templates

        # Find all files matching the pattern 'template_*.py'
        template_files = glob.glob(os.path.join(self.template_dir, 'template_*.py'))

        for template_file_path in template_files:
            file_name = os.path.basename(template_file_path)
            # Extract template name: template_xxx.py -> xxx
            # (e.g., template_docx.py -> docx; template_pdf_moderno.py -> pdf_moderno)
            if file_name.startswith('template_') and file_name.endswith('.py'):
                template_name = file_name[len('template_'):-len('.py')]
                templates[template_name] = {
                    'name': template_name,
                    'file': os.path.abspath(template_file_path)
                }
        return templates

    def get_template(self, template_name: str) -> TemplateModuleType:
        """
        Loads and returns a specific template module by its name.

        Args:
            template_name (str): The name of the template to load
                                 (e.g., 'docx', 'pdf_moderno').

        Returns:
            TemplateModuleType: The loaded Python module for the specified template.

        Raises:
            ValueError: If the template_name is not found among available templates.
            ImportError: If the template module cannot be loaded.
        """
        if template_name not in self.available_templates:
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available: {', '.join(self.list_templates())}"
            )

        template_info = self.available_templates[template_name]
        template_file_path = template_info['file']
        module_name = f"templates.template_{template_name}" # Standard module naming

        try:
            spec = importlib.util.spec_from_file_location(module_name, template_file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create module spec for {template_name} from {template_file_path}")

            template_module = importlib.util.module_from_spec(spec)
            # Add module to sys.modules to allow relative imports within the template if needed
            # sys.modules[module_name] = template_module # Usually not necessary for simple templates
            spec.loader.exec_module(template_module)
        except Exception as e:
            # Catch any exception during module loading and re-raise as ImportError for clarity
            raise ImportError(
                f"Failed to load template module '{template_name}' from '{template_file_path}': {e}"
            ) from e

        return template_module

    def list_templates(self) -> List[str]:
        """
        Lists the names of all discovered and available templates.

        Returns:
            List[str]: A list of template names (e.g., ['docx', 'pdf_moderno']).
        """
        return list(self.available_templates.keys())


if __name__ == '__main__':
    # Example usage when running this module directly (e.g., for testing discovery)
    print("--- Testing TemplateManager ---")
    # Assuming this script is in 'project_root/templates/__init__.py'
    # and template files are in 'project_root/templates/template_*.py'
    # For direct execution, root_dir should point to the project root.
    project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Create dummy template files for testing discovery
    dummy_template_dir = os.path.join(project_root_dir, "templates") # Ensure it's 'templates'
    os.makedirs(dummy_template_dir, exist_ok=True)

    dummy_templates_to_create = {
        "template_testone.py": "# Dummy template one",
        "template_test_two.py": "# Dummy template two",
        "not_a_template.txt": "Ignore me",
        "other_script.py": "# Not a template module"
    }
    for fname, content in dummy_templates_to_create.items():
        with open(os.path.join(dummy_template_dir, fname), "w", encoding="utf-8") as f:
            f.write(content)

    print(f"TemplateManager initialized with template_dir='{dummy_template_dir}' "
          f"(resolved from root_dir='{project_root_dir}')")
    
    # Pass root_dir explicitly if TemplateManager is not in project root itself
    manager = TemplateManager(template_dir='templates', root_dir=project_root_dir)

    print("\nAvailable templates:")
    template_list = manager.list_templates()
    print(template_list)

    assert "testone" in template_list, "Template 'testone' not found."
    assert "test_two" in template_list, "Template 'test_two' not found."
    assert "not_a_template" not in template_list
    assert "other_script" not in template_list # Should not be picked up

    if "testone" in template_list:
        try:
            print("\nLoading template 'testone':")
            testone_module = manager.get_template('testone')
            print(f"Successfully loaded module: {testone_module}")
            # Add more checks if dummy module had functions/attributes
        except Exception as e:
            print(f"Error loading 'testone': {e}")

    # Clean up dummy files
    for fname in dummy_templates_to_create:
        try:
            os.remove(os.path.join(dummy_template_dir, fname))
        except OSError:
            pass # Ignore if file was not created or already removed
    
    # Remove dummy_template_dir if it was created by this test and is empty
    # (Be careful if 'templates' is your actual template directory)
    # For a real test suite, use a dedicated temporary directory.

    print("\n--- TemplateManager test finished ---")
