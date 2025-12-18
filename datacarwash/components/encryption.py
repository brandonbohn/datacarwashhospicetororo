from pathlib import Path
import pyzipper 
import os





def encryption ( input_path: Path, output_path: Path, password: str):

    if input_path.suffix in ['.json']:
        with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED,encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(password.encode('utf-8'))
                zipf.writestr(input_path.name, input_path.read_bytes())
        return True

    else:
        raise ValueError(f"Unsupported file type for encryption: {input_path.suffix}") 



    