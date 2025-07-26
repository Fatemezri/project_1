import time
from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 30        # حداکثر تعداد درخواست
        self.time_window = 300      # بازه زمانی برحسب ثانیه (۵ دقیقه)

    def __call__(self, request):
        ip = self.get_client_ip(request)
        cache_key = f"rate-limit:{ip}"
        request_times = cache.get(cache_key, [])

        now = time.time()
        request_times = [t for t in request_times if now - t < self.time_window]

        if len(request_times) >= self.rate_limit:
            return JsonResponse(
                {"detail": "rrrrrrrrrrrrrrrrr"},
                status=429
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
