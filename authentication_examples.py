"""
Implementation Examples for Updated Authentication System

This file demonstrates how to use the updated authentication system
that supports both BSIS and MACROECONOMICS users.
"""

from langodata.utils.auth_token import authenticate_user
from langodata.utils.data_reader import read_data

# ============================================================================
# EXAMPLE 1: BSIS User Authentication (Default / Backward Compatible)
# ============================================================================
def example_bsis_authentication():
    """
    Authenticate a BSIS user using the default authentication method.
    This is backward compatible with existing code.
    """
    print("=" * 70)
    print("EXAMPLE 1: BSIS User Authentication")
    print("=" * 70)
    
    # Method 1: Using default parameter (BSIS)
    token = authenticate_user()
    
    if token:
        print(f"✓ BSIS user authentication successful")
        print(f"Token: {token[:20]}...")
    else:
        print("✗ BSIS user authentication failed")
    
    print()


# ============================================================================
# EXAMPLE 2: NON-BSIS USERS (Generic: MACROECONOMICS, IT-MONITORING, etc.)
# ============================================================================
def example_non_bsis_static_auth():
    """
    Authenticate any non-BSIS user with static credentials.
    
    Supported data groups:
    - MACROECONOMICS
    - IT-MONITORING
    - IT-SECURITY
    - CURRENCY
    - FINANCIAL-MARKETS
    - PHYSICAL-SECURITY
    - TOURISM
    
    Prerequisites (for each data group):
    Set environment variables:
        {DATA_GROUP}_USERNAME=your_username
        {DATA_GROUP}_PASSWORD=your_password
        {DATA_GROUP}_USE_DOMAIN_LOGIN=false
    
    Examples:
        IT_MONITORING_USERNAME=user1
        IT_MONITORING_PASSWORD=pass1
        IT_MONITORING_USE_DOMAIN_LOGIN=false
        
        OR
        
        CURRENCY_USERNAME=user2
        CURRENCY_PASSWORD=pass2
        CURRENCY_USE_DOMAIN_LOGIN=false
    """
    print("=" * 70)
    print("EXAMPLE 2A: Non-BSIS User (Static Credentials)")
    print("=" * 70)
    
    # Example: Authenticate IT-MONITORING user
    token = authenticate_user("IT-MONITORING")
    
    if token:
        print(f"✓ IT-MONITORING user authentication successful")
        print(f"Token: {token[:20]}...")
    else:
        print("✗ IT-MONITORING user authentication failed")
    
    print()


def example_non_bsis_ad_auth():
    """
    Authenticate any non-BSIS user with Active Directory credentials.
    
    Supported data groups:
    - MACROECONOMICS
    - IT-MONITORING
    - IT-SECURITY
    - CURRENCY
    - FINANCIAL-MARKETS
    - PHYSICAL-SECURITY
    - TOURISM
    
    Prerequisites (for each data group):
    Set environment variables:
        {DATA_GROUP}_USE_DOMAIN_LOGIN=true
        LOGIN_URL=https://your.domain.login.url
        CERT_PATH=./certificate/_.bot.go.tz.crt
        SECRET_KEY=your_secret_key
    """
    print("=" * 70)
    print("EXAMPLE 2B: Non-BSIS User (AD Credentials)")
    print("=" * 70)
    
    # Example: Authenticate CURRENCY user with AD
    token = authenticate_user("CURRENCY")
    
    if token:
        print(f"✓ CURRENCY user (AD) authentication successful")
        print(f"Token: {token[:20]}...")
    else:
        print("✗ CURRENCY user (AD) authentication failed")
    
    print()


def example_it_security_user():
    """Example for IT-SECURITY user"""
    print("=" * 70)
    print("EXAMPLE: IT-SECURITY User")
    print("=" * 70)
    
    token = authenticate_user("IT-SECURITY")
    if token:
        print(f"✓ IT-SECURITY user authenticated")
    else:
        print("✗ IT-SECURITY authentication failed")
    print()


def example_physical_security_user():
    """Example for PHYSICAL-SECURITY user"""
    print("=" * 70)
    print("EXAMPLE: PHYSICAL-SECURITY User")
    print("=" * 70)
    
    token = authenticate_user("PHYSICAL-SECURITY")
    if token:
        print(f"✓ PHYSICAL-SECURITY user authenticated")
    else:
        print("✗ PHYSICAL-SECURITY authentication failed")
    print()


def example_tourism_user():
    """Example for TOURISM user"""
    print("=" * 70)
    print("EXAMPLE: TOURISM User")
    print("=" * 70)
    
    token = authenticate_user("TOURISM")
    if token:
        print(f"✓ TOURISM user authenticated")
    else:
        print("✗ TOURISM authentication failed")
    print()


def example_financial_markets_user():
    """Example for FINANCIAL-MARKETS user"""
    print("=" * 70)
    print("EXAMPLE: FINANCIAL-MARKETS User")
    print("=" * 70)
    
    token = authenticate_user("FINANCIAL-MARKETS")
    if token:
        print(f"✓ FINANCIAL-MARKETS user authenticated")
    else:
        print("✗ FINANCIAL-MARKETS authentication failed")
    print()


