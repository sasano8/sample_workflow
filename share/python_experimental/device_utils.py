import time
import platform
import hashlib
import hmac
import uuid
from typing import BinaryIO
from io import BytesIO


def get_device_identifier():
    "デバイス識別子を取得する"
    system = platform.system()
    if system == "Windows":
        return "Windows-" + platform.node()
    elif system == "Linux":
        with open("/etc/machine-id", "r") as f:
            return "Linux-" + f.read().strip()
    elif system == "Darwin":
        return "Mac-" + platform.node()
    else:
        return "Unknown-" + str(uuid.uuid4())


def get_device_identifier_and_timestamp():
    "デバイス識別子とタイムスタンプを取得する。"
    device_id = get_device_identifier()
    return {"device_id": device_id, "timestamp": int(time.time())}


def create_signature(secret: str, device_id: str, timestamp: int):
    """署名を作成（デバイス識別子 + タイムスタンプ）する"""
    message = device_id + str(timestamp)
    signature = hmac.new(
        DEVICE_SECRET_KEY, message.encode(), hashlib.sha256
    ).hexdigest()
    return {"device_id": device_id, "timestamp": timestamp, "signature": signature}


# 事前にサーバーから発行されたデバイスごとの秘密鍵
DEVICE_SECRET_KEY = b"device_specific_secret_key"

data = create_signature(DEVICE_SECRET_KEY, **get_device_identifier_and_timestamp())
print(data)

# import requests
# response = requests.post("https://example.com/api/register", json=data)
# print(response.json())


from cryptography import x509
from cryptography.hazmat.backends import default_backend

"""
# device_id を含む証明書の csr を作成
[ req ]
default_bits       = 2048
default_keyfile    = device.key
distinguished_name = req_distinguished_name
req_extensions     = v3_req

[ req_distinguished_name ]
CN = device-12345  # ここに `device_id` を入れる

[ v3_req ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = device-12345.example.com  # `device_id` を SAN に含める
"""


def parse_cn_and_san_from_cert_io(io: BinaryIO | str):
    """証明書から CommonName と SubjectAlternativeName を取得する。
    CommonName は DeviceId が含まれることを想定する。
    """
    if isinstance(io, str):
        io = BytesIO(io.encode("UTF-8"))

    cert = x509.load_pem_x509_certificate(io.read(), default_backend())
    common_name = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value

    ext = cert.extensions.get_extension_for_oid(
        x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    )
    subject_alternative_name = ext.value.get_values_for_type(x509.DNSName)

    # これまでは cn が使われていたが、近年では san が推奨されている
    # san はリスト型、かつ、ドメイン形式だが、最終ドメイン（一番左）が１つでもデバイスIDと一致すればよしとする？
    return {"cn": common_name, "san": subject_alternative_name}


def get_certificate_hash(io: BinaryIO | str):
    """証明書のハッシュを取得する。
    そのハッシュを秘密鍵としても利用することができる。
    """
    if isinstance(io, str):
        io = BytesIO(io.encode("UTF-8"))

    cert_data = io.read()
    return hashlib.sha256(cert_data).hexdigest()


def generate_certificate() -> str:
    return """-----BEGIN CERTIFICATE-----
MIIDJTCCAg2gAwIBAgIUX3gljvLSpTt1EwP9l+O1rD2/fnowDQYJKoZIhvcNAQEL
BQAwMTEvMC0GA1UEAwwmTGludXgtM2ViZjg5NzM0YmM1NDU1ZjhkMzZmYTAyZWM2
ZGQxMWIwHhcNMjUwMjAyMDIzNTE2WhcNMjYwMjAyMDIzNTE2WjAxMS8wLQYDVQQD
DCZMaW51eC0zZWJmODk3MzRiYzU0NTVmOGQzNmZhMDJlYzZkZDExYjCCASIwDQYJ
KoZIhvcNAQEBBQADggEPADCCAQoCggEBALaZEHU/ZoIl7twtPHLKq5aY54tIHUP3
/L6yDdKZhUC9KFPamwqq8Jl89Q49H8jnneHc+0+FLS1aHco7A/gY4Mwzdn1e6lH7
sUFFVoXBIiFN30vcRpzsaTcgFPiSKiw8hm7RSO+5bWp9dwXlLviGYlvaEPAIgknd
5IAVrZWDZUeE+fqY1bq9ZrX8kZjck+Vkvt73AH4U7O9zpQAoBtcUkq0WY4/mYUiG
s/VltImZcfj+LRJ0DBd3a1dO+shuPNTQATg/bF30LJQfmaoEMbSegx+jCkA7XXei
i6HuQ67ul1lf8p6BqcA0WJf8ptenS3/PPmyknVEgfK8YSzzf/S8TiSkCAwEAAaM1
MDMwMQYDVR0RBCowKIImTGludXgtM2ViZjg5NzM0YmM1NDU1ZjhkMzZmYTAyZWM2
ZGQxMWIwDQYJKoZIhvcNAQELBQADggEBAF3MlA63cln1XBTDj6zNVp9Br+vIuV3K
KF9OODZ34vFjK22Gz3ijcrBbDZ74Jca+kPnBb3c0oOynOxYVLGynrrWQ1TOgfFsd
rJgq14S3g9978AfyDQ/gL1G2APfW1tB2LTexbtb/0qdf/4Vp9wIAABu6oQHs/Qgc
3JIw+DpWT4YnKyTOQrQQbdDTPo4ZO/e/dWYtuckgNu5Iksx6CXRaP3eruZk3k3PN
forp6q5OTXjRZZOB96Q5Q6WjapLIYiswyH67vvLBQMkMorlh4i47g89yUJkSMpLP
rCfgtoYFJd9wWMWMez6nYN6tQiodqnCTs5eL78rDqxMYgGgg0FdK0Nw=
-----END CERTIFICATE-----"""


cert = generate_certificate()
print(parse_cn_and_san_from_cert_io(cert))
print(get_certificate_hash(cert))
