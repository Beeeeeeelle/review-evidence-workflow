# Belle edition — visual decisions

Primary scene: a personal-web learning page, adapted from the Belle Design System personal-web template. Derived outputs: four 1600 × 900, 24 fps guided films, posters and optional captions. English and Chinese share layout tokens but receive separate line-breaking checks.

## What changed

- White and black establish hierarchy. Orange points to the current action; blue connects an explanation or source. Neutral rules replace the earlier dark cards and heavy frames.
- Large headings introduce one idea. Text prompts use a single black field. Flows use an open sequence; handoffs and outputs use a ledger. Case studies use real-source images next to their explanation.
- Actual workbench captures keep their source pixels. A separate left rail names the action, with numbered markers on the screen, reducing text placed on top of evidence. The camera eases into a close-up and holds. Scroll cues move once, then settle.
- The player combines the two films with a quiet chapter index, previous/next controls, responsive layout and language switching that retains the corresponding chapter. The original edition has its own link.
- Existing Belle illustrations retain their identity and role: turning scattered papers into a question and helping a team develop its rules. No new character art or fabricated UI was generated.

## Figma references consulted

This implementation uses Figma's published design guidance; it was not authored in a connected Figma file.

- [Typography systems](https://www.figma.com/best-practices/typography-systems-in-figma/): a consistent type scale, separate display and body treatments, readable line lengths.
- [Layout grids](https://www.figma.com/best-practices/everything-you-need-to-know-about-layout-grids/): aligned text/image columns, repeatable spacing and responsive reflow.
- [Smart Animate](https://help.figma.com/hc/en-us/articles/360039818874-Smart-animate-layers-between-frames): continuity between states informed the restrained editorial camera moves. Screen states remain authentic captures.

## Preservation and boundaries

The approved baseline is commit `b60d2aa2b2cf2af36dfa77037de1fc9c711a05de`. The original `docs/demo` and `docs/intro` assets and tools are retained. The Belle edition lives entirely under `docs/watch`; core skill logic and research judgments are unchanged. A local backup and SHA-256 manifest were also saved before editing.

Narration and timing come from the approved caches. This is a visual edition, not a new validation study or evidence of time savings. Original source attribution and distinctions among illustration, fictional demo and actual capture remain visible.

## Verification

Results are recorded in [QA.json](QA.json). The checks cover media decode, durations, subtitle timing, original-file preservation, file links, design tokens, and browser interaction. Responsive review uses 1440 × 900, 1024 × 768 and 390 × 844. The player's native fullscreen and optional caption controls are available for small screens.
