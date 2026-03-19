from pydantic import BaseModel
from typing import List, Dict, Optional

class SimpleCounterDTO(BaseModel):
    count: int
    class Config:
        orm_mode = True

class AverageCounterDTO(BaseModel):
    average: float
    class Config:
        orm_mode = True

class CounterByCareerDTO(BaseModel):
    major: str
    count: int
    class Config:
        orm_mode = True

class CareerDistributionDTO(BaseModel):
    students_by_career: List[CounterByCareerDTO]
    class Config:
        orm_mode = True

class AllCountersDTO(BaseModel):
    total_students: int
    processed_report_cards: int
    institutional_average: float
    inactive_students: int
    male_students: int
    female_students: int
    regular_students: int
    irregular_students: int
    students_by_career: List[CounterByCareerDTO]
    registered_users: int
    active_events: int
    uploaded_report_cards: int
    class Config:
        orm_mode = True

class GenderDistributionDTO(BaseModel):
    male: int
    female: int
    class Config:
        orm_mode = True

class RegularityDistributionDTO(BaseModel):
    regular: int
    irregular: int
    class Config:
        orm_mode = True

class AverageRangeDTO(BaseModel):
    rango: str
    cantidad: int

class AverageDistributionDTO(BaseModel):
    distribucion: List[AverageRangeDTO]

class TrendPointDTO(BaseModel):
    periodo: str
    cantidad: int

class LeaveTrendDTO(BaseModel):
    tendencia: List[TrendPointDTO]