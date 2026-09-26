# Problem first, then the real workbench

The first edition explained the two skills before showing a detailed example. This opening follows the conference talk’s problem-led logic, compressed for a short film: recognize the friction, see the actual workbench, then learn the method.

- Chinese: 54.79 seconds; authentic UI begins at 11.25 seconds.
- English: 61.29 seconds; authentic UI begins at 16.21 seconds.
- Three concept scenes: finding a full text, returning from a code to evidence, reconciling different reviewer returns.
- Immediate payoff: the actual Pilot, PDF p. 18 and its source highlight, Revise with a reason, and Correct after verification.
- Closing handoff: the two skills prepare connected stages; people develop rules, verify evidence and resolve disagreements.

## Motion and identity

The first static cut is retained in the local build archive. The published opening uses six transparent generated assets with independent position/opacity timelines, plus simple editorial feedback tokens and progressively drawn paths. It does not merely zoom an entire image. Each entrance settles in roughly 0.65 seconds. Full compositions hold briefly for reading before the real UI appears.

The second layered edition fixes disconnected, jagged routes identified in viewer feedback. Each connection starts and ends on a specific object: paper → paper, paper → hand, paper → lock, code → inspection lens, and A/B returns → the notebook's margins. Object-relative anchors share the artwork's crop and scale. Cubic curves reveal by distance, with rounded ends and 4× antialiasing; they start after the objects settle. The oversized enclosing circle and long line crossing the first scene are removed.

Two character layers were regenerated against the current Belle canonical reference. The evidence-checking pose has a clearer black body and smaller face details. In the feedback scene, a smaller Belle touches both notebook pages instead of sitting with empty hands above disconnected paths. The notebook carries the comparison. Original drawings and the first layered edition are retained, with their shortcomings explicitly recorded in the asset folder's QA record.

## Preservation and playback

The four approved detailed films are byte-for-byte unchanged. This revision also keeps the opening's narration, captions, chapter times and eleven-beat sequence unchanged. Native GitHub attachments play directly in README pages. The local player defaults to this new opening and offers three episodes; continuous playback can be switched off. Language switching keeps the corresponding chapter. Older `video=intro` and `video=pilot` links still work. The `layered` release files retain the first edition; `layered-v2` files contain the corrected connectors and poses.

The UI uses genuine existing public captures, with editorial circles, arrows and camera movement. No scientific decisions or source PDFs were changed. This is a narrated capture sequence, not a continuous screen recording. No measured time saving or accuracy gain is asserted.

## Rebuild

Run `tools/render_opening.py voice --lang zh-CN --build /path/to/cache`, then `preview` or `render` with the same arguments. Repeat with `--lang en`. Voice generation needs edge-tts and network access. Rendering needs Pillow and ffmpeg; font configuration is inherited from `render_belle.py`. The accepted transparent layers and bilingual storyboard files are checked into the repository. Rebuilds may produce different TTS timing, so merge the generated chapter metadata into `videos.json` and review the encoded output before publishing.

[Verification record](QA.json)
