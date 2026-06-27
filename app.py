"""
app.py
-------
Main Streamlit application for the PRD Generator.

Flow:
1. User fills out a form describing their product idea.
2. We validate the form (no empty fields).
3. We send the data to Gemini (via utils/gemini_client.py) which returns
   a structured PRD as a Python dict.
4. We display that PRD nicely on screen.
5. User can download it as a formatted PDF (via utils/report_generator.py)
   or start over with a blank form.

This file is intentionally kept focused on UI/flow logic only - the actual
AI call and PDF generation live in their own modules.
"""

import streamlit as st

from components.styles import get_css
from utils.gemini_client import generate_prd, PRDGenerationError
from utils.report_generator import generate_pdf

# ------------------------------------------------------------------
# Page config - must be the first Streamlit command in the script
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRD Generator",
    page_icon="📋",
    layout="wide",
)

# Inject our custom CSS (dark theme, Inter + JetBrains Mono, no gradients)
st.markdown(get_css(), unsafe_allow_html=True)

# ------------------------------------------------------------------
# Session state setup
# ------------------------------------------------------------------
# session_state lets us remember data between reruns (every click reruns
# the whole script in Streamlit, so we need this to "persist" the PRD).
if "prd_data" not in st.session_state:
    st.session_state.prd_data = None          # holds the generated PRD dict
if "product_name" not in st.session_state:
    st.session_state.product_name = ""        # used in PDF filename/title
if "generation_error" not in st.session_state:
    st.session_state.generation_error = None  # holds any error message to show


def reset_app():
    """Clears everything and takes the user back to a blank form."""
    st.session_state.prd_data = None
    st.session_state.product_name = ""
    st.session_state.generation_error = None


# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <span class="app-badge">AI-Powered Tool</span>
        <h1 class="app-title">PRD Generator</h1>
        <p class="app-subtitle">
            Turn a rough product idea into a complete, structured Product Requirements Document — ready to share with your team.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# View 1: FORM (shown only when we don't have a generated PRD yet)
# ------------------------------------------------------------------
if st.session_state.prd_data is None:

    st.markdown('<div class="section-label">Product Details</div>', unsafe_allow_html=True)

    with st.form("prd_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            product_name = st.text_input(
                "Product Name",
                placeholder="e.g. TaskFlow",
            )
        with col2:
            category = st.selectbox(
                "Product Category",
                options=["SaaS", "Mobile App", "Web App", "API Tool", "Other"],
            )

        problem_statement = st.text_area(
            "Problem Statement",
            placeholder="What problem does this product solve, and for whom?",
            height=90,
        )

        target_users = st.text_area(
            "Target Users",
            placeholder="Who will use this product? e.g. freelance designers, small agency teams...",
            height=80,
        )

        core_features = st.text_area(
            "Core Features",
            placeholder="List the main features you want, one per line or comma-separated.",
            height=110,
        )

        out_of_scope = st.text_area(
            "Out of Scope",
            placeholder="What will this product explicitly NOT do (for this version)?",
            height=80,
        )

        success_metrics = st.text_area(
            "Success Metrics",
            placeholder="How will you measure if this product is successful?",
            height=80,
        )

        submitted = st.form_submit_button("Generate PRD", use_container_width=False)

    # ---------------- Validation + Generation ----------------
    if submitted:
        # Collect all fields so we can validate them together.
        fields = {
            "Product Name": product_name,
            "Problem Statement": problem_statement,
            "Target Users": target_users,
            "Core Features": core_features,
            "Out of Scope": out_of_scope,
            "Success Metrics": success_metrics,
        }

        # Input validation: no empty fields allowed.
        empty_fields = [name for name, value in fields.items() if not value.strip()]

        if empty_fields:
            st.error(
                f"Please fill in the following field(s) before generating: "
                f"{', '.join(empty_fields)}."
            )
        else:
            product_data = {
                "product_name": product_name.strip(),
                "category": category,
                "problem_statement": problem_statement.strip(),
                "target_users": target_users.strip(),
                "core_features": core_features.strip(),
                "out_of_scope": out_of_scope.strip(),
                "success_metrics": success_metrics.strip(),
            }

            # Loading state while we wait for Gemini's response.
            with st.spinner("Generating your PRD with Gemini AI... this can take a few seconds."):
                try:
                    prd_result = generate_prd(product_data)
                    st.session_state.prd_data = prd_result
                    st.session_state.product_name = product_data["product_name"]
                    st.session_state.generation_error = None
                    st.rerun()
                except PRDGenerationError as err:
                    st.session_state.generation_error = str(err)

    # Show any error from a previous attempt (persists across the rerun above)
    if st.session_state.generation_error:
        st.error(st.session_state.generation_error)

