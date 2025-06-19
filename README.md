# `epsg-index-2`

_A spiritual successor to
[`epsg-index`](https://github.com/derhuerst/epsg-index)_

`epsg-index-2` includes a _up-to-date\*_ list of all known EPSGs definitions as well as the nadgrid files, which are referenced by at least one EPSG definitions.

## Installing

```sh
npm install epsg-index-2
```

## Usage

```ts
// import a single EPSG definition:
import EPSG_4326 from 'epsg-index-2/4326';

console.log(EPSG_4326);

// or import all EPSGs at once:
import ALL_EPSGS from 'epsg-index-2'; // WARNING: this is over 5MB (or 500kB gzipped)

console.log(ALL_EPSGS[4326]);
```

```js
{
  code: 3857,
  name: 'WGS 84 / Pseudo-Mercator',
  wkt: 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]',
  proj4: '+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs +type=crs',
  bbox: [ -180, -85.06, 180, 85.06 ],
  unit: 'metre',
  area: 'World between 85.06°S and 85.06°N.',
  accuracy: null,
  deprecated: false
}
```

_(check the [`index.d.ts`](./index.d.ts) for exact types)_

## Using Grids

Some EPSG definitions reference nadgrids files. For example `EPSG:3396`
references `de_adv_BETA2007.tif` like this:

```
+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=bessel +nadgrids=de_adv_BETA2007.tif +units=m +no_defs +type=crs
```

If you want to use the projection with something like
[`proj4js`](https://github.com/proj4js/proj4js), you may need to load these grid
files.

You can load grids directly from this module's `grids/` subdirectory:

```ts
import proj4 from 'proj4';
import { fromUrl } from 'geotiff';

import EPSG_3396 from 'epsg-index-2/3396';
// WARNING: ?url import only works with Vite, but other bundlers may have similar features
// (see https://vite.dev/guide/assets#explicit-url-imports)
import BETA2007_URL from 'epsg-index-2/grids/de_adv_BETA2007.tif?url';

const tiff = await fromUrl(BETA2007_URL);
await proj4.nadgrid('de_adv_BETA2007.tif', tiff).ready;

proj4.defs('EPSG:3396', EPSG_3396.proj4);
```
