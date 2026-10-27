from license_manager import verify_and_consume_license

# تست با لایسنسی که در قدم قبل توی دیتابیس ساختیم
print(verify_and_consume_license("TEST-1234-5678"))

# تست دوباره با همون لایسنس (باید بگه استفاده شده)
print(verify_and_consume_license("TEST-1234-5678"))

# تست یک لایسنس الکی
print(verify_and_consume_license("WRONG-KEY"))