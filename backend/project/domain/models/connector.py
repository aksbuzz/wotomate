from enum import Enum
from typing import Iterable, Optional

class AuthType(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"

class TriggerType:
    """A specific trigger offered by a connector."""
    def __init__(
        self, 
        id: int,
        event_key: str, 
        display_name: str, 
        description: Optional[str],
        config_schema: dict,
        output_schema: dict
    ):
        self.id = id
        self.event_key = event_key
        self.display_name = display_name
        self.description = description
        self.config_schema = config_schema or {}
        self.output_schema = output_schema or {}


class ActionType:
    """A specific action offered by a connector."""
    def __init__(
        self, 
        id: int,
        action_key: str, 
        display_name: str, 
        description: Optional[str],
        config_schema: dict,
        input_schema: Optional[dict],
        output_schema: dict
    ):
        self.id = id
        self.action_key = action_key
        self.display_name = display_name
        self.description = description
        self.config_schema = config_schema or {}
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}

class Connector:
    def __init__(
        self,
        id: int,
        key: str,
        display_name: str,
        description: Optional[str],
        auth_type: Optional[AuthType],
        logo_url: Optional[str],
        trigger_types: Iterable[TriggerType],
        action_types: Iterable[ActionType]
    ):
        self.id = id
        self.key = key
        self.display_name = display_name
        self.description = description
        self.auth_type = auth_type
        self.logo_url = logo_url
        self._trigger_types = list(trigger_types)
        self._action_types = list(action_types)

    @property
    def trigger_types(self) -> list[TriggerType]:
        return self._trigger_types

    @property
    def action_types(self) -> list[ActionType]:
        return self._action_types
