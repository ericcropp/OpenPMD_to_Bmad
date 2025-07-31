import os
import h5py
import pmd_beamphysics
import numpy as np
from pmd_beamphysics import ParticleGroup


def get_particle_paths(f):
    """
    Get particle paths from an h5 file.
    
    Argument:
    f -- h5py object: h5 file to read
    
    Returns:
    pp -- list of particle paths
    """
    pp = pmd_beamphysics.readers.particle_paths(f)
    assert len(pp) == 1, f'Number of particle paths in file: {len(pp)}'
    pp = pp[0]
    unique_strings = set()

    keys = all_keys(f)
    for key in keys:
        if key.startswith(pp) and key != pp:
            suffix = key[len(pp):].strip('/')
            if suffix:
                first_part = suffix.split('/')[0]
                unique_strings.add(first_part)
    if 'position' not in unique_strings:
        # then there is a species issue
        pp = pp + '/' + list(unique_strings)[0]
    return pp

   

def inspect_bmad_h5(filename):
    """
    Looks inside a bmad h5 file.
    Returns a dictionary ("x","y","Px","Py,"Pz","time","timeOffset","totalMomentum").


    Argument:
    filename -- string: full path to file to be inspected

    """
    P={}
    with h5py.File(filename,'r') as f:
        # pp = pmd_beamphysics.readers.particle_paths(f)
        # assert len(pp) == 1, f'Number of particle paths in {filename}: {len(pp)}'


        path = get_particle_paths(f) 

        
        print(path)

        P['x'] = f[path]['position']['x'][()]
        P['y'] = f[path]['position']['y'][()]
        # P['z']=f['data']['00001']['particles']['position']['z'][()]
        P['Px'] = f[path]['momentum']['x'][()]
        P['Py'] = f[path]['momentum']['y'][()]
        P['Pz'] = f[path]['momentum']['z'][()]
        P['time'] = f[path]['time'][()]
        P['timeOffset'] = f[path]['timeOffset'][()]
        # P['totalMomentum']=f[pp[0]]['totalMomentum'][()]   
    return P

def all_keys(obj):
    """
    Returns a tuple of all keys in the h5 file.

    Argument:
    obj  -- h5 object: contents of an h5 file

    See: https://stackoverflow.com/questions/59897093/
    get-all-keys-and-its-hierarchy-in-h5-file-using-python-library-h5py
    """
    keys=(obj.name,)
    if isinstance(obj, h5py.Group):
        for key, value in obj.items():
            if isinstance(value, h5py.Group):
                keys=keys+all_keys(value)
            else:
                keys=keys+(value.name,)
    return keys

def all_attr_keys(keys, obj):
    """
    Returns a dictionary (keys, metadata) of metadata attributes.

    
    Argument:
    obj -- h5 object: contents of an h5 file
    keys -- tuple of keys

    """
    attr_keys={}
    for key in keys:
        attr_keys[key]=list(obj[key].attrs.keys())
    return attr_keys

def search_list_partial(l,searchterm):
    """
    See if a search term is present in a list of lists
    
    Returns bool -- True if searchterm is in l.

    
    Argument:
    l -- list of list of terms
    searchterm -- string: term to search for in list of lists

    """
    x=[True for v in l if searchterm in v]
    if True in x:
        y=True
    else:
        y=False
    return y

def OpenPMD_to_Bmad(filename, tOffset=None):
    """
    Convert from OpenPMD to Bmad h5 format after checking 
    to make sure it is not in Bmad format first

    Edits h5 file, but does not return any variables

    Argument:
    filename -- string: full path to file to be changed
    tOffset -- 1-D np.array: timeOffset from previous bmad file

    """
    with h5py.File(filename, 'r+') as f:  # Open h5 file for writing
        # Get all keys and attribute keys in the file
        keys = all_keys(f)
        attr_keys = all_attr_keys(keys, f)
        # Flatten all attribute keys into a single list
        list_attrs = [k for i in attr_keys.values() for k in i]
        keys = list(keys)
        # Check if the file is in OpenPMD format by searching for 'openPMD' in attributes
        test_openPMD = search_list_partial(list_attrs, 'openPMD')

        if test_openPMD == True:
            # Check if the file already has a timeOffset group
            test_offset = search_list_partial(keys, 'timeOffset')
            if test_offset == True:
                raise ValueError('openPMD file already includes timeOffset!')
            else:
                # Get the particle path using helper function
                pp = get_particle_paths(f)
                print(pp)
                # Load particle data using pmd_beamphysics
                data = pmd_beamphysics.particles.load_bunch_data(f[pp])
                # Filter for particles with status == 1 (alive)
                idx = np.array(data['status']) == 1
                # If a time offset is provided, validate it
                if tOffset is not None:
                    tOffset = np.array(tOffset)
                    assert len(np.shape(tOffset)) == 1, "tOffset not valid"
                    assert len(tOffset) == len(np.array(f[pp]['time'])), "tOffset has wrong length"
                # If no offset is provided, compute it as the weighted average time of alive particles
                if tOffset is None:
                    weights = data['weight']
                    print(pp)
                    # If there is no time data, try to drift to z=0 and retry
                    if len(f[pp + '/time']) == 0:
                        if os.path.isfile('drifted_' + filename):
                            raise ValueError("No time data exists, but drift_to_z() does not resolve the issue")
                        else:
                            P_1 = ParticleGroup(filename)
                            P_1.drift_to_z()
                            P_1.write('drifted_' + filename)
                            OpenPMD_to_Bmad('drifted_' + filename)
                            os.rename(('drifted_' + filename), filename)
                            return
                    # Compute reference time as weighted average
                    tref = np.average(np.array(f[pp]['time'])[idx], weights=weights[idx])
                else:
                    # Use provided offset
                    tref = tOffset

                # Subtract reference time from all times
                t1 = np.array(f[pp]['time']) - tref

                # Write timeOffset dataset and copy attributes from 'time'
                f[pp]['timeOffset'] = np.zeros(len(t1)) + tref
                for key in f[pp]['time'].attrs.keys():
                    f[pp]['timeOffset'].attrs[key] = f[pp]['time'].attrs[key]

                # Update 'time' dataset with new values
                f[pp]['time'][...] = t1

        else:
            raise ValueError('Not an OpenPMD File!')
            
