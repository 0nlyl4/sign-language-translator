# مشروع مستمر: مترجم لغة الإشارة الأمريكية (ASL) في الوقت الفعلي

**هذا ملف تسليم كامل (handoff).** المشروع بدأ في شات سابق وأُكمل عبر عدة شاتات. أكمل من حيث توقفنا بنفس الأسلوب بالضبط.

**الحالة الحالية باختصار:** المرحلة 7 و 8 مكتملتان. 24 حرفاً بدقة 97.17% عبر جلستين مستقلتين. بدأنا للتو المرحلة 9 (النشر على الويب) وأنجزنا أول خطوة فيها.

---

# 1. أسلوب العمل المتفق عليه — مهم جداً

- **أنا طالب**، أخذت Python ترماً واحداً فقط، وهذا **أول مشروع أعمله لوحدي**
- **أتحدث العربية** — كل الردود بالعربية
- **قاعدة أساسية:** لا ننتقل لخطوة جديدة قبل أن أفهم ما فعلته الخطوة السابقة. المطلوب أن أفهم الفكرة لا أن أحفظ الكود
- **الشرح قبل الكود دائماً** — لماذا نفعل هذا، ثم الكود، ثم شرح السطور المهمة
- **الشرح بلغة بسيطة تُفهم** — لا مصطلحات بلا تفسير
- **قائمة واحدة مرتبة** لكل مرحلة، لا ردود متفرقة أنطّ بينها
- **بعد كل خطوة: علامة نجاح واضحة** (ماذا يجب أن أرى) قبل الانتقال للتالية
- **المصطلحات تُشرح ببساطة** أول مرة تُذكر
- أرسل صور شاشة للأخطاء والمخرجات — اقرأها وشخّص منها

## قواعد إضافية اتُفق عليها أثناء العمل

- **عند أي تعديل على كود: أعطني الملف كاملاً**، لا أجزاء. مع **جدول "ما تغيّر"** في الأعلى بسطرين أو ثلاثة
- **لا كومنتات عربية داخل الكود** ولا شرح داخل الكود. التعليقات الإنجليزية القصيرة فقط (عناوين أقسام). الشرح كله **خارج** الكود
- **"الملف الكامل" يعني: استبدل كل محتوى الملف** بما أُرسل. إن كانت إضافة جزئية، يُقال ذلك صراحة
- **كل ما في مربع رمادي = أمر يُكتب في الترمنال**، إلا إذا قيل صراحة إنه كود يوضع في ملف
- **لا تفترض محتوى ملف لم تره.** اطلب الملف قبل استبداله. (حدث خطأ مرة بسبب هذا: أُرسل `[features]` بينما الملف يحتوي `.reshape(1, -1)` أصلاً)
- **التوثيق يُؤجَّل ويُكتب دفعة واحدة** حين أطلبه، لا بعد كل خطوة

## السبب وراء هذا الأسلوب

المشروع للـ resume، وفي المقابلة سيسألونني "لماذا اخترت كذا؟" — فلا فائدة من كود لا أفهمه.

---

# 2. البيئة التقنية

- **ويندوز**، PowerShell، VS Code (إضافة Python الرسمية منصّبة)
- **المسار:** `Y:\l4\uni\MyProjects\sign-language-translator`
- **Python 3.11.9** منصّب بجانب 3.13 الافتراضي للجهاز
  - إنشاء البيئة: `py -3.11 -m venv venv`
  - التفعيل: `venv\Scripts\activate` — علامة النجاح: ظهور `(venv)` في بداية السطر
- **الكاميرا:** لا توجد كاميرا في الجهاز. أستخدم **آيباد عبر Iriun Webcam** (فهرس 0، دقة 640x480)
- **GitHub:** `github.com/0nlyl4/sign-language-translator` (الحساب المعتمد: `0nlyl4`)
- كل الأوامر تُنفَّذ في ترمنال VS Code

## تنبيه PowerShell مهم

**`&&` لا تعمل** في نسخة PowerShell عندي. الأوامر تُكتب على أسطر منفصلة:

```
git add .
```
```
git commit -m "..."
```
```
git push
```

## المكتبات

```
opencv-python · mediapipe==0.10.21 · scikit-learn · numpy · pandas · joblib
```

**مهم:** `mediapipe==0.10.21` **مثبّتة عمداً**. الإصدارات 0.10.31+ أزالت واجهة `mp.solutions` القديمة (`AttributeError: module 'mediapipe' has no attribute 'solutions'`). Google أوقفت دعم legacy solutions. **لا تقترح ترقيتها.**

---

# 3. الفكرة التقنية

لا نُعطي النموذج صوراً. MediaPipe يحوّل اليد إلى **21 نقطة** لكل منها (x, y, z) = **63 رقماً**. ندرّب مصنّفاً على هذه الأرقام.

**الفائدة:** سريع (real-time على CPU)، بيانات أقل بكثير (300 عينة/حرف)، ومقاوم للإضاءة والخلفية.

## الأنبوب (pipeline) — ست مراحل

```
صورة الكاميرا
    ↓  MediaPipe
21 نقطة = 63 رقماً
    ↓  normalize_landmarks()
63 رقماً مطبَّعاً
    ↓  RandomForest
حرف + نسبة ثقة
    ↓  العتبة (0.60)
حرف أو رفض (?)
    ↓  التنعيم (7 إطارات)
حرف مستقر
    ↓  التثبيت (15 إطاراً)
نص على الشاشة
```

| الطبقة | المدخل | المخرج | المشكلة التي تحلها |
|---|---|---|---|
| Landmarks | إطار كاميرا | 63 إحداثياً | تباين الإضاءة والخلفية |
| Normalize | 63 خاماً | 63 مطبَّعاً | موضع اليد ومسافتها |
| Classify | 63 مطبَّعاً | حرف + ثقة | التعرف على الشكل |
| Threshold | حرف + ثقة | حرف أو رفض | مخرج واثق على مدخل مجهول |
| Smooth | حروف لكل إطار | حرف مستقر | الرجفان بين الإطارات |
| Commit | حرف مستقر | نص | القصد مقابل الوجود المستمر |

---

# 4. القرارات التقنية وأسبابها

