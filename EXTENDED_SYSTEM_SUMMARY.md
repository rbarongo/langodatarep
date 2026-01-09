# Authentication System - Extended to 7 Non-BSIS Data Groups

**Update Date:** January 8, 2026  
**Version:** 2.0  
**Status:** ✅ Complete & Ready

---

## 🎉 What's New

The authentication system now supports **7 non-BSIS data groups** (in addition to BSIS):

### Non-BSIS Groups (All with Static + AD Support)
1. ✅ **MACROECONOMICS** (original)
2. ✅ **IT-MONITORING** (new)
3. ✅ **IT-SECURITY** (new)
4. ✅ **CURRENCY** (new)
5. ✅ **FINANCIAL-MARKETS** (new)
6. ✅ **PHYSICAL-SECURITY** (new)
7. ✅ **TOURISM** (new)

### Authentication Methods (for all non-BSIS groups)
- Static credentials (username/password from env vars)
- Active Directory (domain login via HTTP)

---

## 📊 Total System Support

```
BSIS Users (1)
├─ Database authentication (unchanged)
└─ Zero configuration needed

Non-BSIS Groups (7)
├─ MACROECONOMICS
├─ IT-MONITORING
├─ IT-SECURITY
├─ CURRENCY
├─ FINANCIAL-MARKETS
├─ PHYSICAL-SECURITY
└─ TOURISM

Each supports: Static Credentials OR Active Directory
```

---

## 💡 How It Works - Generic Approach

Instead of creating separate functions for each group, the system uses a **single generic function** that works for all non-BSIS groups.

### Environment Variable Pattern

```
{DATA_GROUP}_USERNAME
{DATA_GROUP}_PASSWORD
{DATA_GROUP}_USE_DOMAIN_LOGIN
```

### Examples

**IT-SECURITY with Static:**
```bash
IT_SECURITY_USERNAME=security_user
IT_SECURITY_PASSWORD=secure_pass
IT_SECURITY_USE_DOMAIN_LOGIN=false
```

**CURRENCY with AD:**
```bash
CURRENCY_USE_DOMAIN_LOGIN=true
# (LOGIN_URL and CERT_PATH already set)
```

**FINANCIAL-MARKETS with Static:**
```bash
FINANCIAL_MARKETS_USERNAME=fm_user
FINANCIAL_MARKETS_PASSWORD=fm_pass
FINANCIAL_MARKETS_USE_DOMAIN_LOGIN=false
```

---

## 🚀 Quick Start - 3 Steps

### Step 1: Choose Your Data Group & Method
```
Pick: IT-MONITORING, IT-SECURITY, CURRENCY, FINANCIAL-MARKETS, PHYSICAL-SECURITY, or TOURISM
Method: Static Credentials OR Active Directory
```

### Step 2: Set Environment Variables
```bash
# For Static (example: IT-SECURITY)
setx IT_SECURITY_USERNAME your_username
setx IT_SECURITY_PASSWORD your_password
setx IT_SECURITY_USE_DOMAIN_LOGIN false

# For AD (example: CURRENCY)
setx CURRENCY_USE_DOMAIN_LOGIN true
```

### Step 3: Use in Code
```python
from langodata.utils.auth_token import authenticate_user

# Automatic routing based on data_group
token = authenticate_user("IT-SECURITY")
token = authenticate_user("CURRENCY")
token = authenticate_user("FINANCIAL-MARKETS")
```

---

## 📝 All Data Groups Configuration Reference

### MACROECONOMICS
```bash
# Static
MACROECONOMICS_USERNAME=user
MACROECONOMICS_PASSWORD=pass
MACROECONOMICS_USE_DOMAIN_LOGIN=false

# AD
MACROECONOMICS_USE_DOMAIN_LOGIN=true
```

### IT-MONITORING
```bash
# Static
IT_MONITORING_USERNAME=user
IT_MONITORING_PASSWORD=pass
IT_MONITORING_USE_DOMAIN_LOGIN=false

# AD
IT_MONITORING_USE_DOMAIN_LOGIN=true
```

### IT-SECURITY
```bash
# Static
IT_SECURITY_USERNAME=user
IT_SECURITY_PASSWORD=pass
IT_SECURITY_USE_DOMAIN_LOGIN=false

# AD
IT_SECURITY_USE_DOMAIN_LOGIN=true
```

### CURRENCY
```bash
# Static
CURRENCY_USERNAME=user
CURRENCY_PASSWORD=pass
CURRENCY_USE_DOMAIN_LOGIN=false

# AD
CURRENCY_USE_DOMAIN_LOGIN=true
```

### FINANCIAL-MARKETS
```bash
# Static
FINANCIAL_MARKETS_USERNAME=user
FINANCIAL_MARKETS_PASSWORD=pass
FINANCIAL_MARKETS_USE_DOMAIN_LOGIN=false

# AD
FINANCIAL_MARKETS_USE_DOMAIN_LOGIN=true
```

### PHYSICAL-SECURITY
```bash
# Static
PHYSICAL_SECURITY_USERNAME=user
PHYSICAL_SECURITY_PASSWORD=pass
PHYSICAL_SECURITY_USE_DOMAIN_LOGIN=false

# AD
PHYSICAL_SECURITY_USE_DOMAIN_LOGIN=true
```

