// news-image-20261119 entry (Node 22, standard library only): the image is the
// entry.png beside this file, and the program copies it to /output/entry.png.
// The image itself was composed by compose.py (in this repo) from six
// AI-generated, text-free panels, with every headline and label drawn
// programmatically so the text is pixel-perfect — see README.md.
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = new URL('./entry.png', import.meta.url);
const buf = readFileSync(src);
// A PNG starts with its 8-byte signature; refuse anything else.
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(PNG_SIG)) throw new Error('entry.png is not a PNG');
// The gate takes at most 1 MiB and 1024 by 1024 pixels.
if (buf.length > 1048576) throw new Error('entry.png is over 1 MiB');
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, 'entry.png'));
