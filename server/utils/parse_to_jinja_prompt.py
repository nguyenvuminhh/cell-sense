
from server.constants import JinjaPromptTemplatesNames
from server.models.chat_models import MessageRequest
from server.prompts import get_prompt_template


def parse_to_jinja_prompt(
    request: MessageRequest,
    template_name: JinjaPromptTemplatesNames,
) -> str:
    # Load the template from the prompts/ directory
    template = get_prompt_template(template_name)
    print(f"Using template: {template}")
    # Render the Jinja template with the MessageRequest data
    model_dump_object = request.model_dump()
    print(f"Model dump object: {model_dump_object}")
    rendered = template.render(**model_dump_object)

    return rendered
