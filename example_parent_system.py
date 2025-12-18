"""
Example parent system script showing how to retrieve encryption key
and decrypt files from the datacarwash system.
"""

from pathlib import Path
import json
import pyzipper
from datacarwash.components.key_manager import get_key_for_parent_system


def decrypt_and_load_data(encrypted_dir: Path, output_dir: Path = None):
    """
    Parent system: Retrieve key and decrypt all data files.
    
    Args:
        encrypted_dir: Directory with encrypted ZIP files
        output_dir: Where to save decrypted JSON (optional)
    """
    print("🔓 PARENT SYSTEM - Decryption Process")
    print("="*70)
    
    # Step 1: Retrieve encryption key from datacarwash system
    print("\n🔑 Step 1: Retrieving encryption key from datacarwash...")
    try:
        encryption_key = get_key_for_parent_system()
        print("✅ Encryption key retrieved successfully")
        print("🏦 Key is 256-bit AES strength (NOT displayed for security)")
    except Exception as e:
        print(f"❌ Error retrieving key: {e}")
        print("Make sure the datacarwash pipeline has been run first!")
        return
    
    # Step 2: Decrypt all ZIP files
    print("\n🔓 Step 2: Decrypting data files...")
    
    if not encrypted_dir.exists():
        print(f"❌ Encrypted directory not found: {encrypted_dir}")
        return
    
    decrypted_data = {}
    
    for zip_file in encrypted_dir.glob("*.zip"):
        print(f"\n   Decrypting: {zip_file.name}")
        
        try:
            # Decrypt ZIP file
            with pyzipper.AESZipFile(zip_file, 'r') as zipf:
                zipf.setpassword(encryption_key.encode('utf-8'))
                
                # Get the JSON filename inside the ZIP
                json_filename = zip_file.stem + '.json'
                
                # Read and parse JSON
                json_data = zipf.read(json_filename)
                data = json.loads(json_data)
                
                decrypted_data[zip_file.stem] = data
                
                print(f"   ✅ Decrypted {len(data)} records from {zip_file.name}")
                
                # Optionally save to file
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / json_filename
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"   💾 Saved to: {output_file}")
                    
        except Exception as e:
            print(f"   ❌ Error decrypting {zip_file.name}: {e}")
    
    # Step 3: Summary
    print("\n" + "="*70)
    print("✅ DECRYPTION COMPLETE!")
    print("="*70)
    print(f"\n📊 Decrypted Data Summary:")
    for model_name, records in decrypted_data.items():
        print(f"   {model_name}: {len(records)} records")
    
    print(f"\n🎯 Next Steps:")
    print(f"   - Load data into your database")
    print(f"   - Display in web application")
    print(f"   - Run analytics/reports")
    print(f"   - Export to other systems")
    
    return decrypted_data


def main():
    """Example parent system usage."""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*22 + "PARENT SYSTEM - DECRYPTION" + " "*21 + "║")
    print("║" + " "*15 + "Secure Data Access for Tororo Hospice" + " "*15 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Configuration
    ENCRYPTED_DIR = Path("output/encrypted")
    OUTPUT_DIR = Path("output/decrypted")  # Optional
    
    # Decrypt and load data
    data = decrypt_and_load_data(ENCRYPTED_DIR, OUTPUT_DIR)
    
    if data:
        print("\n✅ Data ready for use in parent system!")
        
        # Example: Access the data
        print("\n📋 Example Data Access:")
        if 'persons' in data:
            print(f"   Total patients: {len(data['persons'])}")
            if data['persons']:
                print(f"   First patient: {data['persons'][0].get('name', 'N/A')}")
        
        if 'encounters' in data:
            print(f"   Total encounters: {len(data['encounters'])}")
        
        if 'observations' in data:
            print(f"   Total observations: {len(data['observations'])}")


if __name__ == "__main__":
    main()
