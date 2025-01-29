from datetime import datetime, timedelta
import hashlib
from cryptography.hazmat.primitives import hashes, hmac

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.hmac_key = os.urandom(32)
        
    def create_session(self, username, ip):
        session_token = hashlib.blake2b(os.urandom(32)).hexdigest()
        self.sessions[session_token] = {
            'username': username,
            'ip': ip,
            'expires': datetime.now() + timedelta(hours=1)
        }
        return session_token

class CryptoEngine:
    @staticmethod
    def encrypt_data(data, key):
        h = hmac.HMAC(key, hashes.SHA512())
        h.update(json.dumps(data).encode())
        return h.finalize()