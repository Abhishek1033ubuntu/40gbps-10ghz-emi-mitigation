"""
Automated Pytest Suite for emi-mitigation-sim
Validates package installation, dataset generation, and IEEE 370 compliance logic.

Author: Abhishek Singh (ORCID: 0009-0004-6913-096X)
"""

import os
import pytest
import emi_mitigation_sim as emi


def test_touchstone_generation(tmp_path):
    """Verify that generate_s8p creates a non-empty Touchstone file."""
    test_file = os.path.join(tmp_path, "test_50ghz.s8p")
    emi.generate_s8p(test_file)
    
    assert os.path.exists(test_file)
    assert os.path.getsize(test_file) > 0


def test_simulation_execution(tmp_path):
    """Verify that run_validation executes without error and returns valid metrics."""
    test_file = os.path.join(tmp_path, "test_50ghz.s8p")
    
    # Run simulation headlessly (no pop-up plot during automated tests)
    metrics = emi.run_validation(data_path=test_file, show_plot=False)
    
    # Check returned dictionary keys
    assert "s11_10ghz_db" in metrics
    assert "s31_10ghz_db" in metrics
    assert "s11_50ghz_db" in metrics
    assert "s31_50ghz_db" in metrics
    assert "ieee_370_passed" in metrics

    # Check physical compliance limits
    assert metrics["s31_10ghz_db"] <= -50.0
    assert metrics["s31_50ghz_db"] <= -40.0
    assert metrics["ieee_370_passed"] is True
