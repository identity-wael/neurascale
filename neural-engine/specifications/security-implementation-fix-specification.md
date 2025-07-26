# Security Implementation Fix Specification

## Document Version

- **Version**: 1.0.0
- **Date**: January 26, 2025
- **Author**: Principal Engineer / Security Engineer
- **Status**: Ready for Implementation

## 1. Executive Summary

This specification addresses the critical security implementation issues in the Neural Engine, including the incorrect directory structure, missing access control components, and HIPAA compliance requirements. The security layer is essential for protecting sensitive neural data and ensuring regulatory compliance.

## 2. Current State Analysis

### 2.1 Existing Issues

1. **Wrong Directory Location**: Security module is in `neural-engine/neural-engine/security/` instead of `neural-engine/security/`
2. **Import Path Problems**: All imports reference the incorrect nested path
3. **Missing Components**: No RBAC implementation, no audit logging middleware, no HIPAA compliance features
4. **Incomplete Integration**: Security not integrated with Neural Ledger

### 2.2 Existing Assets

```
neural-engine/neural-engine/security/
├── __init__.py
├── encryption.py          # KMS-based encryption (working)
├── benchmark_encryption.py # Performance benchmarks
├── example_usage.py       # Usage examples
└── README.md             # Basic documentation
```

### 2.3 Dependencies on This Fix

- Neural Ledger requires encryption for sensitive metadata
- API endpoints need authentication middleware
- Device pairing needs secure key exchange
- All data storage needs field-level encryption

## 3. Functional Requirements

### 3.1 Directory Structure Fix

The system SHALL:

- Move all security files to the correct location
- Update all import statements across the codebase
- Maintain backward compatibility during migration
- Verify no broken imports after migration

### 3.2 Access Control Implementation

The system SHALL provide:

- Role-Based Access Control (RBAC) with predefined roles
- JWT-based authentication with refresh tokens
- Fine-grained permissions for neural data access
- Multi-tenant isolation for SaaS deployment
- Session management with timeout policies

### 3.3 HIPAA Compliance Features

The system SHALL implement:

- PHI data identification and classification
- Automatic anonymization pipelines
- Consent management system
- Data retention and deletion policies
- Access audit trail integration with Neural Ledger

### 3.4 Security Middleware

The system SHALL provide:

- Authentication middleware for all API endpoints
- Authorization checks based on roles and permissions
- Request/response encryption for sensitive data
- Rate limiting and DDoS protection
- Security headers (HSTS, CSP, X-Frame-Options)

## 4. Technical Architecture

### 4.1 New Directory Structure

```
neural-engine/
├── security/
│   ├── __init__.py
│   ├── encryption.py              # Existing KMS encryption
│   ├── access_control.py          # NEW: RBAC implementation
│   ├── authentication.py          # NEW: JWT auth
│   ├── authorization.py           # NEW: Permission checks
│   ├── hipaa_compliance.py        # NEW: HIPAA features
│   ├── middleware.py              # NEW: Security middleware
│   ├── anonymization.py           # NEW: PHI anonymization
│   ├── consent_manager.py         # NEW: Consent tracking
│   ├── key_management.py          # NEW: Key rotation
│   └── utils/
│       ├── __init__.py
│       ├── validators.py          # Input validation
│       └── sanitizers.py          # Data sanitization
```

### 4.2 Role-Based Access Control Schema

