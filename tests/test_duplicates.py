import pytest
import cv2
import numpy as np
from pathlib import Path
from datasetvision.duplicates import find_exact_duplicates, find_near_duplicates

def test_exact_duplicates(tmp_path):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "a.png"), img)
    cv2.imwrite(str(tmp_path / "b.png"), img)
    
    results = find_exact_duplicates(tmp_path)
    assert len(results) == 1
    
def test_near_duplicates(tmp_path):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "a.png"), img)
    img2 = img.copy()
    img2[0,0] = 1
    cv2.imwrite(str(tmp_path / "b.png"), img2)
    
    results = find_near_duplicates(tmp_path)
    assert len(results) == 1
