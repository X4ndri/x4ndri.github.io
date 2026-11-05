# qader.dev revamp — design spec

Date: 2026-11-04
Status: awaiting review
Branch target: new branch off `origin/main`

## Goal

Replace the current landing page (four buttons opening modals) with a site whose
primary job, for the next twelve months, is convincing a neurotech/ML hiring
manager that Ahmad builds closed-loop neural systems that work. Academic peers
and future collaborators are the secondary audience.

Secondary goals: get the blog reachable and worth returning to, and keep the
existing contact form working.

Success: someone from the field can tell within a few seconds that a person who
does this work built the page, and can find the evidence without clicking into
a modal.

## Approved direction

Settled in the design lab:

```
page       = console
instrument = inline
transition = dissolve
ground     = dark only (light dropped 2026-11-05)
type       = IBM Plex Mono throughout
colormap   = theme
presence   = 1.00
measure    = 67ch
```

### Organising idea

The page is a decoder console. Four tiles name the four decoders; one shared
instrument panel sits directly beneath them and shows whichever decoder is
open -- input on the left, decoded output on the right, on one time axis.
Hovering a tile previews it, clicking holds it. The open tile swaps its
signature line for a short paragraph of prose; tile height is fixed so nothing
reflows.

Earlier drafts gave each decoder its own band down a long scroll. Cut: it put
the instrument below the fold, so a visitor never saw a tile and the panel at
the same time and never learned that one drives the other. The console keeps
both on one screen, which is the whole point.

This is the part that cannot be produced from a template: it only makes sense
for someone who has built all of these decoders.

### Idle cycle

Before the visitor touches anything the panel walks the four decoders, so the
tile/panel link is visible without instruction. Dwell in seconds: handwriting 4,
navigation 8, sEMG 3, motifs 6. Engines keep state between visits, so a cut-off
animation resumes rather than restarting and successive passes carry each story
further. Any hover, click or jump ends the cycle permanently.

### Palette

Dark only -- the instrument reads best there and light was dropped on
2026-11-05. Colour appears only inside a readout, where it carries meaning
(movement direction, motif identity, depth). Prose is monochrome, data is
coloured -- figure logic. Interface selection inverts and links underline; the
accent is never spent on chrome.

Five candidates in the lab. They differ on ground lightness, how much hue is in
the ground, and how far the ink sits from it, before accent hue is considered:

| name      | `--bg`  | ground hue       | ink contrast | `--accent` |
|-----------|---------|------------------|--------------|------------|
| void      | #000000 | none, greyscale  | 20:1         | #FF4D00    |
| phosphor  | #040F0A | green, saturated | 9:1          | #52E08C    |
| blueprint | #0A1A2C | blue, saturated  | 13:1         | #E8B339    |
| ember     | #17100E | warm brown       | 12:1         | #74CFC2    |
| graphite  | #1E2124 | cool grey, lit   | 6:1          | #C9D24E    |

phosphor runs one hue for the whole page including body text. blueprint and
ember deliberately pair a cold ground with a warm live colour and the reverse.
graphite is the only one that is not near-black.

An earlier set (amber / vermilion / moss / slate / paper) was rejected: the four
dark members were one near-black with the accent swapped, which read as a single
theme rather than five. **Open question: which of the five ships.**

### Typography

IBM Plex Mono at every size, headings and body included. An earlier draft set
body in Source Serif 4 with mono for labels; the serif-on-dark mix read as two
unrelated pages stapled together. One face, fixed step scale, no display cut.

Measure 67ch. Type scale is fixed steps, not a ratio.

### Deliberately absent

These were in earlier drafts and were cut because they are what makes a page
read as generated: accent-colored stat tiles, skill/tag pill rows, lowercase
monospace nav, generic section names (Work / Papers / Toolkit / Get in touch),
numbered `01 / 02 / 03` markers used as decoration, ambient particles behind
text. Numbers live inside sentences.

The one structural device kept is the rule above each section carrying its
decoder number and signature — `decoder 01 · threshold crossings + spike band
power → characters` — which earns its place because the page genuinely does
swap decoder there.

## Structure

Two candidates, switchable in the lab. **Console is the current preference.**

### Console (compressed)

Identity, then one tile per decoder beside a single shared instrument panel,
then the selected project's prose, then the tail. Hovering a tile previews its
decoder in the panel; clicking pins it; the tiles are buttons, so focus and
arrow keys do the same thing. Nothing is hidden behind scroll — the whole set
of projects is visible at once and the instrument is the thing being operated
rather than something that happens to you as you scroll.

The transition eases on its own clock here, since the scrollbar is no longer
the transport.

