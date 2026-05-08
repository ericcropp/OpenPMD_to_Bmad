import shutil

import OpenPMD_to_Bmad.Update_h5_file as pmd2bmad
import h5py
import pmd_beamphysics
from pmd_beamphysics import ParticleGroup
import numpy as np


shutil.copy('Files/test_new.h5', 'active_beam.h5')

pmd2bmad.OpenPMD_to_Bmad('active_beam.h5')
shutil.rmtree('active_beam.h5', ignore_errors=True)


# def all_keys(obj):
#     """
#     Returns a tuple of all keys in the h5 file.

#     Argument:
#     obj  -- h5 object: contents of an h5 file

#     See: https://stackoverflow.com/questions/59897093/
#     get-all-keys-and-its-hierarchy-in-h5-file-using-python-library-h5py
#     """
#     keys=(obj.name,)
#     if isinstance(obj, h5py.Group):
#         for key, value in obj.items():
#             if isinstance(value, h5py.Group):
#                 keys=keys+all_keys(value)
#             else:
#                 keys=keys+(value.name,)
#     return keys

# def particle_paths(h5, key="particlesPath"):
#     """
#     Uses the basePath and particlesPath to find where openPMD particles should be

#     """
#     basePath = h5.attrs["basePath"].decode("utf-8")
#     print('basePath: ' + basePath)
#     particlesPath = h5.attrs[key].decode("utf-8")
#     print('particlesPath: ' + particlesPath)

#     if "%T" not in basePath:
#         return [basePath + particlesPath]
#     path1, path2 = basePath.split("%T")
    
#     tlist = list(h5[path1])
#     print(tlist)
#     paths = [path1 + t + path2 + particlesPath for t in tlist]
#     print('paths: ' + paths)
#     return paths

# def get_particle_paths(f):
#     """
#     Get particle paths from an h5 file.
    
#     Argument:
#     f -- h5py object: h5 file to read
    
#     Returns:
#     pp -- list of particle paths
#     """
#     pp = particle_paths(f)
#     print(pp)
#     assert len(pp) == 1, f'Number of particle paths in file: {len(pp)}'
#     pp = pp[0]
#     # pp = pp.strip('.')
#     print(pp)
#     unique_strings = set()

#     keys = all_keys(f)
#     print(keys)
#     for key in keys:
#         print('key: ' + key)
#         if key.startswith(pp) and key != pp:
#             suffix = key[len(pp):].strip('/')
#             if suffix:
#                 first_part = suffix.split('/')[0]
#                 unique_strings.add(first_part)
#     print(unique_strings)
#     if 'position' not in unique_strings:
#         # then there is a species issue
#         pp = pp + '/' + list(unique_strings)[0]
#     return pp

# filename = 'active_beam.h5'
# with h5py.File(filename,'r') as f:
#     # pp = pmd_beamphysics.readers.particle_paths(f)
#     # assert len(pp) == 1, f'Number of particle paths in {filename}: {len(pp)}'


#     path = get_particle_paths(f) 

