import pytest
import cv2
import numpy as np
from pathlib import Path
from datasetvision.scanner import scan_dataset

def test_scan_dataset_nonexistent():
    with pytest.raises(FileNotFoundError):
        scan_dataset(Path("nonexistent_path"))

def test_scan_dataset_valid(tmp_path):
    blank = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "blank.png"), blank)
    
    extreme = np.zeros((10, 100, 3), dtype=np.uint8)
    extreme[:, :50] = 255
    cv2.imwrite(str(tmp_path / "extreme.png"), extreme)
    
    (tmp_path / "corrupt.png").write_text("not an image")
    
    results = scan_dataset(tmp_path)
    
    assert results["total_images"] == 3
    assert len(results["blank"]) == 1
    assert len(results["extreme_aspect_ratio"]) == 1
    assert len(results["corrupted"]) == 1
