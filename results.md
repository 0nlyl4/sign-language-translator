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