# ------------------------------------------------------------------
# View 2: GENERATED PRD DISPLAY
# ------------------------------------------------------------------
else:
    prd = st.session_state.prd_data
    name = st.session_state.product_name

    # ---- Top action bar: title + Download/Start Over buttons ----
    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown(
            f'<div class="section-label">Generated PRD</div>'
            f'<h2 style="margin-top:0;">{name}</h2>',
            unsafe_allow_html=True,
        )
    with top_right:
        st.write("")  # small vertical spacer to align buttons with title
        try:
            pdf_bytes = generate_pdf(prd, name)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{name.strip().replace(' ', '_')}_PRD.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"Could not generate PDF: {exc}")

        st.button("Start Over", on_click=reset_app, use_container_width=True, type="secondary")

    st.markdown('<hr class="card-divider">', unsafe_allow_html=True)

    # ---- Executive Summary ----
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Executive Summary <span class="tag">Overview</span></div>
            <p>{prd.get("executive_summary", "")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Problem Statement ----
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Problem Statement</div>
            <p>{prd.get("problem_statement", "")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Goals ----
    goals_html = "".join(f"<li>{g}</li>" for g in prd.get("goals", []))
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Goals and Objectives</div>
            <ul>{goals_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Personas ----
    personas_html = ""
    for persona in prd.get("personas", []):
        personas_html += f"""
        <div class="persona-block">
            <div class="persona-name">{persona.get('name', '')}</div>
            <div class="persona-role">{persona.get('role', '')}</div>
            <p><b>Description:</b> {persona.get('description', '')}</p>
            <p><b>Needs:</b> {persona.get('needs', '')}</p>
            <p><b>Pain Points:</b> {persona.get('pain_points', '')}</p>
        </div>
        """
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">User Personas</div>
            {personas_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- User Stories ----
    stories_html = ""
    for story in prd.get("user_stories", []):
        stories_html += f"""
        <div class="story-block">
            <p><b>As a</b> {story.get('as_a', '')}, <b>I want</b> {story.get('i_want', '')},
            <b>so that</b> {story.get('so_that', '')}.</p>
        </div>
        """
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">User Stories</div>
            {stories_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Feature List ----
    priority_class_map = {
        "High": "priority-high",
        "Medium": "priority-medium",
        "Low": "priority-low",
    }
    features_html = ""
    for feature in prd.get("features", []):
        priority = feature.get("priority", "Medium")
        badge_class = priority_class_map.get(priority, "priority-medium")
        features_html += f"""
        <div class="feature-row">
            <div>
                <div class="feature-name">{feature.get('name', '')}</div>
                <div class="feature-desc">{feature.get('description', '')}</div>
            </div>
            <span class="priority-badge {badge_class}">{priority}</span>
        </div>
        """
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Feature List</div>
            {features_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Out of Scope ----
    scope_html = "".join(f"<li>{item}</li>" for item in prd.get("out_of_scope", []))
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Out of Scope</div>
            <ul>{scope_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Success Metrics ----
    metrics_html = "".join(f"<li>{item}</li>" for item in prd.get("success_metrics", []))
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Success Metrics</div>
            <ul>{metrics_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Timeline Estimate ----
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Timeline Estimate</div>
            <p>{prd.get("timeline_estimate", "")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Risks and Mitigation ----
    risks_html = ""
    for risk in prd.get("risks", []):
        risks_html += f"""
        <div class="risk-block">
            <div class="risk-title">{risk.get('risk', '')}</div>
            <div class="risk-mitigation"><b>Mitigation:</b> {risk.get('mitigation', '')}</div>
        </div>
        """
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Risks and Mitigation</div>
            {risks_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
