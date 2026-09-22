# Real-Time ASL Fingerspelling Recognition

Real-time recognition of 24 static American Sign Language (ASL) fingerspelling letters from webcam video. Trained on hand-landmark coordinates from MediaPipe, not raw images, achieving 97.17% accuracy across independent recording sessions.

**[Live Demo](https://0nlyl4.github.io/sign-language-translator/)** | **[GitHub Repository](https://github.com/0nlyl4/sign-language-translator/)**

This recognizes 24 static handshapes from the ASL fingerspelling alphabet. J and Z are excluded because they require motion, and a single static frame cannot capture a path. This is fingerspelling recognition, not full sign language translation.

---

## Key Results

- **97.17% cross-session accuracy** on 24 static ASL fingerspelling letters
- **4.17% random-guess baseline** (1 out of 24 classes)
- **14,400 landmark samples** (24 letters × 2 sessions × 300 samples each)
- **Two independent recording sessions** with different lighting, distance, background, and hand angles
- **One participant, right hand** — generalization to other signers has not been evaluated

---

## Features

- **Real-time webcam recognition** at camera frame rate
- **MediaPipe hand tracking** extracts 21 3D joint positions (63 coordinates)
- **Normalized landmark features** invariant to hand position and scale
- **Random Forest classifier** with 100 decision trees
- **Confidence thresholding** (60%) rejects ambiguous or unknown shapes
- **Temporal smoothing** (7-frame majority vote) reduces frame-to-frame flicker
- **Hold-to-commit** (15 frames) distinguishes intentional signs from transitions
- **Client-side inference** in the browser — camera video is processed locally and never uploaded

---

## How It Works

```
Camera frame
    ↓
MediaPipe hand tracking (21 landmarks)
    ↓
Normalization (wrist-centered, scale-invariant)
    ↓
Random Forest classifier (100 trees)
    ↓
Confidence threshold (60%)
    ↓
Temporal smoothing (7-frame majority vote)
    ↓
Hold-to-commit (15 consecutive frames)
    ↓
Committed letter
```

Each stage addresses a specific failure mode:

| Stage | Problem Solved |
|-------|----------------|
| MediaPipe landmarks | Lighting and background variance |
| Normalization | Hand position and distance from camera |
| Random Forest | Shape recognition |
| Confidence threshold | Forced predictions on unknown input |
| Temporal smoothing | Frame-to-frame flicker and misreads |
| Hold-to-commit | Unintentional letters during transitions |

---

## Quick Start

### Try Online

Visit the live demo: **[https://0nlyl4.github.io/sign-language-translator/](https://0nlyl4.github.io/sign-language-translator/)**

Your browser will request camera permission. The camera feed is processed entirely on your device and is not uploaded, stored, or recorded.

### Run Locally (Web Version)

Serve the web application from the repository:

```bash
python -m http.server 8000 --directory web
```

Open in your browser:

```
http://localhost:8000/
```

The browser will request camera access. All inference runs locally in JavaScript.

**Controls available on the page:**
- Letter buttons to select reference handshapes
- Add space button
- Delete button
- Clear button
- Mirror camera button

**Keyboard shortcuts** (when not focused on a button):
- `Space` — add space to output
- `Backspace` — delete last character

---

## Project Structure

```
sign-language-translator/
├── data/
│   └── landmarks.csv          # 14,400 samples: label, batch, x0..z20
├── models/
│   └── model.pkl              # Trained Random Forest (4.5 MB)
├── reference/
│   └── [A-Y].png              # Reference handshape images (24 letters)
├── src/
│   ├── features.py            # normalize_landmarks() — core transformation
│   ├── collect_data.py        # Record 300 samples per letter with MediaPipe
│   ├── train_model.py         # Train Random Forest on all data
│   ├── predict_live.py        # Real-time recognition with OpenCV (Python)
│   ├── evaluate_generalization.py  # Cross-session train/test split
│   └── [other scripts]        # Diagnostics, threshold tuning, data cleaning
├── web/
│   ├── index.html             # Landing page
│   ├── app.html               # Interactive recognition interface
│   ├── model.json             # Exported Random Forest (318 KB)
│   ├── shapes.json            # Median handshapes for visualization
│   └── letters/               # SVG reference handshapes
├── results.md                 # Full experimental methodology and history
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Technology Stack

**Python Environment:**
- Python 3.11.9
- MediaPipe 0.10.21 (hand tracking)
- scikit-learn 1.9.0 (Random Forest)
- opencv-python 5.0.0.93 (video capture and display)
- numpy 1.26.4
- pandas 3.0.5

**Browser Environment:**
- MediaPipe Tasks Vision 0.10.21 (hand tracking in JavaScript)
- Exported Random Forest walked in JavaScript (no server)
- Vanilla JavaScript (no frameworks)

**Deployment:**
- GitHub Pages (static site, no backend)

---

## Evaluation Methodology

The model was trained on all 300 samples per letter from **session 1** and evaluated on all 300 samples per letter from **session 2**. The two sessions were recorded on different days with deliberate variation in lighting, distance, background, and hand tilt, but the same camera position relative to the participant.

**Why cross-session evaluation matters:** Evaluating on a random 20% split from a single continuous recording is misleading because consecutive video frames are nearly identical. This causes near-duplicate samples to leak from training into the test set, producing artificially high accuracy (100% within-session vs. 97.17% cross-session). Cross-session evaluation measures whether the model generalizes to new recording conditions rather than memorizing individual frames.

See **[results.md](results.md)** for the full experimental history, including 16 experiments documenting the progression from 5 letters at 47.9% raw-coordinate accuracy to 24 letters at 97.17% with normalized features.

---

## Limitations

- **J and Z are excluded.** Both require motion to distinguish from other letters. A static-frame classifier cannot recognize drawn paths.
- **Single hand orientation.** All data was recorded with the right hand facing the camera from a consistent position. The model has not been evaluated on mirrored or rotated orientations.
- **One participant, two sessions.** Generalization to other signers, hand sizes, or skin tones has not been tested.
- **No rotation normalization.** The feature normalization handles translation and scale, but not wrist rotation. Letters with directional meaning (G, H, P, Q) expect the hand to face the camera similarly to how it was recorded.
- **U, V, and R are close.** These three letters differ only in finger spacing (crossed, together, apart), which forms a continuum rather than three cleanly separated regions. Marginal finger spreads can fall near decision boundaries.
- **Fingerspelling only.** This recognizes 24 static handshapes from the manual alphabet. It does not recognize full ASL grammar, word-level signs, classifiers, facial expressions, or non-manual markers. ASL is a complete language with its own syntax and is not English encoded in gestures.

---

## Privacy

The browser-based demo processes camera frames entirely on your device using JavaScript. Camera video is **not uploaded, stored, or recorded** by the website. The hand-tracking model and the recognition model both run locally in your browser. No frames, landmarks, or predictions are transmitted to a server.

---

## Acknowledgments

- **MediaPipe** (Google) for the hand-tracking model
- **scikit-learn** for the Random Forest implementation

---

## About This Project

This was built as a portfolio project to demonstrate end-to-end machine learning development: data collection, feature engineering, model training, evaluation, deployment, and documentation. The focus was on building a system that works in practice, measuring what matters (cross-session accuracy, not within-session), and documenting the experimental process honestly.
