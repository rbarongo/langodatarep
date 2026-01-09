# Quick Reference Card

**Keep this handy for quick lookup of authentication setup and usage.**

---

## 🚀 For Quick Setup (Choose One)

### Option 1: BSIS Users
```
✓ Already works - no changes needed!
Just use: authenticate_user()
```

### Option 2: Non-BSIS Groups with Static Credentials

Supported groups: MACROECONOMICS, IT-MONITORING, IT-SECURITY, CURRENCY, FINANCIAL-MARKETS, PHYSICAL-SECURITY, TOURISM

```powershell
# Example for IT-SECURITY:
setx IT_SECURITY_USERNAME your_username
setx IT_SECURITY_PASSWORD your_password
setx IT_SECURITY_USE_DOMAIN_LOGIN false

# Example for CURRENCY:
setx CURRENCY_USERNAME your_username
setx CURRENCY_PASSWORD your_password
setx CURRENCY_USE_DOMAIN_LOGIN false
```

Pattern for env vars: `{DATA_GROUP}_USERNAME`, `{DATA_GROUP}_PASSWORD`, `{DATA_GROUP}_USE_DOMAIN_LOGIN`

Then use: `authenticate_user("IT-SECURITY")` or `authenticate_user("CURRENCY")`

### Option 3: Non-BSIS Groups with Active Directory
```powershell
setx MACRO_USE_DOMAIN_LOGIN true
# LOGIN_URL and CERT_PATH already set
```
Then use: `authenticate_user("MACROECONOMICS")`

---

## 📋 Code Usage Patterns

### Pattern 1: Direct Authentication
```python
from langodata.utils.auth_token import authenticate_user

# BSIS (default)
token = authenticate_user()

# Non-BSIS Groups (any of these):
token = authenticate_user("MACROECONOMICS")
token = authenticate_user("IT-MONITORING")
token = authenticate_user("IT-SECURITY")
token = authenticate_user("CURRENCY")
token = authenticate_user("FINANCIAL-MARKETS")
token = authenticate_user("PHYSICAL-SECURITY")
token = authenticate_user("TOURISM")
```

### Pattern 2: Data Reading (Auto-Authentication)
```python
from langodata.utils.data_reader import read_data

# Authentication happens automatically based on data_group
result = read_data(
    data_group="IT-SECURITY",  # Triggers IT-SECURITY auth
    data_source="DWH",
    data_type="security_events",
    bank_code="daily",
    start_period="01-Jan-2024",
    end_period="31-Dec-2024"
)

# Works with any data group
result = read_data("CURRENCY", "DWH", ...)
result = read_data("FINANCIAL-MARKETS", "DWH", ...)
result = read_data("MACROECONOMICS", "DWH", ...)
```

---

## 🔐 Environment Variables Checklist

For **Non-BSIS Groups** (MACROECONOMICS, IT-MONITORING, IT-SECURITY, CURRENCY, FINANCIAL-MARKETS, PHYSICAL-SECURITY, TOURISM):

| Variable Pattern | Static | AD |
|------------------|:------:|:--:|
| {GROUP}_USERNAME | ✓ | ✗ |
| {GROUP}_PASSWORD | ✓ | ✗ |
| {GROUP}_USE_DOMAIN_LOGIN | `false` | `true` |
| LOGIN_URL | ✗ | ✓* |
| CERT_PATH | ✗ | ✓* |
| SECRET_KEY | ✓* | ✓* |
| USER_TOKEN | (auto) | (auto) |

*Already configured in most environments

### Examples:
```bash
# IT-SECURITY with Static:
IT_SECURITY_USERNAME=user1
IT_SECURITY_PASSWORD=pass1
IT_SECURITY_USE_DOMAIN_LOGIN=false

# CURRENCY with AD:
CURRENCY_USE_DOMAIN_LOGIN=true

# FINANCIAL-MARKETS with Static:
FINANCIAL_MARKETS_USERNAME=user2
FINANCIAL_MARKETS_PASSWORD=pass2
FINANCIAL_MARKETS_USE_DOMAIN_LOGIN=false
```

---

## 🔍 Testing Your Setup

