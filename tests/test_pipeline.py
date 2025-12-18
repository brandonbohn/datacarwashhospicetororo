"""
Tests for the main pipeline.
"""

import pytest
import pandas as pd
from pathlib import Path
from datacarwash.pipeline import DataCarWashPipeline


def test_pipeline_initialization():
    """Test that pipeline initializes correctly."""
    pipeline = DataCarWashPipeline()
    assert pipeline is not None
    assert pipeline.loader is not None
    assert pipeline.normalizer is not None
    assert pipeline.deduplicator is not None
    assert pipeline.organizer is not None


def test_pipeline_with_config(tmp_path):
    """Test pipeline initialization with config file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("normalization:\n  missing_value_strategy: drop_rows")
    
    pipeline = DataCarWashPipeline(config_path=config_file)
    assert pipeline.config['normalization']['missing_value_strategy'] == 'drop_rows'
