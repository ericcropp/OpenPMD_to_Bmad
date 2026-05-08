import pytest
import numpy as np
from pathlib import Path
from pmd_beamphysics import ParticleGroup
import shutil
import OpenPMD_to_Bmad.Update_h5_file as pmd2bmad

#copy files to new loc
temp_loc = Path('temp')
unedited_loc = Path('Files')
example_not_OpenPMD = 'Not_OpenPMD.h5'
example_bmad = 'bmad_out.h5'
PGs = ['test_new.h5', 'Old_PG.h5']


# def test_tOffset_exists(tOffset_exists):
        # tOffset_exists


def test_PGs():
    for PG in PGs:
        (temp_loc / PG).unlink(missing_ok=True)
        shutil.copyfile(unedited_loc / PG, temp_loc / PG)

        #Test that this doesn't give an error
        pmd2bmad.OpenPMD_to_Bmad(temp_loc / PG)


def test_tOffset_exists():
    (temp_loc / example_bmad).unlink(missing_ok=True)

    shutil.copyfile(unedited_loc / example_bmad, temp_loc / example_bmad)
    # Test that if a bmad file is given to the function, an exception is raised
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc / example_bmad)


def test_not_OpenPMD():
    (temp_loc / example_not_OpenPMD).unlink(missing_ok=True)
    shutil.copyfile(unedited_loc / example_not_OpenPMD, temp_loc / example_not_OpenPMD)

    # Test that if a non-OpenPMD file is passed, an exception is raised
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc / example_not_OpenPMD)

def test_tOffset_wrong_length():
    # Test if timeOffset has wrong length
    (temp_loc / example_bmad).unlink(missing_ok=True)
    shutil.copyfile(unedited_loc / example_bmad, temp_loc / example_bmad)
    P = pmd2bmad.inspect_bmad_h5(temp_loc / example_bmad)
    tOffset = np.array(P['timeOffset'])
    tOffset = np.append(tOffset, np.zeros(2))
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc / example_bmad, tOffset)


def test_tOffset_wrong_shape():
    # Test if timeOffset has wrong shape
    (temp_loc / example_bmad).unlink(missing_ok=True)
    shutil.copyfile(unedited_loc / example_bmad, temp_loc / example_bmad)
    P = pmd2bmad.inspect_bmad_h5(temp_loc / example_bmad)
    tOffset = np.array(P['timeOffset'])
    test = np.zeros([len(tOffset), 2])
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc / example_bmad, test)


def test_output():
    #Test output
    (temp_loc / example_bmad).unlink(missing_ok=True)
    shutil.copyfile(unedited_loc / example_bmad, temp_loc / example_bmad)
    Pdict = pmd2bmad.bmad_to_OpenPMD(temp_loc / example_bmad)

    pmd2bmad.OpenPMD_to_Bmad(temp_loc / example_bmad, Pdict['timeOffset'])

    P2 = pmd2bmad.inspect_bmad_h5(temp_loc / example_bmad)

    def MSE(x1, x2):
        return np.mean((x1 - x2) ** 2)

    assert MSE(P2['x'], Pdict['x']) < np.std(P2['x']) * 1e-6
    assert MSE(P2['y'], Pdict['y']) < np.std(P2['y']) * 1e-6
    assert MSE(P2['time'], Pdict['time']) < np.std(P2['time']) * 1e-6
    assert MSE(P2['Px'], Pdict['Px']) < np.std(P2['Px']) * 1e-6
    assert MSE(P2['Py'], Pdict['Py']) < np.std(P2['Py']) * 1e-6
    assert MSE(P2['Pz'], Pdict['Pz']) < np.std(P2['Pz']) * 1e-6
    assert MSE(P2['timeOffset'], Pdict['timeOffset']) < np.mean(P2['timeOffset']) * 1e-6


# --- Regression tests ---

def test_path_objects_accepted():
    """Regression: all public functions must accept pathlib.Path, not just str."""
    (temp_loc / example_bmad).unlink(missing_ok=True)
    shutil.copyfile(unedited_loc / example_bmad, temp_loc / example_bmad)

    # inspect_bmad_h5 with Path
    P = pmd2bmad.inspect_bmad_h5(temp_loc / example_bmad)
    assert isinstance(P, dict)

    # bmad_to_OpenPMD with Path
    (temp_loc / example_bmad).unlink(missing_ok=True)
    shutil.copyfile(unedited_loc / example_bmad, temp_loc / example_bmad)
    Pdict = pmd2bmad.bmad_to_OpenPMD(temp_loc / example_bmad)
    assert isinstance(Pdict, dict)

    # OpenPMD_to_Bmad with Path (uses already-converted file from bmad_to_OpenPMD)
    pmd2bmad.OpenPMD_to_Bmad(temp_loc / example_bmad, Pdict['timeOffset'])


def test_drifted_file_stays_in_same_directory(tmp_path):
    """Regression: drifted_ temp file must be placed next to the input file,
    not constructed by prepending 'drifted_' to the full path string."""
    # This test verifies no stray file appears in cwd when input is in a subdir.
    # We check by asserting that after the call, no file beginning with 'drifted_'
    # was created in the cwd (which the old string-concat bug would have caused).
    subdir = tmp_path / 'subdir'
    subdir.mkdir()
    src = Path('Files') / 'test_new.h5'
    dst = subdir / 'test_new.h5'
    shutil.copyfile(src, dst)

    cwd = Path.cwd()
    stray_before = set(cwd.glob('drifted_*'))

    pmd2bmad.OpenPMD_to_Bmad(dst)

    stray_after = set(cwd.glob('drifted_*'))
    new_strays = stray_after - stray_before
    assert not new_strays, (
        f"drifted_ temp file(s) leaked into cwd: {new_strays}. "
        "Path construction is still broken."
    )
