vic_utils
=========

Pre/post processing utilities for the Variable Infiltration Capacity (VIC) hydrological model.

#ISSUES

- Reconfigure plot output (support for shaded regions, decide on time scale).

- Integrate with WECC portfolio projections. 

- Visual disparity between observed and modeled solar irradiance in Colorado Basin.

- Bad correlations for several validation stations. Possibly increase routing model resolution. 

- Several recirculating plants in 'wauna' basin for which there is no water temperature output.

#Sources of routing model error

- Larger stream in same grid cell as smaller grid cell (some in california).
- Misalignment of river and grid cell.
- Nearby dam.
- USGS gauges on snake river reporting strange values.
