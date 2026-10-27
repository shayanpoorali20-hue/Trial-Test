"""
ماژول ارتباط با Cloudflare Worker برای بررسی و مصرف لایسنس‌ها
"""

import logging
import requests
import config

logger = logging.getLogger(__name__)

def verify_and_consume_license(license_key: str) -> tuple[bool, str]:
    """
    کد لایسنس را به کلادفلر می‌فرستد.
    خروجی: (آیا موفق بود؟، پیام خطا یا موفقیت)
    """
    license_key = license_key.strip()
    if not license_key:
        return False, "کد لایسنس نمی‌تواند خالی باشد."

    headers = {
        "Authorization": f"Bearer {config.CLOUDFLARE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"key": license_key}

    try:
        logger.info(f"📡 در حال ارسال لایسنس به کلادفلر... ({license_key})")
        response = requests.post(
            config.CLOUDFLARE_WORKER_URL,
            headers=headers,
            json=payload,
            timeout=10  # ۱۰ ثانیه کافیه چون کلادفلر خیلی سریعه
        )

        # اگر خطای HTTP رخ داد (مثلا 401 یا 500)
        if response.status_code not in (200, 400):
            logger.error(f"Cloudflare HTTP Error {response.status_code}: {response.text}")
            return False, "خطا در ارتباط با سرور لایسنس."

        data = response.json()
        status = data.get("status")
        message = data.get("message", "")

        if status == "success":
            logger.info(f"✅ لایسنس {license_key} تایید و مصرف شد.")
            return True, message
        elif status == "used":
            logger.warning(f"⚠️ لایسنس {license_key} قبلا استفاده شده است.")
            return False, message
        elif status == "invalid":
            logger.warning(f"❌ لایسنس {license_key} معتبر نیست.")
            return False, message
        else:
            logger.error(f"پاسخ نامشخص از کلادفلر: {data}")
            return False, "خطای نامشخص در سیستم لایسنس."

    except requests.exceptions.Timeout:
        logger.error("⏱ تایم‌اوت در ارتباط با کلادفلر.")
        return False, "سیستم لایسنس پاسخ نمی‌دهد. لطفاً بعدا تلاش کنید."
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ خطای شبکه در ارتباط با کلادفلر: {e}")
        return False, "خطا در اتصال به سیستم لایسنس."
    except Exception as e:
        logger.error(f"❌ خطای پیش‌بینی نشده: {e}")
        return False, "خطای داخلی سرور."