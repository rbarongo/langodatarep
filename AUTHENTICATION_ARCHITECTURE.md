# Authentication System Architecture

This document describes the technical design and implementation of the updated authentication system.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                              │
│                                                                     │
│  read_data(data_group, data_source, ...)                          │
│         ↓                                                           │
│  validate_environment(data_group)                                  │
│         ↓                                                           │
│  authenticate_user(data_group)                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION LAYER                             │
│                                                                     │
│         ┌──────────────────────────────────────────────────┐      │
│         │  authenticate_user(data_group="BSIS")           │      │
│         │     ├─ Check existing token                     │      │
│         │     └─ perform_bsis_login(user, pwd)            │      │
│         └──────────────────────────────────────────────────┘      │
│                         ↓                                          │
│         ┌──────────────────────────────────────────────────┐      │
│         │ perform_bsis_login(user, pwd)                  │      │
│         │   └─ DatabaseConnection("BSIS")                │      │
│         │      └─ callproc('bsis_dev.dt_match_...')      │      │
│         └──────────────────────────────────────────────────┘      │
│                                                                     │
│         ┌──────────────────────────────────────────────────┐      │
│         │ authenticate_user(data_group="MACROECONOMICS") │      │
│         │     ├─ Check existing token                     │      │
│         │     └─ perform_macroeconomics_login(user, pwd) │      │
│         └──────────────────────────────────────────────────┘      │
│                         ↓                                          │
│         ┌──────────────────────────────────────────────────┐      │
│         │perform_macroeconomics_login(user, pwd)          │      │
│         │                                                   │      │
│         │ Get config from env:                            │      │
│         │ - MACRO_USERNAME, MACRO_PASSWORD               │      │
│         │ - MACRO_USE_DOMAIN_LOGIN                        │      │
│         │                                                   │      │
│         │ IF MACRO_USE_DOMAIN_LOGIN == false:             │      │
│         │   ├─ Static credential validation               │      │
│         │   └─ Compare: user == MACRO_USERNAME            │      │
│         │             password == MACRO_PASSWORD          │      │
│         │                                                   │      │
│         │ ELSE:                                            │      │
│         │   ├─ Domain login validation                     │      │
│         │   └─ perform_domain_login(user, pwd)            │      │
│         │      └─ POST to LOGIN_URL                       │      │
│         └──────────────────────────────────────────────────┘      │
│                                                                     │
│         ┌──────────────────────────────────────────────────┐      │
│         │ Token Management (All methods)                  │      │
│         │ ├─ generate_token(username)                    │      │
│         │ │  └─ JWT encode with 30-min expiration        │      │
│         │ └─ verify_token(token)                          │      │
│         │    └─ JWT decode & validate signature           │      │
│         └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CREDENTIAL SOURCES                              │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  BSIS Database   │  │ Env Variables│  │ Domain Auth Server │   │
│  │                  │  │              │  │                    │   │
│  │ bsis_dev         │  │ MACRO_*      │  │ LOGIN_URL          │   │
│  │ dt_match_user... │  │ SECRET_KEY   │  │ CERT_PATH          │   │
│  └──────────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. BSIS User Authentication Flow

```
User initiates read_data(data_group="MSP", ...)
         ↓
validate_environment("MSP")
         ↓
authenticate_user("MSP") → Default to "BSIS"
         ↓
Check USER_TOKEN env variable
         ├─ Valid Token Found
         │   └─→ Return existing token ✓
         │
         └─ No Token / Invalid Token
             ↓
             Prompt: "Username: "
             Prompt: "Password: "
             ↓
             perform_bsis_login(username, password)
             ↓
             DatabaseConnection("BSIS")
             ↓
             Call: bsis_dev.dt_match_user_password
             ↓
             Return: 1 (success) or 0 (failure)
             ↓
             ├─ Result == 1
             │   └─→ generate_token(username)
             │       └─→ Set USER_TOKEN env variable
             │       └─→ Return token ✓
             │
             └─ Result == 0
                 └─→ Log error
                 └─→ Return None ✗
```

### 2. MACROECONOMICS User Authentication Flow (Static)

