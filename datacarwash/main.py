"""
Main data collection pipeline for Tororo Hospice.
Bank-level secure encryption with programmatic key access for parent system.
"""

from pathlib import Path
from datacarwash.components.uploadfile import uploadfile, scanfile
from datacarwash.components.normilization import normalization
from datacarwash.components.encryption import encryption
from datacarwash.components.key_manager import get_or_create_key, export_key_metadata


def process_kobo_file(input_file: Path, output_base: Path, encryption_key: str) -> bool:
    """
    Process a single Kobo file through the complete pipeline.
    
    Args:
        input_file: Path to Excel/CSV file
        output_base: Base output directory
        encryption_key: Bank-level encryption key
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Processing: {input_file.name}")
    print(f"{'='*70}")
    
    try:
        # Step 1: Validate file
        print("\n📋 Step 1: Validating file...")
        if not uploadfile(input_file):
            print(f"❌ Invalid file: {input_file}")
            return False
        print("✅ File validated")
        
        # Step 2: Normalize (Excel → JSON with deduplication)
        print("\n🔄 Step 2: Normalizing data...")
        normalized_dir = output_base / "normalized"
        normalization(input_file, normalized_dir)
        print(f"✅ Normalized data saved")
        
        # Step 3: Encrypt each JSON file with bank-level key
        print("\n🔒 Step 3: Encrypting with bank-level security...")
        encrypted_dir = output_base / "encrypted"
        encrypted_dir.mkdir(parents=True, exist_ok=True)
        
        encrypted_count = 0
        for json_file in normalized_dir.glob("*.json"):
            zip_file = encrypted_dir / f"{json_file.stem}.zip"
            encryption(json_file, zip_file, encryption_key)
            print(f"   🔐 {json_file.name} → {zip_file.name}")
            encrypted_count += 1
        
        print(f"\n✅ Encrypted {encrypted_count} files with 256-bit AES encryption")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing file: {e}")
        return False


def process_folder(folder_path: Path, output_base: Path, encryption_key: str) -> int:
    """
    Process all Kobo files in a folder.
    
    Args:
        folder_path: Folder containing Kobo files
        output_base: Base output directory
        encryption_key: Bank-level encryption key
        
    Returns:
        Number of successfully processed files
    """
    print(f"\n🔍 Scanning folder: {folder_path}")
    
    try:
        valid_files = scanfile(folder_path)
    except Exception as e:
        print(f"❌ Error scanning folder: {e}")
        return 0
    
    if not valid_files:
        print("❌ No valid files found!")
        return 0
    
    print(f"✅ Found {len(valid_files)} valid file(s)")
    
    success_count = 0
    for file in valid_files:
        if process_kobo_file(file, output_base, encryption_key):
            success_count += 1
    
    return success_count


def main():
    """Main entry point - Data collection and encryption pipeline."""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "TORORO HOSPICE DATA PIPELINE" + " "*20 + "║")
    print("║" + " "*15 + "Bank-Level Secure Data Collection System" + " "*12 + "║")
    print("╚" + "="*68 + "╝")
    
    # Step 1: Get or generate bank-level encryption key
    print("\n🏦 Step 1: Bank-Level Secure Key Management")
    print("-" * 70)
    encryption_key, is_new = get_or_create_key()
    
    if is_new:
        print("\n⚠️  NEW ENCRYPTION KEY GENERATED!")
        print("🔐 256-bit cryptographically secure key (NOT human-readable)")
        print("🏦 Meets bank-level security standards")
        print("📋 Parent system will retrieve key programmatically")
    else:
        print("\n✅ Using existing encryption key")
    
    # Configuration
    INPUT_FOLDER = Path("client_files")
    OUTPUT_BASE = Path("output")
    HANDOFF_DIR = OUTPUT_BASE / "handoff"
    
    # Create directories if they don't exist
    INPUT_FOLDER.mkdir(exist_ok=True)
    OUTPUT_BASE.mkdir(exist_ok=True)
    
    # Step 2: Process files
    print("\n📂 Step 2: Processing Kobo Data")
    print("-" * 70)
    
    if not INPUT_FOLDER.exists() or not any(INPUT_FOLDER.iterdir()):
        print(f"⚠️  No files found in {INPUT_FOLDER}")
        print(f"📥 Place Excel/CSV files in {INPUT_FOLDER} and run again")
        return
    
    success_count = process_folder(INPUT_FOLDER, OUTPUT_BASE, encryption_key)
    
    if success_count > 0:
        # Step 3: Export parent system interface documentation
        print("\n🔗 Step 3: Preparing Parent System Interface")
        print("-" * 70)
        HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
        
        # Export key access documentation (NOT the key itself!)
        interface_doc = HANDOFF_DIR / "PARENT_SYSTEM_INTERFACE.txt"
        export_key_metadata(interface_doc)
        
        # Create handoff readme
        readme_file = HANDOFF_DIR / "README.txt"
        with open(readme_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("TORORO HOSPICE DATA HANDOFF PACKAGE\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("🔐 BANK-LEVEL SECURITY SYSTEM\n")
            f.write("-" * 70 + "\n")
            f.write("This system uses 256-bit AES encryption (bank-grade security).\n")
            f.write("The encryption key is stored in .env (NOT in this package).\n\n")
            
            f.write("📦 PACKAGE CONTENTS:\n")
            f.write("-" * 70 + "\n")
            f.write(f"1. Encrypted data files: {OUTPUT_BASE / 'encrypted'}/\n")
            f.write(f"   - persons.zip\n")
            f.write(f"   - encounters.zip\n")
            f.write(f"   - observations.zip\n")
            f.write(f"   - treatments.zip\n")
            f.write(f"   - diseases.zip\n")
            f.write(f"   - medical_records.zip\n\n")
            f.write(f"2. Parent system interface: {interface_doc.name}\n")
            f.write(f"   - How to access encryption key programmatically\n")
            f.write(f"   - Decryption code examples\n")
            f.write(f"   - Security best practices\n\n")
            
            f.write("🔑 KEY ACCESS FOR PARENT SYSTEM:\n")
            f.write("-" * 70 + "\n")
            f.write("Parent system retrieves the key programmatically:\n\n")
            f.write("from datacarwash.components.key_manager import get_key_for_parent_system\n\n")
            f.write("# Parent system calls this\n")
            f.write("encryption_key = get_key_for_parent_system()\n\n")
            f.write("The key is NEVER displayed, logged, or stored in plain text files.\n")
            f.write("It exists only in the secure .env file.\n\n")
            
            f.write("🚀 PARENT SYSTEM WORKFLOW:\n")
            f.write("-" * 70 + "\n")
            f.write("1. Call get_key_for_parent_system() to retrieve encryption key\n")
            f.write("2. Use key to decrypt ZIP files\n")
            f.write("3. Load JSON data into database/application\n")
            f.write("4. Process and display data as needed\n\n")
            
            f.write("🔒 SECURITY NOTES:\n")
            f.write("-" * 70 + "\n")
            f.write("- This system (datacarwash) ONLY encrypts, never decrypts\n")
            f.write("- Encryption key is 256-bit AES strength\n")
            f.write("- Key is NOT human-readable (base64-encoded random bytes)\n")
            f.write("- .env file must be secured (chmod 600 on Unix systems)\n")
            f.write("- Parent system accesses key via secure Python API\n")
            f.write("- No plain text password files are created\n\n")
            
            f.write("=" * 70 + "\n")
        
        print(f"📄 Handoff documentation: {readme_file}")
        
        # Summary
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📊 Processing Summary:")
        print(f"   ✅ Successfully processed: {success_count} file(s)")
        print(f"   🔐 Encryption level: 256-bit AES (bank-grade)")
        print(f"   📁 Encrypted files: {OUTPUT_BASE / 'encrypted'}/")
        print(f"   📋 Handoff docs: {HANDOFF_DIR}/")
        
        print(f"\n🔗 Parent System Integration:")
        print(f"   The parent system will call:")
        print(f"   >>> from datacarwash.components.key_manager import get_key_for_parent_system")
        print(f"   >>> key = get_key_for_parent_system()")
        print(f"   >>> # Use key to decrypt files")
        
        print(f"\n🎯 Status:")
        print(f"   This system's job is DONE! ✅")
        print(f"   Ready for parent system to retrieve key and decrypt data.")
        print(f"   No manual password handoff needed - fully automated! 🚀\n")
        
    else:
        print("\n❌ No files were processed successfully.")
        print("Check the error messages above for details.")


if __name__ == "__main__":
    main()
