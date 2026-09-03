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


| 6 | batch1 | batch2 | raw (mislabelled - see Exp 10) | 53.3% | 9.1% |

# Phase 8 — Scaling from 5 to 22 classes

## Experiment 9 — First expansion: a data-consistency collapse

Added D E F G H I, bringing the model to 11 classes. Cross-session accuracy
dropped to 53.3% (baseline 9.1%).

The six new letters scored 88–100%. Three of the five original letters
collapsed: A 1%, Y 0%, L 56%. Their data had not changed — only the class
count had — so the drop could not be caused by the new letters being harder.

Diagnosis via four train/test splits:

| Split            | Result                                   |
|------------------|------------------------------------------|
| Within session 1 | 100% on all 11 letters                   |
| Within session 2 | 100% on all 11 letters                   |
| Session 1 -> 2   | 77.0% — A, L, Y fail; all others 100%    |
| Session 2 -> 1   | 63.6% — same three letters fail          |

Perfect within-session separation rules out feature-space overlap: if A and E
were genuinely similar as vectors, they would be confused within a session
too. The failure is inconsistent labelling — one class name recorded with two
different hand shapes across sessions.

The three failing letters were the only ones recorded without a saved
reference screenshot. The six recorded with references held up, as did C,
which had been re-recorded to a fixed reference after an earlier identical
failure. Reference screenshots became mandatory from this point.

## Experiment 10 — The evaluation script was measuring the wrong pipeline

Successive re-recordings moved cross-session accuracy from 53.3% to 68.0% to
57.76%. Two letters were re-recorded on the basis of these numbers.

The numbers were wrong. An independent diagnostic script performing the
identical train/test split returned 100% where the evaluation script returned
57.76%. Two scripts doing the same thing cannot disagree; one was measuring
something else.

Cause: evaluate_generalization.py was written during Experiment 2, when raw
coordinates were the input. When normalisation was introduced in Phase 6,
train_model.py and predict_live.py were updated; the evaluation script was
not. It had been reporting raw-coordinate performance ever since — which is
why its numbers sat in the 47–68% band already established for raw features.

| Split                  | Before fix | After fix |
|------------------------|-----------:|----------:|
| Session 1 -> Session 2 |     57.76% |   100.00% |

This is the same principle already documented for this project —
normalisation must be applied identically everywhere — surfacing in a file
that was overlooked because it consumes the pipeline rather than defining it.
It was caught only because two independent scripts disagreed. A single
measurement cannot be checked against itself.

## Experiment 11 — Camera position breaks generalisation

Training on session 1 and testing on session 2 gave 100.00% at 11 classes.
Reversing the direction gave 84.2%, with A -> E, B -> F and D -> L failures,
while within-session accuracy stayed at 100%.

The asymmetry traces to a mid-project change in camera position: the iPad was
moved from one side of the subject to the other between sessions. The current
normalisation handles translation and scale, not rotation, so the same hand
shape viewed from the opposite side produces a different 63-number vector.

This is a direct empirical measurement of a limitation that was documented
before it was observed.

Recording protocol updated: lighting, distance, background and hand tilt may
vary between sessions; camera position relative to the subject may not.

## Experiment 12 — Confidence threshold is class-count dependent

The 0.80 threshold was tuned when the model had 5 classes and correct
predictions carried ~100% confidence. With more classes, probability mass
spreads across more options and correct predictions score lower.

| Classes | 5th pct. confidence (correct) | Threshold | Coverage |
|--------:|------------------------------:|----------:|---------:|
|       5 |                          ~1.00 |      0.80 |      n/a |
|      11 |                          0.47  |      0.50 |    91.5% |
|      16 |                          0.44  |      0.55 |    87.0% |
|      19 |                          0.40  |      0.55 |    85.8% |

At 11 classes the inherited 0.80 threshold was suppressing 25.1% of correct
predictions. Selection rule: the lowest threshold giving >=97% accuracy on
shown predictions with >=85% coverage.

At 16 classes the tuning table became genuinely informative for the first
time: with real errors present, raising the threshold improved accuracy on
shown predictions rather than only suppressing correct ones.

Note: some incorrect predictions carry confidence up to 0.87 (95th
percentile). A threshold cannot remove genuine class confusion — it rejects
unknown input, not misclassification.

## Experiment 13 — Adding similar classes can sharpen boundaries

K scored 82% at 16 classes, with K -> G as the dominant error. After adding
U, V and R — three more members of the two-fingers-raised family — K rose to
97% and K -> G fell to zero.

Additional examples of a crowded region gave the classifier more information
about where the boundary lies, rather than blurring it. Class similarity is
not by itself a reason to expect degradation.

## Experiment 14 — U, V and R are points on a continuum

