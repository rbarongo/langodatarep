# Authentication Configuration Guide

## Overview
The updated authentication system now supports both BSIS and MACROECONOMICS users with flexible credential management.

## Supported Data Groups
- **BSIS**: Uses BSIS database validation via `perform_bsis_login()`
- **MACROECONOMICS**: Uses either static credentials or Active Directory validation via `perform_macroeconomics_login()`

## Configuration

### 1. BSIS Users (Default)
BSIS users continue to use the existing database procedure `bsis_dev.dt_match_user_password` for authentication.

**Usage:**
```python
from langodata.utils.auth_token import authenticate_user

# Authenticate BSIS user (default)
token = authenticate_user()  # or authenticate_user("BSIS")
```

### 2. MACROECONOMICS Users with Static Credentials

For MACROECONOMICS users using static username and password, configure these environment variables:

```bash
# Set these environment variables in your system or .env file
MACRO_USERNAME=your_username
MACRO_PASSWORD=your_password
MACRO_USE_DOMAIN_LOGIN=false
```

**Usage:**
```python
from langodata.utils.auth_token import authenticate_user

# Authenticate MACROECONOMICS user with static credentials
token = authenticate_user("MACROECONOMICS")
```

When prompted, enter the username and password. The system will validate against the configured `MACRO_USERNAME` and `MACRO_PASSWORD`.

### 3. MACROECONOMICS Users with Active Directory

For MACROECONOMICS users using domain Active Directory credentials:

```bash
# Set these environment variables in your system or .env file
MACRO_USE_DOMAIN_LOGIN=true
LOGIN_URL=https://your.domain.login.url  # Already configured, update if needed
CERT_PATH=./certificate/_.bot.go.tz.crt  # Already configured, update if needed
SECRET_KEY=your_secret_key  # Already configured, update if needed
```

**Usage:**
```python
from langodata.utils.auth_token import authenticate_user

# Authenticate MACROECONOMICS user with AD credentials
token = authenticate_user("MACROECONOMICS")
```

When prompted, enter your domain username and password. The system will validate credentials against the configured domain login URL.

## Environment Variables Summary

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `MACRO_USERNAME` | For static auth | `john_doe` | Username for MACROECONOMICS static authentication |
| `MACRO_PASSWORD` | For static auth | `secure_password` | Password for MACROECONOMICS static authentication |
| `MACRO_USE_DOMAIN_LOGIN` | Yes | `false` or `true` | Set to `true` for AD auth, `false` for static |
| `LOGIN_URL` | For AD auth | `https://help.bot.go.tz:9090` | Domain login endpoint URL |
| `CERT_PATH` | For AD auth | `./certificate/_.bot.go.tz.crt` | SSL certificate path for domain auth |
| `SECRET_KEY` | Yes | (configured) | JWT token signing secret |
| `USER_TOKEN` | Auto-managed | (auto-set) | Currently active user token (set automatically) |

## Integration with Data Reader

The `read_data()` function automatically passes the `data_group` parameter to authentication:

```python
from langodata.utils.data_reader import read_data

# For MACROECONOMICS data from DWH
data = read_data(
    data_group="MACROECONOMICS",
    data_source="DWH",
    data_type="some_type",
    bank_code="some_code",
    start_period="01-Jan-2024",
    end_period="31-Dec-2024"
)

# For BSIS data
data = read_data(
    data_group="BSIS",
    data_source="BSIS",
    data_type="some_type",
    bank_code="some_code",
    start_period="01-Jan-2024",
    end_period="31-Dec-2024"
)
```

## Setting Environment Variables

### Option 1: Windows Command Prompt
```bash
setx MACRO_USERNAME your_username
setx MACRO_PASSWORD your_password
setx MACRO_USE_DOMAIN_LOGIN false
```

### Option 2: Windows PowerShell
```powershell
[Environment]::SetEnvironmentVariable("MACRO_USERNAME", "your_username", "User")
[Environment]::SetEnvironmentVariable("MACRO_PASSWORD", "your_password", "User")
[Environment]::SetEnvironmentVariable("MACRO_USE_DOMAIN_LOGIN", "false", "User")
```

### Option 3: Create .env file
Create a `.env` file in your project root:
```
MACRO_USERNAME=your_username
MACRO_PASSWORD=your_password
MACRO_USE_DOMAIN_LOGIN=false
```

Then load it in your Python code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
```

## Function Reference

### authenticate_user(data_group="BSIS")
Authenticate a user based on their data group.

**Parameters:**
- `data_group` (str, optional): Data group identifier. Options: "BSIS", "MACROECONOMICS". Default: "BSIS"

**Returns:**
- `str`: JWT token if successful
- `None`: If authentication fails

**Raises:**
- Various exceptions logged to the logger

### perform_macroeconomics_login(username, password)
Authenticate a MACROECONOMICS user with static or AD credentials.

**Parameters:**
- `username` (str): Username
- `password` (str): Password

**Returns:**
- `True`: If authentication is successful
- `False`: If authentication fails

**Behavior:**
- If `MACRO_USE_DOMAIN_LOGIN=false`: Validates against static `MACRO_USERNAME` and `MACRO_PASSWORD`
- If `MACRO_USE_DOMAIN_LOGIN=true`: Validates against configured domain login URL

## Error Handling

The system logs authentication errors to the configured logger:
- BSIS login failures
- MACROECONOMICS static credential mismatches
- AD validation failures
- Configuration errors

Check logs for detailed error messages to troubleshoot authentication issues.

## Security Notes

1. **Never hardcode credentials** in your code. Always use environment variables or configuration files.
2. **Protect your .env file** - add it to `.gitignore` if using version control.
3. **Use secure certificate paths** for AD authentication.
4. **Rotate credentials regularly** and update environment variables accordingly.
5. **SSL/TLS verification** is enabled by default for AD authentication.

## Backward Compatibility

Existing BSIS user code continues to work without modifications:
```python
# This still works exactly the same
token = authenticate_user()
```

## Troubleshooting

### Issue: "MACROECONOMICS static credentials not configured"
**Solution:** Ensure `MACRO_USERNAME` and `MACRO_PASSWORD` environment variables are set.

### Issue: "MACROECONOMICS AD credential validation failed"
**Solution:** 
- Check `LOGIN_URL` is correct
- Verify certificate path in `CERT_PATH`
- Ensure domain credentials are correct

### Issue: "Login not successful" for BSIS
**Solution:** Verify BSIS database connection and user exists in `bsis_dev.dt_match_user_password` procedure.

### Issue: Token has expired
**Solution:** Login again. Tokens expire after 30 minutes (GMT+3).