| القرار | السبب |
|---|---|
| نقاط بدل صور خام | سرعة + بيانات أقل + مقاومة للإضاءة |
| `max_num_hands=1` | أبجدية ASL كلها بيد واحدة؛ يمنع التباس أيدي الخلفية |
| يد واحدة ثابتة في كل التسجيلات | اليمنى واليسرى صورتان معكوستان = أرقام مختلفة تماماً |
| **حفظ البيانات خام** (غير معالجة) | سمح بتطبيق التطبيع لاحقاً بدون إعادة تسجيل |
| استبعاد J و Z | يحتاجان حركة؛ النظام يصنّف لقطات ساكنة ← الهدف 24 حرفاً |
| CSV واحد بعمود `batch` | بدل ملف لكل دفعة؛ سمح بالتصحيح والحذف الانتقائي عدة مرات |
| تثبيت إصدارات المكتبات | مشروع قابل لإعادة الإنتاج |
| **التطبيع يُطبَّق بنفس الطريقة في التدريب والتنبؤ** | أي اختلاف = النموذج يستقبل ما لم يتدرب عليه |
| العتبة والتنعيم والتثبيت **تُقاس لا تُخمَّن** | جواب "لماذا هذا الرقم؟" في المقابلة |
| لقطة مرجعية لكل حرف قبل التسجيل | أثبتت البيانات نفسها أنها تعمل (انظر تجربة 9) |

## معنى `batch` — أهم نقطة في إدارة البيانات

**`batch` = رقم الجلسة، لا مجموعة الحروف.**

- `batch = 1` ← الجلسة الأولى
- `batch = 2` ← جلسة ثانية لنفس الحروف في **ظرف مختلف**

**رقمان فقط في المشروع: 1 و 2.** أي رقم آخر يعني أن الحرف يختفي بصمت من التدريب والاختبار معاً، لأن `evaluate_generalization.py` مبني على `batch == 1` للتدريب و `batch == 2` للاختبار.

## بروتوكول التسجيل (تطوّر بالتجربة)

**ما يجب أن يتغيّر بين الجلستين:** الإضاءة، المسافة، الخلفية، ميلان اليد.

**ما يجب ألا يتغيّر:** **موضع الكاميرا حول الجسم**. نقل الآيباد من جهة لأخرى يخرق قيد الدوران (انظر تجربة 11).

**التنويع أثناء التسجيل يعني:** دوران معصم، تقريب وتبعيد، ميلان.
**لا يعني:** تغيير شكل اليد أو موضع الأصابع. (خطأ كلّف حرف `K` نزوله إلى 0% — انظر تجربة 15)

---

# 5. هيكل المشروع

```
sign-language-translator/
├── src/
│   ├── features.py                ← جوهر المشروع: normalize_landmarks()
│   ├── collect_data.py            ← تسجيل 300 عينة/حرف + تحقق من المُدخَل
│   ├── train_model.py             ← تدريب على كل البيانات ← models/model.pkl
│   ├── predict_live.py            ← تنبؤ حي + عتبة + تنعيم + تجميع كلمات
│   ├── evaluate_generalization.py ← تدريب batch1 / اختبار batch2 (مُصلَح)
│   ├── diagnose.py                ← 4 تجارب: داخل الجلستين + الاتجاهين
│   ├── tune_threshold.py          ← قياس العتبة لا تخمينها
│   ├── clean_label.py             ← حذف حرف (وربما دفعة معينة) بأمان
│   ├── reference_points.py        ← طباعة نقاط مرجعية للمقارنة مع JS
│   ├── compare_features.py        ← خام مقابل مطبَّع (لا تلمسه — الخام مقصود فيه)
│   ├── hand_tracking.py           ← عرض النقاط لأخذ اللقطات المرجعية
│   ├── diagnose_c.py              ← قديم، استُبدل بـ diagnose.py
│   ├── test_camera.py             ← (لم يعد مستخدماً)
│   └── find_camera.py             ← (لم يعد مستخدماً)
├── web/
│   └── index.html                 ← صفحة اختبار MediaPipe JS (الخطوة 9.1)
├── reference/                     ← لقطة مرجعية لكل حرف (24 صورة)
├── data/landmarks.csv             ← label, batch, x0..z20 — 14,400 صف
├── models/model.pkl               ← 4.5 MB · 100 شجرة · 17,492 عقدة
├── results.md                     ← جدول التجارب + تحليل الأخطاء
├── requirements.txt
└── .gitignore                     ← venv/ __pycache__/ *.pyc .DS_Store
```

---

# 6. الأكواد الحالية بالكامل

## `src/features.py` — الدالة المحورية

```python
def normalize_landmarks(row):
    points = np.array(row, dtype=float).reshape(21, 3)
    points = points - points[0]          # الرسغ = نقطة الصفر
    max_dist = np.linalg.norm(points, axis=1).max()
    if max_dist > 0:
        points = points / max_dist       # توحيد الحجم
    return points.flatten()
```

**ملاحظة:** الملف يبدأ بـ `import numpy as np`. الدالة تعالج الإزاحة والحجم — **لا الدوران**، وهذا قيد مقيس فعلياً.

---

## `src/predict_live.py` (الحالي — الإعدادات مقاسة)

```python
import cv2
import mediapipe as mp
import joblib
import numpy as np

from collections import deque, Counter
from features import normalize_landmarks


MODEL_PATH = "models/model.pkl"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.60
SMOOTHING_WINDOW = 7
HOLD_FRAMES = 15

GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


model = joblib.load(MODEL_PATH)
print(f"Model loaded. Knows: {list(model.classes_)}")
print(f"Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
print(f"Smoothing window: {SMOOTHING_WINDOW} frames")
print(f"Hold to commit: {HOLD_FRAMES} frames")
print("Keys: [space] space   [backspace] delete   [c] clear   [q] quit")


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Running.")

history = deque(maxlen=SMOOTHING_WINDOW)
sentence = ""
hold_letter = None
hold_count = 0
committed = False


while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        row = []
        for lm in landmarks.landmark:
            row += [lm.x, lm.y, lm.z]

        features = normalize_landmarks(row).reshape(1, -1)

        probs = model.predict_proba(features)[0]
        best = probs.argmax()
        prediction = model.classes_[best]
        confidence = probs[best]

        if confidence >= CONFIDENCE_THRESHOLD:
            history.append(prediction)
        else:
            history.append(None)

        stable_letter, votes = Counter(history).most_common(1)[0]

        if stable_letter == hold_letter:
            hold_count += 1
        else:
            hold_letter = stable_letter
            hold_count = 1
            committed = False

        if stable_letter is not None and not committed and hold_count >= HOLD_FRAMES:
            sentence += stable_letter
            committed = True

        if stable_letter is not None:
            display_text = stable_letter
            color = GREEN
        else:
            display_text = "?"
            color = RED

        cv2.putText(frame, display_text, (250, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 4, color, 8)
        cv2.putText(frame, f"{confidence:.0%}", (250, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if stable_letter is not None:
            progress = min(hold_count / HOLD_FRAMES, 1.0)
            cv2.rectangle(frame, (250, 230), (400, 245), color, 1)
            cv2.rectangle(frame, (250, 230), (250 + int(150 * progress), 245),
                          color, -1)
    else:
        history.clear()
        hold_letter = None
        hold_count = 0
        committed = False
        cv2.putText(frame, "No hand", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, h - 60), (w, h), BLACK, -1)
    cv2.putText(frame, sentence[-20:], (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, WHITE, 2)

    cv2.imshow("Sign Language Translator", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 32:
        sentence += " "
    elif key == 8:
        sentence = sentence[:-1]
    elif key == ord('c'):
        sentence = ""


cap.release()
cv2.destroyAllWindows()
print(f"Final output: {sentence}")
```

