import pytest
import cv2
import numpy as np
from pathlib import Path
from datasetvision.stats import compute_stats

def test_compute_stats_nonexistent():
    with pytest.raises(FileNotFoundError):
        compute_stats(Path("nonexistent_path"))

def test_compute_stats_empty(tmp_path):
    stats = compute_stats(tmp_path)
    assert stats["num_images"] == 0
    assert stats["mean_size"] is None
    assert stats["mean_channel_values"] is None

def test_compute_stats_valid(tmp_path):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "img1.png"), img)
    
    stats = compute_stats(tmp_path)
    assert stats["num_images"] == 1
    assert stats["mean_size"] == (10, 10)
    assert stats["mean_channel_values"] == [0.0, 0.0, 0.0]
