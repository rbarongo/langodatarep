# Authentication System Update Summary

## What Was Changed

The authentication system has been updated to support multiple user types with flexible credential management. Previously, all users had to authenticate via BSIS, but now MACROECONOMICS users (and other non-BSIS groups) can authenticate using their own methods.

### Key Updates

#### 1. **New Function: `perform_macroeconomics_login()`**
   - Located in: [src/langodata/utils/auth_token.py](src/langodata/utils/auth_token.py)
   - Supports two authentication methods:
     - **Static Credentials**: Validates username/password against environment variables
     - **Active Directory**: Validates credentials against domain login endpoint
   - Automatically selects method based on `MACRO_USE_DOMAIN_LOGIN` environment variable

#### 2. **Enhanced `authenticate_user()` Function**
   - Added optional `data_group` parameter (default: "BSIS")
   - Routes authentication to appropriate method based on data group:
     - `data_group="BSIS"` → Uses `perform_bsis_login()`
     - `data_group="MACROECONOMICS"` → Uses `perform_macroeconomics_login()`
   - Fully backward compatible - existing code works without changes

#### 3. **Updated `validate_environment()` in data_reader.py**
   - Now accepts `data_group` parameter
   - Passes it to `authenticate_user()` for appropriate authentication
   - Maintains backward compatibility with default BSIS authentication

#### 4. **Updated `read_data()` Function**
   - Automatically passes `data_group` to `validate_environment()`
   - No changes needed in calling code - authentication happens automatically based on data group

## Files Modified

| File | Changes |
|------|---------|
| [src/langodata/utils/auth_token.py](src/langodata/utils/auth_token.py) | Added `perform_macroeconomics_login()`, enhanced `authenticate_user()` |
| [src/langodata/utils/data_reader.py](src/langodata/utils/data_reader.py) | Updated `validate_environment()` and `read_data()` to support data group routing |

## Files Created

| File | Purpose |
|------|---------|
| [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) | Complete configuration guide |
| [authentication_examples.py](authentication_examples.py) | Implementation examples and usage patterns |

## Quick Start Guide

### For BSIS Users (No Changes Needed)
```python
from langodata.utils.auth_token import authenticate_user
from langodata.utils.data_reader import read_data

# Existing code continues to work exactly as before
token = authenticate_user()

data = read_data("MSP", "BSIS", "type", "code", "01-Jan-2024", "31-Dec-2024")
```

### For MACROECONOMICS Users (Static Credentials)
```bash
# Set environment variables:
setx MACRO_USERNAME your_username
setx MACRO_PASSWORD your_password
setx MACRO_USE_DOMAIN_LOGIN false
```

```python
from langodata.utils.auth_token import authenticate_user
from langodata.utils.data_reader import read_data

# Authenticate MACROECONOMICS user
token = authenticate_user("MACROECONOMICS")

# Read MACROECONOMICS data from DWH
data = read_data("MACROECONOMICS", "DWH", "type", "monthly", "01-Jan-2024", "31-Dec-2024")
```

### For MACROECONOMICS Users (Active Directory)
```bash
# Set environment variables:
setx MACRO_USE_DOMAIN_LOGIN true
# LOGIN_URL and CERT_PATH should already be configured
```

```python
from langodata.utils.auth_token import authenticate_user

# Authenticate with AD credentials
token = authenticate_user("MACROECONOMICS")
```

## Authentication Flow Diagram

```
authenticate_user(data_group)
    │
    ├─→ Check existing token
    │   └─→ If valid, return token ✓
    │
    └─→ Prompt for credentials
        │
        ├─→ data_group == "BSIS"
        │   └─→ perform_bsis_login(username, password)
        │       └─→ Call BSIS database procedure
        │
        ├─→ data_group == "MACROECONOMICS"
        │   └─→ perform_macroeconomics_login(username, password)
        │       │
        │       ├─→ MACRO_USE_DOMAIN_LOGIN == false
        │       │   └─→ Validate against MACRO_USERNAME/MACRO_PASSWORD
        │       │
        │       └─→ MACRO_USE_DOMAIN_LOGIN == true
        │           └─→ Call perform_domain_login()
        │               └─→ POST to LOGIN_URL
        │
        └─→ Generate JWT token + return
```

## Configuration Quick Reference

| Scenario | Environment Variables |
|----------|----------------------|
| **BSIS Users** | None needed (uses existing config) |
| **MACROECONOMICS (Static)** | `MACRO_USERNAME`, `MACRO_PASSWORD`, `MACRO_USE_DOMAIN_LOGIN=false` |
| **MACROECONOMICS (AD)** | `MACRO_USE_DOMAIN_LOGIN=true`, `LOGIN_URL`, `CERT_PATH`, `SECRET_KEY` |

## Security Considerations

✓ **What's Protected:**
- Passwords are never logged
- JWT tokens expire after 30 minutes
- SSL/TLS verification enabled for AD auth
- Credentials validated per data group requirements

⚠ **Recommendations:**
- Never hardcode credentials in scripts
- Use environment variables or `.env` files
- Add `.env` to `.gitignore` if using version control
- Regularly rotate credentials and update environment variables
- Use domain credentials (AD) for production when possible

## Error Messages & Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "MACROECONOMICS static credentials not configured" | Missing env vars | Set `MACRO_USERNAME` and `MACRO_PASSWORD` |
| "MACROECONOMICS static credential validation failed" | Wrong credentials | Check username/password match env vars |
| "MACROECONOMICS AD credential validation failed" | AD auth failed | Verify AD credentials are correct |
| "BSIS login not successful" | Wrong BSIS credentials | Check user exists in BSIS database |
| "Token has expired" | Token older than 30 min | Login again to get new token |

## Backward Compatibility

✓ **All existing code continues to work unchanged:**
- `authenticate_user()` without parameters defaults to BSIS
- `read_data()` with BSIS data group works exactly as before
- No breaking changes to function signatures
- Existing BSIS database authentication path unchanged

## Next Steps

1. **Review** [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed configuration
2. **Set up** environment variables based on your user group
3. **Test** with [authentication_examples.py](authentication_examples.py)
4. **Update** your scripts to use `authenticate_user("MACROECONOMICS")` if applicable
5. **Monitor** logs for authentication errors

## Support & Questions

- Check [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed configuration
- Review [authentication_examples.py](authentication_examples.py) for code examples
- Check application logs for debugging information
- Verify environment variables are correctly set
