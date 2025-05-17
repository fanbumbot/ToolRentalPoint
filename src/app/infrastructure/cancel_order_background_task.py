from threading import Timer

from .database import SessionLocal
from .service.order import get_order_service

ORDER_CANCEL_TASK_TIME_IN_SECONDS = 60*5

def __background_work_handler():
    with SessionLocal() as session:
        service = get_order_service(session)
        service.cancel_all_with_expired_time()
        session.commit()

        run_cancel_order_background_task()

def run_cancel_order_background_task():
    Timer(ORDER_CANCEL_TASK_TIME_IN_SECONDS, __background_work_handler).start()