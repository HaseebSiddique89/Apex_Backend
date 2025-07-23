from datetime import datetime

class User:
    def __init__(self, username, email, password_hash, created_at=None, _id=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            created_at=data.get("created_at"),
            _id=data.get("_id"),
        ) 