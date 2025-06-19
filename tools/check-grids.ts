/// <reference path="../index.d.ts" />

import { join } from 'node:path';
import { exit } from 'node:process';
import { readFile, readdir } from 'node:fs/promises';
import proj4 from 'proj4';

const MAIN_DIR = join(import.meta.dirname, '..');
const GRIDS_DIR = join(MAIN_DIR, 'grids');

const allEPSGs: EPSG[] = JSON.parse(await readFile(join(import.meta.dirname, '..', 'all.json'), 'utf8'));

let exitCode = 0;

const EXISTING_GRIDS = await readdir(GRIDS_DIR, { withFileTypes: true }).then(arr => new Set(arr.map(x => x.name)));

for (const { code, proj4: proj4Def } of allEPSGs) {
    if (!proj4Def) continue;
    const name = `EPSG:${code}`;
    proj4.defs(name, proj4Def);

    const def = proj4.defs(name);
    if (!def.nadgrids) continue;
    if (EXISTING_GRIDS.has(def.nadgrids)) continue;

    exitCode = 1;
    console.log(`${name} requires grid "${def.nadgrids}", but it is missing.`);
}

exit(exitCode);
