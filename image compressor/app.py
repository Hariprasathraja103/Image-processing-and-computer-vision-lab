"""
app.py
------
Streamlit GUI for the Image Compression System.

Layout:
  Left sidebar  → controls (quality slider, resize %, compress button)
  Main area     → side-by-side image previews + stats cards + download button

Run with:
    streamlit run app.py
"""

import io
import streamlit as st
from PIL import Image
import os

from compressor import compress_image, bytes_to_pil

# ─────────────────────────────────────────────
# Page config  (must be the very first st call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Image Compressor",
    page_icon="🗜️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — clean, dark-accented card style
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* ── Page background ── */
    .stApp {
        background: #0f1117;
        color: #e8e8f0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #16181f;
        border-right: 1px solid #2a2d3a;
    }

    /* ── Stat cards ── */
    .stat-card {
        background: #1c1f2b;
        border: 1px solid #2e3147;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
        transition: border-color .2s;
    }
    .stat-card:hover { border-color: #5b6af8; }
    .stat-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #7b7f9e;
        margin-bottom: 6px;
    }
    .stat-value {
        font-family: 'DM Mono', monospace;
        font-size: 1.6rem;
        font-weight: 500;
        color: #c8cbff;
    }
    .stat-value.good  { color: #56e0a0; }
    .stat-value.warn  { color: #f9c74f; }
    .stat-value.muted { color: #7b7f9e; }

    /* ── Section headers ── */
    .section-header {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        color: #5b6af8;
        margin-bottom: 8px;
    }

    /* ── Upload zone accent ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #2e3147;
        border-radius: 12px;
        padding: 8px;
    }

    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        letter-spacing: .03em;
        transition: all .15s;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    /* ── Divider ── */
    hr { border-color: #2a2d3a; }

    /* ── Image captions ── */
    .img-caption {
        font-size: 0.75rem;
        color: #7b7f9e;
        text-align: center;
        margin-top: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────
for key in ("compressed_bytes", "stats", "original_bytes", "filename"):
    if key not in st.session_state:
        st.session_state[key] = None

# ─────────────────────────────────────────────
# Sidebar — controls
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗜️ Image Compressor")
    st.markdown("Reduce file size while keeping great quality.")
    st.markdown("---")

    # ── Upload ──
    st.markdown('<div class="section-header">① Upload</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Choose an image",
        type=["jpg", "jpeg", "png", "bmp", "webp", "tiff"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # ── Settings ──
    st.markdown('<div class="section-header">② Settings</div>', unsafe_allow_html=True)

    quality = st.slider(
        "JPEG Quality",
        min_value=5,
        max_value=95,
        value=75,
        step=5,
        help="Higher = better image quality but larger file. 70–85 is the sweet spot.",
    )

    resize_pct = st.slider(
        "Resize  (% of original)",
        min_value=10,
        max_value=100,
        value=100,
        step=5,
        help="Shrink dimensions before compression for even smaller files.",
    )

    st.markdown("---")

    # ── Compress button ──
    st.markdown('<div class="section-header">③ Compress</div>', unsafe_allow_html=True)
    compress_btn = st.button("⚡  Compress Image", use_container_width=True, type="primary")

    st.markdown("---")
    st.caption("Built with OpenCV + Pillow + Streamlit")

# ─────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────
st.markdown("# Image Compression System")
st.markdown("Upload an image, tweak the settings in the sidebar, and hit **Compress**.")
st.markdown("---")

# ── Handle upload ──
if uploaded_file is not None:
    # Only re-read if the file changed
    if st.session_state.filename != uploaded_file.name:
        st.session_state.original_bytes = uploaded_file.read()
        st.session_state.filename = uploaded_file.name
        # Reset any previous compression result
        st.session_state.compressed_bytes = None
        st.session_state.stats = None

# ── Handle compress button ──
if compress_btn:
    if st.session_state.original_bytes is None:
        st.warning("Please upload an image first.")
    else:
        with st.spinner("Compressing …"):
            try:
                compressed, stats = compress_image(
                    st.session_state.original_bytes,
                    quality=quality,
                    resize_percent=resize_pct,
                )
                st.session_state.compressed_bytes = compressed
                st.session_state.stats = stats
                st.success("Done! See results below.")
            except Exception as exc:
                st.error(f"Compression failed: {exc}")

# ─────────────────────────────────────────────
# Preview section
# ─────────────────────────────────────────────
if st.session_state.original_bytes:
    orig_img = bytes_to_pil(st.session_state.original_bytes)
    col_orig, col_comp = st.columns(2, gap="large")

    with col_orig:
        st.markdown('<div class="section-header">Original</div>', unsafe_allow_html=True)
        st.image(orig_img, use_container_width=True)
        st.markdown(
            f'<div class="img-caption">'
            f'{orig_img.width} × {orig_img.height} px &nbsp;·&nbsp; '
            f'{round(len(st.session_state.original_bytes)/1024, 1)} KB'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_comp:
        st.markdown('<div class="section-header">Compressed</div>', unsafe_allow_html=True)
        if st.session_state.compressed_bytes:
            comp_img = bytes_to_pil(st.session_state.compressed_bytes)
            st.image(comp_img, use_container_width=True)
            st.markdown(
                f'<div class="img-caption">'
                f'{comp_img.width} × {comp_img.height} px &nbsp;·&nbsp; '
                f'{round(len(st.session_state.compressed_bytes)/1024, 1)} KB'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Compressed preview will appear here after you click **Compress**.")

# ─────────────────────────────────────────────
# Stats cards
# ─────────────────────────────────────────────
if st.session_state.stats:
    stats = st.session_state.stats
    st.markdown("---")
    st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)

    saving = stats["saving_pct"]
    saving_class = "good" if saving >= 40 else ("warn" if saving >= 10 else "muted")

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Original Size",    f'{stats["original_kb"]} KB',   "muted"),
        ("Compressed Size",  f'{stats["compressed_kb"]} KB', "good"),
        ("Space Saved",      f'{saving} %',                  saving_class),
        ("Output Dims",
         f'{stats["compressed_dims"][0]}×{stats["compressed_dims"][1]}',
         "muted"),
    ]
    for col, (label, value, css_class) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-label">{label}</div>'
                f'<div class="stat-value {css_class}">{value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────
# Download button
# ─────────────────────────────────────────────
if st.session_state.compressed_bytes:
    st.markdown("---")
    base_name = os.path.splitext(st.session_state.filename or "image")[0]
    download_name = f"{base_name}_compressed.jpg"

    st.download_button(
        label="⬇️  Download Compressed Image",
        data=st.session_state.compressed_bytes,
        file_name=download_name,
        mime="image/jpeg",
        use_container_width=True,
        type="primary",
    )

# ── Footer when nothing is uploaded yet ──
if st.session_state.original_bytes is None:
    st.markdown(
        """
        <div style="text-align:center; padding:60px 0; color:#3a3f55;">
            <div style="font-size:3rem;">🖼️</div>
            <div style="font-size:1rem; margin-top:12px;">Upload an image from the sidebar to get started</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

import os  # noqa: E402 (needed for splitext above; imported here to keep top tidy)