```
User initiates read_data(data_group="MACROECONOMICS", ...)
         ↓
validate_environment("MACROECONOMICS")
         ↓
authenticate_user("MACROECONOMICS")
         ↓
Check USER_TOKEN env variable
         ├─ Valid Token Found
         │   └─→ Return existing token ✓
         │
         └─ No Token / Invalid Token
             ↓
             Prompt: "Username: "
             Prompt: "Password: "
             ↓
             perform_macroeconomics_login(username, password)
             ↓
             Get env: MACRO_USE_DOMAIN_LOGIN
             ↓
             ├─ MACRO_USE_DOMAIN_LOGIN == "false"
             │   ↓
             │   Get env: MACRO_USERNAME, MACRO_PASSWORD
             │   ↓
             │   ├─ Both set?
             │   │   ├─ username.upper() == MACRO_USERNAME.upper()
             │   │   │   AND password == MACRO_PASSWORD
             │   │   │   └─→ generate_token(username)
             │   │   │       └─→ Return token ✓
             │   │   │
             │   │   └─ Credentials don't match
             │   │       └─→ Log warning
             │   │       └─→ Return None ✗
             │   │
             │   └─ Not configured
             │       └─→ Log warning
             │       └─→ Return None ✗
             │
             └─ MACRO_USE_DOMAIN_LOGIN == "true"
                 ↓
                 perform_domain_login(username, password)
                 ↓
                 POST to LOGIN_URL
                 ↓
                 ├─ Status 200
                 │   └─→ generate_token(username)
                 │       └─→ Return token ✓
                 │
                 └─ Other Status
                     └─→ Log error
                     └─→ Return None ✗
```

### 3. MACROECONOMICS User Authentication Flow (Active Directory)

```
User initiates read_data(data_group="MACROECONOMICS", ...)
         ↓
[Same as Static flow until MACRO_USE_DOMAIN_LOGIN check]
         ↓
MACRO_USE_DOMAIN_LOGIN == "true"
         ↓
perform_domain_login(username, password)
         ↓
requests.Session()
         ↓
POST to LOGIN_URL
├─ Payload: {username, password, submit: "Login"}
├─ Verify: CERT_PATH
│
├─ Response Status 200
│   ├─→ Log: "Domain validation completed successfully"
│   └─→ Return True
│
├─ Response Status != 200
│   ├─→ Log error with status code
│   └─→ Return False
│
└─ RequestException
    ├─→ Log error
    └─→ Return False
         ↓
perform_macroeconomics_login() checks return value
         ├─ True
         │   └─→ generate_token(username)
         │       └─→ Return token ✓
         │
         └─ False
             └─→ Return None ✗
```

---

## Component Specifications

### 1. authenticate_user(data_group="BSIS")

**Location:** `src/langodata/utils/auth_token.py`

**Purpose:** Main authentication entry point

**Parameters:**
```python
data_group : str = "BSIS"
    # "BSIS" → BSIS database authentication
    # "MACROECONOMICS" → MACROECONOMICS-specific authentication
```

**Returns:**
```python
str or None
    # JWT token if successful
    # None if authentication fails
```

**Process:**
1. Check for existing valid token in `USER_TOKEN` environment variable
2. If valid, return existing token (avoid re-authentication)
3. If invalid/missing, prompt for credentials
4. Route to appropriate login function based on `data_group`
5. Generate JWT token on successful authentication
6. Store token in `USER_TOKEN` environment variable
7. Return token

**Error Handling:**
- Logs all errors via Logger
- Returns None on any failure
- Never raises exceptions (graceful degradation)

---

### 2. perform_bsis_login(username, password)

**Location:** `src/langodata/utils/auth_token.py`

**Purpose:** BSIS-specific authentication

**Parameters:**
```python
username : str   # User's BSIS username
password : str   # User's BSIS password
```

**Returns:**
```python
bool
    # True if credentials match in database
    # False if credentials don't match or error occurs
```

