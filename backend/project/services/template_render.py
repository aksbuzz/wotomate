from jinja2 import Environment, StrictUndefined
from typing import Any, Union

env = Environment(undefined=StrictUndefined)

def render_template(template_name: str, context: dict) -> str:
  """
  Renders a Jinja2 template with the provided context.
  """
  try:
    template = env.from_string(template_name)
    return template.render(context)
  except Exception as e:
    raise RuntimeError(f"Templating error: {e} for template '{template_name}' with context keys: {list(context.keys())}")

def resolve_template(data: Union[str, dict, list], context: dict) -> Any:
  """
  Recursively renders Jinja2 templates in a dictionary or list.
  """
  if isinstance(data, str):
    try:
      return render_template(data, context)
    except Exception as e:
      raise ValueError(f"Error rendering template '{data}': {e}")
  elif isinstance(data, dict):
    return {k: resolve_template(v, context) for k, v in data.items()}
  elif isinstance(data, list):
    return [resolve_template(item, context) for item in data]
  else:
    return data