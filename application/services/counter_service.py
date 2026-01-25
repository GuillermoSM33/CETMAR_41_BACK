from sqlalchemy.orm import Session
from application.dtos.counters.counter_dto import (
    AllCountersDTO,
    SimpleCounterDTO,
    AverageCounterDTO,
    CareerDistributionDTO,
    CounterByCareerDTO,
)
from infrastructure.persistence.repositories.counter_repository import CounterRepository

class CounterService:
    @staticmethod
    def get_all_counters(db: Session) -> AllCountersDTO:
        data = CounterRepository.get_all_counters(db)
        return AllCountersDTO(**data)

    @staticmethod
    def get_total_students(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_total_students(db))

    @staticmethod
    def get_processed_report_cards(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_processed_report_cards_count(db))

    @staticmethod
    def get_institutional_average(db: Session) -> AverageCounterDTO:
        return AverageCounterDTO(average=CounterRepository.get_institutional_average(db))

    @staticmethod
    def get_inactive_students(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_inactive_students_count(db))

    @staticmethod
    def get_male_students(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_male_students_count(db))

    @staticmethod
    def get_female_students(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_female_students_count(db))

    @staticmethod
    def get_regular_students(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_regular_students_count(db))

    @staticmethod
    def get_irregular_students(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_irregular_students_count(db))

    @staticmethod
    def get_students_by_career(db: Session) -> CareerDistributionDTO:
        data = CounterRepository.get_students_by_career(db)
        return CareerDistributionDTO(students_by_career=[CounterByCareerDTO(**item) for item in data])

    @staticmethod
    def get_registered_users(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_registered_users_count(db))

    @staticmethod
    def get_active_events(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_active_events_count(db))

    @staticmethod
    def get_uploaded_report_cards(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_uploaded_report_cards_count(db))
