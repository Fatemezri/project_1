from django.http import JsonResponse
import time
from django.core.cache import cache

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100        # حداکثر تعداد درخواست
        self.time_window = 120      # مدت زمان مسدودی به ثانیه (مثلاً ۲ دقیقه)

    def __call__(self, request):
        ip = self.get_client_ip(request)
        cache_key = f"rate-limit:{ip}"
        request_times = cache.get(cache_key, [])

        now = time.time()
        # فقط درخواست‌هایی که هنوز در بازه‌ی زمانی هستند را نگه می‌داریم
        request_times = [t for t in request_times if now - t < self.time_window]

        if len(request_times) >= self.rate_limit:
            return JsonResponse(
                {"detail": "شما به دلیل درخواست‌های زیاد، برای ۲ دقیقه مسدود شده‌اید."},
                status=429,
                json_dumps_params={'ensure_ascii': False}  # 👈 مهم برای نمایش درست فارسی
            )

        request_times.append(now)
        cache.set(cache_key, request_times, timeout=self.time_window)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

