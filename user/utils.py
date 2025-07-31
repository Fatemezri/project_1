from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from sms_ir import SmsIr
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging


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
    # تبدیل اعداد فارسی به انگلیسی
    phone_number = fa_to_en_numbers(phone_number).strip()

    # شماره باید با 09 شروع شود و 11 رقمی باشد
    if phone_number.startswith('0') and len(phone_number) == 11:
        sms_ir = SmsIr(
            api_key=settings.SMS_IR_API_KEY,
            linenumber=settings.SMS_IR_LINE_NUMBER
        )
        template_id = settings.SMS_IR_TEMPLATE_ID
        parameters = [{"name": "code", "value": str(code)}]

        try:
            sms_ir.send_verify_code(phone_number, template_id, parameters)
            print(f"کد تأیید {code} با موفقیت به شماره {phone_number} ارسال شد.")
        except Exception as e:
            print("خطا در ارسال پیامک:", e)
            raise e
    else:
        print("شماره موبایل نامعتبر است:", phone_number)
        raise ValueError("شماره موبایل نامعتبر است.")


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
        print("Upload error:", e)
        return False

def delete_file_from_arvan(key):
    try:
        if key:
            client.delete_object(Bucket=BUCKET_NAME, Key=key)
    except Exception as e:
        print("Delete error:", e)

def generate_presigned_url(key, expiration=3600):
    try:
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        print("URL error:", e)
        return None
