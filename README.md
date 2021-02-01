# ICESat2_xarray

Work with ICESat-2 altimetry data in xarray and intake

### Goal:

- [x] Combine multiple hdf5 files into xarray dataset
- [x] Streamline data loading from local hdf5 files to xarray dataset via intake
- [x] Flexible data visualization defined by common parameters: RGT or Cycle 
- [ ] Streamline data loading from remote server to xarray dataset via intake 
- [ ] Data manipulation in xarray

### Resources
- [Zarr](https://zarr.readthedocs.io/en/stable/tutorial.html#)
- [Zarr vs HDF5](https://www.youtube.com/watch?v=-l445lCPTts)
- [xarray.open zarr](http://xarray.pydata.org/en/stable/generated/xarray.open_zarr.html)
- [Intake introduction](https://www.anaconda.com/blog/intake-taking-the-pain-out-of-data-access)
  - [YAML data format](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html)
  - [Demo: Use intake to read altimetry datasets](http://gallery.pangeo.io/repos/pangeo-gallery/physical-oceanography/02_along_track.html)
  - [Demo: Xarray + Intake](https://github.com/intake/intake-xarray/blob/master/examples/OPeNDAP.ipynb)
- [Icepyx](https://icepyx.readthedocs.io/en/latest/)
- [READ_ICESat-2 by Tyler Sutterley](https://github.com/tsutterley/read-ICESat-2)



