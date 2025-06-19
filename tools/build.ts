/// <reference path="../index.d.ts" />

import { join } from 'node:path';
import { mkdir, cp, writeFile, readFile } from 'node:fs/promises';

const OUT_DIR = join(import.meta.dirname, '..');

const allCodes: EPSG[] = JSON.parse(await readFile(join(import.meta.dirname, '..', 'all.json'), 'utf8'));

await mkdir(join(OUT_DIR, 'codes'), { recursive: true });

await writeFile(
    join(OUT_DIR, 'all.js'),
    'export default ' + JSON.stringify(Object.fromEntries(allCodes.map(e => [e.code, e]))),
    'utf8'
);
console.log('Wrote all.js');

const promises = allCodes
    .map(e => {
        const fileName = join(OUT_DIR, 'codes', `${e.code}.js`);

        return [
            cp(join(import.meta.dirname!, '..', 'single.d.ts'), join(OUT_DIR, 'codes', `${e.code}.d.ts`)),
            writeFile(fileName, 'export default ' + JSON.stringify(e), 'utf8')
        ];
    })
    .flat();

await Promise.all(promises);
console.log('Wrote all codes to codes/');
