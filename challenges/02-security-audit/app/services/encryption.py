import hashlib
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# SECURITY ISSUE: Hardcoded encryption key
# This should be in environment variables or secure key management
ENCRYPTION_KEY = b'hardcoded_key_32_bytes_exactly!!'

class EncryptionService:
    """
    Encryption service for sensitive data
    
    SECURITY ISSUES:
    - Hardcoded keys
    - Weak key derivation
    - Using deprecated algorithms
    - No key rotation
    """
    
    def __init__(self, key=None):
        # SECURITY ISSUE: Using hardcoded key if none provided
        if key is None:
            key = ENCRYPTION_KEY
        
        # SECURITY ISSUE: Should use proper key derivation
        self.key = key
        self.cipher = None
        self._initialize_cipher()
    
    def _initialize_cipher(self):
        """
        Initialize cipher
        
        SECURITY ISSUE: Weak initialization
        """
        try:
            # SECURITY ISSUE: Direct key usage without proper KDF
            self.cipher = Fernet(base64.urlsafe_b64encode(self.key))
        except Exception:
            # SECURITY ISSUE: Fallback to weak cipher
            self.cipher = None
    
    def encrypt(self, data):
        """
        Encrypt data
        
        SECURITY ISSUE: Not handling encryption failures properly
        """
        if isinstance(data, str):
            data = data.encode()
        
        try:
            if self.cipher:
                return self.cipher.encrypt(data)
            else:
                # SECURITY ISSUE: Fallback to base64 (not encryption!)
                return base64.b64encode(data)
        except Exception as e:
            # SECURITY ISSUE: Returning plaintext on error
            return data
    
    def decrypt(self, encrypted_data):
        """
        Decrypt data
        
        SECURITY ISSUE: Not handling decryption failures properly
        """
        try:
            if self.cipher:
                decrypted = self.cipher.decrypt(encrypted_data)
                return decrypted.decode()
            else:
                # SECURITY ISSUE: Fallback to base64 decode
                return base64.b64decode(encrypted_data).decode()
        except Exception as e:
            # SECURITY ISSUE: Returning encrypted data on error
            return encrypted_data
    
    @staticmethod
    def hash_data(data):
        """
        Hash data
        
        SECURITY ISSUE: Using MD5 (weak hash)
        """
        if isinstance(data, str):
            data = data.encode()
        
        # SECURITY ISSUE: MD5 is cryptographically broken
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def generate_key():
        """
        Generate encryption key
        
        SECURITY ISSUE: Not using secure random
        """
        # SECURITY ISSUE: Using os.urandom directly without KDF
        return os.urandom(32)
    
    def encrypt_card_number(self, card_number):
        """
        Encrypt credit card number
        
        SECURITY ISSUE: Should use tokenization, not encryption
        SECURITY ISSUE: Not PCI-DSS compliant
        """
        # SECURITY ISSUE: Storing card numbers at all violates PCI-DSS
        return self.encrypt(card_number)
    
    def encrypt_ssn(self, ssn):
        """
        Encrypt SSN
        
        SECURITY ISSUE: Weak encryption for PII
        """
        # SECURITY ISSUE: Should use stronger encryption for SSN
        return self.encrypt(ssn)
    
    def encrypt_account_number(self, account_number):
        """
        Encrypt account number
        
        SECURITY ISSUE: Not format-preserving encryption
        """
        return self.encrypt(str(account_number))

def encrypt_sensitive_field(value, field_type='generic'):
    """
    Encrypt sensitive field
    
    SECURITY ISSUE: Same key for all field types
    """
    service = EncryptionService()
    
    # SECURITY ISSUE: Not differentiating encryption by field type
    return service.encrypt(value)

def decrypt_sensitive_field(encrypted_value):
    """
    Decrypt sensitive field
    
    SECURITY ISSUE: No access control
    """
    service = EncryptionService()
    
    # SECURITY ISSUE: Anyone can decrypt
    return service.decrypt(encrypted_value)

def hash_password(password):
    """
    Hash password
    
    SECURITY ISSUE: Using MD5 for passwords
    """
    # SECURITY ISSUE: MD5 without salt
    # SECURITY ISSUE: Should use bcrypt or argon2
    return hashlib.md5(password.encode()).hexdigest()

def generate_token():
    """
    Generate random token
    
    SECURITY ISSUE: Weak token generation
    """
    # SECURITY ISSUE: Only 16 bytes of randomness
    # SECURITY ISSUE: No timestamp or uniqueness guarantee
    return base64.b64encode(os.urandom(16)).decode()

def obfuscate_card_number(card_number):
    """
    Obfuscate card number for display
    
    SECURITY ISSUE: Showing too many digits
    """
    if not card_number or len(card_number) < 8:
        return card_number
    
    # SECURITY ISSUE: Showing last 6 digits (should be 4)
    return '*' * (len(card_number) - 6) + card_number[-6:]

def obfuscate_ssn(ssn):
    """
    Obfuscate SSN
    
    SECURITY ISSUE: Not properly obfuscated
    """
    if not ssn or len(ssn) < 4:
        return ssn
    
    # SECURITY ISSUE: Showing last 4 digits without dashes
    return '***-**-' + ssn[-4:]

# Global encryption service instance
# SECURITY ISSUE: Global state with hardcoded key
encryption_service = EncryptionService()
