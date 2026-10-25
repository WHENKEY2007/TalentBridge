"""
TalentBridge AI - Integrated Machine Learning Platform
Portal Layout with Flashcard Navigation & Zero Sidebar Clutter
"""

import importlib
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import streamlit as st

# Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils import inject_custom_css, render_disclaimer

# ==============================================================================
# Page Configuration (Full-Width Portal Mode, No Sidebar)
# ==============================================================================
st.set_page_config(
    page_title="TalentBridge AI — Machine Learning Platform",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply Global Design System & Completely Hide Sidebar
inject_custom_css()

# ==============================================================================
# Maintainable Module Registry
# Defines all 12 independent ML use cases and their assigned owners.
# Future members can update this registry without altering core routing logic.
# ==============================================================================
MODULE_REGISTRY: List[Dict[str, Any]] = [
    {
        "id": "overview",
        "title": "Platform Overview & Team Dashboard",
        "member": "All Team Members",
        "category": "Platform",
        "icon": "🏠",
        "module_path": None,  # Rendered natively
        "status": "Production",
        "badge_color": "#6366f1",
        "description": "Unified platform dashboard, 12-member architectural matrix, and system analytics.",
    },
    {
        "id": "resume_job_matching",
        "title": "Resume–Job Matching",
        "member": "Member 1 (Lead)",
        "category": "Talent Acquisition",
        "icon": "📄",
        "module_path": "modules.resume_job_matching.interface",
        "status": "Production Ready",
        "badge_color": "#10b981",
        "description": "Hybrid TF-IDF & Skills Taxonomy engine analyzing multi-format resumes (PDF/DOCX) and ATS gaps.",
    },
    {
        "id": "fake_job_detection",
        "title": "Fake Job Posting Detection",
        "member": "Member 2",
        "category": "Trust & Safety",
        "icon": "🛡️",
        "module_path": "modules.fake_job_detection.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "NLP text classifier identifying fraudulent recruitment postings, phishing, and scam signals.",
    },
    {
        "id": "student_performance",
        "title": "Student Performance Prediction",
        "member": "Member 3",
        "category": "Education Analytics",
        "icon": "📈",
        "module_path": "modules.student_performance.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Predictive regression modeling historical academic trajectory, GPA trends, and student risk.",
    },
    {
        "id": "entrance_exam_prediction",
        "title": "Entrance Examination Performance",
        "member": "Member 4",
        "category": "Education Analytics",
        "icon": "🎯",
        "module_path": "modules.entrance_exam_prediction.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Forecasts standardized entrance test percentiles and college admission feasibility tiers.",
    },
    {
        "id": "placement_risk",
        "title": "Student Placement Risk Prediction",
        "member": "Member 5",
        "category": "Career Readiness",
        "icon": "⚠️",
        "module_path": "modules.placement_risk.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Identifies graduating students needing proactive interventions before campus placements.",
    },
    {
        "id": "interview_analyzer",
        "title": "AI Interview Performance Analysis",
        "member": "Member 6",
        "category": "Career Readiness",
        "icon": "🎙️",
        "module_path": "modules.interview_analyzer.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Evaluates candidate answer transcripts, STAR alignment, clarity, and delivery pace.",
    },
    {
        "id": "learning_difficulty",
        "title": "Learning Difficulty Detection",
        "member": "Member 7",
        "category": "Adaptive Learning",
        "icon": "🧩",
        "module_path": "modules.learning_difficulty.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Real-time struggle detection and cognitive bottleneck identification in online course quizzes.",
    },
    {
        "id": "fairness_recruitment",
        "title": "Fairness-Aware Recruitment",
        "member": "Member 8",
        "category": "Ethical AI",
        "icon": "⚖️",
        "module_path": "modules.fairness_recruitment.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Algorithmic bias auditor evaluating disparate impact ratios and demographic parity.",
    },
    {
        "id": "employee_attrition",
        "title": "Employee Attrition Prediction",
        "member": "Member 9",
        "category": "Workforce Analytics",
        "icon": "🔄",
        "module_path": "modules.employee_attrition.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Workplace retention forecasting with explainable feature attribution isolating turnover factors.",
    },
    {
        "id": "resume_analyzer",
        "title": "AI Resume Analysis",
        "member": "Member 10",
        "category": "Talent Acquisition",
        "icon": "🔍",
        "module_path": "modules.resume_analyzer.interface",
        "status": "Production Ready",
        "badge_color": "#10b981",
        "description": "Multi-dimensional resume audit examining ATS readiness, action-verb density, and structure.",
    },
    {
        "id": "internship_fraud_detection",
        "title": "Fake Internship Detection",
        "member": "Member 11",
        "category": "Trust & Safety",
        "icon": "🚨",
        "module_path": "modules.internship_fraud_detection.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Protects student applicants against deceptive, unpaid, or fee-charging internship listings.",
    },
    {
        "id": "personalized_learning",
        "title": "Personalized Learning Recommendations",
        "member": "Member 12",
        "category": "Adaptive Learning",
        "icon": "💡",
        "module_path": "modules.personalized_learning.interface",
        "status": "In Development",
        "badge_color": "#f59e0b",
        "description": "Curates custom skill-building roadmaps and learning modules matched to candidate gaps.",
    },
]


def load_module_render_fn(module_path: str) -> Optional[Callable[[], None]]:
    """
    Dynamically imports a module's render() function on demand.
    Avoids loading all 12 ML models into memory during initial app startup.
    """
    try:
        mod = importlib.import_module(module_path)
        render_fn = getattr(mod, "render", None)
        if not render_fn or not callable(render_fn):
            raise AttributeError(f"Module '{module_path}' has no callable 'render()' function.")
        return render_fn
    except Exception as exc:
        st.error(f"❌ **Error Loading Module (`{module_path}`)**")
        st.markdown(
            f"> **Exception:** `{type(exc).__name__}: {str(exc)}`\n\n"
            "This error has been captured safely. Please verify that all dependencies and "
            "module source files are present."
        )
        with st.expander("View Diagnostic Traceback", expanded=False):
            st.code(traceback.format_exc(), language="python")
        return None


def render_top_navbar(current_module: Optional[Dict[str, Any]] = None) -> None:
    """
    Renders a full-width top navigation header bar with brand logo and breadcrumbs.
    """
    nav_col1, nav_col2 = st.columns([3, 1.5])

    with nav_col1:
        if current_module and current_module["id"] != "overview":
            # Inside a module view: Show back button and breadcrumb
            back_clicked = st.button("← Back to All Modules Dashboard", key="nav_back_btn", type="secondary")
            if back_clicked:
                st.session_state["current_module_id"] = "overview"
                st.rerun()

            st.markdown(
                f"""
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">
                    <span style="color: #6366f1; font-weight: 600;">TalentBridge AI</span> / 
                    <span>{current_module['category']}</span> / 
                    <strong style="color: #0f172a;">{current_module['icon']} {current_module['title']}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # On overview: Show primary brand identity
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 2rem; line-height: 1;">🌉</span>
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">
                            TalentBridge AI
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 500;">
                            12-Member Integrated Machine Learning Platform
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with nav_col2:
        st.markdown(
            """
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 0.5rem; height: 100%;">
                <span style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
                             padding: 4px 10px; border-radius: 9999px; font-size: 0.76rem; font-weight: 700;">
                    ● 2 Production Ready
                </span>
                <span style="background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1;
                             padding: 4px 10px; border-radius: 9999px; font-size: 0.76rem; font-weight: 700;">
                    10 Scaffolds
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='border-bottom: 1px solid #e2e8f0; margin: 1rem 0 1.5rem 0;'></div>", unsafe_allow_html=True)


def render_platform_overview() -> None:
    """
    Modern executive landing dashboard with interactive flashcards.
    Clicking any flashcard opens that module directly without sidebar navigation.
    """
    # Hero Section
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
                    padding: 2.5rem 2.5rem; border-radius: 18px; margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 16px 36px -8px rgba(15, 23, 42, 0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="max-width: 820px;">
                    <div style="display: inline-block; background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4);
                                color: #a5b4fc; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.65rem;">
                        ✨ Full-Width Portal Architecture
                    </div>
                    <h1 style="margin: 0; font-size: 2.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em;">
                        Talent Intelligence & ML Ecosystem
                    </h1>
                    <p style="margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 1.02rem; line-height: 1.5;">
                        Explore our 12 independent machine learning modules. Click on any card below to launch its dedicated AI workspace.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="Total ML Engines", value="12 Modules", help="Independent machine learning systems")
    with kpi2:
        st.metric(label="Active Production Engines", value="2 Modules", help="Member 1 (Resume Matching) & Member 10 (Resume Analyzer)")
    with kpi3:
        st.metric(label="Team Contributors", value="12 Leads", help="Strictly isolated development sandboxes")
    with kpi4:
        st.metric(label="Quality Assurance", value="31 Tests Passed", help="Automated pytest suite & GitHub Actions CI")

    st.markdown("<br>", unsafe_allow_html=True)

    # Section Header
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.25rem;">
            <div>
                <h3 style="margin: 0; font-size: 1.4rem; font-weight: 800; color: #0f172a;">
                    ⚡ Interactive Module Flashcards
                </h3>
                <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.92rem;">
                    Click <strong>Open Module</strong> on any card to launch its machine learning interface.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Interactive 3-Column Flashcard Grid
    modules_list = [m for m in MODULE_REGISTRY if m["id"] != "overview"]
    cols = st.columns(3)

    for idx, mod in enumerate(modules_list):
        col = cols[idx % 3]
        badge_bg = f"{mod['badge_color']}15"
        badge_border = f"{mod['badge_color']}40"

        with col:
            # HTML Card visual
            st.markdown(
                f"""
                <div class="flashcard-box">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                            <span style="font-size: 2rem; line-height: 1;">{mod['icon']}</span>
                            <span style="background: {badge_bg}; color: {mod['badge_color']};
                                         border: 1px solid {badge_border}; padding: 3px 10px;
                                         border-radius: 9999px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase;">
                                ● {mod['status']}
                            </span>
                        </div>
                        <h4 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: #0f172a; line-height: 1.3;">
                            {mod['title']}
                        </h4>
                        <div style="color: #6366f1; font-size: 0.82rem; font-weight: 600; margin: 0.35rem 0 0.6rem 0;">
                            👤 {mod['member']} • <span style="color: #64748b;">{mod['category']}</span>
                        </div>
                        <p style="color: #475569; font-size: 0.88rem; line-height: 1.5; margin: 0 0 1rem 0;">
                            {mod['description']}
                        </p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Direct action button for each flashcard
            is_prod = mod["status"] == "Production Ready"
            btn_label = f"⚡ Launch {mod['title']} →" if is_prod else f"🛠️ Open Scaffold ({mod['title']}) →"
            btn_type = "primary" if is_prod else "secondary"

            if st.button(btn_label, key=f"btn_open_{mod['id']}", type=btn_type, use_container_width=True):
                st.session_state["current_module_id"] = mod["id"]
                st.rerun()

            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Architectural Principles
    st.markdown("### 🏛️ Engineering & Architecture Pillars")
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.35rem; height: 100%;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1.05rem; font-weight: 800;">
                    🔒 Strict Module Isolation
                </h4>
                <p style="color: #64748b; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0;">
                    Each team member owns their dedicated directory under <code>modules/</code>.
                    No member alters another member's pipeline, eliminating merge conflicts completely.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.35rem; height: 100%;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1.05rem; font-weight: 800;">
                    ⚡ Dynamic Contract Loading
                </h4>
                <p style="color: #64748b; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0;">
                    All 12 modules adhere to the <code>render()</code> interface contract.
                    Heavy ML models are loaded lazily on demand, ensuring near-instant sub-second startup.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.35rem; height: 100%;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1.05rem; font-weight: 800;">
                    🛡️ Automated CI Verification
                </h4>
                <p style="color: #64748b; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0;">
                    Every Pull Request is validated against the test suite via GitHub Actions CI.
                    Code cannot merge into <code>main</code> unless all integration tests pass.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_disclaimer()


# ==============================================================================
# Main Application Router
# ==============================================================================
def main() -> None:
    # State tracking for active view
    if "current_module_id" not in st.session_state:
        st.session_state["current_module_id"] = "overview"

    active_id = st.session_state["current_module_id"]

    # Locate current module metadata
    active_module = next((m for m in MODULE_REGISTRY if m["id"] == active_id), None)
    if not active_module:
        active_id = "overview"
        active_module = MODULE_REGISTRY[0]
        st.session_state["current_module_id"] = "overview"

    # Render Top Navigation Bar (with back button if inside a module)
    render_top_navbar(current_module=active_module)

    # Route View
    if active_id == "overview":
        render_platform_overview()
    else:
        render_fn = load_module_render_fn(active_module["module_path"])
        if render_fn:
            try:
                render_fn()
            except Exception as exc:
                st.error(
                    f"❌ **Runtime Execution Error in `{active_module['title']}`**"
                )
                st.markdown(f"> `{type(exc).__name__}: {str(exc)}`")
                with st.expander("Diagnostic Stack Trace"):
                    st.code(traceback.format_exc(), language="python")


if __name__ == "__main__":
    main()
