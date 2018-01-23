import pytest
from py._path.local import LocalPath
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import process_fixation_output
import filecmp


def test_all1(tmpdir: LocalPath):
    """This will run a complete testrun with correctly formatted fake data.
    If it fails, actual data output will probably also be wrong

    :param tmpdir:
    :return:
    """
    process_fixation_output._safe_exit = False
    with pytest.raises(SystemExit) as e:
        process_fixation_output.main('test_cases/correct/', tmpdir.__str__())

    assert e.value.code == 0, "Exit code is not 0"
    assert filecmp.cmp('test_cases/correct/allACTFiles.txt', tmpdir.__str__() + '/allACTFiles.txt', False), \
        "Output files are not identical!"
    assert filecmp.cmp('test_cases/correct/allAGSFiles.txt', tmpdir.__str__() + '/allAGSFiles.txt', False), \
        "Output files are not identical!"


def test_malformed_agc(tmpdir: LocalPath):
    """The script has a special return code (4) for when it detects a malformed AGC file, this tests intentionally
    triggers it.

    Malformed AGC files are files that contain a line without the right amount of columns.

    :param tmpdir:
    :return:
    """
    process_fixation_output._safe_exit = False
    with pytest.raises(SystemExit) as e:
        process_fixation_output.main('test_cases/malformed_agc/', tmpdir.__str__())

    assert e.value.code == 4, "Exit code is not 4"


def test_malformed_ags(tmpdir: LocalPath):
    """The script has a special return code (2) for when it detects a malformed AGS file, this tests intentionally
    triggers it.

    Malformed AGS files are files that contain a line without the right amount of columns.

    :param tmpdir:
    :return:
    """
    process_fixation_output._safe_exit = False
    with pytest.raises(SystemExit) as e:
        process_fixation_output.main('test_cases/malformed_ags/', tmpdir.__str__())

    assert e.value.code == 2, "Exit code is not 2"


def test_run_with_invalid_path():
    """The script should return an exit code with the value 3 if a path was specified which Python has no access to.

    :return:
    """
    process_fixation_output._safe_exit = False
    with pytest.raises(SystemExit) as e:
        process_fixation_output.main('/')

    assert e.value.code == 3, "Exit code is not 3"
