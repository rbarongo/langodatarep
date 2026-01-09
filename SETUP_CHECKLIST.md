# Environment Setup Checklist

Use this checklist to ensure proper configuration for your authentication method.

---

## ☐ BSIS Users Configuration

**Status:** ✓ **Already Configured** - No action needed!

BSIS users continue using the existing authentication system. No new configuration required.

### Verification
```python
from langodata.utils.auth_token import authenticate_user
token = authenticate_user()  # Or authenticate_user("BSIS")
```

---

## ☐ MACROECONOMICS Users - Static Credentials Configuration

Use this checklist if MACROECONOMICS users will authenticate with static username/password.

### Prerequisites
- [ ] Username value ready
- [ ] Password value ready
- [ ] Access to set environment variables

### Setup Steps

#### Option 1: Windows Command Prompt
```batch
setx MACRO_USERNAME your_actual_username
setx MACRO_PASSWORD your_actual_password
setx MACRO_USE_DOMAIN_LOGIN false
```
- [ ] Command 1 executed successfully
- [ ] Command 2 executed successfully
- [ ] Command 3 executed successfully

#### Option 2: Windows PowerShell (As Administrator)
```powershell
[Environment]::SetEnvironmentVariable("MACRO_USERNAME", "your_actual_username", "User")
[Environment]::SetEnvironmentVariable("MACRO_PASSWORD", "your_actual_password", "User")
[Environment]::SetEnvironmentVariable("MACRO_USE_DOMAIN_LOGIN", "false", "User")
```
- [ ] PowerShell commands executed
- [ ] No errors displayed

#### Option 3: .env File
Create file: `.env` in your project root
```
MACRO_USERNAME=your_actual_username
MACRO_PASSWORD=your_actual_password
MACRO_USE_DOMAIN_LOGIN=false
```
- [ ] `.env` file created
- [ ] Values set correctly
- [ ] `.env` added to `.gitignore`

### Verification
```python
from langodata.utils.auth_token import authenticate_user
token = authenticate_user("MACROECONOMICS")
# When prompted, enter the username and password
```
- [ ] User prompted for credentials
- [ ] Authentication successful (token returned)
- [ ] No error messages

---

## ☐ MACROECONOMICS Users - Active Directory Configuration

Use this checklist if MACROECONOMICS users will authenticate via domain AD.

### Prerequisites
- [ ] Domain controller URL available
- [ ] SSL certificate path verified
- [ ] Secret key for JWT configured
- [ ] Domain credentials will be used at runtime

### Setup Steps

#### Verify Required Variables Already Set
These should already be configured in your environment:

```powershell
# Check if these are set:
[Environment]::GetEnvironmentVariable("LOGIN_URL", "User")
[Environment]::GetEnvironmentVariable("CERT_PATH", "User")
[Environment]::GetEnvironmentVariable("SECRET_KEY", "User")
```

- [ ] `LOGIN_URL` is set and reachable
- [ ] `CERT_PATH` certificate file exists
- [ ] `SECRET_KEY` is configured

#### Set MACRO_USE_DOMAIN_LOGIN Flag

**Windows Command Prompt:**
```batch
setx MACRO_USE_DOMAIN_LOGIN true
```

**Windows PowerShell (As Administrator):**
```powershell
[Environment]::SetEnvironmentVariable("MACRO_USE_DOMAIN_LOGIN", "true", "User")
```

**.env File:**
```
MACRO_USE_DOMAIN_LOGIN=true
```

- [ ] `MACRO_USE_DOMAIN_LOGIN` set to `true`

#### Verify SSL Certificate
```powershell
# Certificate should exist at this location:
Test-Path ".\certificate\_.bot.go.tz.crt"
```
- [ ] Certificate file exists

### Verification
```python
from langodata.utils.auth_token import authenticate_user
token = authenticate_user("MACROECONOMICS")
# When prompted, enter your domain username and password
```
- [ ] User prompted for domain credentials
- [ ] Authentication successful (token returned)
- [ ] Domain validation message in logs

---

## ☐ Data Reader Configuration

Automatic authentication for data reading based on data_group.

### Usage Example
```python
from langodata.utils.data_reader import read_data

# MACROECONOMICS data (uses MACRO authentication automatically)
result = read_data(
    data_group="MACROECONOMICS",
    data_source="DWH",
    data_type="GDP",
    bank_code="monthly",
    start_period="01-Jan-2024",
    end_period="31-Dec-2024"
)

# BSIS data (uses BSIS authentication automatically)
result = read_data(
    data_group="MSP",
    data_source="BSIS",
    data_type="type",
    bank_code="code",
    start_period="01-Jan-2024",
    end_period="31-Dec-2024"
)
```

