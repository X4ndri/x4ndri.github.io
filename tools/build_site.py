#!/usr/bin/env python3
"""Build the site and the prototype from one source.

The lab carries the switches that let a direction be chosen; the site carries
the direction. Both come out of this, so a change made once reaches both by
rebuilding rather than by being typed twice.

    python3 build_site.py lab.html OUTDIR
      OUTDIR/index.html          the site
      OUTDIR/preview/index.html  the lab, wrapped as a real document, noindex

Fonts are served from this domain in both. Nothing about a visitor reaches a
font CDN, which is one fewer party in the privacy policy and one round trip
less before first paint.
"""
import io, os, re, sys

GA = 'G-2SE668F99F'
WEB3FORMS_KEY = 'c353b0c5-2b7a-4263-a0fb-f32588ce499e'

GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap">\n')

# Root-absolute so the same rules work at / and at /preview/.
FONT_FACES = """/* IBM Plex Mono, served from this domain rather than a CDN.
   SIL Open Font License 1.1 — see assets/fonts/LICENSE. */
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:400;font-display:swap;
  src:url("/assets/fonts/ibm-plex-mono-latin-400-normal.woff2") format("woff2")}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:500;font-display:swap;
  src:url("/assets/fonts/ibm-plex-mono-latin-500-normal.woff2") format("woff2")}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:600;font-display:swap;
  src:url("/assets/fonts/ibm-plex-mono-latin-600-normal.woff2") format("woff2")}
@font-face{font-family:"IBM Plex Mono";font-style:italic;font-weight:400;font-display:swap;
  src:url("/assets/fonts/ibm-plex-mono-latin-400-italic.woff2") format("woff2")}

"""

PRELOAD = ('<link rel="preload" as="font" type="font/woff2" crossorigin\n'
           '      href="/assets/fonts/ibm-plex-mono-latin-400-normal.woff2">\n')

ANALYTICS = """<!-- Analytics, with the visitor's own preference honoured before anything
     loads. '1' is an opt-out made by hand on /privacy.html; '0' is an opt-in
     made by hand, which overrides the browser signal; neither means follow
     the signal. -->
<script>
  (function () {
    var ID = '%(ga)s', K = 'analytics-opt-out';
    function stored() { try { return localStorage.getItem(K); } catch (e) { return null; } }
    function signal() {
      return navigator.globalPrivacyControl === true ||
             navigator.doNotTrack === '1' || window.doNotTrack === '1';
    }
    if (stored() === '1' || (stored() !== '0' && signal())) {
      window['ga-disable-' + ID] = true;
    }
  })();
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=%(ga)s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%(ga)s');
</script>
""" % {'ga': GA}

SITE_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ahmad Abdal Qader</title>
<meta name="description" content="Ahmad Abdal Qader — neural decoding for brain-computer interfaces. Sequence models on intracortical and surface EMG recordings, run online with people with paralysis.">
<link rel="canonical" href="https://qader.dev/">
<link rel="icon" href="/images/brain1.png">
""" + PRELOAD + """
<meta property="og:type" content="profile">
<meta property="og:url" content="https://qader.dev/">
<meta property="og:title" content="Ahmad Abdal Qader">
<meta property="og:description" content="Neural decoding for brain-computer interfaces. Sequence models on intracortical and surface EMG recordings, run online with people with paralysis.">
<meta name="twitter:card" content="summary">

""" + ANALYTICS

PREVIEW_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Design lab — qader.dev</title>
<meta name="robots" content="noindex,nofollow">
<link rel="icon" href="/images/brain1.png">
""" + PRELOAD + """<!-- The prototype, with the switches still attached. Kept out of search on
     purpose; the site itself is at the root. -->
"""


def cut(s, start, end, what, replacement=''):
    """Remove start..end (end exclusive). Both markers must appear exactly once."""
    for m, n in ((start, 'start'), (end, 'end')):
        if s.count(m) != 1:
            sys.exit('%s: %s marker appears %d times, expected 1' % (what, n, s.count(m)))
    a, b = s.index(start), s.index(end)
    if not a < b:
        sys.exit('%s: markers out of order' % what)
    return s[:a] + replacement + s[b:]


def common(s):
    """Everything both outputs need: local fonts, no CDN, no tool-specific hints."""
    if GOOGLE_FONTS not in s:
        sys.exit('font link not found — did the lab head change?')
    s = s.replace(GOOGLE_FONTS, '')
    s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    s = s.replace('<style>\n', '<style>\n' + FONT_FACES, 1)
    s = re.sub(r'<title>.*?</title>\n', '', s, count=1, flags=re.S)
    # One copy of the sprite, at the root, for both pages — the same rule the
    # privacy policy gets. Relative, it resolved to /preview/assets/ and 404'd.
    if "src='assets/depth.png'" not in s:
        sys.exit('depth sprite path not found')
    s = s.replace("src='assets/depth.png'", "src='/assets/depth.png'")
    for bad in ('fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.tailwindcss.com'):
        if bad in s:
            sys.exit('%s still referenced' % bad)
    return s


