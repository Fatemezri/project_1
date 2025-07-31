from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from sms_ir import SmsIr
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging

# Logging setup (no need for utf-8 since logs are now ASCII only)
logging.basicConfig(level=logging.INFO)


def generate_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirmation')

def verify_token(token, max_age=60):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        return serializer.loads(token, salt='email-confirmation', max_age=max_age)
    except Exception:
        return None

def fa_to_en_numbers(s):
    fa_nums = '۰۱۲۳۴۵۶۷۸۹'
    en_nums = '0123456789'
    for f, e in zip(fa_nums, en_nums):
        s = s.replace(f, e)
    return s

def send_verification_sms(phone_number, code):
    # Convert Persian digits to English
    phone_number = fa_to_en_numbers(phone_number).strip()

    # Phone number must start with 09 and be 11 digits
    if phone_number.startswith('0') and len(phone_number) == 11:
        sms_ir = SmsIr(
            api_key=settings.SMS_IR_API_KEY,
            linenumber=settings.SMS_IR_LINE_NUMBER
        )
        template_id = settings.SMS_IR_TEMPLATE_ID
        parameters = [{"name": "code", "value": str(code)}]

        try:
            sms_ir.send_verify_code(phone_number, template_id, parameters)
            logging.info(f"Verification code {code} sent to {phone_number}")
        except Exception as e:
            logging.error("Error sending SMS: %s", e)
            raise e
    else:
        logging.warning("Invalid phone number: %s", phone_number)
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
    try:
        client.upload_fileobj(file_obj, BUCKET_NAME, key)
        return True
    except Exception as e:
        logging.error("Upload error: %s", e)
        return False

def delete_file_from_arvan(key):
    try:
        if key:
            client.delete_object(Bucket=BUCKET_NAME, Key=key)
    except Exception as e:
        logging.error("Delete error: %s", e)

def generate_presigned_url(key, expiration=3600):
    try:
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        logging.error("URL error: %s", e)
        return None
