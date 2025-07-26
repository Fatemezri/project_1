from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

# زمان‌بندی برای هر روز ساعت 18 به وقت خارطوم (Africa/Khartoum)
schedule, created = CrontabSchedule.objects.get_or_create(
    minute='0',
    hour='18',
    timezone='Africa/Khartoum',
)

PeriodicTask.objects.update_or_create(
    name='send-evening-email-task',
    defaults={
        'crontab': schedule,
        'task': 'notification.tasks.send_evening_email',  # مسیر تسک تو
        'args': json.dumps([]),
    }
)