Roughly one screen for the console plus a short tail (papers, contact, footer),
against five full sections in the long-scroll version.

### Long scroll (original)

Single column beside the rail, one section per decoder, the readout
interpolating with scroll position. Kept in the lab for comparison.

Sections in order, each binding a decoder head:

| # | Section | Input | Readout |
|---|---------|-------|---------|
| — | Identity | neural | writing |
| 01 | Writing, without a hand | threshold crossings + spike band power | writing |
| 02 | Control from muscle that barely moves | 95-ch EMG channel × time map | 1-D target acquisition |
| 03 | Reach fast, then select precisely | threshold crossings + spike band power | navigation |
| 04 | Behavior, below the second | 3D depth video (real) | motifs |
| — | Papers | depth | motifs |
| — | Contact | neural | navigation |

The old decoders 03 (reaching) and 04 (gesture classifier) are **one item**.
They were always one argument — the classifier exists because the velocity
decoder cannot settle — and splitting them across two tiles made the page state
the problem and the fix as if they were unrelated results.

Below the fold of the last section: a short "before this" paragraph (wearable
cervical-spine tracker, hidden-hearing-loss rig, source extraction in morphing
cells, running the student IT team), teaching, and the footer links.

### The instrument

Fixed rail, `clamp(124px, 13.5vw, 182px)`, full viewport height, `border-right`
only. Time runs downward. Input occupies the upper portion, readout the lower,
separated by a seam rule. Below 760px the rail becomes a 116px band pinned to
the top and the page flows beneath it.

Inputs:

- **neural** — threshold-crossing raster beside spike-band-power traces. Every
  mark is positioned from its own age against one shared 104 px/s, so the two
  halves cannot desync. Traces are a mixture of three OU latents with different
  time constants plus a shared transient; the same latents modulate the firing
  rates, so the halves visibly co-vary. 5–9 trace lines depending on room.
- **emg** — the high-density array as a channel × time map. This is a view of
  the input, not a decode, so it sits on the input side. Column rate derives
  from the shared scroll speed, so it travels with everything else.
- **depth** — real data. 600 extracted, egocentrically aligned frames from frame
  43000 of `results_00.h5`. In the rail the frame sits at the top and the
  measured centroid velocity runs down the rest on the same downward time axis.
  A `frame 43xxx · N mm/s` readout is always shown; a genotype-and-dose caption
  is toggleable.

Readouts:

- **writing** — characters stroked out of the stream with a nib at the reveal edge
- **1-d control** — one-dimensional pursuit. The target path scrolls downward as
  a line of dots: each trial leaves baseline, swings out as a Gaussian and
  returns, with the side alternating, so the cursor has to travel out to the
  peak and back to clear both halves. Between trials the baseline eases across
  to the next side rather than jumping, keeping the target continuous.
  Tracking is a damped spring (ζ ≈ 0.83) with a little noise, so it lags
  slightly on the steep limb and settles on the flat — the contrast with the
  clean 2-D reaches in decoder 03 is the point. The cursor flips to face its
  direction of travel rather than rotating. Built as a generic dot-eater: no
  name, no ghosts, no maze, site accent rather than yellow.
- **navigation** — the paper's argument in two acts, on a loop.

  *Act 1, the problem.* A centre-out reach to a small target (radius 0.085 of
  the ring) arrives fast and then cannot land: the cursor loops in and out while
  a counter tallies the dwell resets. Only `continuous` exists in the mode
  strip, at full width, because at this point there is only one way to drive
  the cursor.

  *Act 2, the fix.* A 10×10 grid with a random target, start forced onto the
  far side (≥55% of the grid away). A continuous reach gets close and lands a
  couple of cells off. `continuous` gives up half its width and `discrete`
  slides in beside it with a short shiver — added on top of point-and-click,
  not replacing it. The mode flips, the cursor locks to the cell it is already
  in, and five gesture bars (up / down / left / right / click) step it to the
  target.

  There is **one control law** for every continuous movement on the page:
  commanded speed is `min(VMAX, K × error)` against noise of fixed amplitude,
  so a fast directed reach and a hopeless dial-in are the same equation at
  different distances, with nothing to blend at the seam. Noise is a slow
  wandering bias (OU, τ ≈ 0.75 s) plus jitter held at the decoder update rate;
  the bias is what bends the grid reach and what drags the cursor off target.

  Measured: speed 1.76 → 0.37 units/s across a reach; 27–50% of dial-in time
  inside the target, ~27 boundary crossings and 4–6 dwell resets per attempt;
  start-to-target distances of 6–11 cells. The gesture bars are faithful — 41
  sampled commits, 0 mismatches between the winning bar and the move executed.
