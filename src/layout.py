import streamlit as st
import html

# SBB style layout (written assisted by AI)
def sbb_header(title: str):
    safe_title = html.escape(title)

    st.markdown(f"""
    <style>

    /* Full-width SBB-style header */
    .sbb-hero {{
        width: 100vw;
        height: 150px;

        background: #e00000;

        display: flex;
        align-items: center;

        padding-left: 48px;

        color: white;

        margin-left: calc(-50vw + 50%);
        box-sizing: border-box;
    }}

    .sbb-hero h1 {{
        font-size: 34px;
        font-weight: 700;
        margin: 0;
    }}

    </style>

    <div class="sbb-hero">
        <h1>{safe_title}</h1>
    </div>
    """, unsafe_allow_html=True)

    st.space("large")
