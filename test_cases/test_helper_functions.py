#!/usr/bin/env python3
import pytest
from py._path.local import LocalPath
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import process_fixation_output as p

def test_exists_in_path():
    """exists_in_path should be able to find commands in path.

    We check by asking it if the ls command is available, as this should be present on any POSIX compliant thingy.

    When running on Windows we return true, as it will fail otherwise.
    """

    assert p.exists_in_path('ls') or sys.platform == "win32", "ls was not found in path, but should've been"


def test_ask_true():
    """The ask function should return true when 'y' is provided as user input"""
    p.raw_input = lambda x: 'y'

    assert p.ask('Test'), "Ask should've returned True, but didn't"


def test_ask_true_default():
    """The ask function should return true when arbitrary text is provided as user input"""
    p.raw_input = lambda x: 'yawdwadawfd'

    assert p.ask('Test'), "Ask should've returned True, but didn't"


def test_ask_false():
    """The ask function should return false when 'n' is provided as user input"""
    p.raw_input = lambda x: 'n'

    assert not p.ask('Test'), "Ask should've returned False, but didn't"


def test_check_path_writable_excecutable_true(tmpdir: LocalPath):
    """The check_path_writable_excecutable function should return true for the temp dir"""
    assert p.check_path_writable_executable(tmpdir.__str__())


def test_check_path_writable_excecutable_false():
    """The check_path_writable_excecutable function should return false for the root dir"""
    assert not p.check_path_writable_executable(os.path.abspath(os.sep))


def test_safe_exit_0():
    """safe_exit should exit the programme with a default exit code of 0"""
    p.raw_input = lambda x: ''
    with pytest.raises(SystemExit) as e:
        p.safe_exit()
    assert e.value.code == 0, "Exit code is not 0"


def test_safe_exit_1():
    """safe_exit should exit the programme with the provided exit code of 1"""
    p.raw_input = lambda x: ''
    with pytest.raises(SystemExit) as e:
        p.safe_exit(1)
    assert e.value.code == 1, "Exit code is not 0"


def test_safe_exit_1030():
    """safe_exit should exit the programme with the provided exit code of 1030"""
    p.raw_input = lambda x: ''
    with pytest.raises(SystemExit) as e:
        p.safe_exit(1030)
    assert e.value.code == 1030, "Exit code is not 0"


def test_check_number_columns_in_row_0():
    """check_number_columns_in_row should return true with a list of 5 items and a supposed length of 5"""
    row = ['a', 'b', 'c', 'd', 'e']
    assert p.check_number_columns_in_row(row, 5, False)


def test_check_number_columns_in_row_2():
    """check_number_columns_in_row should return false with a list of 5 items and a supposed length of 4"""
    row = ['a', 'b', 'c', 'd', 'e']
    assert not p.check_number_columns_in_row(row, 4, False)


def test_check_number_columns_in_row_3():
    """check_number_columns_in_row should return true with a list of 5 items and a supposed length of 5 and
    hard_fail true"""
    row = ['a', 'b', 'c', 'd', 'e']
    assert p.check_number_columns_in_row(row, 5, True)


def test_check_number_columns_in_row_4():
    """check_number_columns_in_row should exit the programme with a list of 5 items and a supposed length of
    4 and hard_fail true"""
    row = ['a', 'b', 'c', 'd', 'e']
    with pytest.raises(SystemExit):
        p.check_number_columns_in_row(row, 4, True)
