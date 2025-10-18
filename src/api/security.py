"""
Security utilities for the EEG authentication system.
Implements rate limiting, input validation, and security headers.
"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Rate limiting storage (in-memory, use Redis in production)
rate_limit_storage: Dict[str, list] = defaultdict(list)
failed_login_attempts: Dict[str, list] = defaultdict(list)


class SecurityValidator:
    """Security validation and sanitization utilities."""
    
    # File upload constraints
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.npy', '.edf', '.bdf'}
    
    # Password policy
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # Username policy
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            (is_valid, error_message)
        """
        if len(password) < SecurityValidator.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {SecurityValidator.MIN_PASSWORD_LENGTH} characters"
        
        if len(password) > SecurityValidator.MAX_PASSWORD_LENGTH:
            return False, f"Password must be less than {SecurityValidator.MAX_PASSWORD_LENGTH} characters"
        
        # Check for character variety
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and numbers"
        
        if not has_special:
            logger.warning("Password missing special characters (recommended)")
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format.
        
        Returns:
            (is_valid, error_message)
        """
        if len(username) < SecurityValidator.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {SecurityValidator.MIN_USERNAME_LENGTH} characters"
        
        if len(username) > SecurityValidator.MAX_USERNAME_LENGTH:
            return False, f"Username must be less than {SecurityValidator.MAX_USERNAME_LENGTH} characters"
        
        if not SecurityValidator.USERNAME_PATTERN.match(username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        # Prevent SQL injection patterns
        dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
        username_upper = username.upper()
        if any(pattern in username_upper for pattern in dangerous_patterns):
            return False, "Username contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_file_upload(filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate uploaded file.
        
        Returns:
            (is_valid, error_message)
        """
        # Check file size
        if file_size > SecurityValidator.MAX_FILE_SIZE:
            return False, f"File size exceeds {SecurityValidator.MAX_FILE_SIZE / 1024 / 1024}MB limit"
        
        # Check file extension
        import os
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SecurityValidator.ALLOWED_EXTENSIONS:
            return False, f"File type {ext} not allowed. Allowed types: {', '.join(SecurityValidator.ALLOWED_EXTENSIONS)}"
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename"
        
        # Check filename length
        if len(filename) > 255:
            return False, "Filename too long"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal."""
        # Remove path components
        import os
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        return filename
    
    @staticmethod
    def generate_secure_token() -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()


class RateLimiter:
    """Rate limiting to prevent brute force attacks."""
    
    @staticmethod
    def check_rate_limit(client_ip: str, endpoint: str) -> bool:
        """
        Check if request is within rate limit.
        
        Returns:
            True if allowed, False if rate limited
        """
        key = f"{client_ip}:{endpoint}"
        now = datetime.now()
        
        # Clean old entries
        rate_limit_storage[key] = [
            timestamp for timestamp in rate_limit_storage[key]
            if now - timestamp < timedelta(minutes=1)
        ]
        
        # Check limit
        if len(rate_limit_storage[key]) >= SecurityValidator.MAX_REQUESTS_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
            return False
        
        # Add current request
        rate_limit_storage[key].append(now)
        return True
    
    @staticmethod
    def check_login_attempts(username: str, client_ip: str) -> tuple[bool, Optional[datetime]]:
        """
        Check if login attempts are within limit.
        
        Returns:
            (is_allowed, lockout_until)
        """
        key = f"{username}:{client_ip}"
        now = datetime.now()
        
        # Clean old entries
        failed_login_attempts[key] = [
            timestamp for timestamp in failed_login_attempts[key]
            if now - timestamp < SecurityValidator.LOCKOUT_DURATION
        ]
        
        # Check if locked out
        if len(failed_login_attempts[key]) >= SecurityValidator.MAX_LOGIN_ATTEMPTS:
            lockout_until = failed_login_attempts[key][0] + SecurityValidator.LOCKOUT_DURATION
            if now < lockout_until:
                logger.warning(f"Account locked for {username} from {client_ip}")
                return False, lockout_until
            else:
                # Lockout expired, clear attempts
                failed_login_attempts[key] = []
        
        return True, None
    
    @staticmethod
    def record_failed_login(username: str, client_ip: str):
        """Record a failed login attempt."""
        key = f"{username}:{client_ip}"
        failed_login_attempts[key].append(datetime.now())
        logger.warning(f"Failed login attempt for {username} from {client_ip}")
    
    @staticmethod
    def clear_failed_logins(username: str, client_ip: str):
        """Clear failed login attempts after successful login."""
        key = f"{username}:{client_ip}"
        if key in failed_login_attempts:
            del failed_login_attempts[key]


def add_security_headers(response: JSONResponse) -> JSONResponse:
    """Add security headers to response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


async def rate_limit_middleware(request: Request, call_next):
    """Middleware for rate limiting."""
    client_ip = request.client.host
    endpoint = request.url.path
    
    # Exclude docs endpoints from rate limiting
    excluded_paths = ["/docs", "/redoc", "/openapi.json", "/"]
    if endpoint in excluded_paths or endpoint.startswith("/docs") or endpoint.startswith("/redoc"):
        response = await call_next(request)
        return response
    
    if not RateLimiter.check_rate_limit(client_ip, endpoint):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    response = await call_next(request)
    return add_security_headers(response)


# Input sanitization for XSS prevention
def sanitize_html(text: str) -> str:
    """Sanitize HTML to prevent XSS attacks."""
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Escape special characters
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text


# CSRF token management
csrf_tokens: Dict[str, datetime] = {}

def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    token = SecurityValidator.generate_secure_token()
    csrf_tokens[token] = datetime.now() + timedelta(hours=1)
    return token

def validate_csrf_token(token: str) -> bool:
    """Validate a CSRF token."""
    if token not in csrf_tokens:
        return False
    
    if datetime.now() > csrf_tokens[token]:
        del csrf_tokens[token]
        return False
    
    return True