**Process:**
1. Create DatabaseConnection with "BSIS" data source
2. Create cursor and output variable for PL/SQL result
3. Call stored procedure: `bsis_dev.dt_match_user_password`
4. Check if returned value == 1 (success)
5. Return True/False accordingly

**Database Interaction:**
```sql
CALL bsis_dev.dt_match_user_password(username, password, match_result)
-- Returns: 1 if credentials valid, 0 if invalid
```

---

### 3. perform_macroeconomics_login(username, password)

**Location:** `src/langodata/utils/auth_token.py`

**Purpose:** MACROECONOMICS-specific authentication

**Parameters:**
```python
username : str   # User's username
password : str   # User's password
```

**Returns:**
```python
bool
    # True if authentication succeeds
    # False if authentication fails or configuration error
```

**Configuration (Environment Variables):**
```python
MACRO_USERNAME : str        # For static auth
MACRO_PASSWORD : str        # For static auth
MACRO_USE_DOMAIN_LOGIN : str # "true" or "false"
```

**Process:**
1. Get configuration from environment variables
2. If `MACRO_USE_DOMAIN_LOGIN == false`:
   - Validate static credentials
   - Compare `username.upper() == MACRO_USERNAME.upper()`
   - Compare `password == MACRO_PASSWORD`
   - Return True if both match, False otherwise
3. If `MACRO_USE_DOMAIN_LOGIN == true`:
   - Call `perform_domain_login(username, password)`
   - Return result from domain login
4. Handle all exceptions and log appropriately

**Supported Methods:**
- **Static Credentials:** In-memory comparison against env variables
- **Active Directory:** HTTP POST to configured domain login endpoint

---

### 4. perform_domain_login(username, password)

**Location:** `src/langodata/utils/auth_token.py`

**Purpose:** Active Directory authentication

**Parameters:**
```python
username : str   # Domain username
password : str   # Domain password
```

**Returns:**
```python
bool
    # True if domain login successful (HTTP 200)
    # False if login fails or network error
```

**Configuration (Environment Variables):**
```python
LOGIN_URL : str   # Domain login endpoint (e.g., https://help.bot.go.tz:9090)
CERT_PATH : str   # Path to SSL certificate
```

**Process:**
1. Create requests.Session()
2. Prepare payload: `{username, password, submit: "Login"}`
3. POST to `LOGIN_URL` with SSL verification using `CERT_PATH`
4. Check response status code
5. Return True if 200, False otherwise
6. Catch and log RequestExceptions

---

### 5. Token Management Functions

#### generate_token(username)

**Location:** `src/langodata/utils/auth_token.py`

**Purpose:** Create JWT token with expiration

**Parameters:**
```python
username : str   # Username to embed in token
```

**Returns:**
```python
str or None
    # Encoded JWT token
    # None if error occurs
```

**Token Payload:**
```python
{
    "username": username,
    "exp": datetime.now(GMT+3) + timedelta(minutes=30)
}
```

**Signature Algorithm:** HS256

**Expiration:** 30 minutes from creation (GMT+3 timezone)

#### verify_token(token)

**Location:** `src/langodata/utils/auth_token.py`

**Purpose:** Validate and decode JWT token

**Parameters:**
```python
token : str   # JWT token to verify
```

**Returns:**
```python
dict or None
    # Decoded token payload if valid
    # None if invalid or expired
```

**Validation Checks:**
- Valid JWT signature (matches SECRET_KEY)
- Token not expired
- No JWT errors

---

## Environment Variables Reference

### BSIS Authentication
No special environment variables needed beyond default configuration.

### MACROECONOMICS Authentication (Static)
```python
MACRO_USERNAME : str           # Static username
MACRO_PASSWORD : str           # Static password
MACRO_USE_DOMAIN_LOGIN : str   # Must be "false"
```

### MACROECONOMICS Authentication (Active Directory)
```python
MACRO_USE_DOMAIN_LOGIN : str   # Must be "true"
LOGIN_URL : str                # Domain login endpoint
CERT_PATH : str                # Path to SSL certificate
SECRET_KEY : str               # JWT signing secret
```

### All Methods
```python
SECRET_KEY : str               # JWT signing secret
USER_TOKEN : str               # Current token (auto-managed)
```

