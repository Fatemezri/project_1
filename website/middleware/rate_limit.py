from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import time

class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = request.META.get('REMOTE_ADDR')  # اگر لاگین نیست با IP محدود کنیم

        key = f"rate_limit:{user_id}"
        current_time = int(time.time())

        window = 300  # پنجره زمانی: ۵ دقیقه = 300 ثانیه
        limit = 3    # بیش از 30 درخواست مجاز نیست

        history = cache.get(key, [])

        # فیلتر درخواست‌های قدیمی‌تر از ۵ دقیقه
        history = [t for t in history if current_time - t < window]
        history.append(current_time)

        cache.set(key, history, timeout=window)

        if len(history) > limit:
            return JsonResponse({
                "error": "درخواست‌های بیش از حد مجاز. لطفاً بعداً تلاش کنید."
            }, status=429)
