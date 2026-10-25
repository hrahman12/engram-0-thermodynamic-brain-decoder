# Fast Cirq & Quantum dynamics tests
from verify_quantum_dynamics import run_quantum_verification_suite

def test_cirq_qhn_all_assertions():
    res = run_quantum_verification_suite()
    assert res["all_assertions_passed"] is True