```python
import os
from langodata.utils.auth_token import authenticate_user, verify_token

# Check configuration
macro_config = os.getenv("MACRO_USE_DOMAIN_LOGIN", "false").lower() == "true"
print(f"Using AD: {macro_config}")

# Test authentication
token = authenticate_user("MACROECONOMICS")

# Verify token works
if token:
    decoded = verify_token(token)
    print(f"Success! Username: {decoded.get('username')}")
else:
    print("Authentication failed - check logs")
```

---

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "credentials not configured" | Set `{GROUP}_USERNAME` and `{GROUP}_PASSWORD` |
| "credential validation failed" | Check username/password env vars match |
| "AD credential validation failed" | Verify AD credentials are correct |
| "Token has expired" | Login again (tokens expire after 30 min) |
| Env vars not working | Restart terminal/IDE after setting |
| Wrong data group | Check spelling: MACROECONOMICS, IT-MONITORING, IT-SECURITY, CURRENCY, FINANCIAL-MARKETS, PHYSICAL-SECURITY, TOURISM |
| "Invalid data group" error | Data group must be in supported list |
| Multiple groups configured | Each group uses separate env vars - no conflicts |
| Unsupported data group | Use authenticate_user() without parameter or use BSIS |

---

## 📚 Documentation Map

```
IMPLEMENTATION_SUMMARY.md ← Start here for overview
├── AUTHENTICATION_UPDATE_SUMMARY.md (what changed + examples)
├── AUTHENTICATION_SETUP.md (complete configuration guide)
├── SETUP_CHECKLIST.md (step-by-step setup)
├── AUTHENTICATION_ARCHITECTURE.md (technical deep-dive)
└── authentication_examples.py (working code examples)
```

---

## 🎯 Daily Usage

```python
# Just use this in your code:

from langodata.utils.data_reader import read_data

# Everything else is automatic!
data = read_data(
    data_group="MACROECONOMICS",  # Auth happens automatically
    data_source="DWH",
    data_type="GDP",
    bank_code="monthly",
    start_period="01-Jan-2024",
    end_period="31-Dec-2024"
)
```

---

## 🔗 Key Functions

| Function | Purpose | Parameters |
|----------|---------|-----------|
| `authenticate_user(data_group="BSIS")` | Get/create auth token | data_group: str |
| `read_data(...)` | Read data (auto-auth) | data_group, data_source, ... |
| `perform_macroeconomics_login()` | MACRO-specific auth | username, password |
| `perform_bsis_login()` | BSIS-specific auth | username, password |

---

## 💾 Configuration Methods

### Method 1: Windows Command Prompt
```batch
setx MACRO_USERNAME myusername
setx MACRO_PASSWORD mypassword
setx MACRO_USE_DOMAIN_LOGIN false
```

### Method 2: PowerShell (Admin)
```powershell
[Environment]::SetEnvironmentVariable("MACRO_USERNAME", "myusername", "User")
[Environment]::SetEnvironmentVariable("MACRO_PASSWORD", "mypassword", "User")
[Environment]::SetEnvironmentVariable("MACRO_USE_DOMAIN_LOGIN", "false", "User")
```

### Method 3: .env File
Create `.env` in project root:
```
MACRO_USERNAME=myusername
MACRO_PASSWORD=mypassword
MACRO_USE_DOMAIN_LOGIN=false
```

---

## ✅ Pre-Deployment Checklist

- [ ] Environment variables configured for your method
- [ ] Test BSIS authentication still works
- [ ] Test MACROECONOMICS authentication works
- [ ] Can read data from appropriate source
- [ ] Logs show no authentication errors
- [ ] Credentials are not in version control

---

## 🆘 Need Help?

1. **Check this card** for common issues
2. **Read** AUTHENTICATION_SETUP.md for detailed help
3. **Run** authentication_examples.py to test
4. **Check logs** for error messages
5. **Verify** environment variables are set:
   ```powershell
   echo %MACRO_USERNAME%
   echo %MACRO_PASSWORD%
   echo %MACRO_USE_DOMAIN_LOGIN%
   ```

---

## 📞 Quick Facts

| Fact | Value |
|------|-------|
| Token Expiration | 30 minutes |
| Auth Method for BSIS | Database procedure |
| Auth Methods for MACRO | Static or AD |
| Backward Compatible | 100% - yes! |
| Breaking Changes | None! |

---

**Last Updated:** January 8, 2026  
**Version:** 1.0  
**Status:** ✓ Ready to Use