# Get time offset and convert h5 file from bmad to OpenPMD  
# 
# 
def get_species(f,pp):
    """
    Get species from an h5 ParticleGroup file.
    
    Argument:
    f -- h5py object: h5 file to read
    pp -- particle path
    
    Returns:
    pp -- string: particle path with species appended
    """
    unique_strings = set()
    keys = all_keys(f)
    print(keys)
    
    if '//' in pp:
        pp = pp.replace('//', '/')
    print(pp)
    for key in keys:
        if key.startswith(pp) and key != pp:
            suffix = key[len(pp):].strip('/')
            if suffix:
                first_part = suffix.split('/')[0]
                unique_strings.add(first_part)
    print(unique_strings)
    species = sorted(unique_strings)
    return species[0] if len(species) == 1 else None
    

def bmad_to_OpenPMD(filename):
    """
    Get time offset and convert h5 file from bmad to OpenPMD      
    
    Edits h5 file, returns a dictionary as specified in inspect_bmad_h5

    Argument:
    filename -- string: full path to file to be read and changed
    
    """
    # Inspect the bmad h5 file and get particle data dictionary
    Pdict = inspect_bmad_h5(filename)
    try:
        # Try to load the file as a ParticleGroup (OpenPMD format)
        P = ParticleGroup(filename)
    except:
        # If loading fails, assume it's in newer bmad/ParticleGroup format and needs conversion
        with h5py.File(filename, "r+") as f:
            # Get particle paths
            pp = pmd_beamphysics.readers.particle_paths(f)
            assert len(pp) == 1, f'Number of particle paths in {filename}: {len(pp)}'
            pp = pp[0]
            # Get all keys in the file
            ak = all_keys(f)
            # Find all leaf paths (datasets, not groups)
            leaf_paths = [
                p for p in ak
                if not any(other != p and other.startswith(p.rstrip("/") + "/") for other in ak)
            ]

            print(leaf_paths)
            # Get species name from the file
            species = get_species(f, pp)
            print(f"Species: {species}")
            print(type(species))
            print(species.encode("utf-8"))

            # Find the path to position/x dataset
            matches = [p for p in leaf_paths if '/position/x' in p]
            assert len(matches) == 1, f'Number of position/x paths in {filename}: {len(matches)}'
            n = f[matches[0]].shape[0]  # Number of particles
            # Find non-leaf paths (groups)
            non_leaf_paths = set(ak) - set(leaf_paths)
            # Find the group corresponding to the species
            matches = [p for p in list(non_leaf_paths) if p.endswith(species)]
            assert len(matches) == 1, f'Number of species paths in {filename}: {len(matches)}'
            obj = f[matches[0]]
            # Get charge and unit attributes
            tc = obj.attrs.get('chargeLive', None)
            u = obj.attrs.get('chargeUnitSI', None)

            # Move datasets out of the species group and update attributes
            for key in leaf_paths:
                if species in key:
                    # Remove species from the path
                    newpath = key.replace('/'+species,"")
                    attrs = dict(f[key].attrs) 
                    print(attrs)
                    print(f"Moving {key} to {newpath}")
                    f.move(key, newpath)
                    # Restore attributes and set speciesType
                    for k, v in attrs.items():
                        f[newpath].attrs[k] = v
                    obj = f[newpath]
                    if 'speciesType' in obj.attrs:
                        del obj.attrs['speciesType']
                    if isinstance(species, str):
                        obj.attrs['speciesType'] = np.string_(species)
                    else:
                        obj.attrs['speciesType'] = species
                else:
                    # For other groups, just update speciesType
                    obj = f[key]
                    if 'speciesType' in obj.attrs:
                        del obj.attrs['speciesType']    
                    if isinstance(species, str):
                        obj.attrs['speciesType'] = np.string_(species)
                    else:
                        obj.attrs['speciesType'] = species
            
            # Update attributes for all non-leaf (group) paths
            for key in non_leaf_paths:
                print(key)
                obj = f[key]
                if 'speciesType' in obj.attrs:
                    del obj.attrs['speciesType']
                if isinstance(species, str):
                    obj.attrs['speciesType'] = np.string_(species)
                else:
                    obj.attrs['speciesType'] = species
                if 'numParticles' in obj.attrs:
                    del obj.attrs['numParticles']
                if 'totalCharge' in obj.attrs:
                    del obj.attrs['totalCharge']
                obj.attrs['numParticles'] = n
                obj.attrs['totalCharge'] = tc 
                if 'chargeUnitSI' in obj.attrs:
                    del obj.attrs['chargeUnitSI']
                obj.attrs['chargeUnitSI'] = u 

                print(dict(obj.attrs))

        # Now reload as ParticleGroup and drift to z=0
        P = ParticleGroup(filename)
    P.drift_to_z()
    P.write(filename)
    return Pdict