### منطق التثبيت والقفل (مهم لفهمه)

- `hold_count` يتصاعد ما دام الحرف المستقر هو نفسه
- عند تغيّر الحرف: يُصفَّر العدّاد ويُفتح القفل (`committed = False`)
- الحرف يُضاف مرة واحدة فقط، ولا يُضاف ثانية حتى **يتغيّر** الحرف المستقر
- **قيد معروف:** الحرف المكرر (`LL`) يحتاج كسر الشكل بين المرتين
- الإطار الضعيف يدخل التاريخ كـ `None` (صوت رفض) لا يُتجاهل — وإلا بقي الحرف القديم معروضاً بعد أن تحركت اليد

---

## `src/collect_data.py` (مع التحقق من المُدخَل)

```python
import cv2
import mediapipe as mp
import csv
import os
import time

# ---------- Settings ----------
SAMPLES_PER_LETTER = 300
COUNTDOWN_SECONDS = 3
CSV_PATH = "data/landmarks.csv"
VALID_BATCHES = ("1", "2")
# ------------------------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


def create_csv_if_needed():
    if not os.path.exists(CSV_PATH):
        header = ["label", "batch"]
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(header)
        print(f"Created {CSV_PATH}")


def ask_batch():
    while True:
        value = input("Batch (1 or 2): ").strip()
        if value in VALID_BATCHES:
            return value
        print(f"Invalid batch '{value}'. Enter 1 or 2 only.")


def ask_label():
    while True:
        value = input("\nLetter (or 'exit' to quit): ").strip().upper()
        if value == "EXIT":
            return None
        if len(value) == 1 and value.isalpha():
            return value
        print("Enter a single letter A-Z.")


def extract_landmarks(hand_landmarks):
    row = []
    for lm in hand_landmarks.landmark:
        row += [lm.x, lm.y, lm.z]
    return row


def collect(label, batch):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    collected = []
    state = "countdown"
    start_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        hand_found = False
        if results.multi_hand_landmarks:
            hand_found = True
            landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        if state == "countdown":
            remaining = COUNTDOWN_SECONDS - int(time.time() - start_time)
            if remaining > 0:
                cv2.putText(frame, str(remaining), (280, 250),
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 6)
                cv2.putText(frame, f"Get ready: {label}  (batch {batch})", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            else:
                state = "capturing"

        elif state == "capturing":
            if hand_found:
                collected.append(extract_landmarks(landmarks))

            count = len(collected)
            cv2.putText(frame, f"{label}:  {count}/{SAMPLES_PER_LETTER}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"batch {batch}", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            bar_width = int((count / SAMPLES_PER_LETTER) * 400)
            cv2.rectangle(frame, (10, 60), (410, 85), (80, 80, 80), -1)
            cv2.rectangle(frame, (10, 60), (10 + bar_width, 85), (0, 255, 0), -1)

            if not hand_found:
                cv2.putText(frame, "NO HAND - paused", (10, 145),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if count >= SAMPLES_PER_LETTER:
                break

        cv2.imshow("Collecting Data", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            collected = []
            print("Cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if collected:
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            for row in collected:
                writer.writerow([label, batch] + row)
        print(f"Saved {len(collected)} samples for '{label}' (batch {batch})")


def main():
    create_csv_if_needed()

    batch = ask_batch()
    print(f"Recording session: batch {batch}")

    while True:
        label = ask_label()
        if label is None:
            break
        print(f"-> {label}, batch {batch}")
        collect(label, batch)

    print("\nDone.")


main()
```

---

## `src/clean_label.py` (يسأل، يؤكد، ينسخ احتياطياً)

```python
import sys
import shutil
import pandas as pd

CSV_PATH = "data/landmarks.csv"
BACKUP_PATH = "data/landmarks_backup.csv"

df = pd.read_csv(CSV_PATH)

print(df.groupby(["label", "batch"]).size())

target = input("\nLabel to remove: ").strip().upper()

if target not in df["label"].unique():
    print(f"'{target}' not found. Nothing removed.")
    sys.exit()

batch_input = input("Batch (1, 2, or blank for all): ").strip()

mask = df["label"] == target
scope = f"'{target}' (all batches)"

if batch_input:
    batch = int(batch_input)
    mask = mask & (df["batch"] == batch)
    scope = f"'{target}' batch {batch}"

count = mask.sum()

if count == 0:
    print(f"No rows match {scope}. Nothing removed.")
    sys.exit()

print(f"This will remove {count} rows for {scope}.")

if input("Type the label again to confirm: ").strip().upper() != target:
    print("Cancelled. Nothing removed.")
    sys.exit()

shutil.copy(CSV_PATH, BACKUP_PATH)
print(f"Backup saved to {BACKUP_PATH}")

df = df[~mask]
df.to_csv(CSV_PATH, index=False)

print(f"Removed {count} rows for {scope}")
print(f"Remaining: {len(df)} rows")
print(df.groupby(["label", "batch"]).size())
```

---

## `src/evaluate_generalization.py` (بعد إصلاح التطبيع)

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from features import normalize_landmarks

CSV_PATH = "data/landmarks.csv"

df = pd.read_csv(CSV_PATH)

train_df = df[df["batch"] == 1]
test_df = df[df["batch"] == 2]

print(f"Train (session 1): {len(train_df)} samples")
print(f"Test  (session 2): {len(test_df)} samples")

X_train = np.array([normalize_landmarks(r)
                    for r in train_df.drop(columns=["label", "batch"]).values])
y_train = train_df["label"]
X_test = np.array([normalize_landmarks(r)
                   for r in test_df.drop(columns=["label", "batch"]).values])