```python
from enum import Enum
from dataclasses import dataclass
from typing import Set, Optional, Dict, Any

class Role(Enum):
    """System roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"      # Full system access
    ADMIN = "admin"                  # Organizational admin
    CLINICIAN = "clinician"          # Patient data access
    RESEARCHER = "researcher"        # Anonymized data access
    PATIENT = "patient"              # Own data access only
    DEVICE = "device"                # Device API access
    SERVICE = "service"              # Internal service account

class Permission(Enum):
    """Granular permissions for resources"""
    # Data permissions
    READ_NEURAL_DATA = "read_neural_data"
    WRITE_NEURAL_DATA = "write_neural_data"
    DELETE_NEURAL_DATA = "delete_neural_data"
    EXPORT_NEURAL_DATA = "export_neural_data"

    # Session permissions
    CREATE_SESSION = "create_session"
    VIEW_SESSION = "view_session"
    MODIFY_SESSION = "modify_session"
    DELETE_SESSION = "delete_session"

    # Device permissions
    REGISTER_DEVICE = "register_device"
    PAIR_DEVICE = "pair_device"
    MANAGE_DEVICE = "manage_device"

    # User management
    CREATE_USER = "create_user"
    MODIFY_USER = "modify_user"
    DELETE_USER = "delete_user"
    ASSIGN_ROLE = "assign_role"

    # System permissions
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_CONSENT = "manage_consent"
    CONFIGURE_SYSTEM = "configure_system"
    VIEW_ANALYTICS = "view_analytics"

@dataclass
class RolePermissionMapping:
    """Maps roles to their allowed permissions"""
    role_permissions: Dict[Role, Set[Permission]] = {
        Role.SUPER_ADMIN: set(Permission),  # All permissions

        Role.ADMIN: {
            Permission.READ_NEURAL_DATA,
            Permission.WRITE_NEURAL_DATA,
            Permission.CREATE_SESSION,
            Permission.VIEW_SESSION,
            Permission.MODIFY_SESSION,
            Permission.REGISTER_DEVICE,
            Permission.PAIR_DEVICE,
            Permission.MANAGE_DEVICE,
            Permission.CREATE_USER,
            Permission.MODIFY_USER,
            Permission.ASSIGN_ROLE,
            Permission.VIEW_AUDIT_LOG,
            Permission.VIEW_ANALYTICS,
        },

        Role.CLINICIAN: {
            Permission.READ_NEURAL_DATA,
            Permission.WRITE_NEURAL_DATA,
            Permission.CREATE_SESSION,
            Permission.VIEW_SESSION,
            Permission.MODIFY_SESSION,
            Permission.PAIR_DEVICE,
            Permission.VIEW_AUDIT_LOG,
        },

        Role.RESEARCHER: {
            Permission.READ_NEURAL_DATA,  # Anonymized only
            Permission.VIEW_SESSION,       # Anonymized only
            Permission.EXPORT_NEURAL_DATA, # With approval
            Permission.VIEW_ANALYTICS,
        },

        Role.PATIENT: {
            Permission.READ_NEURAL_DATA,   # Own data only
            Permission.VIEW_SESSION,       # Own sessions only
            Permission.EXPORT_NEURAL_DATA, # Own data only
            Permission.MANAGE_CONSENT,     # Own consent only
        },

        Role.DEVICE: {
            Permission.WRITE_NEURAL_DATA,
            Permission.CREATE_SESSION,
            Permission.MODIFY_SESSION,
        },

        Role.SERVICE: {
            Permission.READ_NEURAL_DATA,
            Permission.WRITE_NEURAL_DATA,
        }
    }
```

### 4.3 JWT Authentication Implementation

```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

class JWTManager:
    """Manages JWT token generation and validation"""

    def __init__(self,
                 secret_key: str,
                 algorithm: str = "HS256",
                 access_token_expire_minutes: int = 30,
                 refresh_token_expire_days: int = 7):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_expire = timedelta(days=refresh_token_expire_days)

    def generate_access_token(self,
                            user_id: str,
                            role: Role,
                            tenant_id: Optional[str] = None) -> str:
        """Generate access token with user claims"""
        payload = {
            "sub": user_id,
            "role": role.value,
            "tenant_id": tenant_id,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.access_expire,
            "jti": secrets.token_urlsafe(16),  # Unique token ID
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token for token renewal"""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.refresh_expire,
            "jti": secrets.token_urlsafe(16),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Validate and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError(f"Invalid token type. Expected {token_type}")

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
```

### 4.4 HIPAA Compliance Implementation

```python
from typing import Dict, Any, List, Optional
import hashlib
import re

class PHIAnonymizer:
    """Anonymizes Protected Health Information (PHI)"""

    # PHI identifiers per HIPAA
    PHI_PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'mrn': r'\b[A-Z]{2}\d{6,8}\b',  # Medical Record Number
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }

    def __init__(self, salt: str):
        self.salt = salt

    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize PHI in neural data metadata"""
        anonymized = data.copy()

        # Direct identifiers
        if 'patient_id' in anonymized:
            anonymized['patient_id'] = self._hash_identifier(data['patient_id'])

        if 'name' in anonymized:
            anonymized['name'] = 'REDACTED'

        if 'date_of_birth' in anonymized:
            # Keep year only for age calculation
            dob = anonymized['date_of_birth']
            anonymized['birth_year'] = dob.year if hasattr(dob, 'year') else None
            del anonymized['date_of_birth']

        # Scan for PHI patterns in all string fields
        for key, value in anonymized.items():
            if isinstance(value, str):
                anonymized[key] = self._redact_phi_patterns(value)

        return anonymized

    def _hash_identifier(self, identifier: str) -> str:
        """Create consistent one-way hash of identifier"""
        return hashlib.sha256(f"{identifier}{self.salt}".encode()).hexdigest()[:16]

    def _redact_phi_patterns(self, text: str) -> str:
        """Redact PHI patterns from text"""
        for pattern_name, pattern in self.PHI_PATTERNS.items():
            text = re.sub(pattern, f"[{pattern_name.upper()}_REDACTED]", text)
        return text

class ConsentManager:
    """Manages patient consent for data usage"""

    def __init__(self, firestore_client):
        self.db = firestore_client
        self.collection = 'consent_records'

    async def record_consent(self,
                           patient_id: str,
                           consent_type: str,
                           granted: bool,
                           purpose: str,
                           expiry_date: Optional[datetime] = None) -> str:
        """Record patient consent decision"""
        consent_record = {
            'patient_id': patient_id,
            'consent_type': consent_type,
            'granted': granted,
            'purpose': purpose,
            'timestamp': datetime.utcnow(),
            'expiry_date': expiry_date,
            'ip_address': 'REDACTED',  # Store separately for audit
            'version': '1.0',  # Consent form version
        }

        # Store in Firestore
        doc_ref = self.db.collection(self.collection).document()
        await doc_ref.set(consent_record)

        # Log to Neural Ledger
        await self._log_consent_event(consent_record)

        return doc_ref.id

    async def check_consent(self,
                          patient_id: str,
                          consent_type: str,
                          purpose: str) -> bool:
        """Check if valid consent exists"""
        query = self.db.collection(self.collection).where(
            'patient_id', '==', patient_id
        ).where(
            'consent_type', '==', consent_type
        ).where(
            'granted', '==', True
        ).order_by('timestamp', direction='DESCENDING').limit(1)

        docs = await query.get()

        if not docs:
            return False

        consent = docs[0].to_dict()

        # Check expiry
        if consent.get('expiry_date') and consent['expiry_date'] < datetime.utcnow():
            return False

        # Check purpose matches
        if purpose not in consent.get('purpose', ''):
            return False

        return True
```

