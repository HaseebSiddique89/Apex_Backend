from datetime import datetime

class User:
    def __init__(self, username, email, password_hash, created_at=None, _id=None, is_email_verified=False, email_verification_token=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.is_email_verified = is_email_verified
        self.email_verification_token = email_verification_token

    def to_dict(self):
        return {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "is_email_verified": self.is_email_verified,
            "email_verification_token": self.email_verification_token,
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            created_at=data.get("created_at"),
            _id=data.get("_id"),
            is_email_verified=data.get("is_email_verified", False),
            email_verification_token=data.get("email_verification_token"),
        ) 