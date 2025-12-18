# Data Car Wash 🚗✨

A Python data processing pipeline that takes dirty data from KoBoToolbox and other sources, cleans it, and outputs pristine, organized data.

## Overview

Data Car Wash is a modular data processing pipeline with the following stages:

1. **Load** - Import data from KoBoToolbox, CSV, Excel, or JSON files
2. **Normalize** - Standardize formats, handle missing values, clean text
3. **Deduplicate** - Remove duplicate records based on configurable rules
4. **Organize** - Group, sort, and filter data based on your requirements
5. **Save** - Export as a zip file with optional encryption

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Project Structure

```
datacarwashhospicetororo/
├── datacarwash/              # Main package
│   ├── __init__.py
│   ├── cli.py                # Command-line interface
│   ├── pipeline.py           # Main pipeline orchestration
│   ├── kobo.py               # KoBoToolbox integration
│   ├── normalization.py      # Data normalization
│   ├── deduplication.py      # Duplicate removal
│   ├── organization.py       # Data organization
│   ├── encryption.py         # Encryption/decryption
│   └── utils/                # Utility modules
│       ├── logger.py
│       └── zipper.py
├── config/                   # Configuration files
│   └── default.yaml
├── data/                     # Data directories
│   ├── input/               # Input data
│   ├── output/              # Processed output
│   └── temp/                # Temporary files
├── tests/                    # Test suite
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Usage

### Command Line Interface

The main command is `datacarwash`:

```bash
# Basic usage - process data
datacarwash wash -i data/input/my_data.csv -o data/output/clean_data.zip

# With encryption
datacarwash wash -i data/input/my_data.csv -o data/output/clean_data.zip \
  --encrypt --password mypassword

# With custom configuration
datacarwash wash -i data/input/my_data.csv -o data/output/clean_data.zip \
  -c config/my_config.yaml

# Verbose logging
datacarwash wash -i data/input/my_data.csv -o data/output/clean_data.zip -v
```

### Fetch from KoBoToolbox

```bash
datacarwash fetch-kobo \
  --url https://kobo.example.com \
  --token YOUR_API_TOKEN \
  --form-id YOUR_FORM_ID \
  --output data/input/kobo_data.json
```

### Decrypt Files

```bash
datacarwash decrypt \
  -f data/output/encrypted.zip \
  -o data/output/decrypted.zip \
  --password mypassword
```

## Configuration

Create a YAML configuration file to customize the pipeline behavior:

```yaml
# config/my_config.yaml

normalization:
  missing_value_strategy: keep  # keep, drop_rows, or drop_columns
  date_columns:
    - submission_date
    - created_at
  custom_rules:
    status:
      lowercase: true
    category:
      value_map:
        old_value: new_value

deduplication:
  strategy: key_columns  # all_columns or key_columns
  key_columns:
    - participant_id
    - submission_date
  keep: first  # first, last, or false

organization:
  sort:
    columns:
      - category
      - date
    ascending: true
  grouping:
    column: category  # Group into separate files by this column
  filters:
    - column: status
      operator: equals
      value: complete
```

## Python API

You can also use the pipeline programmatically:

```python
from pathlib import Path
from datacarwash.pipeline import DataCarWashPipeline

# Initialize pipeline
pipeline = DataCarWashPipeline(config_path=Path("config/my_config.yaml"))

# Run the pipeline
pipeline.run(
    input_path=Path("data/input/my_data.csv"),
    output_path=Path("data/output/clean_data.zip"),
    encrypt=True,
    password="mypassword"
)
```

## Features

- ✅ **Multiple Input Formats**: CSV, Excel, JSON
- ✅ **KoBoToolbox Integration**: Direct API access to fetch form submissions
- ✅ **Flexible Normalization**: Configurable rules for data standardization
- ✅ **Smart Deduplication**: Remove duplicates based on all columns or specific keys
- ✅ **Data Organization**: Group, sort, and filter data
- ✅ **Encryption**: Secure your data with password-based encryption
- ✅ **Zip Output**: Clean data packaged in a compressed archive
- ✅ **Full Control**: Extensive configuration options for complete control

## Development

### Running Tests

```bash
pytest tests/
```

### Adding Custom Processing Steps

The pipeline is designed to be extensible. You can add custom processing steps by:

1. Creating a new module in the `datacarwash/` directory
2. Implementing your processing logic
3. Integrating it into the pipeline in `pipeline.py`

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.