y_test = test_df["label"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
baseline = 1 / len(y_train.unique())

print("\n" + "=" * 45)
print("CROSS-SESSION EVALUATION")
print(f"Accuracy:  {accuracy:.2%}")
print(f"Baseline:  {baseline:.2%}")
print("=" * 45)

print("\nPer-letter report:")
print(classification_report(y_test, y_pred))

print("Confusion matrix:")
labels = sorted(y_train.unique())
print("     " + "  ".join(labels))
cm = confusion_matrix(y_test, y_pred, labels=labels)
for i, row in enumerate(cm):
    print(f"{labels[i]}  " + "  ".join(f"{v:3d}" for v in row))
```

---

## `src/diagnose.py` (أداة التشخيص المحورية)

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from features import normalize_landmarks

df = pd.read_csv("data/landmarks.csv")


def prep(d):
    X = np.array([normalize_landmarks(r)
                  for r in d.drop(columns=["label", "batch"]).values])
    return X, d["label"].values


def run(train_df, test_df, name):
    X_train, y_train = prep(train_df)
    X_test, y_test = prep(test_df)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    print(f"\n=== {name} ===")
    print(f"overall: {(pred == y_test).mean():.1%}")
    for letter in sorted(set(y_test)):
        mask = y_test == letter
        acc = (pred[mask] == letter).mean()
        wrong = pred[mask][pred[mask] != letter]
        top = pd.Series(wrong).value_counts()
        confused = f"-> {top.index[0]}" if len(top) else ""
        print(f"  {letter}: {acc:>5.0%}  {confused}")


b1 = df[df["batch"] == 1]
b2 = df[df["batch"] == 2]

tr, te = train_test_split(b1, test_size=0.2, random_state=42,
                          stratify=b1["label"])
run(tr, te, "WITHIN session 1")

tr, te = train_test_split(b2, test_size=0.2, random_state=42,
                          stratify=b2["label"])
run(tr, te, "WITHIN session 2")

run(b1, b2, "session 1 -> session 2")
run(b2, b1, "session 2 -> session 1")
```

### كيف تُقرأ نتيجته — الجدول المرجعي

| ما تراه | المعنى | العلاج |
|---|---|---|
| 100% داخل الجلستين + فشل بينهما | شكلان تحت اسم واحد | إعادة تسجيل بشكل مرجعي |
| فاشل **حتى داخل** الجلسة | تداخل حقيقي في الملامح | ملامح أفضل — لا إعادة تسجيل |
| يلتبس مع حرف **مختلف** حسب الاتجاه | تناقض بيانات | إعادة تسجيل |
| يلتبس مع **نفس** الحرف في الاتجاهين | تداخل مستقر | ملامح أفضل |
| اتجاه واحد ممتاز والآخر سيّئ | تنويع ضيق في الجلسة الضعيفة | إعادة تسجيل تلك الجلسة بتنويع أوسع |

**تنبيه:** نتائج "داخل الجلسة" مضخّمة عمداً (فيها تسريب بيانات). تُستخدم **كأداة تشخيص لا كمقياس أداء** — والمنطق قوي بسببه: إن فشل حرف حتى مع التسريب، فتداخله حقيقي بلا شك.

---

## `src/tune_threshold.py`

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from features import normalize_landmarks

df = pd.read_csv("data/landmarks.csv")

train_df = df[df["batch"] == 1]
test_df = df[df["batch"] == 2]

X_train = np.array([normalize_landmarks(r)
                    for r in train_df.drop(columns=["label", "batch"]).values])
y_train = train_df["label"]
X_test = np.array([normalize_landmarks(r)
                   for r in test_df.drop(columns=["label", "batch"]).values])
y_test = test_df["label"].values

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)
pred = model.classes_[proba.argmax(axis=1)]
conf = proba.max(axis=1)
correct = (pred == y_test)

print(f"Classes: {len(model.classes_)}   Baseline: {1/len(model.classes_):.1%}")
print(f"Accuracy (no threshold): {correct.mean():.2%}\n")

print(f"Confidence on CORRECT   predictions: "
      f"mean {conf[correct].mean():.2f}, "
      f"5th percentile {np.percentile(conf[correct], 5):.2f}")

if (~correct).sum() > 0:
    print(f"Confidence on INCORRECT predictions: "
          f"mean {conf[~correct].mean():.2f}, "
          f"95th percentile {np.percentile(conf[~correct], 95):.2f}")
else:
    print("No incorrect predictions in this split.")

print(f"\n{'thresh':>7} {'shown':>8} {'acc_shown':>11} {'rejected':>9}")
print("-" * 40)
for t in [0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9]:
    keep = conf >= t
    if keep.sum() == 0:
        print(f"{t:>7.2f} {0:>8.1%} {'-':>11} {1:>9.1%}")
        continue
    print(f"{t:>7.2f} {keep.mean():>8.1%} "
          f"{correct[keep].mean():>11.2%} {(~keep).mean():>9.1%}")
```

**قاعدة اختيار العتبة:** أقل عتبة تعطي `acc_shown ≥ 97%` مع `shown ≥ 85%`، مع النظر إلى نقطة تناقص العائد.

---

## `src/reference_points.py` (للمقارنة مع JS)

```python
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

