# D:\PROJECT\MIZAN_GOSTAR\PROJECT\USER\signals.py

import logging
from django.dispatch import Signal

logger = logging.getLogger(__name__)
good_evening_email_sent_signal = Signal()
good_evening_email_failed_signal = Signal()
user_registered_signal = Signal()
