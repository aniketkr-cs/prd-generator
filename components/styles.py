"""
components/styles.py
---------------------
All custom CSS for the app lives here, in one place, so app.py stays
readable. We inject this CSS into Streamlit using st.markdown(..., unsafe_allow_html=True).

Design rules followed here (on purpose):
- Flat dark theme. No gradients, no blur/glassmorphism.
- Background:        #0a0a0a
- Card background:   #161616
- Border:            #222222
- Text primary:      #f2f2f2
- Text secondary:    #8a8a8a
- Accent (green):    #22c55e
- Fonts: Inter (body text) + JetBrains Mono (labels/badges/code-like text)
"""

# Color tokens kept as constants so other files (like report_generator.py)
# can reuse the same hex values if needed.
BG = "#0a0a0a"
CARD_BG = "#161616"
BORDER = "#222222"
TEXT_PRIMARY = "#f2f2f2"
TEXT_SECONDARY = "#8a8a8a"
ACCENT_GREEN = "#22c55e"


def get_css() -> str:
    """
    Returns a <style> block (as a plain string) with every custom style
    used across the app. Called once in app.py right after set_page_config.
    """
    return f"""
    <style>
        /* ---------- Fonts ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        /* ---------- Page background ---------- */
        .stApp {{
            background-color: {BG};
            color: {TEXT_PRIMARY};
        }}

        /* Hide default Streamlit chrome we don't need for a clean tool look */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{background: transparent;}}

        /* ---------- Header / badge ---------- */
        .app-header {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding: 28px 0 20px 0;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 28px;
        }}

        .app-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            width: fit-content;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: {ACCENT_GREEN};
            background-color: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(34, 197, 94, 0.35);
            padding: 4px 10px;
            border-radius: 4px;
        }}

        .app-badge::before {{
            content: "";
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: {ACCENT_GREEN};
            display: inline-block;
        }}

        .app-title {{
            font-size: 28px;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin: 0;
        }}

        .app-subtitle {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
            margin: 0;
        }}

        /* ---------- Section labels (JetBrains Mono) ---------- */
        .section-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {TEXT_SECONDARY};
            margin-bottom: 6px;
        }}

        /* ---------- Cards ---------- */
        .card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 20px 22px;
            margin-bottom: 16px;
        }}

        .card-title {{
            font-size: 15px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .card-title .tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: {ACCENT_GREEN};
            border: 1px solid rgba(34, 197, 94, 0.35);
            border-radius: 4px;
            padding: 1px 6px;
        }}

        .card p, .card li {{
            font-size: 14px;
            color: {TEXT_PRIMARY};
            line-height: 1.55;
        }}

        .card-divider {{
            border: none;
            border-top: 1px solid {BORDER};
            margin: 14px 0;
        }}

        /* ---------- Priority badges ---------- */
        .priority-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        .priority-high {{
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.4);
            background-color: rgba(239, 68, 68, 0.08);
        }}
        .priority-medium {{
            color: #eab308;
            border: 1px solid rgba(234, 179, 8, 0.4);
            background-color: rgba(234, 179, 8, 0.08);
        }}
        .priority-low {{
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER};
            background-color: rgba(138, 138, 138, 0.08);
        }}

        /* ---------- Feature row ---------- */
        .feature-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 10px 0;
            border-bottom: 1px solid {BORDER};
            gap: 12px;
        }}
        .feature-row:last-child {{
            border-bottom: none;
        }}
        .feature-name {{
            font-weight: 600;
            font-size: 14px;
            color: {TEXT_PRIMARY};
        }}
        .feature-desc {{
            font-size: 13px;
            color: {TEXT_SECONDARY};
            margin-top: 2px;
        }}

        /* ---------- Persona block ---------- */
        .persona-block {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 14px 16px;
            margin-bottom: 10px;
            background-color: #121212;
        }}
        .persona-name {{
            font-weight: 700;
            font-size: 14px;
            color: {ACCENT_GREEN};
        }}
        .persona-role {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: {TEXT_SECONDARY};
            margin-bottom: 8px;
        }}

        /* ---------- User story block ---------- */
        .story-block {{
            border-left: 2px solid {ACCENT_GREEN};
            padding: 6px 12px;
            margin-bottom: 10px;
            background-color: #121212;
            border-radius: 0 6px 6px 0;
        }}

        /* ---------- Risk block ---------- */
        .risk-block {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px 14px;
            margin-bottom: 8px;
        }}
        .risk-title {{
            font-weight: 600;
            font-size: 13px;
            color: #ef4444;
        }}
        .risk-mitigation {{
            font-size: 13px;
            color: {TEXT_SECONDARY};
            margin-top: 4px;
        }}

        /* ---------- Buttons ---------- */
        .stButton > button, .stDownloadButton > button {{
            background-color: {ACCENT_GREEN};
            color: #0a0a0a;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            padding: 10px 18px;
            transition: opacity 0.15s ease;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            opacity: 0.85;
            color: #0a0a0a;
        }}

        /* Secondary / "Start Over" button gets an outline look via Streamlit's
           own secondary button type, restyled here */
        button[kind="secondary"] {{
            background-color: transparent !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {BORDER} !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: {ACCENT_GREEN} !important;
            color: {ACCENT_GREEN} !important;
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            color: {TEXT_PRIMARY} !important;
            border-radius: 6px !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: {ACCENT_GREEN} !important;
            box-shadow: none !important;
        }}
        label {{
            color: {TEXT_SECONDARY} !important;
            font-size: 13px !important;
        }}

        /* ---------- Misc ---------- */
        hr {{
            border-color: {BORDER};
        }}
    </style>
    """
