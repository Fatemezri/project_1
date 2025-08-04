import logging
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from sms_ir import SmsIr
import boto3
from botocore.exceptions import ClientError

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


def generate_token(email):
    """
    تولید یک توکن امن برای ایمیل.
    """
    logger.info(f"Generating token for email: {email}")
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirmation')

def verify_token(token, max_age=180):
    """
    تأیید اعتبار یک توکن.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-confirmation', max_age=max_age)
        logger.info(f"Token verification successful for email: {email}")
        return email
    except Exception as e:
        logger.warning(f"Token verification failed: {e}", exc_info=True)
        return None

def fa_to_en_numbers(s):
    """
    تبدیل ارقام فارسی به انگلیسی.
    """
    fa_nums = '۰۱۲۳۴۵۶۷۸۹'
    en_nums = '0123456789'
    for f, e in zip(fa_nums, en_nums):
        s = s.replace(f, e)
    return s

def send_verification_sms(phone_number, code):
    """
    ارسال پیامک تأیید.
    """
    # تبدیل ارقام فارسی به انگلیسی
    phone_number = fa_to_en_numbers(phone_number).strip()
    logger.info(f"Attempting to send SMS to '{phone_number}' with code '{code}'.")

    # شماره تلفن باید با 09 شروع شود و 11 رقم باشد
    if phone_number.startswith('09') and len(phone_number) == 11:
        try:
            sms_ir = SmsIr(
                api_key=settings.SMS_IR_API_KEY,
                linenumber=settings.SMS_IR_LINE_NUMBER
            )
            template_id = settings.SMS_IR_TEMPLATE_ID
            parameters = [{"name": "code", "value": str(code)}]

            sms_ir.send_verify_code(phone_number, template_id, parameters)
            logger.info(f"✅ Verification code '{code}' sent successfully to '{phone_number}'.")
        except Exception as e:
            logger.error(f"❌ Error sending SMS to '{phone_number}': {e}", exc_info=True)
            raise e
    else:
        logger.warning(f"❌ Invalid phone number format: '{phone_number}'. SMS not sent.")
        raise ValueError("Invalid phone number.")

session = boto3.session.Session()
client = session.client(
    service_name='s3',
    endpoint_url=settings.ARVAN_ENDPOINT,
    aws_access_key_id=settings.ARVAN_ACCESS_KEY,
    aws_secret_access_key=settings.ARVAN_SECRET_KEY,
)

BUCKET_NAME = settings.ARVAN_BUCKET


def upload_file_to_arvan(file_obj, key):
    """
    آپلود یک فایل در فضای ابری ArvanCloud.
    """
    try:
        logger.info(f"Attempting to upload file with key: '{key}'.")
        client.upload_fileobj(file_obj, BUCKET_NAME, key)
        logger.info(f"✅ File with key '{key}' uploaded successfully.")
        return True
    except Exception as e:
        logger.error(f"❌ Upload error for file '{key}': {e}", exc_info=True)
        return False

def delete_file_from_arvan(key):
    """
    حذف یک فایل از فضای ابری ArvanCloud.
    """
    try:
        if key:
            logger.info(f"Attempting to delete file with key: '{key}'.")
            client.delete_object(Bucket=BUCKET_NAME, Key=key)
            logger.info(f"✅ File with key '{key}' deleted successfully.")
    except Exception as e:
        logger.error(f"❌ Delete error for file '{key}': {e}", exc_info=True)

def generate_presigned_url(key, expiration=3600):
    """
    تولید یک URL امضاشده برای دسترسی به فایل.
    """
    try:
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=expiration,
        )
        logger.info(f"✅ Presigned URL generated for file with key '{key}'.")
        return url
    except ClientError as e:
        logger.error(f"❌ URL generation error for file '{key}': {e}", exc_info=True)
        return None
