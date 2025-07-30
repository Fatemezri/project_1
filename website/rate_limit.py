import time
import logging
from django.core.cache import cache
from django.http import HttpResponseForbidden

logger = logging.getLogger('ratelimit')

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = 30
        self.duration = 60 * 5
        self.block_duration = 60 * 2

    def __call__(self, request):
        ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{ip}"
        block_key = f"block_ip_{ip}"

        if cache.get(block_key):
            logger.warning(f"Blocked IP tried access: {ip}")
            return HttpResponseForbidden("⛔ شما برای ۲ دقیقه مسدود شده‌اید. لطفاً بعداً تلاش کنید.")

        now = time.time()
        request_times = cache.get(cache_key, [])
        request_times = [t for t in request_times if now - t < self.duration]
        request_times.append(now)
        cache.set(cache_key, request_times, timeout=self.duration)

        logger.debug(f"IP {ip} has made {len(request_times)} requests in the last 5 minutes.")

        if len(request_times) > self.max_requests:
            logger.error(f"IP {ip} is blocked for 2 minutes due to rate limit exceeded.")
            cache.set(block_key, True, timeout=self.block_duration)
            return HttpResponseForbidden("⛔ شما برای ۲ دقیقه مسدود شده‌اید. لطفاً بعداً تلاش کنید.")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

