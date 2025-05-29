"""
Defines the Abstract Base Class (ABC) for CV generators.

This module provides `BaseCvGenerator`, an ABC that establishes a common
interface for all CV generator classes. It mandates the implementation
of a `generate_cv` method and provides utility methods for managing
output file paths and directories, ensuring that generated CVs are
saved to a consistent location (`generated_cvs` subdirectory).
"""
import abc
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data_loader import DataLoader # For type hinting
    # Assuming template_module is a module object, which is hard to type precisely
    # without knowing its structure. Using 'Any' or a more generic type if available.
    from typing import Any as TemplateModuleType


class BaseCvGenerator(abc.ABC):
    """
    Abstract Base Class for CV generators.

    Defines a common interface for generating different CV formats and provides
    helper methods for output path management.

    Attributes:
        loader (DataLoader): An instance of DataLoader providing CV data.
        template (TemplateModuleType): The loaded template module specific to the CV format.
        expected_extension (str): The expected file extension for the generated CV
                                  (e.g., ".pdf", ".docx"). Must be set by subclasses.
    """

    def __init__(self, data_loader: 'DataLoader', template_module: 'TemplateModuleType'):
        """
        Initializes the BaseCvGenerator.

        Args:
            data_loader (DataLoader): An instance of DataLoader providing CV data.
            template_module (TemplateModuleType): The loaded template module specific
                                                  to the CV format being generated.
        """
        self.loader: 'DataLoader' = data_loader
        self.template: 'TemplateModuleType' = template_module
        self.expected_extension: str = ""  # Must be set by concrete subclasses

    @abc.abstractmethod
    def generate_cv(self) -> str:
        """
        Generates the CV document and saves it to a file.

        This method must be implemented by concrete subclasses. It should handle
        the specifics of creating the document in the target format, saving it,
        and returning the path to the saved file.

        Returns:
            str: The absolute path to the generated CV file.
        """
        pass

    def _ensure_output_directory(
        self,
        base_dir: str,
        sub_dir_name: str = "generated_cvs"
    ) -> str:
        """
        Ensures the output directory exists and returns its absolute path.

        The directory is created under `base_dir/sub_dir_name`.

        Args:
            base_dir (str): The base directory, typically the project root
                            (obtained from `self.loader.root_dir`).
            sub_dir_name (str): The name of the subdirectory for generated CVs.
                                Defaults to "generated_cvs".

        Returns:
            str: The absolute path to the output directory.
        """
        abs_base_dir = os.path.abspath(base_dir)
        output_dir = os.path.join(abs_base_dir, sub_dir_name)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except OSError as e:
                print(f"Error creating output directory {output_dir}: {e}")
                # Fallback or re-raise depending on desired error handling
                # For now, let's assume if it fails, subsequent save will fail.
                # Or, could raise an exception here.
                raise
        return output_dir

    def _get_full_output_path(self, default_prefix: str, extension: str) -> str:
        """
        Constructs the full absolute path for the output file.

        The path will be located within the `generated_cvs` subdirectory of the
        `self.loader.root_dir`. The filename is determined by
        `self.loader.get_output_filename()` or a default.

        Args:
            default_prefix (str): The default prefix for the filename if not specified
                                  in the loaded CV data (e.g., "Curriculo", "CV_ATS").
            extension (str): The file extension including the dot (e.g., ".docx", ".pdf").

        Returns:
            str: The absolute path for the output file.

        Raises:
            ValueError: If `self.loader.root_dir` is not set or if the extension format is incorrect.
        """
        if not self.loader.root_dir:
            raise ValueError("DataLoader's root_dir is not set. Cannot determine output path.")
        if not extension or not extension.startswith('.'):
            raise ValueError(f"Invalid extension format: '{extension}'. Must start with a dot.")

        # Get base filename from DataLoader (this name usually incorporates language, user name etc.)
        filename_base_from_loader = self.loader.get_output_filename(default_prefix=default_prefix)

        # Ensure the base name doesn't inadvertently contain path separators or unwanted extensions
        # os.path.basename is used to be safe, although get_output_filename should return a clean base
        clean_base_name = os.path.basename(os.path.splitext(filename_base_from_loader)[0])

        final_filename = clean_base_name + extension

        # Determine the output directory using the loader's root_dir
        output_dir = self._ensure_output_directory(base_dir=self.loader.root_dir)

        absolute_path = os.path.join(output_dir, final_filename)
        return absolute_path


if __name__ == '__main__':
    # This block is for illustrative purposes and basic checks.
    # More comprehensive testing would involve mock objects and a test framework.
    print("BaseCvGenerator class defined.")

    # Example of how a subclass might use it (conceptual)
    class _MockLoader:
        """A simplified mock DataLoader for testing BaseCvGenerator."""
        def __init__(self, root_path: str, lang_code: str = "en"):
            self.root_dir = os.path.abspath(root_path)
            self.language_code = lang_code

        def get_output_filename(self, default_prefix: str = "Default") -> str:
            return f"{default_prefix}_MockName_{self.language_code}" # No extension

    class _MyTestGenerator(BaseCvGenerator):
        """A concrete test generator inheriting from BaseCvGenerator."""
        def __init__(self, data_loader: '_MockLoader', template_module: 'TemplateModuleType'):
            super().__init__(data_loader, template_module)
            self.expected_extension = ".txt" # Set the expected extension

        def generate_cv(self) -> str:
            """Generates a simple text CV for testing."""
            # Use the helper from BaseCvGenerator to get the output path
            path = self._get_full_output_path(
                default_prefix="MyCVTest",
                extension=self.expected_extension
            )
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("Hello CV from MyTestGenerator")
                print(f"Test CV generated at: {path}")
            except IOError as e:
                print(f"Error writing test CV file: {e}")
                raise
            return path

    # Setup for a quick test
    print("\n--- Running BaseCvGenerator Example Test ---")
    # Use a temporary directory for test output that is clearly for testing
    temp_test_dir_name = "_temp_base_generator_test_output"
    if not os.path.exists(temp_test_dir_name):
        os.makedirs(temp_test_dir_name)

    mock_loader_instance = _MockLoader(root_path=temp_test_dir_name, lang_code="test")
    # Template module is not used in this simple _MyTestGenerator's generate_cv
    test_generator = _MyTestGenerator(mock_loader_instance, None)

    try:
        generated_file_path = test_generator.generate_cv()
        expected_dir = os.path.join(os.path.abspath(temp_test_dir_name), "generated_cvs")
        expected_file = os.path.join(expected_dir, "MyCVTest_MockName_test.txt")

        assert generated_file_path == expected_file, \
            f"Path mismatch: Expected {expected_file}, Got {generated_file_path}"
        assert os.path.exists(generated_file_path), \
            f"Test file {generated_file_path} was not created."
        print("Test file created successfully in the 'generated_cvs' subdirectory.")

        # Clean up: Remove the generated file and directories
        if os.path.exists(generated_file_path):
            os.remove(generated_file_path)
        if os.path.exists(expected_dir) and not os.listdir(expected_dir): # Remove generated_cvs if empty
            os.rmdir(expected_dir)
        if os.path.exists(temp_test_dir_name) and not os.listdir(temp_test_dir_name): # Remove test_output if empty
            os.rmdir(temp_test_dir_name)
        print("Test cleanup successful.")

    except Exception as e:
        print(f"An error occurred during the test: {e}")
        import traceback
        traceback.print_exc()
    print("--- BaseCvGenerator Example Test Finished ---")
