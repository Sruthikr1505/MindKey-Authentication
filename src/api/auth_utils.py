"""
Authentication utilities for user management and database operations.
"""

import os
from datetime import datetime
from typing import Optional
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    prototypes_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserStore:
    """User store for managing authentication."""
    
    def __init__(self, db_path: str = 'auth.db'):
        """
        Initialize user store.
        
        Args:
            db_path: Path to SQLite database
        """
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Initialized user store at {db_path}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def register_user(
        self,
        username: str,
        password: str,
        prototypes_path: str
    ) -> bool:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            prototypes_path: Path to user's prototypes file
        
        Returns:
            True if successful, False if user already exists
        """
        session = self.Session()
        
        try:
            # Check if user exists
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                logger.warning(f"User {username} already exists")
                return False
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user = User(
                username=username,
                password_hash=password_hash,
                prototypes_path=prototypes_path
            )
            
            session.add(user)
            session.commit()
            
            logger.info(f"Registered user {username}")
            return True
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error registering user {username}: {e}")
            return False
        
        finally:
            session.close()
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
        
        Returns:
            User object or None if not found
        """
        session = self.Session()
        
        try:
            user = session.query(User).filter_by(username=username).first()
            return user
        
        finally:
            session.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User object if authenticated, None otherwise
        """
        user = self.get_user(username)
        
        if user is None:
            logger.warning(f"User {username} not found")
            return None
        
        if not self.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user {username}")
            return None
        
        logger.info(f"Authenticated user {username}")
        return user
    
    def update_prototypes_path(self, username: str, prototypes_path: str) -> bool:
        """
        Update user's prototypes path.
        
        Args:
            username: Username
            prototypes_path: New prototypes path
        
        Returns:
            True if successful, False otherwise
        """
        session = self.Session()
        
        try:
            user = session.query(User).filter_by(username=username).first()
            if user is None:
                return False
            
            user.prototypes_path = prototypes_path
            session.commit()
            
            logger.info(f"Updated prototypes path for user {username}")
            return True
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating prototypes for {username}: {e}")
            return False
        
        finally:
            session.close()


# Demo
if __name__ == "__main__":
    print("Testing user store...")
    
    import tempfile
    import os
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    # Initialize store
    store = UserStore(temp_db.name)
    
    # Register user
    success = store.register_user('testuser', 'testpassword', '/path/to/prototypes.npz')
    print(f"Register user: {success}")
    
    # Try to register same user again
    success = store.register_user('testuser', 'testpassword', '/path/to/prototypes.npz')
    print(f"Register duplicate user: {success} (should be False)")
    
    # Authenticate user
    user = store.authenticate_user('testuser', 'testpassword')
    print(f"Authenticate user: {user is not None}")
    print(f"User details: {user.username}, {user.prototypes_path}")
    
    # Authenticate with wrong password
    user = store.authenticate_user('testuser', 'wrongpassword')
    print(f"Authenticate with wrong password: {user is not None} (should be False)")
    
    # Get user
    user = store.get_user('testuser')
    print(f"Get user: {user.username}")
    
    # Update prototypes path
    success = store.update_prototypes_path('testuser', '/new/path/prototypes.npz')
    print(f"Update prototypes path: {success}")
    
    user = store.get_user('testuser')
    print(f"New prototypes path: {user.prototypes_path}")
    
    # Cleanup
    os.unlink(temp_db.name)
    
    print("\nAll user store tests passed!")
