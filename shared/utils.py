"""
TalentBridge AI - Shared Design System & UI Utilities
Provides modern typography injection, sleek cards, metric widgets, and resilient loaders.
Ensures platform-wide visual elegance without coupling modules or breaking contracts.
"""

import importlib
import traceback
from typing import Callable, Optional, Sequence


def inject_custom_css() -> None:
    """
    Injects global enterprise design system styles:
    - Plus Jakarta Sans typography from Google Fonts
    - Polished card elevation, soft drop-shadows, and smooth micro-animations
    - High-contrast, modern metric displays
    - Sleek tabs and button gradients
    """
    import streamlit as st

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* Global Typography & Font Smoothing */
        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            letter-spacing: -0.01em;
        }

        /* Smooth page background */
        .stApp {
            background-color: #f8fafc;
        }

        /* Top header padding normalization */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1280px !important;
        }

        /* Primary Button Styling */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.65rem 1.4rem !important;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.35) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.45) !important;
        }

        /* Secondary Button Styling */
        div.stButton > button:not([kind="primary"]) {
            background-color: #ffffff !important;
            color: #334155 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button:not([kind="primary"]):hover {
            border-color: #cbd5e1 !important;
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }

        /* Metric Cards Styling */
        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stMetric"]:hover {
            box-shadow: 0 6px 16px -4px rgba(0, 0, 0, 0.08) !important;
            border-color: #cbd5e1 !important;
        }

        div[data-testid="stMetricLabel"] p {
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
            line-height: 1.2 !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background-color: #f1f5f9 !important;
            padding: 5px !important;
            border-radius: 12px !important;
            border-bottom: none !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            color: #64748b !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.2s ease !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            color: #4f46e5 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
        }

        /* Text Areas & Inputs */
        div[data-baseweb="textarea"] {
            border-radius: 10px !important;
            border-color: #e2e8f0 !important;
            background-color: #ffffff !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        }

        div[data-baseweb="textarea"]:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #6366f1 0%, #10b981 100%) !important;
            border-radius: 9999px !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }

        /* Custom Card Class */
        .tb-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.04);
            transition: all 0.25s ease;
        }

        .tb-card:hover {
            box-shadow: 0 10px 24px -4px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_module_header(
    title: str,
    member: str,
    description: str,
    badge: str = "Active Baseline",
    badge_color: str = "#22c55e",
) -> None:
    """
    Renders an executive, modern hero banner for any module.
    """
    import streamlit as st

    inject_custom_css()

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                    padding: 1.75rem 2rem; border-radius: 16px; margin-bottom: 1.75rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.25);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4);
                                width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center;
                                justify-content: center; font-size: 1.35rem;">
                        ⚡
                    </div>
                    <div>
                        <h2 style="color: #ffffff; margin: 0; font-weight: 800; font-size: 1.65rem; letter-spacing: -0.02em;">
                            {title}
                        </h2>
                    </div>
                </div>
                <span style="background-color: {badge_color}1a; color: {badge_color};
                             border: 1px solid {badge_color}4d; padding: 0.35rem 0.85rem;
                             border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;">
                    ● {badge}
                </span>
            </div>
            <p style="color: #94a3b8; margin: 0.75rem 0 0.5rem 0; font-size: 0.95rem; line-height: 1.5; max-width: 850px;">
                {description}
            </p>
            <div style="display: flex; align-items: center; gap: 1rem; margin-top: 0.75rem; font-size: 0.85rem;">
                <span style="color: #38bdf8; font-weight: 600;">
                    👤 Assigned Lead: <span style="color: #ffffff;">{member}</span>
                </span>
                <span style="color: #64748b;">•</span>
                <span style="color: #a5b4fc; font-weight: 500;">
                    TalentBridge AI Enterprise Suite
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer(
    custom_message: Optional[str] = None,
) -> None:
    """
    Renders an elegant ethical AI disclaimer banner.
    """
    import streamlit as st

    default_msg = (
        "<strong>Ethical AI & Compliance Notice:</strong> Machine learning metrics (similarity scores, "
        "placement forecasts, and match classifications) are algorithmic decision-support tools. A high similarity score "
        "indicates textual and competency correspondence; it is <strong>not</strong> an automated hiring guarantee, "
        "employment probability, or admission certificate. Final decisions must always involve holistic human review."
    )
    msg = custom_message if custom_message else default_msg

    st.markdown(
        f"""
        <div style="background-color: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b;
                    padding: 1rem 1.25rem; border-radius: 10px; margin: 2rem 0 1rem 0;
                    color: #92400e; font-size: 0.88rem; line-height: 1.5; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="display: flex; gap: 0.65rem; align-items: flex-start;">
                <span style="font-size: 1.15rem; line-height: 1;">🛡️</span>
                <div>{msg}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder(
    module_key: str,
    module_title: str,
    member_name: str,
    expected_inputs: Sequence[str],
    expected_outputs: Sequence[str],
    suggested_models: Optional[Sequence[str]] = None,
) -> None:
    """
    Renders a modern, structured blueprint interface for upcoming modules.
    Guides assigned team members on where to insert their implementation.
    """
    import streamlit as st

    render_module_header(
        title=module_title,
        member=member_name,
        description=f"Isolated machine learning module scaffold for {module_title}. Ready for pipeline integration.",
        badge="In Development",
        badge_color="#f59e0b",
    )

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem 1.5rem;
                    margin-bottom: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; gap: 0.65rem; color: #4f46e5; font-weight: 700;">
                <span style="font-size: 1.2rem;">🚧</span>
                <span>Module Scaffold Active</span>
            </div>
            <p style="color: #475569; margin: 0.4rem 0 0 0; font-size: 0.92rem;">
                This module is assigned to <strong>{member_name}</strong>. The code is isolated inside
                <code>modules/{module_key}/</code>. Follow the specification blueprint below to complete the algorithm.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; height: 100%;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1rem; font-weight: 700;">📥 Expected Inputs</h4>
            """,
            unsafe_allow_html=True,
        )
        for item in expected_inputs:
            st.markdown(f"- **{item}**")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; height: 100%;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1rem; font-weight: 700;">📤 Expected Outputs</h4>
            """,
            unsafe_allow_html=True,
        )
        for item in expected_outputs:
            st.markdown(f"- **{item}**")
        st.markdown("</div>", unsafe_allow_html=True)

    if suggested_models:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🧠 Recommended Machine Learning Architectures")
        chips = " ".join([
            f"<span style='background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin: 4px; display: inline-block;'>{model}</span>"
            for model in suggested_models
        ])
        st.markdown(chips, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛠️ Developer Checklist for Module Owner")
    st.markdown(
        f"""
        1. Open directory: `modules/{module_key}/`
        2. Put training data in `modules/{module_key}/data/`.
        3. Implement your data preparation and ML model in `model.py` and `train.py`.
        4. Replace `render_placeholder()` in `interface.py` inside `def render():` with your Streamlit UI.
        5. Write unit tests in `modules/{module_key}/tests/`.
        6. Verify all tests pass: `python -m pytest -v`.
        """
    )

    render_disclaimer()


def safe_import_render(module_path: str) -> Optional[Callable[[], None]]:
    """
    Safely imports the `render()` callable from a module path.
    Catches and formats import errors without crashing the main application.
    """
    try:
        mod = importlib.import_module(module_path)
        render_fn = getattr(mod, "render", None)
        if render_fn is None or not callable(render_fn):
            raise AttributeError(f"Module '{module_path}' does not define a callable 'render()' function.")
        return render_fn
    except Exception as exc:
        import streamlit as st

        st.error(
            f"❌ **Failed to load module `{module_path}`**: {str(exc)}"
        )
        with st.expander("Show Traceback Details"):
            st.code(traceback.format_exc(), language="python")
        return None
