#!/usr/bin/env python3
"""Turn the design lab into the shipping page.

The lab and the site are one source. The lab carries the switches that let a
direction be chosen; the site carries the direction. Running this strips the
former and keeps the latter, so a change made in the lab reaches the site by
rebuilding rather than by being typed twice.

    python3 build_site.py lab.html site/index.html
"""
import io, re, sys

GA = 'G-2SE668F99F'
WEB3FORMS_KEY = 'c353b0c5-2b7a-4263-a0fb-f32588ce499e'


def cut(s, start, end, what, replacement=''):
    """Remove start..end (end exclusive). Both markers must appear exactly once."""
    for m, n in ((start, 'start'), (end, 'end')):
        if s.count(m) != 1:
            sys.exit('%s: %s marker appears %d times, expected 1' % (what, n, s.count(m)))
    a, b = s.index(start), s.index(end)
    if not a < b:
        sys.exit('%s: markers out of order' % what)
    return s[:a] + replacement + s[b:]


def build(src):
    s = io.open(src, encoding='utf-8').read()

    # 1. Palettes other than void. Keep the one that ships.
    for name in ('phosphor', 'blueprint', 'ember', 'graphite'):
        s = re.sub(r'#stage\[data-pal="%s"\]\{.*?\n\}\n' % name, '', s, flags=re.S)
    if 'data-pal="phosphor"' in s:
        sys.exit('palette strip failed')

    # 2. The lab's control panel — styles, markup, the tokens it painted
    #    itself with, and the code behind it.
    s = cut(s, '/* control panel */', '@media (prefers-reduced-motion:reduce)', 'panel css')
    s = cut(s, ':root{\n  --lab-panel', '*{box-sizing:border-box}', 'panel tokens')
    s = cut(s, '<aside class="lab-panel"', '\n<script>', 'panel markup')
    s = cut(s, '/* ---------- controls ---------- */', 'let tick=false;', 'controls js',
            '/* The lab drove these from its panel; the site has nothing to sync. */\n'
            'function syncUI(){}\n\n')

    # 3. A real form. Same markup, so the design is untouched; names and the
    #    action are what Web3Forms needs, and `required` lets the browser
    #    enforce the consent box without JavaScript.
    s = s.replace(
        '<form class="s-cmain" id="cform" novalidate>',
        '<form class="s-cmain" id="cform" action="https://api.web3forms.com/submit" method="POST">\n'
        '          <input type="hidden" name="access_key" value="%s">\n'
        '          <input type="hidden" name="subject" value="New contact request from qader.dev">\n'
        '          <input type="hidden" name="from_name" value="qader.dev">\n'
        '          <input type="checkbox" name="botcheck" class="s-hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
        % WEB3FORMS_KEY)
    for cid, attrs in (
            ('cf1', 'name="name" type="text" autocomplete="name" required'),
            ('cf2', 'name="email" type="email" autocomplete="email" required')):
        s = s.replace('<input id="%s" type="%s" autocomplete="%s">' % (
            cid, 'text' if cid == 'cf1' else 'email',
            'name' if cid == 'cf1' else 'email'),
            '<input id="%s" %s>' % (cid, attrs))
    s = s.replace('<textarea id="cf3" rows="5"></textarea>',
                  '<textarea id="cf3" name="message" rows="5" required></textarea>')
    s = s.replace('<p class="s-cnote" id="cfn">Posts to Web3Forms, as the current site does.</p>',
                  '<p class="s-cnote" id="cfn">I read everything and reply to most of it.</p>')
    for needed in ('name="name"', 'name="email"', 'name="message"', 'name="access_key"'):
        if needed not in s:
            sys.exit('form rewrite failed: %s missing' % needed)

    # 4. Submit over fetch so nobody is thrown onto a stock confirmation page.
    #    Without JavaScript the plain POST still works.
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

    # 5. The page is no longer a lab: retitle it, and drop the hint meant for
    #    the tool it was prototyped in.
    s = s.replace('<title>qader.dev Design Lab</title>',
                  '<title>Ahmad Abdal Qader</title>', 1)
    s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    if 'Design Lab' in s:
        sys.exit('title rewrite failed')

    # 6. The honeypot has to be in the stylesheet, not inline, or a bot reads it.
    s = s.replace('@media (prefers-reduced-motion:reduce)',
                  '.s-hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none}\n'
                  '@media (prefers-reduced-motion:reduce)')

    return DOC_OPEN + s.lstrip() + DOC_CLOSE


DOC_OPEN = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Ahmad Abdal Qader — neural decoding for brain–computer interfaces. Sequence models on intracortical and surface EMG recordings, run online with people with paralysis.">
<link rel="canonical" href="https://qader.dev/">
<link rel="icon" href="images/brain1.png">

<meta property="og:type" content="profile">
<meta property="og:url" content="https://qader.dev/">
<meta property="og:title" content="Ahmad Abdal Qader">
<meta property="og:description" content="Neural decoding for brain–computer interfaces. Sequence models on intracortical and surface EMG recordings, run online with people with paralysis.">
<meta name="twitter:card" content="summary">

<!-- Analytics, with the visitor's own preference honoured before anything loads.
     '1' is an opt-out made by hand on /privacy; '0' is an opt-in made by hand,
     which overrides the browser signal; neither means follow the signal. -->
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

DOC_CLOSE = "\n</body>\n</html>\n"


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    out = build(sys.argv[1])
    # the lab's <title> and font <link> land in <head>; everything after opens <body>
    out = out.replace('<style>', '</head>\n<body>\n<style>', 1)
    io.open(sys.argv[2], 'w', encoding='utf-8').write(out)
    print('wrote %s (%d bytes)' % (sys.argv[2], len(out)))
