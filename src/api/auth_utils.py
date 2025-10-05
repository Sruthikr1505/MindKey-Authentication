"""
Authentication Utilities
User database management with SQLAlchemy and bcrypt password hashing.
"""

import os
from datetime import datetime
from pathlib import Path
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    prototypes_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"


class AuthLog(Base):
    """Authentication log model"""
    __tablename__ = 'auth_logs'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    authenticated = Column(Boolean, nullable=False)
    score = Column(Float, nullable=True)
    probability = Column(Float, nullable=True)
    is_spoof = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuthLog(username='{self.username}', authenticated={self.authenticated})>"


class UserDatabase:
    """User database manager"""
    
    def __init__(self, db_path: str = 'data/users.db'):
        """Initialize database connection"""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def register_user(self, username: str, password: str, prototypes_path: str) -> User:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            prototypes_path: Path to user's prototype embeddings
            
        Returns:
            user: Created User object
            
        Raises:
            ValueError: If username already exists
        """
        # Check if user exists
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user = User(
            username=username,
            password_hash=password_hash,
            prototypes_path=prototypes_path
        )
        
        self.session.add(user)
        self.session.commit()
        
        return user
    
    def get_user(self, username: str) -> User:
        """Get user by username"""
        return self.session.query(User).filter_by(username=username).first()
    
    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            user: User object if authenticated, None otherwise
        """
        user = self.get_user(username)
        if user and self.verify_password(password, user.password_hash):
            return user
        return None
    
    def delete_user(self, username: str):
        """Delete user by username"""
        user = self.get_user(username)
        if user:
            self.session.delete(user)
            self.session.commit()
    
    def list_users(self):
        """List all users"""
        return self.session.query(User).all()
    
    def log_authentication(self, username: str, authenticated: bool, score: float = None, 
                          probability: float = None, is_spoof: bool = None):
        """
        Log an authentication attempt.
        
        Args:
            username: Username attempting authentication
            authenticated: Whether authentication was successful
            score: Similarity score
            probability: Calibrated probability
            is_spoof: Whether spoof was detected
        """
        log_entry = AuthLog(
            username=username,
            authenticated=authenticated,
            score=score,
            probability=probability,
            is_spoof=is_spoof
        )
        self.session.add(log_entry)
        self.session.commit()
        return log_entry
    
    def get_auth_logs(self, username: str = None, limit: int = 100):
        """
        Get authentication logs.
        
        Args:
            username: Filter by username (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of AuthLog objects
        """
        query = self.session.query(AuthLog)
        if username:
            query = query.filter_by(username=username)
        return query.order_by(AuthLog.timestamp.desc()).limit(limit).all()
    
    def get_statistics(self):
        """Get authentication statistics"""
        total_attempts = self.session.query(AuthLog).count()
        successful = self.session.query(AuthLog).filter_by(authenticated=True).count()
        failed = self.session.query(AuthLog).filter_by(authenticated=False).count()
        spoofs = self.session.query(AuthLog).filter_by(is_spoof=True).count()
        
        return {
            'total_attempts': total_attempts,
            'successful': successful,
            'failed': failed,
            'impostor_attempts': failed,
            'spoof_attempts': spoofs,
            'success_rate': (successful / total_attempts * 100) if total_attempts > 0 else 0
        }


if __name__ == "__main__":
    # Demo
    print("Testing user database...")
    
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/test_users.db"
        db = UserDatabase(db_path)
        
        # Register user
        user = db.register_user(
            username='alice',
            password='secret123',
            prototypes_path='/path/to/alice_prototypes.npy'
        )
        print(f"Registered user: {user}")
        
        # Try duplicate registration
        try:
            db.register_user('alice', 'another_password', '/path/to/proto.npy')
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"Duplicate registration blocked: {e}")
        
        # Authenticate
        auth_user = db.authenticate_user('alice', 'secret123')
        assert auth_user is not None
        print(f"Authentication successful: {auth_user}")
        
        # Wrong password
        auth_user = db.authenticate_user('alice', 'wrong_password')
        assert auth_user is None
        print("Wrong password rejected")
        
        # Get user
        retrieved_user = db.get_user('alice')
        assert retrieved_user.username == 'alice'
        print(f"Retrieved user: {retrieved_user}")
        
        # List users
        users = db.list_users()
        print(f"Total users: {len(users)}")
        
        # Delete user
        db.delete_user('alice')
        users = db.list_users()
        assert len(users) == 0
        print("User deleted successfully")
    
    print("User database tests passed!")
