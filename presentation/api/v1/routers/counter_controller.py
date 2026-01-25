from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infrastructure.persistence.repositories.db import get_db
from application.services.counter_service import CounterService
from application.dtos.counters.counter_dto import (
    AllCountersDTO,
    SimpleCounterDTO,
    AverageCounterDTO,
    CareerDistributionDTO,
    GenderDistributionDTO,
    RegularityDistributionDTO,
)

router = APIRouter()

@router.get("/all", response_model=AllCountersDTO)
def get_all_counters(db: Session = Depends(get_db)):
    return CounterService.get_all_counters(db)

@router.get("/students/total", response_model=SimpleCounterDTO)
def get_total_students(db: Session = Depends(get_db)):
    return CounterService.get_total_students(db)

@router.get("/report-cards/processed", response_model=SimpleCounterDTO)
def get_processed_report_cards(db: Session = Depends(get_db)):
    return CounterService.get_processed_report_cards(db)

@router.get("/statistics/institutional-average", response_model=AverageCounterDTO)
def get_institutional_average(db: Session = Depends(get_db)):
    return CounterService.get_institutional_average(db)

@router.get("/students/inactive", response_model=SimpleCounterDTO)
def get_inactive_students(db: Session = Depends(get_db)):
    return CounterService.get_inactive_students(db)

@router.get("/students/gender", response_model=GenderDistributionDTO)
def get_students_by_gender(db: Session = Depends(get_db)):
    return CounterService.get_students_by_gender(db)

@router.get("/students/regularity", response_model=RegularityDistributionDTO)
def get_students_by_regularity(db: Session = Depends(get_db)):
    return CounterService.get_students_by_regularity(db)

@router.get("/students/by-career", response_model=CareerDistributionDTO)
def get_students_by_career(db: Session = Depends(get_db)):
    return CounterService.get_students_by_career(db)

@router.get("/users/registered", response_model=SimpleCounterDTO)
def get_registered_users(db: Session = Depends(get_db)):
    return CounterService.get_registered_users(db)

@router.get("/events/active", response_model=SimpleCounterDTO)
def get_active_events(db: Session = Depends(get_db)):
    return CounterService.get_active_events(db)

@router.get("/report-cards/uploaded", response_model=SimpleCounterDTO)
def get_uploaded_report_cards(db: Session = Depends(get_db)):
    return CounterService.get_uploaded_report_cards(db)
