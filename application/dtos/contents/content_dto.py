from pydantic import BaseModel, model_validator
from datetime import date
from typing import Optional

class ContentBaseDTO(BaseModel):
    Description: str
    Titule: str
    Type: str
    UrlImage: Optional[str] = None
    UrlDocument: Optional[str] = None
    IsAnAdvice: bool = False
    CreationDate: Optional[date] = None
    EndDate: Optional[date] = None
    IsActive: bool = True

    @model_validator(mode='after')
    def check_dates(self):
        if self.CreationDate and self.EndDate:
            if self.EndDate < self.CreationDate:
                raise ValueError("La fecha de finalización (EndDate) no puede ser anterior a la de creación (CreationDate)")
        return self

class CreateContentDTO(ContentBaseDTO):
    pass

class UpdateContentDTO(ContentBaseDTO):
    pass

class GetContentDTO(ContentBaseDTO):
    Id: int

    class Config:
        from_attributes = True