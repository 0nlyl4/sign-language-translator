# Results

Real-time ASL fingerspelling recognition from MediaPipe hand landmarks.

## Experiments

| # | Train | Test | Features | Letters | Accuracy | Baseline |
|---|---|---|---|---|---|---|
| 1 | batch 1 (80%) | batch 1 (20%) | raw | 5 | 100% | 20% |
| 2 | batch 1 | batch 2 | raw | 5 | 47.9% | 20% |
| 3 | batch 1 | batch 2 | normalized | 5 | 79.8% | 20% |
| 4 | batch 1 | batch 2 | raw (after fixing C) | 5 | 73.1% | 20% |
| 5 | batch 1 | batch 2 | normalized (after fixing C) | 5 | **99.8%** | 20% |

Letters: A, B, C, L, Y. Each batch is an independent recording session
(different lighting, distance, and background), 300 samples per letter.

## 1. Within-session accuracy was misleading

Experiment 1 reported 100%, but the split was random across frames from a
single continuous recording. Consecutive video frames are nearly identical,
so near-duplicate samples leaked from the training set into the test set.

Evaluating on a separate recording session (experiment 2) dropped accuracy
to 47.9% — the real generalization performance. All subsequent numbers are
cross-session.

## 2. Raw coordinates encode position, not shape

MediaPipe returns landmarks as absolute image coordinates. Moving the hand
across the frame or closer to the camera changes all 63 values even when
the hand shape is identical.

Normalization (`src/features.py`):
1. Translate all points so the wrist is the origin
2. Divide by the largest distance from the wrist

This makes the features invariant to hand position and scale. Letters with
compact shapes (A, B) went from 0/300 correct to 300/300.

## 3. Error analysis: letter C

After normalization, accuracy was 79.8% with C misclassified 100% of the
time. Two diagnostic experiments isolated the cause:

| Test | Result |
|---|---|
| Reverse direction (train batch 2 → test batch 1) | C still collapsed, but into B instead of Y |
| Within batch 2 only (random split) | C classified perfectly (60/60) |

C was internally consistent within each session but inconsistent between
them — two different hand shapes had been recorded under one label. The
target letter changing with training direction ruled out a representation
problem: a genuine shape ambiguity would collapse into the same letter both
ways.

The fix was re-recording C against a fixed reference shape. No model or
feature change was involved. Cross-session accuracy went from 79.8% to 99.8%.

## Known limitations

- **J and Z are excluded.** Both require motion; this system classifies
  single static frames. Supporting them would need a sequence model.
- **Single hand orientation.** All data was recorded with one hand. The
  model does not generalize to the mirrored hand.
- **Two recording sessions.** More sessions across different days, people,
  and environments would give a more reliable estimate.
- **Rotation sensitivity.** Normalization handles translation and scale but
  not wrist rotation.

  ## Experiment 6 — Confidence Threshold

Motivation: the classifier is forced to return one of its known classes on
every frame. Untrained hand shapes and mid-transition frames were displayed
as confident predictions. Measured the confidence distribution across three
conditions to select a rejection threshold instead of guessing one.

| Condition                    | Confidence range |
|------------------------------|------------------|
| Trained letter, held steady  | 100%             |
| Transition between two signs | 24% – 64%        |
| Untrained hand shape         | ~27%             |

Gap: 64% – 100%.

Threshold selected: 80%. Placed above the highest observed transition frame
(64%) with a 16-point safety margin, and well below the confidence of held
signs. A tighter threshold such as 70% risks admitting transition frames;
a stricter one such as 95% would suppress correct predictions once the
class count grows and votes split across visually similar letters
(U / V / R in batch 3).

Behaviour: predictions below the threshold render as "?" in red instead of
a letter in green.

Trade-off: a small number of correct low-confidence predictions are
suppressed in exchange for eliminating confidently-wrong output. For a
user-facing system, showing nothing is preferable to showing a wrong letter
with full certainty.

Caveat: the 100% figure reflects only 5 well-separated classes. This
threshold should be re-measured after each new batch of letters is added.

## Experiment 7 — Temporal Smoothing

Motivation: each frame was classified independently, with no memory of the
previous frame. A single misread frame or slight hand tremor changed the
on-screen output, producing visible flicker on a steadily held sign.

Method: majority vote over a sliding window of the last N predictions
(collections.deque with maxlen=N). Frames below the confidence threshold
are pushed into the window as an explicit rejection vote rather than being
discarded, so the display does not keep showing a stale letter after the
hand has moved on. The window is cleared when the hand leaves the frame.

Window size: 10 frames (~__ ms at 30 fps)

Result: a held sign reaches a full N/N majority and remains stable. Isolated
misread frames are absorbed by the vote and never reach the display.

Trade-off: adds roughly N/30 seconds of latency before a new letter appears.
This is acceptable, and in practice desirable, since it also suppresses the
transient letters produced while moving between two signs.

## Experiment 8 — Letter Commit and Word Assembly

Motivation: the smoothed classifier produced a stable letter on every frame
but had no notion of user intent. Appending that letter directly would
repeat the same character roughly 30 times per second while the hand was
held in place.

Method: two mechanisms on top of the smoothed prediction.

1. Hold — a letter is committed to the output string only after remaining
   stable for HOLD_FRAMES consecutive frames.
2. Latch — once committed, the letter is locked and cannot be committed
   again until the stable prediction changes.

The hold separates an intentional sign from letters that appear briefly
while moving between signs. The latch prevents a single held sign from
being appended repeatedly. A progress bar renders the hold counter so the
commit state is visible to the user rather than implicit. Keyboard controls
provide space, backspace and clear; the assembled string is printed on exit.

Hold duration: 25 frames (~830 ms at 30 fps)

Tuned from an initial 15 frames (~500 ms) after hands-on use. The shorter
hold committed unintended letters during slow transitions between signs,
and left too little margin to abort a sign once started. 25 frames removed
the unintended commits without the input feeling unresponsive.

Known limitation: doubled letters (e.g. "LL") require breaking the hand
shape between repetitions, since the latch releases only on a change in the
stable prediction. This is inherent to hold-to-commit fingerspelling input
and would require an explicit repeat gesture or a timed re-arm to resolve.

## Pipeline Summary (Phase 7)

Each stage addresses a failure mode of the stage before it.

| Stage      | Input              | Output           | Problem solved                    |
|------------|--------------------|------------------|-----------------------------------|
| Landmarks  | Camera frame       | 63 coordinates   | Lighting and background variance  |
| Normalize  | 63 raw coordinates | 63 normalized    | Hand position and distance        |
| Classify   | 63 normalized      | Letter + score   | Shape recognition                 |
| Threshold  | Letter + score     | Letter or reject | Confident output on unknown input |
| Smooth     | Per-frame letters  | Stable letter    | Frame-to-frame flicker            |
| Commit     | Stable letter      | Output string    | Intent vs. continuous presence    |