---

## Security Features

### 1. Token-Based Authentication
- **Mechanism:** JWT tokens with 30-minute expiration
- **Benefit:** Prevents repeated authentication prompts
- **Implementation:** Stored in `USER_TOKEN` environment variable

### 2. Credential Validation
- **BSIS:** Database procedure validates credentials
- **Static MACROECONOMICS:** In-memory comparison
- **AD MACROECONOMICS:** Domain server validation

### 3. SSL/TLS for Remote Auth
- **Certificate Verification:** Enabled for domain login
- **Endpoint:** Validated via configured certificate path
- **Prevention:** Man-in-the-middle attacks

### 4. Password Protection
- **No Logging:** Passwords never logged to files
- **No Storage:** Only validated, never stored
- **Cleanup:** Removed from memory after validation

### 5. Error Messages
- **Generic Messages:** Don't reveal specific validation failures
- **Detailed Logging:** Errors logged internally for debugging
- **No Credential Echo:** Credentials never appear in error messages

---

## Extensibility

### Adding New Data Groups

To add support for a new data group (e.g., "ITRS"):

1. **Create login function:**
```python
def perform_itrs_login(username, password):
    """Authenticate ITRS user"""
    # Implementation
    pass
```

2. **Update authenticate_user():**
```python
def authenticate_user(data_group="BSIS"):
    # ... existing code ...
    elif data_group.upper() == "ITRS":
        if not perform_itrs_login(username, password):
            logger.error(f"ITRS login failed")
            return None
```

3. **Update data_reader.py if needed:**
```python
# If ITRS needs special validation
def validate_environment(data_group="BSIS"):
    # ... existing code ...
    if not authenticate_user(data_group):
        return f"User authentication failed for {data_group}."
```

---

## Testing Strategy

### Unit Tests

1. **Token Generation and Validation**
```python
token = generate_token("testuser")
decoded = verify_token(token)
assert decoded["username"] == "testuser"
```

2. **BSIS Login Mock**
```python
with mock.patch("DatabaseConnection"):
    result = perform_bsis_login("user", "pass")
    assert isinstance(result, bool)
```

3. **MACROECONOMICS Static Login**
```python
os.environ["MACRO_USERNAME"] = "testuser"
os.environ["MACRO_PASSWORD"] = "testpass"
os.environ["MACRO_USE_DOMAIN_LOGIN"] = "false"
result = perform_macroeconomics_login("testuser", "testpass")
assert result == True
```

4. **MACROECONOMICS AD Login Mock**
```python
with mock.patch("requests.Session"):
    os.environ["MACRO_USE_DOMAIN_LOGIN"] = "true"
    result = perform_macroeconomics_login("user", "pass")
    assert isinstance(result, bool)
```

### Integration Tests

1. **Full Authentication Flow**
2. **Token Caching and Reuse**
3. **Token Expiration Handling**
4. **Multiple Data Groups in Sequence**

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Token Generation | < 10ms | JWT encoding |
| Token Verification | < 5ms | JWT decoding |
| BSIS Login | 100-500ms | Database call |
| AD Login | 500-2000ms | Network call |
| Static Login | < 5ms | In-memory comparison |

**Optimization:** Token caching via `USER_TOKEN` env variable prevents re-authentication for 30 minutes.

---

## Backward Compatibility Matrix

| Scenario | Code Change | Behavior |
|----------|:-----------:|----------|
| BSIS user, existing code | ✗ None | Works unchanged |
| BSIS user, data_group="BSIS" | ✗ None | Works unchanged |
| MACROECONOMICS user, new | ✓ Required | Routes to new auth |
| Mixed data groups in app | ✓ Required | Auto-routes correctly |

---

## Deployment Checklist

- [ ] All environment variables configured
- [ ] Certificate paths verified for AD auth
- [ ] Static credentials secure (not in code)
- [ ] Test BSIS authentication still works
- [ ] Test MACROECONOMICS authentication works
- [ ] Monitor logs for auth errors
- [ ] Document configuration for team
- [ ] Plan credential rotation schedule
