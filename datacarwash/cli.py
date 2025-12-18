"""
Command-line interface for the Data Car Wash pipeline.
"""

import click
import logging
from pathlib import Path
from typing import Optional

from datacarwash.pipeline import DataCarWashPipeline
from datacarwash.utils.logger import setup_logger


@click.group()
@click.version_option()
def main():
    """Data Car Wash - Process data from dirty to clean."""
    pass


@main.command()
@click.option('--input', '-i', 'input_path', required=True, type=click.Path(exists=True),
              help='Input data file or directory')
@click.option('--output', '-o', 'output_path', required=True, type=click.Path(),
              help='Output zip file path')
@click.option('--config', '-c', 'config_path', type=click.Path(exists=True),
              help='Configuration file (YAML)')
@click.option('--encrypt/--no-encrypt', default=False,
              help='Encrypt the output')
@click.option('--password', '-p', type=str,
              help='Password for encryption/decryption')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def wash(input_path: str, output_path: str, config_path: Optional[str],
         encrypt: bool, password: Optional[str], verbose: bool):
    """
    Run the data car wash pipeline.
    
    Takes dirty data from input, cleans it, and outputs a clean zip file.
    """
    logger = setup_logger(verbose=verbose)
    logger.info("🚗 Starting Data Car Wash...")
    
    try:
        pipeline = DataCarWashPipeline(config_path=config_path)
        pipeline.run(
            input_path=Path(input_path),
            output_path=Path(output_path),
            encrypt=encrypt,
            password=password
        )
        logger.info("✨ Data Car Wash completed successfully!")
    except Exception as e:
        logger.error(f"❌ Data Car Wash failed: {e}")
        raise click.ClickException(str(e))


@main.command()
@click.option('--encrypted-file', '-f', required=True, type=click.Path(exists=True),
              help='Encrypted file to decrypt')
@click.option('--output', '-o', 'output_path', required=True, type=click.Path(),
              help='Output decrypted file path')
@click.option('--password', '-p', required=True, type=str,
              help='Password for decryption')
def decrypt(encrypted_file: str, output_path: str, password: str):
    """Decrypt an encrypted file."""
    from datacarwash.encryption import DataEncryption
    
    logger = setup_logger()
    logger.info(f"🔓 Decrypting {encrypted_file}...")
    
    try:
        encryptor = DataEncryption()
        encryptor.decrypt_file(Path(encrypted_file), Path(output_path), password)
        logger.info(f"✅ Decrypted to {output_path}")
    except Exception as e:
        logger.error(f"❌ Decryption failed: {e}")
        raise click.ClickException(str(e))


@main.command()
@click.option('--url', required=True, help='KoBoToolbox API URL')
@click.option('--token', required=True, help='API token')
@click.option('--form-id', required=True, help='Form ID to fetch')
@click.option('--output', '-o', 'output_path', required=True, type=click.Path(),
              help='Output file path for fetched data')
def fetch_kobo(url: str, token: str, form_id: str, output_path: str):
    """Fetch data from KoBoToolbox."""
    from datacarwash.kobo import KoboClient
    
    logger = setup_logger()
    logger.info(f"📥 Fetching data from KoBoToolbox...")
    
    try:
        client = KoboClient(api_url=url, token=token)
        data = client.fetch_form_data(form_id)
        client.save_data(data, Path(output_path))
        logger.info(f"✅ Data saved to {output_path}")
    except Exception as e:
        logger.error(f"❌ Fetch failed: {e}")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()
