# Analytics and privacy — what was decided, and what to wire up

Decision, taken 2026-11-05: **keep Google Analytics, disclose it, honour browser
privacy signals automatically, no consent banner.** Recruiter tracking is done
with tagged links instead, because that is the thing that actually answers the
question.

The page is built: `privacy.html`, in the site's own palette tokens, with a
working opt-out. Not legal advice — an accurate description of what the site does.

---

## 1. Why this option

You wanted to know whether recruiters open the site. Analytics cannot tell you
that — GA4 has no individual-visitor identification, and the products that claim
it work by IP-to-company matching and are a much worse idea on a personal site.
So the opt-out was never costing you the thing you were trying to protect.

What it does cost: essentially nothing. Visitors sending GPC or DNT are a modest
slice, and people who find a button on a privacy page are close to none. In
exchange you get a position that is honest, that matches what the page actually
does, and that needs no banner — which is the only privacy furniture that would
have damaged the design.

The recruiter question gets answered properly in §3.

## 2. Wire up on every page

Immediately **above** the existing gtag tags in `<head>`:

```html
<script>
  (function () {
    var ID = 'G-2SE668F99F', K = 'analytics-opt-out';
    function stored() { try { return localStorage.getItem(K); } catch (e) { return null; } }
    function signal() {
      return navigator.globalPrivacyControl === true ||
             navigator.doNotTrack === '1' || window.doNotTrack === '1';
    }
    /* '1' = opted out by hand. '0' = opted in by hand, overriding the signal.
       Neither = follow the signal. */
    if (stored() === '1' || (stored() !== '0' && signal())) {
      window['ga-disable-' + ID] = true;
    }
  })();
</script>
<!-- existing gtag tags, unchanged -->
```

`privacy.html` carries the matching button and prints the current state. Tested:
default on; click turns it off and sets `ga-disable-G-2SE668F99F`; survives
reload; clicking again turns it back on; a visitor sending GPC arrives already
off and is told why.

## 3. Tracking links — the actual recruiter answer

Put a distinct URL on each application, each emailed CV, each cold message:

```
qader.dev/?r=meta-ctrl-labs
qader.dev/?r=apple-neuro
qader.dev/?r=tacit
```

GA4 picks the parameter up on its own if you use the campaign names instead
(`?utm_source=application&utm_campaign=meta-ctrl-labs`), and either way a visit
tells you *which* application produced it, with a timestamp. That is exact where
analytics is vague, identifies nobody, and still works if the visitor blocks
analytics entirely — the parameter is in the URL.

For the narrower question "did that specific person look at me," LinkedIn's
*who viewed your profile* answers it by name, which GA never will.

## 4. Before publishing

- **Date** — `privacy.html` says *November 2026*. Set it to the real publish month.
- **Web3Forms tier** — free emails you the submission; paid also stores it in a
  dashboard. The retention sentence changes if you're on paid.
- **Fonts** — the page discloses Google Fonts because the site loads them from the
  CDN. Self-host IBM Plex Mono from `static/public/fonts/` and you can delete that
  paragraph and shorten the recipients list. Cheapest cleanup available.
- **Tailwind** — the current site pulls `cdn.tailwindcss.com`. The new design uses
  no framework, so this should disappear on rebuild. If any page still loads it,
  add Cloudflare to the recipients list.

## 5. Where it goes

- `privacy.html` at the repo root.
- Footer link — already in the lab, beside CV / Blog / GitHub.
- The contact form's consent checkbox — already points at it.
