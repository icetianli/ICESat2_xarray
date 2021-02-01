"""
Data format conversion
"""

import itertools
import numpy as np
import os
import fnmatch
import h5py
import xarray as xr
import h5netcdf

def file_list(folder_dir, endswith='*.h5'):
    """
    get all file directories in a folder
    """
    file_path_list = []
    for dirpath, dirs, files in os.walk(folder_dir): # loop through all subdirs      
        for filename in fnmatch.filter(files, endswith):          
            file_path_list.append(os.path.join(dirpath, filename))
    return file_path_list

def icesat2_hdf5_to_xarray(fid, laser, chunksize, h5groups = ['/land_ice_segments', '/land_ice_segments/geophysical']):
    """
    Write different subgroups of ICESat-2 hdf5 datafiles of one single beam into a xarray dataset
    The coordinates of xarray are: segment_id, laser, rgt, cycle_number
    parameters:
        fid: hdf5 file path
        laser: ground track name
        chunksize: dask chunk size
        h5group: data groups of interest from hdf5 file, defaults are '/land_ice_segments' & '/land_ice_segments/geophysical'
    """
    try:
        # subgroup
        group1, group2, group3 = ['orbit_info', laser + h5groups[0], laser + h5groups[1]]
        # orbit_info
        group1_ds = xr.open_dataset(fid, group=group1, engine='h5netcdf', chunks=chunksize)
        # land_ice_segments
        group2_ds = xr.open_dataset(fid, group=group2, engine='h5netcdf', chunks=chunksize)
        # geophysical
        group3_ds = xr.open_dataset(fid, group=group3, engine='h5netcdf', chunks=chunksize).assign_coords({"delta_time": group2_ds.delta_time})
        # combine all subgroups
        combined_ds = xr.combine_by_coords([group2_ds, group3_ds], combine_attrs='override').swap_dims({'delta_time': 'segment_id'}).reset_coords(['delta_time','latitude','longitude'])
        combined_ds = combined_ds.expand_dims({'laser':[laser], 'rgt':[group1_ds.rgt.values[0]], 'cycle_number':[group1_ds.cycle_number.values[0]]})
    except:
        return None
    return combined_ds


#-- PURPOSE: encoder for copying the file attributes
def attributes_encoder(attr):
    """
    Custom encoder for copying file attributes in Python 3
    
    Reference: https://github.com/tsutterley/read-ICESat-2/blob/master/scripts/nsidc_icesat2_zarr.py
    Author: Tyler Sutterley
    """
    if isinstance(attr, (bytes, bytearray)):
        return attr.decode('utf-8')
    if isinstance(attr, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32,
        np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(attr)
    elif isinstance(attr, (np.float_, np.float16, np.float32, np.float64)):
        return float(attr)
    elif isinstance(attr, (np.ndarray)):
        if not isinstance(attr[0], (object)):
            return attr.tolist()
    elif isinstance(attr, (np.bool_)):
        return bool(attr)
    elif isinstance(attr, (np.void)):
        return None
    else:
        return attr
    
#-- PURPOSE: Copy a named variable from the HDF5 file to the zarr file
def copy_from_HDF5(source, dest, name, **create_kws):
    """
    Copy a named variable from the `source` HDF5 into the `dest` zarr
    
    Reference: https://github.com/tsutterley/read-ICESat-2/blob/master/scripts/nsidc_icesat2_zarr.py
    Author: Tyler Sutterley
    """
    if hasattr(source, 'shape'):
        #-- copy a dataset/array
        if dest is not None and name in dest:
            raise CopyError('an object {!r} already exists in destination '
                '{!r}'.format(name, dest.name))
        #-- setup creation keyword arguments
        kws = create_kws.copy()
        #-- setup chunks option, preserve by default
        kws.setdefault('chunks', source.chunks)
        #-- setup compression options
        #-- from h5py to zarr: use zarr default compression options
        kws.setdefault('fill_value', source.fillvalue)
        #-- create new dataset in destination
        ds=dest.create_dataset(name,shape=source.shape,dtype=source.dtype,**kws)
        #-- copy data going chunk by chunk to avoid loading in entirety
        shape = ds.shape
        chunks = ds.chunks
        chunk_offsets = [range(0, s, c) for s, c in zip(shape, chunks)]
        for offset in itertools.product(*chunk_offsets):
            sel = tuple(slice(o, min(s, o + c)) for o, s, c in
                zip(offset, shape, chunks))
            ds[sel] = source[sel]
        #-- copy attributes
        attrs = {key:attributes_encoder(source.attrs[key]) for key in
            source.attrs.keys() if attributes_encoder(source.attrs[key])}
        ds.attrs.update(attrs)
    else:
        #-- copy a group
        if (dest is not None and name in dest and hasattr(dest[name], 'shape')):
            raise CopyError('an array {!r} already exists in destination '
                '{!r}'.format(name, dest.name))
        #-- require group in destination
        grp = dest.require_group(name)
        #-- copy attributes
        attrs = {key:attributes_encoder(source.attrs[key]) for key in
            source.attrs.keys() if attributes_encoder(source.attrs[key])}
        grp.attrs.update(attrs)
        #-- recursively copy from source
        for k in source.keys():
            copy_from_HDF5(source[k], grp, name=k)