- **motifs** — a single-lane ethogram, frame-locked to the depth video on screen

Every engine primes before its first visible frame, so the page is full at rest
rather than filling in from the leading edge.

`prefers-reduced-motion` freezes the instrument to a single static frame.

## Data assets

`assets/depth.png` — 319 KB sprite sheet, 600 frames of 80×80 at 32 depth
levels, 25×24 grid. Built from `results_00.h5` by applying `frames_mask`
(removes speckle and wall reflections in one step), a 3×3 median filter,
largest-connected-component only, and a 0.5 px Gaussian. The sheet stores
height, not color; the ramp is applied in-canvas so the depth map can follow
the page palette.

Frame metadata and the velocity array are inlined in the page (~2.5 KB) rather
than fetched, so the only network asset is the PNG.

The generator script should be committed alongside, so the sheet can be rebuilt
if the window or the cleanup changes.

## Technical

- Static site, no build step. One `index.html`, one stylesheet, one script,
  plus `assets/`. Served by GitHub Pages from a new branch off `origin/main`,
  `CNAME` preserved.
- Content lives in a single `site.js` data object; layout is a function over it.
  Changing copy never touches markup.
- Contact form keeps posting to Web3Forms with the existing access key.
- Keep the existing Google Analytics tag, `images/brain1.png` favicon, and the
  `/blog` and `/redirects` trees untouched by this work.
- Quality floor: keyboard focus visible, canvas marked `aria-hidden`, the page
  readable and complete with JavaScript disabled, no horizontal scroll at 400px.

## Out of scope for this pass

Restyling the Hugo blog theme; writing new blog posts; any change to
`/redirects` or `/visual-projects`.

## Ethogram labels

`results_00.h5` is moseq2-extract output and carries no `labels` array, so the
AR-HMM's own sequence is not available yet.

In its place the page ships a sequence derived from the same frames, so the
strip and the mouse are always the same moment: changepoints from the real
extraction scalars (velocity, height, length, width, area, turning rate),
smoothed, with a 300 ms minimum segment; segment means clustered into 12
identities. 52 segments over the 600 frames, median 366 ms, range 300–566 ms —
the range real syllables occupy.

It is labelled `provisional` on the page and must be replaced when the
moseq2-model output turns up. The generator script is committed so the swap is
a one-line change of source.

## Settled since first draft

- Decoder 02: EMG heat map moves to the **input** side; readout is 1-D target
  acquisition.
- Decoders 02 and 03 of the first draft merged into one two-act animation: the
  velocity decoder reaches fast and then cannot settle, and discrete gesture
  decoding is added on top to finish the selection. The gesture bars are
  faithful -- the winning bar is the move the cursor actually executes (41
  sampled commits, 0 mismatches).
- Structure: **console**, not long scroll. Tiles and instrument share a screen.
- Blog stays its own world. No restyle this pass.
- Typography: IBM Plex Mono throughout. The serif/mono mix is cut.
- Ground: **dark only**. The light palette is removed.
- Content rewritten 2026-11-05 to field language; the "verb, comma, promise"
  headline construction is gone, and an invented `<20 ms` latency figure was
  removed rather than kept because it sounded right.
- Links, recovered from the current site: CV `pdfs/cv-redacted.pdf`,
  blog `/blog`, GitHub `github.com/X4ndri`, ORCID `0009-0001-3030-9864`,
  LinkedIn `in/aaqader`, Stack Overflow `users/20828014/ahmad`,
  Twitter `forrealahmad`. **There is no Google Scholar profile anywhere in the
  repo** -- ORCID is used instead, which is the better identifier regardless.
- Header mark recovers the old site's brain-in-angle-brackets as one inline SVG.
- Session caption is a toggle in the lab so the wording can be judged before
  committing to it.

## Open questions

1. **Palette** -- which of void / phosphor / blueprint / ember / graphite ships.
2. **moseq2-model output** -- still being located; the ethogram is `provisional`
   until it turns up. See above.
3. **Session caption** -- keep it on, and in which wording?
4. **Longer prose** -- a tile shows one short paragraph when open. Whether the
   fuller project writeups get their own pages, an expanded state, or are cut.
5. **Working tree** -- the repo sits on `codex/site-redesign` with ~115 modified,
   deleted and untracked paths, none committed, plus a stale `redesign-preview/`
   worktree. This branch was cut from `origin/main` in a separate worktree to
   avoid it; that tree still needs resolving before the real build.
6. **Hero** -- the first screen is the name, one line of affiliation, a
   paragraph and the methods block. Possibly too quiet. Worth a look once the
   real page exists.
