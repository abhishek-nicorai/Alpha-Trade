import os
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect


load_dotenv()

class AuthManager:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.client_id = os.getenv("CLIENT_ID")
        self.password = os.getenv("PASSWORD")
        self.totp_token = os.getenv("TOTP_TOKEN")
        self.smart_api = SmartConnect(api_key=self.api_key)

    def login(self):
        try:
            totp = pyotp.TOTP(self.totp_token).now()
            data = self.smart_api.generateSession(self.client_id, self.password, totp)
            
            if data['status']:
                print(f"✅ Login Successful for Client: {self.client_id}")
                # We return BOTH the api object and the jwtToken
                return self.smart_api, data['data']['jwtToken']
            else:
                print(f"❌ Login Failed: {data['message']}")
                return None, None
        except Exception as e:
            print(f"⚠️ Auth Error: {e}")
            return None, None