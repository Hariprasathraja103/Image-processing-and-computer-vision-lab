# 🗜️ Image Compression System

A clean, interactive image compression tool built with **Python**, **OpenCV**, **Pillow**, and **Streamlit**.

---

## 📁 Project Structure

```
image_compressor/
├── app.py            ← Streamlit GUI (all UI logic)
├── compressor.py     ← Core compression logic (OpenCV + Pillow)
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## ⚙️ How It Works — Step by Step

### Step 1 — Upload
The user picks any image (JPEG, PNG, BMP, WebP, TIFF) via the sidebar file uploader. Streamlit reads it as raw bytes and stores them in session state.

### Step 2 — Decode with OpenCV
`cv2.imdecode` converts the raw bytes into a NumPy BGR array — the native format OpenCV works with.

### Step 3 — Optional Resize
If the *Resize* slider is below 100 %, OpenCV scales the image down using `cv2.INTER_AREA` interpolation, which is the best algorithm for shrinking (minimises aliasing).

### Step 4 — JPEG Compression
`cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])` re-encodes the image at the chosen quality level (1–95). Lower quality → smaller file → more artefacts. The sweet spot is **70–85**.

### Step 5 — Stats
Original and compressed byte lengths are compared to show:
- File sizes in KB
- Percentage of space saved
- Final image dimensions

### Step 6 — Preview & Download
The compressed bytes are decoded back to a PIL Image for the side-by-side preview. Streamlit's `st.download_button` lets the user save the result as a `.jpg` file.

---

## 🚀 Quick Start

```bash
# 1. Clone / download the project
cd image_compressor

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The browser will open automatically at `http://localhost:8501`.

---

## 🎛️ Controls

| Control | Description |
|---|---|
| **Upload** | Accepts JPEG, PNG, BMP, WebP, TIFF |
| **JPEG Quality** slider | 5–95. Higher = better quality, bigger file |
| **Resize %** slider | Shrinks dimensions before encoding |
| **Compress** button | Runs the compression pipeline |
| **Download** button | Saves the compressed JPEG to your machine |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Image decoding, resizing, JPEG encoding |
| `Pillow` | PIL Image ↔ bytes conversion for Streamlit display |
| `numpy` | Array operations (used internally by OpenCV) |
| `streamlit` | Web-based GUI |

---

## 💡 Tips

- PNG screenshots compress especially well — expect 60–80 % savings.
- For photos, quality **75** with no resize is a great default.
- If you need the smallest possible file, drop resize to **50 %** and quality to **60**.