### 4.5 Security Middleware

```python
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import time

class SecurityMiddleware:
    """FastAPI security middleware for all requests"""

    def __init__(self, jwt_manager: JWTManager, rbac: RBACManager):
        self.jwt_manager = jwt_manager
        self.rbac = rbac
        self.bearer = HTTPBearer()

    async def authenticate(self,
                         credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        """Authenticate request and return user context"""
        token = credentials.credentials

        try:
            payload = self.jwt_manager.validate_token(token)
            return {
                'user_id': payload['sub'],
                'role': Role(payload['role']),
                'tenant_id': payload.get('tenant_id'),
                'token_id': payload['jti'],
            }
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))

    def require_permission(self, permission: Permission):
        """Decorator to check permissions for endpoints"""
        async def permission_checker(user_context: Dict = Depends(self.authenticate)):
            if not self.rbac.has_permission(user_context['role'], permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied. Required: {permission.value}"
                )
            return user_context
        return permission_checker

    def require_resource_access(self, resource_type: str):
        """Check access to specific resources"""
        async def resource_checker(
            resource_id: str,
            user_context: Dict = Depends(self.authenticate)
        ):
            # Check if user has access to specific resource
            has_access = await self.rbac.check_resource_access(
                user_context['user_id'],
                user_context['role'],
                resource_type,
                resource_id,
                user_context.get('tenant_id')
            )

            if not has_access:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied to {resource_type}/{resource_id}"
                )

            return user_context
        return resource_checker

class RateLimiter:
    """Rate limiting middleware"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.limits = {
            Role.DEVICE: {"requests": 1000, "window": 60},      # 1000/min
            Role.SERVICE: {"requests": 10000, "window": 60},    # 10k/min
            Role.RESEARCHER: {"requests": 100, "window": 60},   # 100/min
            Role.PATIENT: {"requests": 60, "window": 60},       # 60/min
        }

    async def check_rate_limit(self, user_id: str, role: Role) -> bool:
        """Check if request is within rate limits"""
        key = f"rate_limit:{user_id}"
        window = self.limits.get(role, {"requests": 60, "window": 60})

        current = await self.redis.incr(key)

        if current == 1:
            await self.redis.expire(key, window["window"])

        if current > window["requests"]:
            return False

        return True
```

## 5. Implementation Plan

### 5.1 Phase 1: Directory Migration (2 hours)

```bash
#!/bin/bash
# Migration script: migrate_security_module.sh

# Step 1: Create new security directory
mkdir -p neural-engine/security

# Step 2: Copy existing files
cp -r neural-engine/neural-engine/security/* neural-engine/security/

# Step 3: Update imports in all Python files
find neural-engine -name "*.py" -type f -exec sed -i '' \
  's/from neural_engine\.neural_engine\.security/from neural_engine.security/g' {} \;

find neural-engine -name "*.py" -type f -exec sed -i '' \
  's/import neural_engine\.neural_engine\.security/import neural_engine.security/g' {} \;

# Step 4: Run tests to verify
pytest neural-engine/tests/unit/test_security/

# Step 5: Remove old directory after verification
rm -rf neural-engine/neural-engine/security
```

### 5.2 Phase 2: Core Security Components (6 hours)

1. **Access Control Implementation**

   - Create `access_control.py` with RBAC logic
   - Create `authentication.py` with JWT management
   - Create `authorization.py` with permission checks
   - Write unit tests for all components

