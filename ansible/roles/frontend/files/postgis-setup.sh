#!/bin/sh

sudo -u postgres /usr/bin/psql btl <<END
CREATE EXTENSION postgis;
ALTER VIEW geography_columns OWNER TO btl;
ALTER VIEW geometry_columns  OWNER TO btl;
ALTER VIEW raster_columns    OWNER TO btl;
ALTER VIEW raster_overviews  OWNER TO btl;
ALTER TABLE spatial_ref_sys  OWNER TO btl;
END

touch /home/btl/postgis-setup-done
