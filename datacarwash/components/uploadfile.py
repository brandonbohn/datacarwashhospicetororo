from pathlib import Path


def uploadfile ( input_path: Path):

   if input_path.exists():
        return input_path.suffix in ['.xlsx', '.csv', '.xls']
   else:
        raise FileNotFoundError(f"File {input_path} does not exist.")   

def scanfile ( folder_path: Path):
 
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder {folder_path} does not exist.")
    if not folder_path.is_dir():
        raise NotADirectoryError(f"{folder_path} is not a directory.")

    valid_files = []

    for item in folder_path.iterdir():
        if item.is_file() and item.suffix in ['.xlsx', '.csv', '.xls']:
            valid_files.append(item)

    return valid_files