from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
import uuid

class SystemSettingBase(BaseModel):
    maintenance_mode: bool
    allow_registrations: bool
    session_timeout: int

class SystemSettingUpdate(SystemSettingBase):
    pass

class SystemSettingOut(SystemSettingBase):
    id: uuid.UUID
    updated_at: datetime
    updated_by: uuid.UUID | None
    model_config = ConfigDict(from_attributes=True)