from sqlalchemy.orm import Session
from collections import Counter
from application.dtos.counters.counter_dto import (
    AllCountersDTO,
    AverageDistributionDTO,
    LeaveTrendDTO,
    SimpleCounterDTO,
    AverageCounterDTO,
    CareerDistributionDTO,
    CounterByCareerDTO,
    GenderDistributionDTO,
    RegularityDistributionDTO,
    AverageRangeDTO,
    TrendPointDTO
)
from infrastructure.persistence.repositories.counter_repository import CounterRepository

class CounterService:
    @staticmethod
    def get_all_counters(db: Session) -> AllCountersDTO:
        data = CounterRepository.get_all_counters(db)
        # Asegurar que students_by_career es una lista de CounterByCareerDTO y filtrar los que tengan major None
        students_by_career = [CounterByCareerDTO(**item) for item in data.get("students_by_career", []) if item.get("major") is not None]
        return AllCountersDTO(
            total_students=data.get("total_students", 0),
            processed_report_cards=data.get("processed_report_cards", 0),
            institutional_average=data.get("institutional_average", 0.0),
            inactive_students=data.get("inactive_students", 0),
            male_students=data.get("students_by_gender", {}).get("male", 0),
            female_students=data.get("students_by_gender", {}).get("female", 0),
            regular_students=data.get("students_by_regularity", {}).get("regular", 0),
            irregular_students=data.get("students_by_regularity", {}).get("irregular", 0),
            students_by_career=students_by_career,
            registered_users=data.get("registered_users", 0),
            active_events=data.get("active_events", 0),
            uploaded_report_cards=data.get("uploaded_report_cards", 0),
        )

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
    def get_students_by_gender(db: Session) -> GenderDistributionDTO:
        data = CounterRepository.get_students_by_gender(db)
        return GenderDistributionDTO(**data)

    @staticmethod
    def get_students_by_regularity(db: Session) -> RegularityDistributionDTO:
        data = CounterRepository.get_students_by_regularity(db)
        return RegularityDistributionDTO(**data)

    @staticmethod
    def get_uploaded_report_cards(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_uploaded_report_cards_count(db))

    @staticmethod
    def get_students_by_career(db: Session) -> CareerDistributionDTO:
        data = CounterRepository.get_students_by_career(db)
        # Filtrar majors None
        students_by_career = [CounterByCareerDTO(**item) for item in data if item.get("major") is not None]
        return CareerDistributionDTO(students_by_career=students_by_career)

    @staticmethod
    def get_registered_users(db: Session) -> SimpleCounterDTO:
        return SimpleCounterDTO(count=CounterRepository.get_registered_users_count(db))

    @staticmethod
    def get_averages_distribution(db: Session) -> AverageDistributionDTO:
        data = CounterRepository.get_averages_distribution(db)
        distribucion = [AverageRangeDTO(**item) for item in data]
        return AverageDistributionDTO(distribucion=distribucion)
    
    from collections import Counter
# Asegúrate de importar LeaveTrendDTO y TrendPointDTO

    @staticmethod
    def get_leave_trend(db: Session) -> LeaveTrendDTO:
        fechas_crudas = CounterRepository.get_leave_dates(db)
        
        conteo_meses = Counter()
        
        for fecha in fechas_crudas:
            # Asumiendo que tus fechas están en formato 'YYYY-MM-DD' (ej. 2023-08-14)
            # Cortamos solo los primeros 7 caracteres para quedarnos con 'YYYY-MM'
            if len(fecha) >= 7:
                mes_anio = fecha[:7] 
                conteo_meses[mes_anio] += 1
                
        # Ordenamos las fechas cronológicamente para que la línea de la gráfica tenga sentido
        puntos = [
            TrendPointDTO(periodo=periodo, cantidad=cantidad)
            for periodo, cantidad in sorted(conteo_meses.items())
        ]
        
        return LeaveTrendDTO(tendencia=puntos)