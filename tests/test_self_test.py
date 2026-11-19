from buzzinga.self_test import run_self_test


def test_self_test_passes_in_a_complete_installation(capsys):
    assert run_self_test() == 0
    assert "FAIL" not in capsys.readouterr().out
