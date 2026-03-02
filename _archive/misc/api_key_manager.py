"""
API Key Generator
Generates secure API keys for Budget Analysis App
"""

import secrets
import string
import hashlib
import json
import os
from datetime import datetime

def generate_api_key(length=32):
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key

def hash_api_key(api_key):
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key(name, description=""):
    """
    Create a new API key with metadata
    
    Args:
        name: Name/identifier for this API key
        description: Optional description
    
    Returns:
        dict with key, hash, and metadata
    """
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    
    key_data = {
        'name': name,
        'key': api_key,
        'key_hash': key_hash,
        'description': description,
        'created': datetime.now().isoformat(),
        'active': True
    }
    
    return key_data

def save_api_key(key_data, filename='api_keys.json'):
    """Save API key to file"""
    # Load existing keys
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            keys = json.load(f)
    else:
        keys = []
    
    # Add new key (don't save the actual key, only the hash)
    safe_key_data = {
        'name': key_data['name'],
        'key_hash': key_data['key_hash'],
        'description': key_data['description'],
        'created': key_data['created'],
        'active': key_data['active']
    }
    
    keys.append(safe_key_data)
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(keys, f, indent=2)
    
    print(f"✅ API key saved to {filename}")

def list_api_keys(filename='api_keys.json'):
    """List all API keys (without showing actual keys)"""
    if not os.path.exists(filename):
        print("No API keys found")
        return []
    
    with open(filename, 'r') as f:
        keys = json.load(f)
    
    print("\n" + "=" * 80)
    print("API KEYS")
    print("=" * 80)
    
    for i, key in enumerate(keys, 1):
        status = "✅ Active" if key['active'] else "❌ Inactive"
        print(f"\n{i}. {key['name']}")
        print(f"   Status: {status}")
        print(f"   Created: {key['created']}")
        print(f"   Description: {key.get('description', 'N/A')}")
        print(f"   Hash: {key['key_hash'][:16]}...")
    
    print("\n" + "=" * 80)
    return keys

def deactivate_api_key(name, filename='api_keys.json'):
    """Deactivate an API key"""
    if not os.path.exists(filename):
        print("No API keys found")
        return
    
    with open(filename, 'r') as f:
        keys = json.load(f)
    
    found = False
    for key in keys:
        if key['name'] == name:
            key['active'] = False
            found = True
            print(f"✅ Deactivated API key: {name}")
            break
    
    if not found:
        print(f"❌ API key not found: {name}")
        return
    
    with open(filename, 'w') as f:
        json.dump(keys, f, indent=2)

def verify_api_key(provided_key, filename='api_keys.json'):
    """Verify if an API key is valid"""
    if not os.path.exists(filename):
        return False
    
    with open(filename, 'r') as f:
        keys = json.load(f)
    
    provided_hash = hash_api_key(provided_key)
    
    for key in keys:
        if key['key_hash'] == provided_hash and key['active']:
            return True
    
    return False

# ============================================================================
# MAIN SCRIPT
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 80)
    print("🔐 API KEY MANAGER")
    print("=" * 80)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python api_key_manager.py create <name> [description]")
        print("  python api_key_manager.py list")
        print("  python api_key_manager.py deactivate <name>")
        print("  python api_key_manager.py verify <key>")
        print()
        print("Examples:")
        print('  python api_key_manager.py create "Production API" "Main production key"')
        print('  python api_key_manager.py create "Dev API" "Development testing"')
        print('  python api_key_manager.py list')
        print('  python api_key_manager.py deactivate "Dev API"')
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a name for the API key")
            sys.exit(1)
        
        name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        
        print(f"Creating API key: {name}")
        print()
        
        key_data = create_api_key(name, description)
        save_api_key(key_data)
        
        print()
        print("=" * 80)
        print("⚠️  IMPORTANT - SAVE THIS KEY NOW!")
        print("=" * 80)
        print()
        print(f"API Key: {key_data['key']}")
        print()
        print("This is the ONLY time you will see this key!")
        print("Store it securely - you cannot retrieve it later.")
        print()
        print("Add to your .env file:")
        print(f"API_KEY={key_data['key']}")
        print()
        print("=" * 80)
    
    elif command == 'list':
        list_api_keys()
    
    elif command == 'deactivate':
        if len(sys.argv) < 3:
            print("❌ Error: Please provide the name of the API key to deactivate")
            sys.exit(1)
        
        name = sys.argv[2]
        deactivate_api_key(name)
    
    elif command == 'verify':
        if len(sys.argv) < 3:
            print("❌ Error: Please provide the API key to verify")
            sys.exit(1)
        
        key = sys.argv[2]
        if verify_api_key(key):
            print("✅ API key is VALID and ACTIVE")
        else:
            print("❌ API key is INVALID or INACTIVE")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)