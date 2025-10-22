from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Base directory for all prompt templates
BASE_DIR = Path(__file__).resolve().parent

# Jinja environment setup
_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR)),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)

def get_all_prompt_template_names():
    """
    Return a list of all Jinja2 template filenames in the prompts/ directory.
    """
    return [f.name for f in BASE_DIR.glob("*.md")]

def read_from_file(file_path: Path) -> str:
    """
    Read and return the content of a file as a string.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def get_prompt_template(name: str):
    """
    Load and return a Jinja2 template by filename.
    Example:
        template = get_prompt_template("prompt.jinja")
        rendered = template.render(...)
    """
    template_content = read_from_file(BASE_DIR / name)
    return _env.from_string(template_content)

__all__ = ["get_prompt_template", "get_all_prompt_template_names"]
