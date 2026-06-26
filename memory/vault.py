import base64
import hashlib
import os

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

class MemoryVault:
    """Provides secure, encrypted storage for sensitive data like notes and passwords."""
    
    def __init__(self, master_password="jarvis_master_key"):
        # Derive a key from the master password using SHA-256
        self.key = hashlib.sha256(master_password.encode()).digest()
        
        if HAS_CRYPTOGRAPHY:
            # Fernet requires a base64url-encoded 32-byte key
            fernet_key = base64.urlsafe_b64encode(self.key)
            self.cipher = Fernet(fernet_key)
        else:
            self.cipher = None

    def encrypt(self, plaintext: str) -> str:
        """Encrypts plaintext string to a base64 encoded ciphertext string."""
        if not plaintext:
            return ""
        
        data = plaintext.encode('utf-8')
        
        if HAS_CRYPTOGRAPHY and self.cipher:
            encrypted_data = self.cipher.encrypt(data)
            return encrypted_data.decode('utf-8')
        else:
            # Simple, fallback encryption (XOR with key repeating)
            encrypted_bytes = bytearray()
            for i, byte in enumerate(data):
                key_byte = self.key[i % len(self.key)]
                encrypted_bytes.append(byte ^ key_byte)
            return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts base64 encoded ciphertext string to plaintext string."""
        if not ciphertext:
            return ""
        
        try:
            if HAS_CRYPTOGRAPHY and self.cipher:
                decrypted_bytes = self.cipher.decrypt(ciphertext.encode('utf-8'))
                return decrypted_bytes.decode('utf-8')
            else:
                # Fallback decryption (XOR with key repeating)
                encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
                decrypted_bytes = bytearray()
                for i, byte in enumerate(encrypted_bytes):
                    key_byte = self.key[i % len(self.key)]
                    decrypted_bytes.append(byte ^ key_byte)
                return decrypted_bytes.decode('utf-8')
        except Exception:
            return "[Decryption Failed: Invalid master password or corrupted data]"
            
    def encrypt_file(self, source_path: str, dest_path: str) -> bool:
        """Encrypts a file and writes it to dest_path."""
        if not os.path.exists(source_path):
            return False
        try:
            with open(source_path, 'rb') as f:
                data = f.read()
                
            if HAS_CRYPTOGRAPHY and self.cipher:
                encrypted = self.cipher.encrypt(data)
            else:
                encrypted_bytes = bytearray()
                for i, byte in enumerate(data):
                    key_byte = self.key[i % len(self.key)]
                    encrypted_bytes.append(byte ^ key_byte)
                encrypted = base64.b64encode(encrypted_bytes)
                
            with open(dest_path, 'wb') as f:
                f.write(encrypted)
            return True
        except Exception:
            return False

    def decrypt_file(self, source_path: str, dest_path: str) -> bool:
        """Decrypts an encrypted file and writes it to dest_path."""
        if not os.path.exists(source_path):
            return False
        try:
            with open(source_path, 'rb') as f:
                data = f.read()
                
            if HAS_CRYPTOGRAPHY and self.cipher:
                decrypted = self.cipher.decrypt(data)
            else:
                decoded_bytes = base64.b64decode(data)
                decrypted_bytes = bytearray()
                for i, byte in enumerate(decoded_bytes):
                    key_byte = self.key[i % len(self.key)]
                    decrypted_bytes.append(byte ^ key_byte)
                decrypted = bytes(decrypted_bytes)
                
            with open(dest_path, 'wb') as f:
                f.write(decrypted)
            return True
        except Exception:
            return False