# ============================================================================
# EXAMPLE 3: MACROECONOMICS User Authentication (Static Credentials)
# ============================================================================
def example_macroeconomics_static_auth():
    """
    Authenticate a MACROECONOMICS user with static credentials.
    
    Prerequisites:
    Set environment variables:
        MACROECONOMICS_USERNAME=your_username
        MACROECONOMICS_PASSWORD=your_password
        MACROECONOMICS_USE_DOMAIN_LOGIN=false
    """
    print("=" * 70)
    print("EXAMPLE 3: MACROECONOMICS User (Static Credentials)")
    print("=" * 70)
    
    # Authenticate with MACROECONOMICS data group
    token = authenticate_user("MACROECONOMICS")
    
    if token:
        print(f"✓ MACROECONOMICS user authentication successful")
        print(f"Token: {token[:20]}...")
    else:
        print("✗ MACROECONOMICS user authentication failed")
    
    print()


# ============================================================================
# EXAMPLE 4: MACROECONOMICS User Authentication (AD Credentials)
# ============================================================================
def example_macroeconomics_ad_auth():
    """
    Authenticate a MACROECONOMICS user with Active Directory credentials.
    
    Prerequisites:
    Set environment variables:
        MACROECONOMICS_USE_DOMAIN_LOGIN=true
        LOGIN_URL=https://your.domain.login.url
        CERT_PATH=./certificate/_.bot.go.tz.crt
        SECRET_KEY=your_secret_key
    """
    print("=" * 70)
    print("EXAMPLE 4: MACROECONOMICS User (AD Credentials)")
    print("=" * 70)
    
    # Authenticate with MACROECONOMICS data group
    token = authenticate_user("MACROECONOMICS")
    
    if token:
        print(f"✓ MACROECONOMICS user (AD) authentication successful")
        print(f"Token: {token[:20]}...")
    else:
        print("✗ MACROECONOMICS user (AD) authentication failed")
    
    print()


# ============================================================================
# EXAMPLE 5: Read Data with Different Data Groups
# ============================================================================
def example_read_non_bsis_data():
    """
    Read data from various non-BSIS sources with automatic authentication.
    """
    print("=" * 70)
    print("EXAMPLE 5: Read Data from Various Non-BSIS Sources")
    print("=" * 70)
    
    data_groups = [
        ("MACROECONOMICS", "DWH"),
        ("IT-MONITORING", "DWH"),
        ("CURRENCY", "DWH"),
        ("FINANCIAL-MARKETS", "DWH"),
    ]
    
    for data_group, data_source in data_groups:
        try:
            result = read_data(
                data_group=data_group,
                data_source=data_source,
                data_type="sample_type",
                bank_code="monthly",
                start_period="01-Jan-2024",
                end_period="31-Dec-2024"
            )
            
            if result["df"].empty:
                print(f"✗ {data_group}: No data. Debug: {result['debug']}")
            else:
                print(f"✓ {data_group}: {len(result['df'])} rows retrieved")
        except Exception as e:
            print(f"✗ {data_group}: Error - {e}")
    
    print()


# ============================================================================
# Main Execution
# ============================================================================
if __name__ == "__main__":
    """
    Run examples selectively. Comment/uncomment as needed.
    """
    
    # Uncomment the examples you want to run:
    
    # example_bsis_authentication()
    
    # Non-BSIS User Examples (Generic for all non-BSIS groups)
    # example_non_bsis_static_auth()
    # example_non_bsis_ad_auth()
    
    # Specific Data Group Examples
    # example_macroeconomics_static_auth()
    # example_macroeconomics_ad_auth()
    # example_it_security_user()
    # example_physical_security_user()
    # example_tourism_user()
    # example_financial_markets_user()
    
    # Data Reading Examples
    # example_read_non_bsis_data()
    # example_read_bsis_data()
    
    print("""
    AUTHENTICATION SYSTEM EXAMPLES
    ==============================
    
    Supported Data Groups:
    ├─ BSIS (existing)
    ├─ MACROECONOMICS (static/AD)
    ├─ IT-MONITORING (static/AD)
    ├─ IT-SECURITY (static/AD)
    ├─ CURRENCY (static/AD)
    ├─ FINANCIAL-MARKETS (static/AD)
    ├─ PHYSICAL-SECURITY (static/AD)
    └─ TOURISM (static/AD)
    
    This file contains implementation examples for the authentication 
    system supporting BSIS and multiple non-BSIS data groups.
    
    To run examples, uncomment the function calls above and execute 
    the script.
    
    Environment Variable Pattern for Non-BSIS Groups:
    {DATA_GROUP}_USERNAME
    {DATA_GROUP}_PASSWORD
    {DATA_GROUP}_USE_DOMAIN_LOGIN
    
    Examples:
    IT_MONITORING_USERNAME=user1
    IT_SECURITY_PASSWORD=secure_pass
    CURRENCY_USE_DOMAIN_LOGIN=true
    
    See AUTHENTICATION_SETUP.md for detailed configuration instructions.
    """)