def build_site(s):
    # Palettes other than the one that ships.
    for name in ('phosphor', 'blueprint', 'ember', 'graphite'):
        s = re.sub(r'#stage\[data-pal="%s"\]\{.*?\n\}\n' % name, '', s, flags=re.S)
    if 'data-pal="phosphor"' in s:
        sys.exit('palette strip failed')

    # The lab's control panel: styles, the tokens it painted itself with,
    # its markup, and the code behind it.
    s = cut(s, '/* control panel */', '@media (prefers-reduced-motion:reduce)', 'panel css')
    s = cut(s, ':root{\n  --lab-panel', '*{box-sizing:border-box}', 'panel tokens')
    s = cut(s, '<aside class="lab-panel"', '\n<script>', 'panel markup')
    s = cut(s, '/* ---------- controls ---------- */', 'let tick=false;', 'controls js',
            '/* The lab drove these from its panel; the site has nothing to sync. */\n'
            'function syncUI(){}\n\n')

    # A real form. Same markup, so the design is untouched; the names and the
    # action are what Web3Forms needs, and `required` lets the browser enforce
    # the consent box with no JavaScript at all.
    s = s.replace(
        '<form class="s-cmain" id="cform" novalidate>',
        '<form class="s-cmain" id="cform" action="https://api.web3forms.com/submit" method="POST">\n'
        '          <input type="hidden" name="access_key" value="%s">\n'
        '          <input type="hidden" name="subject" value="New contact request from qader.dev">\n'
        '          <input type="hidden" name="from_name" value="qader.dev">\n'
        '          <input type="checkbox" name="botcheck" class="s-hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
        % WEB3FORMS_KEY)
    s = s.replace('<input id="cf1" type="text" autocomplete="name">',
                  '<input id="cf1" name="name" type="text" autocomplete="name" required>')
    s = s.replace('<input id="cf2" type="email" autocomplete="email">',
                  '<input id="cf2" name="email" type="email" autocomplete="email" required>')
    s = s.replace('<textarea id="cf3" rows="5"></textarea>',
                  '<textarea id="cf3" name="message" rows="5" required></textarea>')
    s = s.replace('<p class="s-cnote" id="cfn">Posts to Web3Forms, as the current site does.</p>',
                  '<p class="s-cnote" id="cfn">I read everything and reply to most of it.</p>')
    for needed in ('name="name"', 'name="email"', 'name="message"', 'name="access_key"'):
        if needed not in s:
            sys.exit('form rewrite failed: %s missing' % needed)

    # Submit over fetch, so nobody is thrown onto a stock confirmation page.
    # With JavaScript off the plain POST still works.
    s = cut(s, 'function wireForm(){', '\n/* the scrollbar is the transport', 'form handler', """function wireForm(){
  const f=document.getElementById('cform'); if(!f) return;
  const note=document.getElementById('cfn'), btn=f.querySelector('.s-send');
  const say=t=>{note.textContent=t;};
  f.addEventListener('submit',async e=>{
    e.preventDefault();                 /* only fires once the browser is satisfied */
    btn.disabled=true; say('Sending…');
    try{
      const r=await fetch(f.action,{method:'POST',body:new FormData(f),
                                    headers:{'Accept':'application/json'}});
      const j=await r.json().catch(()=>({}));
      if(r.ok&&j.success!==false){ f.reset(); say('Sent. I read everything and reply to most of it.'); }
      else { btn.disabled=false; say('That did not send. Try again, or find me on LinkedIn.'); }
    }catch(err){ btn.disabled=false; say('That did not send — check your connection and try again.'); }
  });
}
""")

    # The honeypot belongs in the stylesheet, not inline, or a bot reads it.
    s = s.replace('@media (prefers-reduced-motion:reduce)',
                  '.s-hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none}\n'
                  '@media (prefers-reduced-motion:reduce)')
    return s


def build_preview(s):
    # The prototype keeps its panel. Only the policy link has to leave, since
    # the canonical copy lives at the root and a page may have exactly one.
    return s.replace('href="privacy.html"', 'href="/privacy.html"')


def close(body, head):
    return head + '</head>\n<body>\n' + body.lstrip() + '\n</body>\n</html>\n'


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    lab = common(io.open(sys.argv[1], encoding='utf-8').read())
    out = sys.argv[2]
    os.path.isdir(out) or os.makedirs(out)
    os.path.isdir(out + '/preview') or os.makedirs(out + '/preview')

    for path, body, head in (
            (out + '/index.html', build_site(lab), SITE_HEAD),
            (out + '/preview/index.html', build_preview(lab), PREVIEW_HEAD)):
        text = close(body, head)
        io.open(path, 'w', encoding='utf-8').write(text)
        print('%-28s %7d bytes' % (path, len(text)))
