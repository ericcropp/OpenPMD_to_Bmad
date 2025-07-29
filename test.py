import pytest
import numpy as np
from pmd_beamphysics import ParticleGroup
import shutil
import Update_h5_file as pmd2bmad
import os

#copy files to new loc
temp_loc='./temp/'
unedited_loc='./Files/'
example_not_OpenPMD='Not_OpenPMD.h5'
example_bmad='bmad_out.h5'
PGs = ['New_PG.h5','Old_PG.h5']


    
# def test_tOffset_exists(tOffset_exists):
        # tOffset_exists


def test_PGs():
    for PG in PGs:
        try: os.remove(temp_loc + PG)
        except: pass
        shutil.copyfile(unedited_loc + PG, temp_loc + PG)

        #Test that this doesn't give an error
        pmd2bmad.OpenPMD_to_Bmad(temp_loc + example_bmad)


def test_tOffset_exists():
    # temp_loc,unedited_loc,example_not_OpenPMD,example_bmad=def_funcs

    try: os.remove(temp_loc + example_bmad)
    except: pass

    shutil.copyfile(unedited_loc + example_bmad, temp_loc + example_bmad)
    # Test that if a bmad file is given to the function, an exception is raised
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc + example_bmad)


def test_not_OpenPMD():
    try: os.remove(temp_loc + example_not_OpenPMD)
    except: pass
    shutil.copyfile(unedited_loc + example_not_OpenPMD, temp_loc + example_not_OpenPMD)

    # Test that if a non-OpenPMD file is passed, an exception is raised
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc + example_not_OpenPMD)

def test_tOffset_wrong_length():
    # Test if timeOffset has wrong length
    try: os.remove(temp_loc + example_bmad)
    except: pass
    shutil.copyfile(unedited_loc + example_bmad, temp_loc + example_bmad)
    P = pmd2bmad.inspect_bmad_h5(temp_loc + example_bmad)
    tOffset = np.array(P['timeOffset'])
    tOffset = np.append(tOffset, np.zeros(2))
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc + example_bmad, tOffset)

        
def test_tOffset_wrong_shape():
    # Test if timeOffset has wrong shape
    try: os.remove(temp_loc + example_bmad)
    except: pass
    shutil.copyfile(unedited_loc + example_bmad, temp_loc + example_bmad)
    P = pmd2bmad.inspect_bmad_h5(temp_loc + example_bmad)
    tOffset = np.array(P['timeOffset'])
    test = np.zeros([len(tOffset), 2])
    with pytest.raises(ValueError):
        pmd2bmad.OpenPMD_to_Bmad(temp_loc + example_bmad, test)


        
def test_output():
    #Test output
    try: os.remove(temp_loc + example_bmad)
    except: pass
    shutil.copyfile(unedited_loc + example_bmad, temp_loc + example_bmad)
    Pdict = pmd2bmad.bmad_to_OpenPMD(temp_loc + example_bmad)

    pmd2bmad.OpenPMD_to_Bmad(temp_loc + example_bmad, Pdict['timeOffset'])

    P2 = pmd2bmad.inspect_bmad_h5(temp_loc + example_bmad)

    def MSE(x1, x2):
        return np.mean((x1 - x2) ** 2)

    assert MSE(P2['x'], Pdict['x']) < np.std(P2['x']) * 1e-6
    assert MSE(P2['y'], Pdict['y']) < np.std(P2['y']) * 1e-6
    assert MSE(P2['time'], Pdict['time']) < np.std(P2['time']) * 1e-6
    assert MSE(P2['Px'], Pdict['Px']) < np.std(P2['Px']) * 1e-6
    assert MSE(P2['Py'], Pdict['Py']) < np.std(P2['Py']) * 1e-6
    assert MSE(P2['Pz'], Pdict['Pz']) < np.std(P2['Pz']) * 1e-6
    assert MSE(P2['timeOffset'], Pdict['timeOffset']) < np.mean(P2['timeOffset']) * 1e-6
    
    
    
    