### TOURISM
```bash
# Static
TOURISM_USERNAME=user
TOURISM_PASSWORD=pass
TOURISM_USE_DOMAIN_LOGIN=false

# AD
TOURISM_USE_DOMAIN_LOGIN=true
```

---

## 💻 Code Examples

### Authenticate Different Groups
```python
from langodata.utils.auth_token import authenticate_user

# Each group authenticates independently
token1 = authenticate_user("IT-MONITORING")
token2 = authenticate_user("CURRENCY")
token3 = authenticate_user("PHYSICAL-SECURITY")
```

### Read Data from Different Groups
```python
from langodata.utils.data_reader import read_data

# Authentication happens automatically based on data_group
result = read_data("IT-SECURITY", "DWH", "events", "daily", "01-Jan-2024", "31-Dec-2024")
result = read_data("FINANCIAL-MARKETS", "DWH", "prices", "hourly", "01-Jan-2024", "31-Dec-2024")
result = read_data("TOURISM", "DWH", "visitors", "monthly", "01-Jan-2024", "31-Dec-2024")
```

### Token Reuse (30 minutes)
```python
# First call - authenticates
token = authenticate_user("IT-MONITORING")

# Later call - reuses cached token (no re-authentication)
token = authenticate_user("IT-MONITORING")  # Returns cached token
```

---

## ✨ Key Features

✅ **Generic Implementation** - One function handles all groups  
✅ **Easy Configuration** - Simple environment variables  
✅ **Flexible Methods** - Choose static or AD per group  
✅ **No Code Duplication** - Reusable code pattern  
✅ **Backward Compatible** - Existing code unchanged  
✅ **Automatic Routing** - Data group determines auth method  
✅ **Token Caching** - Avoid re-authentication for 30 minutes  
✅ **Secure** - Passwords never logged, SSL/TLS support  

---

## 📚 Documentation

See **[EXTENDED_DATA_GROUPS.md](EXTENDED_DATA_GROUPS.md)** for complete details including:
- Detailed configuration for each group
- Security considerations
- Testing recommendations
- Troubleshooting guide
- FAQ section

Also reference:
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Updated with new groups
- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Detailed setup guide
- [authentication_examples.py](authentication_examples.py) - Code examples for each group

---

## 🔧 Code Changes Summary

### Files Modified: 2

#### auth_token.py
- Added `perform_non_bsis_login(data_group, username, password)` - Generic handler
- Refactored `perform_macroeconomics_login()` to use generic function
- Updated `authenticate_user()` to support all 7 non-BSIS groups

#### data_reader.py
- Added 6 new data groups to validation list

### Files Updated: 2

#### authentication_examples.py
- Added examples for each data group
- Updated configuration reference

#### QUICK_REFERENCE.md
- Updated with all new data groups
- Updated code patterns
- Updated environment variable reference

---

## ✅ Testing

Test each data group:

```python
from langodata.utils.auth_token import authenticate_user

groups = [
    "MACROECONOMICS", "IT-MONITORING", "IT-SECURITY",
    "CURRENCY", "FINANCIAL-MARKETS", "PHYSICAL-SECURITY", "TOURISM"
]

for group in groups:
    token = authenticate_user(group)
    print(f"{group}: {'✓' if token else '✗'}")
```

---

## 🔐 Security Notes

- All env var names are UPPERCASE
- Hyphens in group names become underscores in env vars
- Passwords never hardcoded - use env vars or .env file
- SSL/TLS enabled for AD authentication
- Tokens expire after 30 minutes
- No credential exposure in logs or error messages

---

## 📋 Supported Data Groups Summary

| Group | Env Var Pattern | Methods | Status |
|-------|-----------------|---------|--------|
| BSIS | N/A (database) | Database only | ✓ Existing |
| MACROECONOMICS | MACROECONOMICS_* | Static / AD | ✓ Original |
| IT-MONITORING | IT_MONITORING_* | Static / AD | ✓ New |
| IT-SECURITY | IT_SECURITY_* | Static / AD | ✓ New |
| CURRENCY | CURRENCY_* | Static / AD | ✓ New |
| FINANCIAL-MARKETS | FINANCIAL_MARKETS_* | Static / AD | ✓ New |
| PHYSICAL-SECURITY | PHYSICAL_SECURITY_* | Static / AD | ✓ New |
| TOURISM | TOURISM_* | Static / AD | ✓ New |

---

## 🎯 Next Steps

1. **Choose** which data groups you need
2. **Set** environment variables for each group
3. **Test** authentication with `authenticate_user("GROUP-NAME")`
4. **Deploy** updated code files
5. **Use** in your applications

---

## 💬 Common Questions

**Q: Do I need to configure all 7 groups?**  
A: No, only configure the groups you use.

**Q: Can I use different methods for different groups?**  
A: Yes! IT-MONITORING can use static while CURRENCY uses AD.

**Q: Will BSIS users be affected?**  
A: No, BSIS users work exactly as before.

**Q: Do I need to change my code?**  
A: No code changes needed, just set environment variables.

---

## 🎉 Summary

✅ **8 Total Data Groups Supported** (1 BSIS + 7 Non-BSIS)  
✅ **14 Total Auth Methods** (7 groups × 2 methods each)  
✅ **100% Backward Compatible**  
✅ **Production Ready**  
✅ **Fully Documented**  

---

**Status: ✅ COMPLETE & READY FOR PRODUCTION**

For complete details, see [EXTENDED_DATA_GROUPS.md](EXTENDED_DATA_GROUPS.md)