- [ ] Data reader can be called with different data groups
- [ ] Authentication happens automatically based on data_group

---

## ☐ Verification Commands

Run these commands to verify your setup:

### Check Environment Variables
```powershell
# View all authentication environment variables
Get-ChildItem Env: | Where-Object { $_.Name -like "*MACRO*" -or $_.Name -like "*SECRET*" -or $_.Name -like "*LOGIN*" }
```
- [ ] All required variables appear in output

### Test Authentication
```python
import os
from langodata.utils.auth_token import authenticate_user

# Check what method will be used
macro_config = os.getenv("MACRO_USE_DOMAIN_LOGIN", "false").lower() == "true"
print(f"Using AD: {macro_config}")

# Test authentication
token = authenticate_user("MACROECONOMICS")
print(f"Success: {token is not None}")
```
- [ ] Script runs without errors
- [ ] Token is returned (not None)

### Verify Token Validity
```python
from langodata.utils.auth_token import verify_token, authenticate_user

token = authenticate_user("MACROECONOMICS")
decoded = verify_token(token)
print(f"Token valid: {decoded is not None}")
print(f"Username: {decoded.get('username') if decoded else 'N/A'}")
```
- [ ] Token is valid (not expired)
- [ ] Username is in decoded token

---

## ☐ Troubleshooting Checklist

### Issue: "Environment variables not found"
- [ ] Restart terminal/IDE after setting environment variables
- [ ] Verify variables in `echo %MACRO_USERNAME%` (CMD) or `echo $env:MACRO_USERNAME` (PS)
- [ ] Check variable is in User or System scope (not just session)

### Issue: "Static credentials failed"
- [ ] Verify `MACRO_USERNAME` and `MACRO_PASSWORD` are correctly set
- [ ] Check username case sensitivity (auto-converted to uppercase)
- [ ] Verify no trailing spaces in environment variable values
- [ ] Ensure `MACRO_USE_DOMAIN_LOGIN=false`

### Issue: "AD authentication failed"
- [ ] Verify `MACRO_USE_DOMAIN_LOGIN=true`
- [ ] Test domain credentials manually on another system
- [ ] Verify `LOGIN_URL` is correct and reachable
- [ ] Check SSL certificate at `CERT_PATH` location
- [ ] Verify `SECRET_KEY` is set

### Issue: "Token expired"
- [ ] Tokens expire after 30 minutes (GMT+3)
- [ ] Login again to get a fresh token
- [ ] Check system time is correct

---

## ☐ Security Review

Before going to production:

- [ ] Environment variables NOT hardcoded in scripts
- [ ] `.env` file added to `.gitignore`
- [ ] Passwords stored securely (not in version control)
- [ ] SSL/TLS verification enabled for AD auth
- [ ] Credentials will be rotated periodically
- [ ] Logs contain no sensitive information (passwords masked)
- [ ] Access to `.env` file restricted to necessary users

---

## ☐ Documentation & Testing

- [ ] Team reviewed [AUTHENTICATION_UPDATE_SUMMARY.md](AUTHENTICATION_UPDATE_SUMMARY.md)
- [ ] Configuration tested in development environment
- [ ] Tested both BSIS and MACROECONOMICS authentication flows
- [ ] Error messages understood and documented
- [ ] Deployment plan reviewed with team
- [ ] Rollback plan in place if needed

---

## Next Steps

1. **Complete** the relevant checklist section above
2. **Test** authentication using the verification commands
3. **Review** error messages in logs if any issues occur
4. **Refer** to [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed help
5. **Contact** support if issues persist

---

## Quick Reference: Environment Variable Values

| Variable | BSIS | MACRO (Static) | MACRO (AD) |
|----------|:----:|:--------------:|:----------:|
| `MACRO_USERNAME` | ✗ | ✓ | ✗ |
| `MACRO_PASSWORD` | ✗ | ✓ | ✗ |
| `MACRO_USE_DOMAIN_LOGIN` | ✗ | `false` | `true` |
| `LOGIN_URL` | ✗ | ✗ | ✓ |
| `CERT_PATH` | ✗ | ✗ | ✓ |
| `SECRET_KEY` | ✓ | ✓ | ✓ |

Legend: ✓ = Required, ✗ = Not needed
