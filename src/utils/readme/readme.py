from siphon.ingestion.github.flatten_directory import flatten_directory
from conduit.sync import Prompt, Model, Conduit, ConduitCache, Verbosity, Response
from pathlib import Path
from rich.console import Console
import argparse
import logging
import sys

# Configuration
CONSOLE = Console()
VERBOSITY = Verbosity.COMPLETE
PROMPT_PATH = Path(__file__).parent / "prompt.jinja2"
UPDATE_PROMPT_PATH = Path(__file__).parent / "update_prompt.jinja2"
PREFERRED_MODEL = "claude"
EXAMPLE_PATH = Path("~/Brian_Code/database-clients").expanduser()
assert EXAMPLE_PATH.is_dir(), f"Directory {EXAMPLE_PATH} does not exist."

# Singleton instances
Model.console = CONSOLE
Model.conduit_cache = ConduitCache()

# Set up logging
logger = logging.getLogger(__name__)
# Set root logger level to DEBUG to capture all logs
logging.basicConfig(level=logging.DEBUG)
# Silence overly verbose loggers like httpcore and markdown_it
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("markdown_it").setLevel(logging.WARNING)


def generate_readme(xml_str: str) -> str:
    """
    LLM call.
    """
    logger.info("Generating README content from XML representation.")
    prompt = Prompt(PROMPT_PATH.read_text())
    model = Model(PREFERRED_MODEL)
    conduit = Conduit(model=model, prompt=prompt)
    response = conduit.run(input_variables={"xml": xml_str}, verbose=VERBOSITY)
    assert isinstance(response, Response), (
        f"Expected a Response object, got {type(response)}"
    )
    return str(response.content)


def update_readme(xml_str: str, readme_file: str) -> str:
    """
    LLM call to update existing README content.
    """
    logger.info("Updating existing README content.")
    prompt = Prompt(UPDATE_PROMPT_PATH.read_text())
    model = Model(PREFERRED_MODEL)
    conduit = Conduit(model=model, prompt=prompt)
    response = conduit.run(
        input_variables={"xml": xml_str, "readme_file": readme_file},
        verbose=VERBOSITY,
    )
    assert isinstance(response, Response), (
        f"Expected a Response object, got {type(response)}"
    )
    return str(response.content)


def process_project_directory(directory: Path) -> str:
    """
    Wrapper function to process a project directory and generate README content.
    """
    logger.info(f"Flattening directory: {directory}")
    xml_representation = flatten_directory(str(directory))
    logger.debug(
        f"XML Representation: {xml_representation[:500]}..."
    )  # Log first 500 chars
    readme_content = generate_readme(xml_representation)
    logger.debug(f"Generated README Content: {readme_content[:500]}...")
    return readme_content


def create_readme_file(directory: Path, content: str):
    """
    Create a README.md file in the specified directory with the given content.
    """
    logger.info(f"Creating README.md in directory: {directory}")
    readme_path = directory / "README.md"
    with open(readme_path, "w") as f:
        f.write(content)
    logger.info(f"README.md created at {readme_path}")
    CONSOLE.print(f"README.md created at {readme_path}", style="bold green")


def main():
    parser = argparse.ArgumentParser(
        description="Generate README from project directory."
    )
    parser.add_argument(
        "directory",
        type=str,
        nargs="?",
        help="Path to the project directory (default: example path).",
    )
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        help="Update the README.md file in the specified directory.",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="Save (or over-write) the generated README.md file in the specified directory.",
    )
    args = parser.parse_args()
    try:
        project_dir = Path(args.directory).expanduser()
    except Exception as e:
        CONSOLE.print(f"Error: Invalid directory path. {e}", style="bold red")
        return
    if not project_dir.is_dir():
        CONSOLE.print(
            f"Error: {project_dir} is not a valid directory.", style="bold red"
        )
        return
    if args.update:
        readme_path = project_dir / "README.md"
        if not readme_path.exists():
            CONSOLE.print(
                f"Error: README.md does not exist in {project_dir}. Cannot update.",
                style="bold red",
            )
            return
        existing_readme = readme_path.read_text()
        CONSOLE.print(f"Updating README in: {project_dir}", style="bold blue")
        updated_readme = update_readme(
            flatten_directory(str(project_dir)), existing_readme
        )
        from rich.markdown import Markdown

        CONSOLE.print(Markdown(updated_readme))
        if args.save:
            create_readme_file(project_dir, updated_readme)
        sys.exit(0)
    else:
        CONSOLE.print(f"Processing directory: {project_dir}", style="bold blue")
        readme_content = process_project_directory(project_dir)
        from rich.markdown import Markdown

        CONSOLE.print(Markdown(readme_content))
        if args.save:
            create_readme_file(project_dir, readme_content)


if __name__ == "__main__":
    main()
