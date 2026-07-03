from pydantic import BaseModel

class ValidateConfigurationCommand(BaseModel):
    """Command to trigger parsing and validation of local config files."""
    pass
