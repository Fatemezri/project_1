import time
import logging
from django.core.cache import cache
from django.http import HttpResponseForbidden

logger = logging.getLogger('ratelimit')

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = 300
        self.duration = 60 * 5
        self.block_duration = 60 * 2

        logger.info("RateLimitMiddleware initialized.")

    def __call__(self, request):
        ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{ip}"
        block_key = f"block_ip_{ip}"

        if cache.get(block_key):
            logger.warning(f"[BLOCKED ACCESS] IP {ip} is currently blocked from making requests.")
            return HttpResponseForbidden("⛔ شما برای ۲ دقیقه مسدود شده‌اید. لطفاً بعداً تلاش کنید.")

        now = time.time()
        request_times = cache.get(cache_key, [])
        request_times = [t for t in request_times if now - t < self.duration]
        request_times.append(now)
        cache.set(cache_key, request_times, timeout=self.duration)

        logger.debug(f"[REQUEST LOG] IP {ip} made {len(request_times)} requests in the last 5 minutes.")

        if len(request_times) > self.max_requests:
            logger.error(f"[RATE LIMIT EXCEEDED] IP {ip} exceeded limit and is now blocked for {self.block_duration} seconds.")
            cache.set(block_key, True, timeout=self.block_duration)
            return HttpResponseForbidden("⛔ شما برای ۲ دقیقه مسدود شده‌اید. لطفاً بعداً تلاش کنید.")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
            logger.debug(f"[IP DETECTED] Using X-Forwarded-For: {ip}")
            return ip
        ip = request.META.get("REMOTE_ADDR")
        logger.debug(f"[IP DETECTED] Using REMOTE_ADDR: {ip}")
        return ip