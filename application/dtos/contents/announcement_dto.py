from pydantic import BaseModel, model_validator
from datetime import date
from typing import Optional

class AnnouncementBaseDTO(BaseModel):
    Titule: str  
    Description: str
    Type: str
    UrlImage: Optional[str] = None
    UrlDocument: Optional[str] = None
    IsAnAdvice: bool = True
    CreationDate: Optional[date] = None
    EndDate: Optional[date] = None
    IsActive: bool = True

    @model_validator(mode='after')
    def check_dates(self):
        if self.CreationDate and self.EndDate:
            if self.EndDate < self.CreationDate:
                raise ValueError("La fecha de finalización no puede ser anterior a la de creación")
        return self

class CreateAnnouncementDTO(AnnouncementBaseDTO):
    pass

class UpdateAnnouncementDTO(AnnouncementBaseDTO):
    pass

class GetAnnouncementDTO(AnnouncementBaseDTO):
    Id: int

    class Config:
        from_attributes = True