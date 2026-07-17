# Print-first Guitar/Bass presentation contract

There is no Guitar/Bass selector. Shared theory and every completed
instrument-specific application remain visible together on screen and in
print. The `data-instrument` attributes are semantic styling hooks only; no
JavaScript may hide either application.

Basic Concepts Chapters 1–8 and Core Level 1 Chapters 20–30 have completed
their current Guitar/Bass text pass. Chapters 9–19 still await their content
pass, and identified Guitar Pro bass artwork remains deferred for the author.

## Authoring instrument variants

Shared theory stays outside an instrument wrapper and appears once. Add a pair
only when both applications are ready:

```html
<div class="instrument-variants">
  <section class="instrument-variant" data-instrument="guitar">
    <h2 class="instrument-variant__title">Guitar application</h2>
    <p>Guitar-specific content.</p>
  </section>
  <section class="instrument-variant" data-instrument="bass">
    <h2 class="instrument-variant__title">Bass application</h2>
    <p>Bass-specific content.</p>
  </section>
</div>
```

- Use the heading level appropriate to the surrounding chapter.
- Keep variants block-level, paired, and non-nested.
- Give elements inside each variant unique IDs, normally suffixed `-guitar`
  and `-bass`.
- Do not mark existing guitar material until its bass counterpart is ready.
- Level 1 bass memorizes E, A, and D. The G string may appear as an upper
  interval note, but its note-map recall belongs to Level 2.

Both labeled applications must remain visible with or without JavaScript and
when printed.

## Authoring shared diagrams

Do not make separate diagrams merely because a figure shows six strings.

- Keep one shared figure when all active notes lie on strings shared by guitar
  and four-string bass. Explain that the fret pattern is identical and the bass
  sounds one octave lower when appropriate.
- A six-string outline is acceptable when the text clearly tells bassists which
  strings to use and which unused strings to ignore.
- Make a bass-specific figure when active notes, string numbers, tablature, or
  notation depend on the guitar-only B or high E strings.
- Prefer a shared E–A–D–G crop when it communicates the idea more cleanly than
  a six-string board with unused rows.

## Updating the current static site

Edit the authoritative files in `web/chapters/` directly. Keep shared theory
outside instrument wrappers and verify that all Guitar/Bass applications remain
visible on screen and in print. Run `_build/qa_check.py` after changes.
