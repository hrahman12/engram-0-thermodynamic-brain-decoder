# Run both verification test suites
import pytest
from verify_quantum_dynamics import run_quantum_verification_suite
from verify_personal_dynamics import run_personal_verification_suite

def test_full_quantum_and_personal_suite():
    q_res = run_quantum_verification_suite()
    p_res = run_personal_verification_suite()
    assert q_res["all_assertions_passed"] is True
    assert p_res["all_assertions_passed"] is True
