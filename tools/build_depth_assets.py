#!/usr/bin/env python3
"""Rebuild the depth sprite sheet, velocity metadata and provisional motif
sequence used by the site's MoSeq section.

    python3 tools/build_depth_assets.py results_00.h5 --start 43000 --n 600

Writes assets/depth.png plus a JS snippet (DEPTH_META, MOTIFS) to stdout.
Replace the motif half with the moseq2-model labels when they are available:
the sequence is just one integer per frame over the same window.
"""
import argparse, json
import numpy as np, h5py
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2, whiten
from PIL import Image

FEATURES = ['velocity_2d_mm','height_ave_mm','length_mm','width_mm','area_mm','angle']
MIN_FRAMES = 9        # ~300 ms at 30 fps, the floor on a syllable
K = 12                # syllable identities


def clean(frames, masks):
    """Extraction mask removes speckle and wall reflections; the rest is
    residual salt-and-pepper and stray components."""
    out = np.zeros_like(frames, dtype=np.float32)
    for i in range(len(frames)):
        x = frames[i] * masks[i]
        x = ndi.median_filter(x, size=3)
        b = x > 1.5
        lab, n = ndi.label(b)
        if n > 1:
            sizes = ndi.sum(b, lab, range(1, n + 1))
            x = x * (lab == (np.argmax(sizes) + 1))
        out[i] = ndi.gaussian_filter(x, 0.5)
    return out


def motifs(scalars, n):
    ang = np.unwrap(scalars['angle'])
    F = np.column_stack([scalars['velocity_2d_mm'], scalars['height_ave_mm'],
                         scalars['length_mm'], scalars['width_mm'],
                         scalars['area_mm'], np.abs(np.gradient(ang))])
    F = np.array([ndi.gaussian_filter1d(F[:, j], 2.0) for j in range(F.shape[1])]).T
    Z = (F - F.mean(0)) / (F.std(0) + 1e-9)
    d = ndi.gaussian_filter1d(np.linalg.norm(np.gradient(Z, axis=0), axis=1), 1.5)
    bounds = [0]
    for i in np.argsort(-d):
        if all(abs(i - b) >= MIN_FRAMES for b in bounds) and abs(n - i) >= MIN_FRAMES:
            bounds.append(int(i))
        if len(bounds) >= 70:
            break
    bounds = sorted(set(bounds + [n]))
    segs = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    segs = [s for s in segs if s[1] - s[0] >= MIN_FRAMES]
    means = np.array([Z[a:b].mean(0) for a, b in segs])
    np.random.seed(7)
    _, lab = kmeans2(whiten(means), K, minit='++', seed=7)
    seq = np.zeros(n, int)
    for (a, b), l in zip(segs, lab):
        seq[a:b] = int(l)
    durs = [(b - a) / 30 * 1000 for a, b in segs]
    print(f'# {len(segs)} segments, median {int(np.median(durs))} ms, '
          f'range {int(min(durs))}-{int(max(durs))} ms')
    return seq


def main():
    p = argparse.ArgumentParser()
    p.add_argument('h5'); p.add_argument('--start', type=int, default=43000)
    p.add_argument('--n', type=int, default=600); p.add_argument('--cols', type=int, default=25)
    p.add_argument('--out', default='assets/depth.png')
    a = p.parse_args()
    S, N = a.start, a.n

    with h5py.File(a.h5, 'r') as f:
        frames = f['frames'][S:S + N].astype(np.float32)
        masks = f['frames_mask'][S:S + N]
        sc = {k: f['scalars'][k][S:S + N].astype(float) for k in FEATURES}
        fps = int(f['metadata/extraction/parameters/fps'][()])
        vel = f['scalars/velocity_2d_mm'][S:S + N].astype(float)

    out = clean(frames, masks)
    hi = float(np.percentile(out[out > 0], 99.5))
    q = (np.round(np.clip(out / hi, 0, 1) * 31) * (255 / 31)).astype(np.uint8)

    rows = int(np.ceil(N / a.cols))
    sheet = np.zeros((rows * 80, a.cols * 80), np.uint8)
    for i in range(N):
        r, c = divmod(i, a.cols)
        sheet[r * 80:(r + 1) * 80, c * 80:(c + 1) * 80] = q[i]
    Image.fromarray(sheet, 'L').quantize(colors=32, method=Image.MEDIANCUT) \
         .save(a.out, optimize=True)

    seq = motifs(sc, N)
    alphabet = '0123456789abcdefghij'
    print('const DEPTH_META=' + json.dumps({
        'n': N, 'cols': a.cols, 'rows': rows, 'tile': 80, 'fps': fps,
        'startFrame': S, 'velocity': [round(float(v), 1) for v in vel]},
        separators=(',', ':')) + ';')
    print('const MOTIFS="' + ''.join(alphabet[v] for v in seq) + '";')


if __name__ == '__main__':
    main()
