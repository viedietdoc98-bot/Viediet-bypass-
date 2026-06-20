# api_engine.py
import requests
import json
import time
import logging
from config import DEFAULT_API_CONFIG
from database import get_api_config, log_usage

logger = logging.getLogger(__name__)

class ViedietAPI:
    def __init__(self, user_id, phone=None, otp=None):
        self.user_id = user_id
        self.phone = phone
        self.otp = otp
        self.config = self._load_config()
        self.session = requests.Session()
        self.headers = self.config.get('headers', {}).copy()
        self.base_url = self.config.get('base_url', '')
        self.request_id = None
        self.log_details = {}

    def _load_config(self):
        saved = get_api_config()
        if saved:
            # Merge with defaults
            merged = DEFAULT_API_CONFIG.copy()
            for k, v in saved.items():
                merged[k] = v
            return merged
        return DEFAULT_API_CONFIG

    def _replace_placeholders(self, obj):
        if isinstance(obj, dict):
            return {k: self._replace_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_placeholders(item) for item in obj]
        elif isinstance(obj, str):
            return obj.format(phone=self.phone or '', otp=self.otp or '', requestId=self.request_id or '')
        else:
            return obj

    def _request(self, endpoint_key, payload_override=None):
        endpoint = self.config['endpoints'].get(endpoint_key)
        if not endpoint:
            raise ValueError(f"Endpoint {endpoint_key} not configured.")
        url = self.base_url + endpoint
        payload_template = self.config['payloads'].get(endpoint_key, {})
        if payload_override:
            payload = payload_override
        else:
            payload = self._replace_placeholders(payload_template)

        # Update headers with dynamic tokens
        headers = self.headers.copy()
        # Add auth tokens from previous responses
        if hasattr(self, 'auth_tokens'):
            headers.update(self.auth_tokens)

        response = self.session.post(url, json=payload, headers=headers, timeout=30)
        self._update_headers_from_response(response)
        return response

    def _update_headers_from_response(self, response):
        # Extract tokens defined in auth.token_extract
        token_keys = self.config.get('auth', {}).get('token_extract', [])
        if not hasattr(self, 'auth_tokens'):
            self.auth_tokens = {}
        for key in token_keys:
            if key in response.headers:
                self.auth_tokens[key] = response.headers[key]
            elif key in response.cookies:
                self.auth_tokens[key] = response.cookies.get(key)
        # Also store raw cookies
        cookie_str = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])
        if cookie_str:
            self.auth_tokens['Cookie'] = cookie_str
        # Merge into headers for next requests
        self.headers.update(self.auth_tokens)

    def send_otp(self):
        """Step 1: Send OTP"""
        try:
            resp = self._request('send_otp')
            if resp.status_code == 200:
                data = resp.json()
                # Extract requestId
                if 'RESPONSE' in data and 'actionResponseContext' in data['RESPONSE']:
                    self.request_id = data['RESPONSE']['actionResponseContext'].get('requestId')
                self.log_details['send_otp'] = 'Success'
                return True, data
            else:
                self.log_details['send_otp'] = f'HTTP {resp.status_code}'
                return False, None
        except Exception as e:
            self.log_details['send_otp'] = str(e)
            return False, None

    def verify_otp(self):
        """Step 2: Verify OTP"""
        if not self.request_id:
            return False, None
        try:
            resp = self._request('verify_otp')
            if resp.status_code == 200:
                data = resp.json()
                if data.get('SESSION', {}).get('isLoggedIn'):
                    self.log_details['verify_otp'] = 'Success'
                    return True, data
                else:
                    self.log_details['verify_otp'] = 'Login failed'
                    return False, data
            else:
                self.log_details['verify_otp'] = f'HTTP {resp.status_code}'
                return False, None
        except Exception as e:
            self.log_details['verify_otp'] = str(e)
            return False, None

    def get_user_state(self):
        """Step 3: User state (optional)"""
        try:
            resp = self._request('user_state')
            if resp.status_code == 200:
                self.log_details['user_state'] = 'Success'
                return True, resp.json()
            else:
                self.log_details['user_state'] = f'HTTP {resp.status_code}'
                return False, None
        except Exception as e:
            self.log_details['user_state'] = str(e)
            return False, None

    def fetch_homepage(self):
        """Step 4: Fetch homepage (optional)"""
        try:
            resp = self._request('fetch_homepage')
            if resp.status_code == 200:
                self.log_details['fetch_homepage'] = 'Success'
                return True, resp.json()
            else:
                self.log_details['fetch_homepage'] = f'HTTP {resp.status_code}'
                return False, None
        except Exception as e:
            self.log_details['fetch_homepage'] = str(e)
            return False, None

    def collect(self):
        """Step 5: Collect reward"""
        try:
            resp = self._request('collect')
            if resp.status_code == 200:
                data = resp.json()
                if data.get('RESPONSE', {}).get('actionSuccess'):
                    self.log_details['collect'] = 'Success'
                    return True, data
                else:
                    self.log_details['collect'] = 'Action failed'
                    return False, data
            else:
                self.log_details['collect'] = f'HTTP {resp.status_code}'
                return False, None
        except Exception as e:
            self.log_details['collect'] = str(e)
            return False, None

    def run_flow(self):
        """Execute complete flow"""
        # Step 1
        ok, _ = self.send_otp()
        if not ok:
            return False, self.log_details
        time.sleep(2)

        # Step 2
        ok, _ = self.verify_otp()
        if not ok:
            return False, self.log_details

        # Optional steps (ignore failures)
        self.get_user_state()
        self.fetch_homepage()

        # Step 5
        ok, _ = self.collect()
        return ok, self.log_details

def execute_offer(user_id, phone, otp):
    """Main entry point for bot commands"""
    api = ViedietAPI(user_id, phone, otp)
    success, logs = api.run_flow()
    # Log to database
    offer_name = api.config.get('offer_name', 'Unknown')
    platform = api.config.get('platform', 'Unknown')
    status = 'success' if success else 'failed'
    log_usage(user_id, offer_name, platform, status, json.dumps(logs))
    return success, logs
