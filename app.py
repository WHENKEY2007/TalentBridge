"""
TalentBridge AI - Integrated Machine Learning Platform
Central Streamlit Application & Enterprise Module Registry
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

from shared.utils import inject_custom_css, render_disclaimer, render_module_header

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="TalentBridge AI — Enterprise ML Platform",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Global Enterprise Design System
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
        "description": "Hybrid TF-IDF & Skills Taxonomy engine analyzing document resumes (PDF/DOCX) and ATS gaps.",
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


def render_platform_overview() -> None:
    """
    Sleek, modern executive landing dashboard showcasing platform architecture,
    live module statuses, and team matrix in an elegant 3-column card grid.
    """
    # Hero Section
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
                    padding: 2.75rem 2.5rem; border-radius: 18px; margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 16px 36px -8px rgba(15, 23, 42, 0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 1.25rem;">
                    <div style="background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(99, 102, 241, 0.5);
                                width: 60px; height: 60px; border-radius: 14px; display: flex; align-items: center;
                                justify-content: center; font-size: 2.2rem; box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);">
                        🌉
                    </div>
                    <div>
                        <h1 style="margin: 0; font-size: 2.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em;">
                            TalentBridge AI
                        </h1>
                        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 1.05rem; font-weight: 400;">
                            Integrated Machine Learning Platform for Talent Intelligence, Education & Workforce Analytics
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);
                                 padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700;">
                        ● System Healthy
                    </span>
                    <span style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3);
                                 padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700;">
                        12 Modules
                    </span>
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
        st.metric(label="Quality Assurance", value="18 Tests Passed", help="Automated pytest suite & GitHub Actions CI")

    st.markdown("<br>", unsafe_allow_html=True)

    # Section Header
    st.markdown("### 📋 12-Member Use Case Ecosystem")
    st.markdown(
        "<p style='color: #64748b; font-size: 0.95rem; margin-top: -0.5rem;'>"
        "Each module is developed independently inside <code>modules/&lt;name&gt;/</code> "
        "and loaded on demand through the platform interface contract."
        "</p>",
        unsafe_allow_html=True,
    )

    # 3-Column Modern Grid of Module Cards
    non_overview_modules = [m for m in MODULE_REGISTRY if m["id"] != "overview"]
    cols = st.columns(3)

    for idx, mod in enumerate(non_overview_modules):
        col = cols[idx % 3]
        badge_bg = f"{mod['badge_color']}15"
        badge_border = f"{mod['badge_color']}40"

        with col:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
                            padding: 1.35rem; margin-bottom: 1.25rem; min-height: 220px;
                            display: flex; flex-direction: column; justify-content: space-between;
                            box-shadow: 0 4px 12px -2px rgba(0,0,0,0.03); transition: transform 0.2s ease;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.65rem;">
                            <span style="font-size: 1.6rem; line-height: 1;">{mod['icon']}</span>
                            <span style="background: {badge_bg}; color: {mod['badge_color']};
                                         border: 1px solid {badge_border}; padding: 0.2rem 0.65rem;
                                         border-radius: 9999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">
                                {mod['status']}
                            </span>
                        </div>
                        <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #0f172a; line-height: 1.3;">
                            {mod['title']}
                        </h4>
                        <div style="color: #6366f1; font-size: 0.8rem; font-weight: 600; margin: 0.35rem 0 0.5rem 0;">
                            👤 {mod['member']} • <span style="color: #64748b;">{mod['category']}</span>
                        </div>
                        <p style="color: #475569; font-size: 0.84rem; line-height: 1.45; margin: 0;">
                            {mod['description']}
                        </p>
                    </div>
                    <div style="margin-top: 0.85rem; padding-top: 0.65rem; border-top: 1px solid #f1f5f9;
                                display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #94a3b8;">
                        <code>modules/{mod['id']}/</code>
                        <span style="color: #6366f1; font-weight: 600;">Select in sidebar →</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Architectural Principles
    st.markdown("### 🏛️ Engineering & Architecture Pillars")
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1rem; font-weight: 700;">
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
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1rem; font-weight: 700;">
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
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem;">
                <h4 style="margin-top: 0; color: #0f172a; font-size: 1rem; font-weight: 700;">
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
# Sidebar Navigation & Execution
# ==============================================================================
def main() -> None:
    # Sidebar Header Branding
    st.sidebar.markdown(
        """
        <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid #f1f5f9; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
                <span style="font-size: 1.85rem; line-height: 1;">🌉</span>
                <div>
                    <h3 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 1.2rem; letter-spacing: -0.02em;">
                        TalentBridge AI
                    </h3>
                    <span style="background: #e0e7ff; color: #4338ca; padding: 2px 7px; border-radius: 4px;
                                 font-size: 0.68rem; font-weight: 700; text-transform: uppercase;">
                        v1.0 • Enterprise Edition
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Format list for radio buttons with clear icons
    module_labels = [f"{m['icon']} {m['title']}" for m in MODULE_REGISTRY]

    selected_idx = st.sidebar.radio(
        label="Select Application Module:",
        options=range(len(MODULE_REGISTRY)),
        format_func=lambda i: module_labels[i],
        index=0,
    )

    selected_module = MODULE_REGISTRY[selected_idx]

    # Sidebar Active Module Card
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    status_color = selected_module.get("badge_color", "#6366f1")
    status_text = selected_module.get("status", "Active")

    st.sidebar.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
                    padding: 0.9rem; font-size: 0.82rem; margin-bottom: 1rem;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.3rem;">
                {selected_module['icon']} {selected_module['title']}
            </div>
            <div style="color: #64748b; margin-bottom: 0.2rem;">
                <strong>Lead:</strong> {selected_module['member']}
            </div>
            <div style="color: #64748b; margin-bottom: 0.4rem;">
                <strong>Category:</strong> {selected_module['category']}
            </div>
            <div>
                <span style="background: {status_color}1a; color: {status_color}; border: 1px solid {status_color}4d;
                             padding: 2px 8px; border-radius: 9999px; font-weight: 700; font-size: 0.72rem; text-transform: uppercase;">
                    ● {status_text}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div style="font-size: 0.75rem; color: #94a3b8; text-align: center; padding-top: 1rem;">
            TalentBridge AI • 12-Member Modular Architecture
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render selected module or overview
    if selected_module["id"] == "overview":
        render_platform_overview()
    else:
        render_fn = load_module_render_fn(selected_module["module_path"])
        if render_fn:
            try:
                render_fn()
            except Exception as exc:
                st.error(
                    f"❌ **Runtime Execution Error in `{selected_module['title']}`**"
                )
                st.markdown(f"> `{type(exc).__name__}: {str(exc)}`")
                with st.expander("Diagnostic Stack Trace"):
                    st.code(traceback.format_exc(), language="python")


if __name__ == "__main__":
    main()
