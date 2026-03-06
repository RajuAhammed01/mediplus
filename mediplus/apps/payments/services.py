import requests
import json
import uuid
from django.conf import settings
from django.utils import timezone
from .models import Payment, Refund
import logging

logger = logging.getLogger(__name__)

class BKashService:
    """bKash Payment Gateway Integration"""
    
    def __init__(self):
        self.base_url = settings.BKASH_BASE_URL
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.token = None
        self.token_expiry = None
    
    def _get_token(self):
        """Get authentication token from bKash"""
        if self.token and self.token_expiry and timezone.now() < self.token_expiry:
            return self.token
        
        url = f"{self.base_url}/tokenized/checkout/token/grant"
        headers = {
            'Content-Type': 'application/json',
            'username': self.username,
            'password': self.password
        }
        payload = {
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('id_token')
                # Token expires in 1 hour (3500 seconds)
                self.token_expiry = timezone.now() + timezone.timedelta(seconds=3500)
                return self.token
            else:
                logger.error(f"bKash token error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"bKash token exception: {str(e)}")
            return None
    
    def create_payment(self, amount, merchant_invoice_number=None):
        """Create a bKash payment"""
        token = self._get_token()
        if not token:
            return {'error': 'Failed to get bKash token'}
        
        url = f"{self.base_url}/tokenized/checkout/create"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            'X-APP-Key': self.app_key
        }
        
        if not merchant_invoice_number:
            merchant_invoice_number = f"INV{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
        
        payload = {
            'mode': '0011',
            'payerReference': '1',
            'callbackURL': f"{settings.SITE_URL}/api/payments/bkash/callback/",
            'amount': str(amount),
            'currency': 'BDT',
            'intent': 'sale',
            'merchantInvoiceNumber': merchant_invoice_number
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"bKash create payment error: {response.text}")
                return {'error': 'Failed to create payment'}
        except Exception as e:
            logger.error(f"bKash create payment exception: {str(e)}")
            return {'error': str(e)}
    
    def execute_payment(self, payment_id):
        """Execute a bKash payment"""
        token = self._get_token()
        if not token:
            return {'error': 'Failed to get bKash token'}
        
        url = f"{self.base_url}/tokenized/checkout/execute"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            'X-APP-Key': self.app_key
        }
        
        payload = {
            'paymentID': payment_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"bKash execute payment error: {response.text}")
                return {'error': 'Failed to execute payment'}
        except Exception as e:
            logger.error(f"bKash execute payment exception: {str(e)}")
            return {'error': str(e)}
    
    def query_payment(self, payment_id):
        """Query payment status"""
        token = self._get_token()
        if not token:
            return {'error': 'Failed to get bKash token'}
        
        url = f"{self.base_url}/tokenized/checkout/payment/status"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            'X-APP-Key': self.app_key
        }
        
        payload = {
            'paymentID': payment_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"bKash query payment error: {response.text}")
                return {'error': 'Failed to query payment'}
        except Exception as e:
            logger.error(f"bKash query payment exception: {str(e)}")
            return {'error': str(e)}
    
    def refund_payment(self, payment_id, amount, trx_id, reason):
        """Process refund"""
        token = self._get_token()
        if not token:
            return {'error': 'Failed to get bKash token'}
        
        url = f"{self.base_url}/tokenized/checkout/payment/refund"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            'X-APP-Key': self.app_key
        }
        
        payload = {
            'paymentID': payment_id,
            'amount': str(amount),
            'trxID': trx_id,
            'sku': 'refund',
            'reason': reason
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"bKash refund error: {response.text}")
                return {'error': 'Failed to process refund'}
        except Exception as e:
            logger.error(f"bKash refund exception: {str(e)}")
            return {'error': str(e)}