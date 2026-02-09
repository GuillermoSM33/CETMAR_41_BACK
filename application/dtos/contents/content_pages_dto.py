from pydantic import BaseModel
from typing import Optional

class ContentPageBaseDTO(BaseModel):
    Description: Optional[str] = None
    Titule: Optional[str] = None
    UrlImage: Optional[str] = None
    Page: Optional[str] = None
    ComponentPage: Optional[str] = None

class CreateContentPageDTO(ContentPageBaseDTO):
    Page: str 
    ComponentPage: str

class UpdateContentPageDTO(ContentPageBaseDTO):
    pass

class GetContentPageDTO(ContentPageBaseDTO):
    Id: int

    class Config:
        from_attributes = True