At 19 classes, R was the weakest letter (f1 0.82), confused with U in one
direction only: R->U 84, U->R 8. Within-session accuracy was 100% for all
letters, ruling out feature-space overlap.

A live top-2 probability overlay showed V at 0.98 when the fingers are
clearly spread, and U:0.49 / V:0.31 when the spread is marginal. U, V and R
differ only in finger separation — crossed, together, apart — which is a
continuum rather than three separable regions. Marginal separations fall near
the U/V boundary by construction.

The perceived sluggishness during live use was the threshold correctly
rejecting an ambiguous shape, not latency. Live smoothing and hold were
retuned from (10, 25) to (7, 15), since the values had been set when the
model had 5 classes and predictions never wavered.

## Experiment 15 — Recording variation, not recording shape

Both R and K failed asymmetrically at some point: the model trained on
session 2 recognised session 1 at 98–100%, while the reverse gave 63–75%.
Within-session accuracy was 100% in every case.

The cause is not an inconsistent shape but an insufficiently varied one.
Session 2 was recorded across a wider range of wrist angles and distances,
covering session 1's narrower distribution; session 1 does not cover session
2's.

An attempt to fix K by re-recording session 1 "with wider variation" sent K
to 0%, with all 300 samples classified as D. Widening the variation had
changed the finger position rather than the viewing conditions. Re-recording
both sessions with a fixed shape and varied wrist angle restored K to 100%.

Variation means wrist rotation, distance and tilt. It does not mean varying
the hand shape.

## Experiment 16 — Re-recording three letters at the current camera position

A and B had been recorded before the camera-position change and collapsed in
the reverse direction (A 4% -> I, B 0% -> W). After adding S and T — two more
closed-fist shapes — A collapsed entirely in both directions (A -> S 181,
A -> T 119), dragging S and T's precision down to 0.62 and 0.71.

Re-recording A alone at the current camera position fixed three letters at
once: A returned to 100%, and S and T rose to 1.00 and 0.98 precision as they
stopped absorbing it. Overall accuracy rose from 91.20% to 94.48%.

Re-recording B and K completed the cleanup:

| Change                          | Accuracy |
|---------------------------------|---------:|
| 22 classes, A/B/K legacy data   |   91.20% |
| After re-recording A            |   94.48% |
| After re-recording B and K      |   96.97% |

Session symmetry, which measures whether any letter's data is direction-
dependent:

| Stage                        | 1 -> 2 | 2 -> 1 | Gap  |
|------------------------------|-------:|-------:|-----:|
| B still on old camera data   |  94.5% |  86.1% |  8.4 |
| 19 classes, before cleanup   |  94.5% |  91.9% |  2.6 |
| 22 classes, after cleanup    |  97.0% |  96.8% |  0.2 |

The gap closing to 0.2 points is direct evidence that the camera-position
artefact has been removed from the dataset.

## Phase 8 result

| Classes | Accuracy | Baseline | Ratio |
|--------:|---------:|---------:|------:|
|       5 |    99.8% |    20.0% |  x5.0 |
|      11 |   100.0% |     9.1% | x11.0 |
|      16 |    96.0% |     6.3% | x15.4 |
|      19 |    94.9% |     5.3% | x18.0 |
|      22 |    97.0% |     4.6% | x21.3 |

All 22 letters separate perfectly within a single recording session. The
remaining cross-session error is concentrated in R (75% recall, confused
with U), which is the continuum problem described in Experiment 14.

Live settings, all measured rather than guessed:
confidence threshold 0.55, smoothing window 7 frames, hold-to-commit 15
frames.

## Tooling hardened during Phase 8

Two data-loss incidents and three mis-entered batch numbers were caused by
tools that trusted the operator rather than validating input.

- clean_label.py had the target label hard-coded, and deleted that label on
  every run regardless of intent. It now prompts for the label, accepts an
  optional batch filter, requires the label to be typed twice, and writes a
  backup before deleting.
- collect_data.py accepted any batch number. A double keypress produced
  batch 11 three times, which silently excludes the letter from both the
  training and test split. It now accepts only 1 or 2, and displays the
  active batch on screen throughout recording.

## Known limitations

- J and Z excluded (require motion; need a sequential model)
- M and N not yet attempted: the distinguishing feature is thumb position
  beneath the fingers, which is occluded from the camera, so MediaPipe infers
  rather than measures those landmarks
- Single hand only; does not work mirrored
- Normalisation handles translation and scale, not rotation
- Two recording sessions, one signer
- U/V/R separation degrades on marginal finger spread (Experiment 14)
- No negative class: non-letter hand shapes are rejected by threshold rather
  than classified as "not a letter". A resting hand fell near Q and had to be
  suppressed by raising the threshold. A trained NONE class would address the
  cause and permit a lower threshold. Deferred.