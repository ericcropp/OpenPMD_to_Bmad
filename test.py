import pytest
# import Update_h5_file
import numpy as np
import h5py
from pmd_beamphysics import ParticleGroup
import shutil
from Update_h5_file import *
import os

temp_loc='./temp'
unedited_loc='./Files'


example_not_OpenPMD='Not_OpenPMD.h5'
example_bmad='ideal_beam.h5'

#copy files to new loc
temp_loc='./temp/'
unedited_loc='./Files/'
example_not_OpenPMD='Not_OpenPMD.h5'
example_bmad='ideal_beam.h5'



    
# def test_tOffset_exists(tOffset_exists):
        # tOffset_exists
def test_tOffset_exists():
    # temp_loc,unedited_loc,example_not_OpenPMD,example_bmad=def_funcs
    
    try: os.remove(temp_loc+example_bmad)
    except: pass

    shutil.copyfile(unedited_loc+example_bmad, temp_loc+example_bmad)
    # Test that if a bmad file is given to the function, an exception is raised
    with pytest.raises(ValueError):
        OpenPMD_to_Bmad(temp_loc+example_bmad)
        
        
def test_not_OpenPMD():
    try: os.remove(temp_loc+example_not_OpenPMD)
    except: pass
    shutil.copyfile(unedited_loc+example_not_OpenPMD, temp_loc+example_not_OpenPMD)
    
    # Test that if a non-OpenPMD file is passed, an exception is raised
    with pytest.raises(ValueError):
        OpenPMD_to_Bmad(temp_loc+example_not_OpenPMD)
        
def test_tOffset_wrong_length():
    # Test if timeOffset has wrong length
    try: os.remove(temp_loc+example_bmad)
    except: pass
    shutil.copyfile(unedited_loc+example_bmad, temp_loc+example_bmad)
    P=inspect_bmad_h5(temp_loc+example_bmad)
    tOffset=np.array(P['timeOffset'])
    tOffset=np.append(tOffset,np.zeros(2))
    with pytest.raises(ValueError):
        OpenPMD_to_Bmad(temp_loc+example_bmad,tOffset)
        
        
def test_tOffset_wrong_shape():
    # Test if timeOffset has wrong shape
    try: os.remove(temp_loc+example_bmad)
    except: pass
    shutil.copyfile(unedited_loc+example_bmad, temp_loc+example_bmad)
    P=inspect_bmad_h5(temp_loc+example_bmad)
    tOffset=np.array(P['timeOffset'])
    test=np.zeros([len(tOffset),2])
    with pytest.raises(ValueError):
        OpenPMD_to_Bmad(temp_loc+example_bmad,test)
        

        
def test_output():
    #Test output
    try: os.remove(temp_loc+example_bmad)
    except: pass
    shutil.copyfile(unedited_loc+example_bmad, temp_loc+example_bmad)
    Pdict=bmad_to_OpenPMD(temp_loc+example_bmad)
    
    OpenPMD_to_Bmad(temp_loc+example_bmad,Pdict['timeOffset'])
    
    P2=ParticleGroup(temp_loc+example_bmad)
    
    def MSE(x1,x2):
        return np.mean((x1-x2)**2)
    
    assert MSE(P2['x'],P['x'])<np.std(P['x'])*1e-6
    assert MSE(P2['y'],P['y'])<np.std(P['y'])*1e-6
    assert MSE(P2['t'],P['t'])<np.std(P['t'])*1e-6
    assert MSE(P2['px'],P['px'])<np.std(P['px'])*1e-6
    assert MSE(P2['py'],P['py'])<np.std(P['py'])*1e-6
    assert MSE(P2['pz'],P['pz'])<np.std(P['pz'])*1e-6
    
    
    
    
    