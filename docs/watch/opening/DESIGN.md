# Problem first, then the real workbench

The first edition explained the two skills before showing a detailed example. This opening follows the conference talk’s problem-led logic, compressed for a short film: recognize the friction, see the actual workbench, then learn the method.

- Chinese: 54.79 seconds; authentic UI begins at 11.25 seconds.
- English: 61.29 seconds; authentic UI begins at 16.21 seconds.
- Three concept scenes: finding a full text, returning from a code to evidence, reconciling different reviewer returns.
- Immediate payoff: the actual Pilot, PDF p. 18 and its source highlight, Revise with a reason, and Correct after verification.
- Closing handoff: the two skills prepare connected stages; people develop rules, verify evidence and resolve disagreements.

## Motion and identity

The first static cut is retained in the local build archive. The published opening uses six transparent generated assets with independent position/opacity timelines, plus simple editorial feedback tokens and progressively drawn paths. It does not merely zoom an entire image. Each entrance settles in roughly 0.65 seconds. Full compositions hold briefly for reading before the real UI appears.

Characters were checked against the current Belle canonical reference. Rejected generations included oversized eyes, a smile, and horizontally stretched hair. The final artwork keeps the continuous up-left black hair, tiny eyes, deadpan face, small black body, internal stars and one four-wing butterfly. See the asset folder’s QA record.

## Preservation and playback

The four approved detailed films are byte-for-byte unchanged. New narration, bilingual captions, six chapter markers and renderer are separate. Native GitHub attachments play directly in README pages. The local player defaults to this new opening and offers three episodes; continuous playback can be switched off. Language switching keeps the corresponding chapter. Older `video=intro` and `video=pilot` links still work.

The UI uses genuine existing public captures, with editorial circles, arrows and camera movement. No scientific decisions or source PDFs were changed. This is a narrated capture sequence, not a continuous screen recording. No measured time saving or accuracy gain is asserted.

## Rebuild

Run `tools/render_opening.py voice --lang zh-CN --build /path/to/cache`, then `preview` or `render` with the same arguments. Repeat with `--lang en`. Voice generation needs edge-tts and network access. Rendering needs Pillow and ffmpeg; font configuration is inherited from `render_belle.py`. The accepted transparent layers and bilingual storyboard files are checked into the repository. Rebuilds may produce different TTS timing, so merge the generated chapter metadata into `videos.json` and review the encoded output before publishing.

[Verification record](QA.json)
