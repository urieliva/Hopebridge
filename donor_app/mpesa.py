import requests
import base64
from datetime import datetime
from decouple import config

def lipa_na_mpesa(phone_number, amount):
    # Load credentials
    consumer_key = config('MPESA_CONSUMER_KEY')
    consumer_secret = config('MPESA_CONSUMER_SECRET')
    shortcode = config('MPESA_SHORT_CODE')
    passkey = config('MPESA_PASSKEY')
    env = config('MPESA_ENV', default='sandbox')
    callback_url = config('CALLBACK_URL')

    # Choose environment URL
    if env == 'sandbox':
        base_url = "https://sandbox.safaricom.co.ke"
    else:
        base_url = "https://api.safaricom.co.ke"

    # Get access token
    auth_url = f"{base_url}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')

    if not access_token:
        return {"error": "Failed to get access token", "details": response.json()}

    # Prepare password
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = shortcode + passkey + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    # STK Push request
    stk_push_url = f"{base_url}/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": "HopeBridge",
        "TransactionDesc": "Donation Payment"
    }

    stk_response = requests.post(stk_push_url, json=payload, headers=headers)
    return stk_response.json()