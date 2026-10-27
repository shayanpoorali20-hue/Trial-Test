"""
مدیریت صف درخواست‌ها برای جلوگیری از کرش کردن سرور
"""

import queue
import threading
import logging

logger = logging.getLogger(__name__)

# صف سراسری (FIFO - اول ورود، اول خروج)
task_queue = queue.Queue()

def worker(process_func, mark_free_func):
    """
    کارگر پس‌زمینه که مدام صف را چک می‌کند.
    process_func: تابعی که باید پردازش را انجام دهد (_process)
    mark_free_func: تابعی که قفل کاربر را آزاد می‌کند (_mark_free)
    """
    logger.info("[QUEUE] Worker thread started.")
    while True:
        user_id, message, is_link = task_queue.get()
        
        try:
            logger.info(f"[QUEUE] Picked up task for user {user_id}.")
            process_func(message, is_link)
        except Exception as e:
            logger.error(f"[QUEUE] Error processing task for user {user_id}: {e}")
        finally:
            # 👈 این خط تضمین میکنه که صف هیچ‌وقت قفل نمیشه
            mark_free_func(user_id)
            task_queue.task_done()

def start_worker(process_func, mark_free_func):
    """شروع ترد کارگر در پس‌زمینه"""
    t = threading.Thread(target=worker, args=(process_func, mark_free_func), daemon=True)
    t.start()

def add_to_queue(user_id: int, message, is_link: bool) -> int:
    """
    افزودن درخواست به صف
    خروجی: تعداد نفرات درون صف (شامل خود کاربر)
    """
    task_queue.put((user_id, message, is_link))
    return task_queue.qsize()