"""
Conditional Branching Example

Demuestra cómo implementar lógica condicional en Airflow
usando BranchPythonOperator y @task.branch decorator.
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
import logging
import random

logger = logging.getLogger(__name__)


@dag(
    dag_id='conditional_example',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['conditional', 'example', 'branching'],
    description='Ejemplo de branching condicional',
    default_args={
        'owner': 'snail-data',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
)
def conditional_example():
    """
    DAG que demuestra branching condicional:
    1. Evalúa una condición
    2. Ejecuta diferentes caminos según el resultado
    3. Converge al final
    """

    start = EmptyOperator(task_id='start')

    @task.branch
    def check_data_quality():
        """
        Simula verificación de calidad de datos
        Retorna el task_id del siguiente task a ejecutar
        """
        logger.info("Verificando calidad de datos...")

        # Simular score de calidad (0-100)
        quality_score = random.randint(0, 100)
        logger.info(f"Score de calidad: {quality_score}")

        # Decidir branch basado en score
        if quality_score >= 80:
            logger.info("✓ Calidad ALTA - Procesando normalmente")
            return 'high_quality_path'
        elif quality_score >= 50:
            logger.info("⚠ Calidad MEDIA - Procesando con validaciones extra")
            return 'medium_quality_path'
        else:
            logger.info("✗ Calidad BAJA - Enviando a reprocesamiento")
            return 'low_quality_path'

    @task
    def high_quality_processing():
        """Procesamiento estándar para datos de alta calidad"""
        logger.info("Procesando datos de alta calidad...")
        logger.info("Aplicando transformaciones estándar")
        return {'status': 'success', 'records_processed': 1000}

    @task
    def medium_quality_processing():
        """Procesamiento con validaciones extra para datos de calidad media"""
        logger.info("Procesando datos de calidad media...")
        logger.info("Aplicando validaciones adicionales")
        logger.info("Limpiando registros problemáticos")
        return {'status': 'success_with_warnings', 'records_processed': 800, 'records_cleaned': 200}

    @task
    def low_quality_processing():
        """Procesamiento especial para datos de baja calidad"""
        logger.info("Procesando datos de baja calidad...")
        logger.info("Aplicando limpieza intensiva")
        logger.info("Marcando registros para revisión manual")
        return {'status': 'needs_review', 'records_processed': 500, 'records_flagged': 500}

    @task
    def send_notification(processing_result: dict):
        """Envía notificación con los resultados del procesamiento"""
        logger.info("Enviando notificación...")
        logger.info(f"Status: {processing_result.get('status', 'unknown')}")
        logger.info(f"Registros procesados: {processing_result.get('records_processed', 0)}")

        if 'records_cleaned' in processing_result:
            logger.info(f"Registros limpiados: {processing_result['records_cleaned']}")

        if 'records_flagged' in processing_result:
            logger.info(f"⚠ Registros marcados para revisión: {processing_result['records_flagged']}")

    # Tasks de convergencia (se ejecutan después de cualquier branch)
    join = EmptyOperator(
        task_id='join',
        trigger_rule='none_failed_min_one_success'  # Ejecuta si al menos un branch tuvo éxito
    )

    end = EmptyOperator(task_id='end')

    # Ejemplo adicional: Branch basado en día de la semana
    @task.branch
    def check_day_of_week():
        """Ejecuta diferentes tareas según el día de la semana"""
        day = datetime.now().weekday()  # 0 = Lunes, 6 = Domingo
        logger.info(f"Día de la semana: {day}")

        if day < 5:  # Lunes a Viernes
            logger.info("Es día laboral - Ejecutando procesamiento completo")
            return 'weekday_processing'
        else:  # Sábado o Domingo
            logger.info("Es fin de semana - Ejecutando procesamiento reducido")
            return 'weekend_processing'

    weekday_processing = EmptyOperator(task_id='weekday_processing')
    weekend_processing = EmptyOperator(task_id='weekend_processing')

    join_day = EmptyOperator(
        task_id='join_day',
        trigger_rule='none_failed_min_one_success'
    )

    # Definir flujo del DAG

    # Branch principal: calidad de datos
    branch_quality = check_data_quality()

    high_quality = high_quality_processing()
    medium_quality = medium_quality_processing()
    low_quality = low_quality_processing()

    # Configurar branches
    start >> branch_quality
    branch_quality >> high_quality >> join
    branch_quality >> medium_quality >> join
    branch_quality >> low_quality >> join

    # Notificar y continuar
    join >> send_notification(high_quality) >> end
    join >> send_notification(medium_quality) >> end
    join >> send_notification(low_quality) >> end

    # Branch secundario: día de la semana
    start >> check_day_of_week()
    check_day_of_week() >> [weekday_processing, weekend_processing] >> join_day >> end


conditional_example()