KEY_POINTS = [0, 4, 8, 12]

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Hold your hand still. Press 'p' to print, 'q' to quit.")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    landmarks = None
    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        h, w = frame.shape[:2]
        for i in KEY_POINTS:
            lm = landmarks.landmark[i]
            px, py = int(lm.x * w), int(lm.y * h)
            cv2.putText(frame, str(i), (px + 8, py),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.putText(frame, "Press 'p' to print", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No hand", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Reference Points", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p') and landmarks is not None:
        print("")
        for i in KEY_POINTS:
            lm = landmarks.landmark[i]
            print(f"point {i:2d}:  x={lm.x:.4f}  y={lm.y:.4f}  z={lm.z:.4f}")
        print("-" * 42)

cap.release()
cv2.destroyAllWindows()
```

---

## `web/index.html` (صفحة اختبار MediaPipe JS — أُنجزت)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Landmark Check</title>
  <style>
    body { background: #111; color: #eee; font-family: monospace; padding: 20px; }
    canvas { border: 1px solid #444; }
    pre { font-size: 15px; line-height: 1.6; }
    button { font-size: 16px; padding: 8px 20px; margin-top: 10px; }
  </style>
</head>
<body>
  <h3>Landmark Check</h3>
  <video id="video" style="display:none" playsinline></video>
  <canvas id="canvas" width="640" height="480"></canvas>
  <br>
  <button id="printBtn">Print points</button>
  <pre id="output">loading...</pre>

<script type="module">
import { FilesetResolver, HandLandmarker }
  from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/vision_bundle.mjs";

const KEY_POINTS = [0, 4, 8, 12];

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const output = document.getElementById("output");

let landmarks = null;

const vision = await FilesetResolver.forVisionTasks(
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/wasm"
);

const handLandmarker = await HandLandmarker.createFromOptions(vision, {
  baseOptions: {
    modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
  },
  runningMode: "VIDEO",
  numHands: 1,
  minHandDetectionConfidence: 0.7,
  minTrackingConfidence: 0.5
});

const stream = await navigator.mediaDevices.getUserMedia({
  video: { width: 640, height: 480 }
});
video.srcObject = stream;
await video.play();

output.textContent = "ready - hold your hand still, then click Print";

function loop() {
  ctx.save();
  ctx.scale(-1, 1);
  ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
  ctx.restore();

  const result = handLandmarker.detectForVideo(canvas, performance.now());

  if (result.landmarks.length > 0) {
    landmarks = result.landmarks[0];
    ctx.fillStyle = "red";
    for (const lm of landmarks) {
      ctx.beginPath();
      ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 4, 0, 6.29);
      ctx.fill();
    }
    ctx.fillStyle = "yellow";
    ctx.font = "18px monospace";
    for (const i of KEY_POINTS) {
      const lm = landmarks[i];
      ctx.fillText(String(i), lm.x * canvas.width + 8, lm.y * canvas.height);
    }
  } else {
    landmarks = null;
  }

  requestAnimationFrame(loop);
}

loop();

document.getElementById("printBtn").onclick = () => {
  if (!landmarks) {
    output.textContent = "no hand";
    return;
  }
  let text = "";
  for (const i of KEY_POINTS) {
    const lm = landmarks[i];
    text += `point ${String(i).padStart(2)}:  ` +
            `x=${lm.x.toFixed(4)}  y=${lm.y.toFixed(4)}  z=${lm.z.toFixed(4)}\n`;
  }
  output.textContent = text;
};
</script>
</body>
</html>
```

**كيف تُشغَّل:**
```
python -m http.server 8000
```
ثم `http://localhost:8000/web/` في المتصفح. `Ctrl + C` للإيقاف.

**لماذا خادم ولا نفتح الملف مباشرة؟** المتصفح يمنع الكاميرا في صفحات `file://`.

**تنبيه:** Iriun لا يسمح لبرنامجين باستخدام الكاميرا معاً. أغلق نوافذ Python قبل فتح الصفحة.

---

# 7. النتائج الكاملة

## جدول التوسّع

| الحروف | الدقة عبر الجلسات | Baseline | التفوّق |
|---:|---:|---:|---:|
| 5 | 99.8% | 20.0% | ×5.0 |
| 11 | 100.0% | 9.1% | ×11.0 |
| 16 | 96.0% | 6.3% | ×15.4 |
| 19 | 94.9% | 5.3% | ×18.0 |
| 22 | 96.97% | 4.6% | ×21.3 |
| **24** | **97.17%** | **4.17%** | **×23.3** |

## تجارب المرحلة 8 — مفصّلة

### تجربة 9 — انهيار أول توسّع (53.3%)
أُضيفت D E F G H I ← 11 فئة. الدقة نزلت إلى 53.3%.
الحروف الجديدة 88–100%، لكن `A` نزل إلى 1% و `Y` إلى 0% و `L` إلى 56% — **رغم أن بياناتها لم تتغيّر**.
التشخيص: 100% داخل كل جلسة ← لا تداخل ملامح. المشكلة **شكلان تحت اسم واحد**.
السبب: الثلاثة كانت الحروف الوحيدة المسجّلة **بلا لقطة مرجعية**. الستة الجديدة سُجّلت بلقطات وصمدت كلها.
**العلاج:** إعادة تسجيل بلقطات مرجعية. ومنذ ذلك الحين صارت اللقطات إلزامية.

### تجربة 10 — سكربت التقييم كان يقيس الأنبوب الخطأ ⭐
الأرقام تحرّكت 53.3% ← 68.0% ← 57.76% عبر إعادات تسجيل متتالية.
**الأرقام كانت خاطئة.** سكربت تشخيص مستقل على **نفس التقسيم** أعطى 100% بينما التقييم أعطى 57.76%. سكربتان يفعلان الشيء نفسه لا يمكن أن يختلفا.
السبب: `evaluate_generalization.py` كُتب في التجربة 2 حين كانت الملامح خام. حين أُدخل التطبيع في المرحلة 6، حُدّث `train_model.py` و `predict_live.py` ونُسي ملف التقييم. فبقي يقيس **الأداء الخام** — ولهذا كانت أرقامه في نطاق 47–68% المعروف للخام.
**الإصلاح:** تطبيق `normalize_landmarks` في ملف التقييم. النتيجة: 57.76% ← 100.00%.
**الدرس:** حين تغيّر أنبوب المعالجة، ابحث عن **كل** مكان يستهلكه — لا التدريب والتنبؤ فقط. واكتُشف هذا فقط لأن قياسين مستقلين تناقضا. **القياس الواحد لا يمكن فحصه بنفسه.**

### تجربة 11 — موضع الكاميرا يكسر التعميم
100% في اتجاه، 84.2% في العكس، مع 100% داخل الجلسة.
السبب: نُقل الآيباد من جهة الجسم إلى الجهة المقابلة بين الجلستين. التطبيع يعالج الإزاحة والحجم **لا الدوران**، فنفس اليد من الجهة المقابلة = 63 رقماً مختلفاً.
**قياس مباشر لقيد كان موثّقاً قبل أن يُرى.**
**البروتوكول تحدّث:** الإضاءة والمسافة والخلفية والميلان تتغيّر؛ موضع الكاميرا لا.

### تجربة 12 — العتبة تعتمد على عدد الفئات
| الفئات | 5th pct (صحيح) | العتبة | التغطية |
|---:|---:|---:|---:|
| 5 | ~1.00 | 0.80 | — |
| 11 | 0.47 | 0.50 | 91.5% |
| 16 | 0.44 | 0.55 | 87.0% |
| 19 | 0.40 | 0.55 | 85.8% |
| 24 | 0.58 | 0.60 | 92.1% |

عند 11 فئة كانت عتبة 0.80 الموروثة تكتم **25.1%** من التصنيفات الصحيحة.
**ملاحظة:** بعض الأخطاء تأتي بثقة تصل إلى 0.87. **العتبة لا تمنع الالتباس الحقيقي** — هي ترفض المدخل المجهول لا التصنيف الخاطئ.
**ملاحظة مضادة للحدس:** عند 24 فئة **ارتفع** الـ5th percentile إلى 0.58 (بعد أن كان 0.40 عند 19). السبب أن البيانات صارت أنظف بعد إعادة تسجيل A و B و K. **جودة البيانات تغلب عدد الفئات.**

### تجربة 13 — إضافة فئات متشابهة قد تحدّ الحدود
`K` كان 82% عند 16 فئة، وأكبر خطأ فيه `K → G`.
بعد إضافة `U V R` — ثلاثة أعضاء آخرين من عائلة الإصبعين المرفوعين — ارتفع `K` إلى **97%** و `K → G` صار **صفراً**.
**تشابه الفئات ليس بذاته سبباً لتوقّع التدهور.**

### تجربة 14 — U و V و R نقاط على متصل
`R` أضعف حرف (f1 0.82)، يلتبس مع `U` في اتجاه واحد: `R→U` 84 مقابل `U→R` 8.
عرض احتمالي حي (أعلى تنبؤين) أظهر: `V:0.98` حين التباعد واضح، و `U:0.49 / V:0.31` حين التباعد حدّي.
الثلاثة تختلف بـ**تباعد الأصابع فقط** — متشابك / ملتصق / متباعد — وهذا **متصل لا ثلاث مناطق منفصلة**. الأشكال الحدّية تقع على الحدود بالضرورة.
**البطء المُحسّ في الاستخدام الحي كان العتبة ترفض شكلاً غامضاً بشكل صحيح، لا تأخيراً.** وضُبط التنعيم والتثبيت من (10, 25) إلى (7, 15).

### تجربة 15 — التنويع في الظرف لا في الشكل
`R` و `K` فشلا بشكل غير متماثل: التدريب على الجلسة 2 يتعرف على الجلسة 1 بنسبة 98–100%، والعكس 63–75%. 100% داخل الجلسة في الحالتين.
السبب ليس شكلاً غير متسق بل **تنويعاً غير كافٍ**: الجلسة 2 سُجّلت بمدى أوسع من زوايا المعصم والمسافات، فتغطي توزيع الجلسة 1 الأضيق، والعكس لا.
**محاولة فاشلة موثّقة:** إعادة تسجيل `K` في الجلسة 1 "بتنويع أوسع" أرسلته إلى **0%**، وكل الـ300 عينة صُنّفت `D`. التوسيع غيّر **وضع الأصابع** لا ظرف التصوير. أُعيد تسجيل الجلستين بشكل ثابت وزاوية معصم متنوعة فعاد `K` إلى 100%.

### تجربة 16 — إعادة تسجيل ثلاثة حروف بالزاوية الحالية
`A` و `B` سُجّلا قبل تغيير موضع الكاميرا وكانا ينهاران عكسياً (A 4%→I، B 0%→W).
بعد إضافة `S` و `T` — قبضتين أخريين — انهار `A` تماماً في الاتجاهين (A→S 181، A→T 119)، وسحب precision لـ `S` و `T` إلى 0.62 و 0.71.
**إعادة تسجيل `A` وحده أصلحت ثلاثة حروف:** عاد `A` إلى 100%، وارتفع `S` و `T` إلى 1.00 و 0.98 لأنهما توقفا عن ابتلاعه.

| التغيير | الدقة |
|---|---:|
| 22 فئة ببيانات A/B/K القديمة | 91.20% |
| بعد إعادة تسجيل A | 94.48% |
| بعد إعادة تسجيل B و K | **96.97%** |

**تماثل الجلستين** — مقياس هل بيانات أي حرف تعتمد على الاتجاه:

| المرحلة | 1→2 | 2→1 | الفجوة |
|---|---:|---:|---:|
| B ببيانات الكاميرا القديمة | 94.5% | 86.1% | 8.4 |
| 19 فئة قبل التنظيف | 94.5% | 91.9% | 2.6 |
| 22 فئة بعد التنظيف | 97.0% | 96.8% | **0.2** |
| 24 فئة (نهائي) | 97.2% | 96.6% | **0.6** |

انغلاق الفجوة إلى 0.2 دليل مباشر على زوال أثر موضع الكاميرا من البيانات.

### تجربة 17 — M و N: الحجب قرار تسجيل لا حد ثابت
كان متوقعاً أن يكونا الأصعب: قبضتان تختلفان بعدد الأصابع فوق الإبهام (اثنان أو ثلاثة)، والإبهام عادةً محجوب فيقدّر MediaPipe نقاطه بدل قياسها.
**النتيجة:** M بـ 97% recall / 1.00 precision، و N بـ 100% / 0.98، و**صفر التباس بينهما**. والدقة الكلية ارتفعت من 96.97% إلى 97.17%.
**السبب:** سُجّل الشكلان مع دفع طرف الإبهام للخارج من بين الأصابع قدر ما تسمح الإشارة، فبقيت تلك النقاط **مقيسة لا مخمّنة**. الحجب عومل كشيء يُتحكَّم به أثناء التسجيل، لا كخاصية ثابتة للإشارة.
عائلة القبضات المجاورة لم تتأثر: A و S و E عند 100%، و T عند 0.98.

**هذه ثالث مرة يخطئ فيها التوقع النظري** بعد P/Q مع الدوران و K مع إضافة U/V/R. **القياس أوثق من التوقع.**

---

# 8. الحالة الحالية بالضبط

## البيانات والنموذج

- **24 حرفاً:** A B C D E F G H I K L M N O P Q R S T U V W X Y (بلا J و Z)
- **14,400 عينة** = 24 حرفاً × جلستين × 300
- **`models/model.pkl`:** 4.5 MB · 100 شجرة · 17,492 عقدة (≈175 عقدة/شجرة — نموذج صغير جداً)
- **الدقة عبر الجلسات: 97.17%** · baseline 4.17%
- **داخل كل جلسة: 100%** لكل الحروف — لا تداخل حقيقي في أي مكان
- **تماثل الاتجاهين:** 97.2% / 96.6%

## الإعدادات الحية (كلها مقاسة)

```python
CONFIDENCE_THRESHOLD = 0.60
SMOOTHING_WINDOW = 7
HOLD_FRAMES = 15
```

## الأخطاء المتبقية في التقييم

```
R → U : 75     (recall 75% — الضعف الوحيد المعتبر)
G → O : 31
O → E : 28
P → D : 14
```

## النقاط المرجعية لمقارنة MediaPipe (كف مفتوح، أصابع لأعلى)

**من Python:**
```
point  0:  x=0.2738  y=0.7321  z=0.0000
point  4:  x=0.4528  y=0.6078  z=-0.0602
point  8:  x=0.4194  y=0.3912  z=-0.0603
point 12:  x=0.3604  y=0.3397  z=-0.0556
```

**من المتصفح** (يد أبعد وفي موضع مختلف، فالمقارنة الخام غير صالحة):
```
point  0:  x=0.1976  y=0.7858  z=0.0000
point  4:  x=0.3465  y=0.6217  z=-0.0391
point  8:  x=0.3168  y=0.4619  z=-0.0388
point 12:  x=0.2597  y=0.4184  z=-0.0362
```

**ما تأكّد:** ترتيب النقاط متطابق (0 رسغ، 4 إبهام، 8 سبابة، 12 وسطى) · `z=0` عند الرسغ في الاثنين · المدى 0–1 · العكس بنفس الاتجاه.
**ما لم يتأكد قطعياً:** التطابق العددي بعد التطبيع، لأن اليد لم تكن في نفس الوضع تماماً. الحساب اليدوي أعطى فروقاً صغيرة في نطاق اختلاف الوضع. **القرار: المضي وإثبات التطابق بالنتيجة النهائية (هل يتعرف النموذج على الحرف؟) بدل إطالة مقارنة الأرقام.**

---

# 9. المشاكل المتكررة والفخاخ (تعلَّمناها بثمن)

| الخطأ | تكرر | الحالة |
|---|---|---|
| `batch 11` بضغطة مزدوجة | 3 مرات (E, L, O) | ✅ مُنع بالتحقق في `collect_data.py` |
| `clean_label.py` يحذف الحرف الخطأ | مرتان (حذف `C` مرتين) | ✅ مُنع بالسؤال والتأكيد والنسخة الاحتياطية |
| `git checkout` ألغى عملاً صحيحاً | مرة | ⚠️ يحتاج عادة: **commit فور كل نقطة شغالة** |
| شكل يد غير ثابت بين الجلستين | 4 حروف (A L Y C) | ⚠️ يحتاج انضباط اللقطة المرجعية |
| سكربت يقيس الأنبوب الخطأ | مرة | ✅ أُصلح — لكن افحص أي سكربت جديد |
| `&&` في PowerShell | مرة | ⚠️ اكتب الأوامر على أسطر منفصلة |
| توسيع "التنويع" غيّر الشكل | مرة (K → 0%) | ⚠️ التنويع = الظرف لا الشكل |

## قواعد الأمان الثلاث

**1. `commit` فور كل تسجيل ناجح** — لا تنتظر نهاية المرحلة. `git checkout` يعيد الملف لآخر commit، فاجعل آخر commit هو عملك الأخير.

**2. اللقطة المرجعية مفتوحة أثناء التسجيل** لا قبله فقط.

**3. لا تحرّك الآيباد** حول الجسم بين الجلستين.

## أمر التحقق القياسي بعد كل تسجيل

```
python -c "import pandas as pd; df=pd.read_csv('data/landmarks.csv'); print(df.groupby(['label','batch']).size())"
```

أو للحروف المحددة فقط:

```
python -c "import pandas as pd; df=pd.read_csv('data/landmarks.csv'); print(df[df['label'].isin(['X','Y'])].groupby(['label','batch']).size()); print('total labels:', len(df['label'].unique()))"
```

## تصحيح رقم دفعة خاطئ

```
copy data\landmarks.csv data\landmarks_backup.csv
```
```
python -c "import pandas as pd; df=pd.read_csv('data/landmarks.csv'); df.loc[(df['label']=='X') & (df['batch']==11), 'batch']=1; df.to_csv('data/landmarks.csv', index=False); print(df.groupby(['label','batch']).size())"
```

---

# 10. القيود المعروفة (موثّقة عمداً في results.md)

- **J و Z مستبعدان** — يحتاجان حركة؛ يتطلبان نموذجاً تسلسلياً
- **التطبيع يعالج الإزاحة والحجم لا الدوران** — قيد مقيس فعلياً (تجربة 11)، ويُلاحظ حياً: الحروف ذات الاتجاه القوي (G H P Q L Y) تتطلب من المستخدم مواجهة نفس اتجاه التسجيل، بينما الأشكال شبه المتماثلة دورانياً (A S E O) متسامحة
- **يد واحدة فقط** — لا يعمل مع اليد المعكوسة
- **جلستا تسجيل فقط، لشخص واحد**
- **U/V/R** تتدهور مع التباعد الحدّي (تجربة 14)
- **لا فئة سالبة (NONE)** — أشكال اليد غير الحرفية تُرفض بالعتبة لا تُصنَّف كـ"ليس حرفاً". اليد المرتخية وقعت قرب `Q` (لأن `Q` هو `G` متجهاً لأسفل، واليد المرتخية تتدلى لأسفل) واضطررنا لرفع العتبة. **فئة NONE مدرَّبة تعالج السبب وتسمح بعتبة أقل. مؤجَّلة عمداً.**

---

# 11. أين توقفنا بالضبط — المرحلة 9

## الهدف

**رابط يفتحه أي شخص فيعمل النظام في متصفحه مباشرة** — بلا خادم، بلا تثبيت. هذا البند الثاني في قائمة ما يهم للسيرة، والوحيد غير المنجز.

## القرار المعماري المتخذ

**كل شيء في المتصفح** (MediaPipe JS + النموذج داخل الصفحة)، لا خادم Python.

**الأسباب:** لا تأخير شبكة (المشروع اسمه "في الوقت الفعلي") · استضافة مجانية على GitHub Pages · لا خادم ينام بعد خمول · الكاميرا تبقى على جهاز الزائر (نقطة خصوصية للـREADME) · "Python + JavaScript، ML في المتصفح" أقوى في السيرة.

**النموذج صغير:** 17,492 عقدة فقط. تصدير مباشر إلى JSON مضغوط يتوقع **أقل من ميجابايت** (الـ4.5 MB الحالية بسبب تخزين joblib بدقة 64 بت مع بنية Python كاملة).

## الخطر الرئيسي في هذه المرحلة

إعادة بناء الأنبوب بلغة أخرى تعني **ثلاث فرص لخرق القاعدة الأساسية**: MediaPipe مختلف، تطبيع مكتوب من جديد، نموذج محوَّل. وتجربة 10 أثبتت أن الاختلاف يمكن أن يمر **بلا رسالة خطأ لأسابيع**.

**لهذا الخطوات 1–3 كلها تحقق من التطابق، والواجهة بعدها.**

## الخطوات الست

| # | الخطوة | ما ننتجه | علامة النجاح | الحالة |
|---|---|---|---|---|
| **9.1** | تحقق من MediaPipe JS | `web/index.html` | ترتيب النقاط ومداها متطابق | ✅ **تم** |
| **9.2** | صدّر النموذج | `model.json` | نفس التنبؤات، حجم < 1 MB | ⬅️ **التالي** |
| **9.3** | أعد بناء الأنبوب في JS | تطبيع + غابة + عتبة + تنعيم + تثبيت | نفس نتائج Python على نفس العينات | لم يبدأ |
| **9.4** | التصميم | واجهة HTML/CSS | تبدو كمنتج لا كتجربة | لم يبدأ |
| **9.5** | النشر | GitHub Pages | يعمل من الجوال | لم يبدأ |
| **9.6** | README | القصة كاملة | يفهمه من لم يرَ الكود | لم يبدأ |

## تفاصيل الخطوة 9.2 (التالية مباشرة)

**الفكرة:** `RandomForest` ليس سحراً — هو 100 شجرة قرار. كل عقدة تسأل: "هل الميزة رقم X أقل من العتبة Y؟" فتذهب يميناً أو يساراً حتى تصل إلى ورقة فيها التصويت.

نستخرج هذه البنية من `model.pkl` ونحفظها JSON، ثم يمشي JavaScript فيها بنفسه.

**ما نحتاج استخراجه لكل شجرة:** `children_left`, `children_right`, `feature`, `threshold`, `value` — كلها متاحة عبر `model.estimators_[i].tree_`.

**فائدة إضافية للمقابلة:** بعد كتابة المشي في الأشجار يدوياً، سؤال "كيف يعمل RandomForest؟" لن يكون تعريفاً محفوظاً — سيكون شيئاً نُفِّذ بالفعل.

## ملاحظات على JavaScript (اتُفق على تعلّمه هنا)

الطالب لم يكتب JS من قبل. الاتفاق أن المنطق **مكتوب أصلاً** في Python، والمطلوب ترجمة صياغة لا تعلّم برمجة جديدة:

| Python | JavaScript |
|---|---|
| `for lm in landmarks.landmark` | `for (const lm of landmarks)` |
| `points - points[0]` | حلقة طرح |
| `deque(maxlen=7)` | `array.push()` ثم `shift()` |
| `Counter(history).most_common(1)` | حلقة عدّ |
| `f"x={v}"` | `` `x=${v}` `` |
| `while True:` | `requestAnimationFrame(loop)` |
| — | `const` / `let` / `await` |

**التقدير:** أقل من 150 سطراً من المنطق. المصطلحات تُشرح أول ظهور كما في Python.

---

# 12. ما يهم للـ resume (بالترتيب المتفق عليه)

1. **أرقام مقابل baseline** — "97.17% عبر جلسات مستقلة مقابل 4.17% baseline"
2. **demo يشتغل برابط** — لا مجرد repo ← **هذا ما نعمل عليه الآن**
3. **قرارات مبرَّرة** — لماذا نقاط بدل صور؟ لماذا استُبعد J و Z؟ لماذا تُثبَّت الإصدارات؟ لماذا العتبة 0.60؟
4. **تحليل أخطاء** — قصة سكربت التقييم المعطوب، وقيد الدوران، ومحاولة إصلاح K الفاشلة
5. **بيانات مجموعة ذاتياً** — 14,400 عينة، لا dataset جاهز من Kaggle

## السطر المستهدف في الـ resume

> Real-time ASL fingerspelling recognition — 97.2% accuracy across independent recording sessions on the full 24-letter static alphabet (4.2% baseline), self-collected dataset of 14,400 samples, with landmark normalisation and measured confidence thresholding.

## أقوى خمس قصص للمقابلة

1. **أداة القياس نفسها كانت معطوبة** (تجربة 10) — اكتُشفت بتناقض بين قياسين مستقلين. أقوى من قصة حرف C.
2. **قيد وُثّق قبل أن يُرى ثم قِيس** (تجربة 11 — الدوران).
3. **نتيجة مضادة للحدس** (تجربة 13 — فئات متشابهة حسّنت التصنيف).
4. **فئات ليست منفصلة بل نقاط على متصل** (تجربة 14 — U/V/R).
5. **محاولة إصلاح فاشلة موثّقة** (تجربة 15 — K إلى 0%) مع سبب دقيق. توثيق ما لم ينجح هو ما يفصل تقريراً صادقاً عن عرض تسويقي.

---

# 13. المعلّق (لم يُنجز عمداً)

- **`R`** — أضعف حرف (75% recall). تنويع `batch 1` أضيق من `batch 2`. يُصلَح بحذف `R` من `batch 1` فقط وإعادة تسجيله بتنويع أوسع في **الظرف** (دوران معصم ومسافة) لا في الشكل
- **فئة `NONE`** — تعالج سبب رفض الأشكال غير الحرفية بدل رفعها بالعتبة
- **تطبيع الدوران** — خطوة ثالثة في `normalize_landmarks` تدوّر النقاط بحيث يشير محور (الرسغ ← قاعدة الإصبع الأوسط، أي النقطة 0 ← النقطة 9) في اتجاه ثابت. **مقايضة حقيقية:** قد يجعل `P` و `K` متطابقين، و `Q` و `G` متطابقين (لأن `P` هو `K` مقلوباً و `Q` هو `G` مقلوباً). قابل للقياس: طبّق، شغّل `evaluate_generalization.py`، قارن، وارجع بـcommit إن ساء
- **جلسة ثالثة (`batch 3`)** — بديل أبسط لتطبيع الدوران، لكنه يغيّر منهج التقييم (يصبح: درّب على 1+2، اختبر على 3)
- **`E.png`** في `reference/` من ظرف قديم (خلفية فاتحة). `E` عند 100% فلا خطر، لكن لا تُستخدم كمرجع لو احتاج إعادة تسجيل
- **`diagnose_c.py`** — قديم، استُبدل بـ `diagnose.py`. يمكن حذفه
- **`results.md` السطر ~171** — يجب التأكد أن الصف القديم صار:
  `| 6 | batch1 | batch2 | raw (mislabelled - see Exp 10) | 53.3% | 9.1% |`
  بدل `normalized` (كان يقيس الخام فعلاً)

---

# 14. أول رد في الشات الجديد

المتوقع أن يبدأ بـ **الخطوة 9.2 — تصدير النموذج إلى JSON**:

1. شرح ما هو RandomForest فعلياً (100 شجرة، كل عقدة سؤال) بلغة بسيطة
2. سكربت `src/export_model.py` يستخرج بنية الأشجار
3. قياس حجم الناتج
4. التحقق: نفس التنبؤات على نفس العينات بين Python و JSON

**بالأسلوب المتفق عليه:** شرح قبل الكود، ملف كامل مع جدول "ما تغيّر"، علامة نجاح بعد كل خطوة، لا كومنتات عربية داخل الكود، أوامر PowerShell على أسطر منفصلة.
