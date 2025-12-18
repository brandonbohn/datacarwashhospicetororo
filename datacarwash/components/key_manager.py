"""
Bank-level secure key management using Python secrets.
Generates cryptographically secure encryption keys.
Parent system retrieves key programmatically (never human-readable).
"""

import secrets
import base64
from pathlib import Path
from typing import Optional


def generate_bank_level_key(bits: int = 256) -> str:
    """
    Generate bank-level cryptographically secure key.
    
    Args:
        bits: Key strength in bits (default 256-bit = AES-256 strength)
        
    Returns:
        Base64-encoded random key (not human-readable)
    """
    # Generate random bytes
    key_bytes = secrets.token_bytes(bits // 8)
    
    # Encode as base64 for storage
    key_b64 = base64.b64encode(key_bytes).decode('utf-8')
    
    return key_b64


def get_or_create_key(env_path: Path = None) -> tuple[str, bool]:
    """
    Get existing key from .env or create new one.
    
    Args:
        env_path: Path to .env file (default: project root)
        
    Returns:
        Tuple of (key, is_new)
        - key: The encryption key (base64-encoded)
        - is_new: True if newly generated, False if loaded
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent.parent / ".env"
    
    # Try to load existing key
    if env_path.exists():
        key = load_key_from_env(env_path)
        if key:
            print("🔑 Loaded existing encryption key from .env")
            return key, False
    
    # Generate new bank-level key
    print("🔐 No key found - generating bank-level secure key...")
    key = generate_bank_level_key(bits=256)  # AES-256 strength
    save_key_to_env(key, env_path)
    
    print(f"✅ Generated 256-bit cryptographically secure key")
    print(f"🏦 Bank-level security: Key saved to .env")
    print(f"⚠️  Key is NOT human-readable (base64-encoded random bytes)")
    
    return key, True


def load_key_from_env(env_path: Path) -> Optional[str]:
    """Load encryption key from .env file."""
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ENCRYPTION_KEY='):
                    key = line.split('=', 1)[1].strip()
                    if key:
                        return key
    except Exception as e:
        print(f"⚠️  Error reading .env: {e}")
    
    return None


def save_key_to_env(key: str, env_path: Path):
    """Save encryption key to .env file."""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing content
    existing_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_lines = [line for line in f if not line.strip().startswith('ENCRYPTION_KEY=')]
    
    # Write back with new key
    with open(env_path, 'w') as f:
        # Add security header
        f.write("# TORORO HOSPICE ENCRYPTION KEY\n")
        f.write("# WARNING: This file contains cryptographically secure keys\n")
        f.write("# NEVER commit this file to version control\n")
        f.write("# NEVER share this file via insecure channels\n")
        f.write("# Parent system accesses this key programmatically\n\n")
        
        # Add key
        f.write(f"ENCRYPTION_KEY={key}\n")
        f.write("\n")
        
        # Write other existing variables
        for line in existing_lines:
            if line.strip() and not line.strip().startswith('#'):
                f.write(f"{line}\n")


def get_key_for_parent_system() -> str:
    """
    API endpoint for parent system to retrieve encryption key.
    Parent system calls this function to get the key programmatically.
    
    Returns:
        Encryption key (base64-encoded)
        
    Raises:
        RuntimeError: If key doesn't exist
    """
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    key = load_key_from_env(env_path)
    
    if not key:
        raise RuntimeError(
            "Encryption key not found. "
            "Run the datacarwash pipeline first to generate the key."
        )
    
    return key


def export_key_metadata(output_path: Path):
    """
    Export key metadata (NOT the key itself) for parent system.
    Parent system uses this to know how to retrieve the key.
    
    Args:
        output_path: Where to save metadata file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("TORORO HOSPICE ENCRYPTION KEY - PARENT SYSTEM INTERFACE\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("SECURITY NOTICE:\n")
        f.write("-" * 70 + "\n")
        f.write("This system uses bank-level cryptographic security.\n")
        f.write("The encryption key is:\n")
        f.write("  - 256-bit AES strength\n")
        f.write("  - Generated using Python secrets module\n")
        f.write("  - NOT human-readable (base64-encoded random bytes)\n")
        f.write("  - Stored in .env file (git-ignored)\n\n")
        
        f.write("PARENT SYSTEM INTEGRATION:\n")
        f.write("-" * 70 + "\n")
        f.write("To retrieve the encryption key programmatically:\n\n")
        
        f.write("Option 1: Python API (Recommended)\n")
        f.write("```python\n")
        f.write("from datacarwash.components.key_manager import get_key_for_parent_system\n\n")
        f.write("# Parent system retrieves key\n")
        f.write("encryption_key = get_key_for_parent_system()\n")
        f.write("```\n\n")
        
        f.write("Option 2: Environment Variable\n")
        f.write("```python\n")
        f.write("import os\n")
        f.write("from pathlib import Path\n\n")
        f.write("# Load .env file\n")
        f.write("env_path = Path('path/to/.env')\n")
        f.write("with open(env_path, 'r') as f:\n")
        f.write("    for line in f:\n")
        f.write("        if line.startswith('ENCRYPTION_KEY='):\n")
        f.write("            key = line.split('=', 1)[1].strip()\n")
        f.write("```\n\n")
        
        f.write("Option 3: Shared Secret System (Production)\n")
        f.write("For production deployment, consider:\n")
        f.write("  - AWS Secrets Manager\n")
        f.write("  - HashiCorp Vault\n")
        f.write("  - Azure Key Vault\n")
        f.write("  - Google Secret Manager\n\n")
        
        f.write("DECRYPTION EXAMPLE:\n")
        f.write("-" * 70 + "\n")
        f.write("```python\n")
        f.write("import pyzipper\n")
        f.write("from datacarwash.components.key_manager import get_key_for_parent_system\n\n")
        f.write("# Get key from datacarwash system\n")
        f.write("key = get_key_for_parent_system()\n\n")
        f.write("# Decrypt file\n")
        f.write("with pyzipper.AESZipFile('persons.zip', 'r') as zipf:\n")
        f.write("    zipf.setpassword(key.encode('utf-8'))\n")
        f.write("    data = zipf.read('persons.json')\n")
        f.write("```\n\n")
        
        f.write("SECURITY BEST PRACTICES:\n")
        f.write("-" * 70 + "\n")
        f.write("1. Access .env file via secure filesystem permissions (chmod 600)\n")
        f.write("2. Use encrypted filesystems for production storage\n")
        f.write("3. Rotate keys periodically (re-encrypt with new key)\n")
        f.write("4. Log key access for audit trails\n")
        f.write("5. Never log or display the actual key value\n\n")
        
        f.write("=" * 70 + "\n")
    
    print(f"📋 Key metadata exported to: {output_path}")
