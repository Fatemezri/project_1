from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def generate_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirmation')

def verify_token(token, max_age=120):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-confirmation', max_age=max_age)
        return email
    except Exception:
        return None

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