2. **Database Schema for Security**

   ```sql
   -- Users table
   CREATE TABLE users (
       id UUID PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL,
       role VARCHAR(50) NOT NULL,
       tenant_id UUID,
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW()
   );

   -- Sessions table
   CREATE TABLE user_sessions (
       id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id),
       token_id VARCHAR(255) UNIQUE NOT NULL,
       expires_at TIMESTAMP NOT NULL,
       revoked BOOLEAN DEFAULT FALSE,
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- Permissions override table
   CREATE TABLE user_permissions (
       user_id UUID REFERENCES users(id),
       permission VARCHAR(100) NOT NULL,
       resource_type VARCHAR(50),
       resource_id VARCHAR(255),
       granted BOOLEAN DEFAULT TRUE,
       expires_at TIMESTAMP,
       PRIMARY KEY (user_id, permission, resource_type, resource_id)
   );
   ```

### 5.3 Phase 3: HIPAA Compliance (4 hours)

1. **PHI Anonymization**

   - Implement `anonymization.py` with PHI patterns
   - Create anonymization pipeline for batch processing
   - Add real-time anonymization for API responses

2. **Consent Management**

   - Implement `consent_manager.py`
   - Create Firestore collections for consent records
   - Add consent check middleware

3. **Data Retention**
   - Create retention policy configuration
   - Implement automated deletion jobs
   - Add audit trail for deletions

### 5.4 Phase 4: Integration (4 hours)

1. **Neural Ledger Integration**

   ```python
   # Log all security events to Neural Ledger
   async def log_security_event(event_type: str,
                               user_id: str,
                               details: Dict[str, Any]):
       event = NeuralLedgerEvent(
           event_type=EventType.AUTH_SUCCESS,  # or AUTH_FAILURE, ACCESS_GRANTED, etc.
           user_id=user_id,
           metadata=details,
           # ... other fields
       )
       await ledger_processor.process_event(event)
   ```

2. **API Integration**

   - Add security middleware to all endpoints
   - Implement resource-based access control
   - Add rate limiting

3. **Testing**
   - Integration tests with Neural Ledger
   - Load tests for authentication
   - Security penetration testing

## 6. Security Considerations

### 6.1 Key Management

- JWT signing keys rotated monthly
- Encryption keys managed by Cloud KMS
- Service account keys rotated quarterly
- API keys with expiration dates

### 6.2 Defense in Depth

- Network layer: VPC, firewall rules
- Application layer: Authentication, authorization
- Data layer: Encryption at rest and in transit
- Audit layer: All actions logged to Neural Ledger

### 6.3 Zero Trust Principles

- Verify every request
- Least privilege access
- Assume breach mentality
- Continuous verification

## 7. Monitoring and Alerting

### 7.1 Security Metrics

```yaml
# Prometheus metrics
neural_security_auth_attempts_total{result="success|failure"}
neural_security_permission_checks_total{permission="...", granted="true|false"}
neural_security_token_validations_total{result="valid|expired|invalid"}
neural_security_phi_anonymizations_total
neural_security_consent_checks_total{result="granted|denied"}
```

### 7.2 Security Alerts

- Failed authentication spike (>100 in 5 minutes)
- Privilege escalation attempts
- Unusual data access patterns
- Expired certificate warnings
- Rate limit violations

## 8. Testing Requirements

### 8.1 Unit Tests

- RBAC permission logic
- JWT token generation/validation
- PHI anonymization patterns
- Consent checking logic

### 8.2 Integration Tests

- End-to-end authentication flow
- Permission checks with real resources
- Rate limiting under load
- Security middleware with API

### 8.3 Security Tests

- Penetration testing
- OWASP Top 10 verification
- SQL injection prevention
- XSS prevention
- CSRF protection

## 9. Migration Checklist

- [ ] Backup existing security module
- [ ] Run migration script
- [ ] Verify all imports updated
- [ ] Deploy RBAC implementation
- [ ] Deploy JWT authentication
- [ ] Deploy HIPAA compliance features
- [ ] Update API with security middleware
- [ ] Run integration tests
- [ ] Security audit
- [ ] Update documentation

## 10. Success Criteria

1. **Functional**

   - All imports reference correct path
   - Authentication works for all user types
   - Permissions enforced correctly
   - PHI properly anonymized

2. **Performance**

   - Authentication adds <10ms latency
   - Permission checks <5ms
   - Token validation <2ms

3. **Security**
   - Passes penetration testing
   - HIPAA compliance verified
   - No unauthorized access possible
   - Audit trail complete

## 11. Cost Impact

```yaml
# Additional monthly costs
Cloud KMS operations: $20 (key rotations)
Firestore (consent): $50 (10GB + operations)
Redis (rate limiting): $100 (1 instance)
Additional compute: $50
Total: ~$220/month
```
