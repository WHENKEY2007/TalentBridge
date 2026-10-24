"""
TalentBridge AI - AI Resume Analysis Interactive Interface.
Exposes the required render() contract for TalentBridge AI.
Assigned Lead: Member 10
"""

from typing import Dict, Optional
import streamlit as st

from shared.utils import render_disclaimer, render_module_header
from .config import (
    CAREER_LEVELS,
    SAMPLE_RESUMES,
    TARGET_INDUSTRIES,
)
from .model import ResumeAnalyzer
from .preprocessing import parse_document


@st.cache_resource
def get_analyzer_instance() -> ResumeAnalyzer:
    """Caches ResumeAnalyzer instance for high-performance inference."""
    return ResumeAnalyzer()


def render() -> None:
    """
    Entry point for AI Resume Analysis UI in TalentBridge AI.
    Replaces initial scaffold with complete interactive Streamlit interface.
    """
    # 1. Module Header
    render_module_header(
        title="AI Resume Analysis & ATS Readiness",
        member="Member 10",
        description="Deep multi-dimensional resume parsing, structure scoring, action-verb density, and ATS readiness diagnostics.",
        badge="Active ML Model",
        badge_color="#38bdf8",
    )

    analyzer = get_analyzer_instance()

    # Session state for resume text and presets
    if "ra_resume_text" not in st.session_state:
        st.session_state["ra_resume_text"] = SAMPLE_RESUMES["Entry-Level CS Graduate (High Quality)"]["text"]
    if "ra_text_input" not in st.session_state:
        st.session_state["ra_text_input"] = st.session_state["ra_resume_text"]
    if "ra_target_industry" not in st.session_state:
        st.session_state["ra_target_industry"] = "Software & Technology"
    if "ra_career_level" not in st.session_state:
        st.session_state["ra_career_level"] = "Entry-Level / Graduate"

    # 2. Preset Selection & Quick Loaders
    st.markdown("### ⚡ Quick-Load Benchmark Presets")
    st.caption("Select a curated benchmark profile to instantly evaluate model inference across different experience tiers:")
    cols_presets = st.columns(len(SAMPLE_RESUMES))
    for idx, (preset_name, preset_data) in enumerate(SAMPLE_RESUMES.items()):
        with cols_presets[idx]:
            if st.button(preset_name, key=f"btn_preset_{idx}", use_container_width=True):
                st.session_state["ra_resume_text"] = preset_data["text"]
                st.session_state["ra_text_input"] = preset_data["text"]
                st.session_state["ra_target_industry"] = preset_data["industry"]
                st.session_state["ra_career_level"] = preset_data["level"]
                st.session_state["ra_industry_select"] = preset_data["industry"]
                st.session_state["ra_level_radio"] = preset_data["level"]
                st.rerun()

    st.markdown("---")

    # 3. Main Input Section
    col_input, col_config = st.columns([1.6, 1.0], gap="large")

    with col_input:
        st.markdown("#### 📄 Candidate Resume Input")
        upload_tab, text_tab = st.tabs(["✍️ Plain Text / Markdown", "📤 Upload Resume (PDF / TXT)"])

        with text_tab:
            resume_text_input = st.text_area(
                "Resume Content (Markdown / Plain Text)",
                value=st.session_state.get("ra_text_input", st.session_state["ra_resume_text"]),
                height=340,
                key="ra_text_input",
                placeholder="Paste the full text of candidate resume here...",
            )
            st.session_state["ra_resume_text"] = resume_text_input

        with upload_tab:
            uploaded_file = st.file_uploader(
                "Upload a PDF or TXT resume document",
                type=["pdf", "txt"],
                help="Uploaded files are processed locally in-memory via pypdfium2.",
                key="ra_file_uploader",
            )
            if uploaded_file is not None:
                parsed_content = parse_document(uploaded_file, filename=uploaded_file.name)
                if parsed_content:
                    st.session_state["ra_resume_text"] = parsed_content
                    st.session_state["ra_text_input"] = parsed_content
                    st.success(f"Extracted {len(parsed_content.split())} words from '{uploaded_file.name}'!")

    with col_config:
        st.markdown("#### ⚙️ Role & Target Alignment")
        selected_industry = st.selectbox(
            "Target Industry / Domain",
            options=TARGET_INDUSTRIES,
            index=TARGET_INDUSTRIES.index(st.session_state["ra_target_industry"])
            if st.session_state["ra_target_industry"] in TARGET_INDUSTRIES
            else 0,
            key="ra_industry_select",
        )
        st.session_state["ra_target_industry"] = selected_industry

        selected_level = st.radio(
            "Target Career Level",
            options=CAREER_LEVELS,
            index=CAREER_LEVELS.index(st.session_state["ra_career_level"])
            if st.session_state["ra_career_level"] in CAREER_LEVELS
            else 0,
            key="ra_level_radio",
        )
        st.session_state["ra_career_level"] = selected_level

        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button("🚀 Analyze Resume with AI", type="primary", use_container_width=True)

    # 4. Analysis and Inference Execution
    current_text = st.session_state.get("ra_resume_text", "").strip()

    if not current_text:
        st.info("💡 Please upload or paste a resume above, or select a Quick-Load Preset to begin analysis.")
        render_disclaimer()
        return

    # Run analysis
    with st.spinner("Executing multi-dimensional NLP audit and ATS scoring..."):
        result = analyzer.analyze_resume(
            current_text,
            industry=st.session_state["ra_target_industry"],
            career_level=st.session_state["ra_career_level"],
        )

    # 5. Visual Dashboard of Results
    overall_score = result["overall_ats_score"]
    tier = result["tier"]
    grade = result["grade"]

    # Color scheme determination
    if overall_score >= 85:
        theme_color = "#22c55e"  # emerald
        status_label = "Elite / High ATS Pass Rate"
    elif overall_score >= 68:
        theme_color = "#38bdf8"  # sky blue
        status_label = "Competitive / Strong Candidate"
    elif overall_score >= 48:
        theme_color = "#f59e0b"  # amber
        status_label = "Developing / Optimization Recommended"
    else:
        theme_color = "#f43f5e"  # rose red
        status_label = "Needs Overhaul / High ATS Rejection Risk"

    st.markdown("<br>", unsafe_allow_html=True)

    # Hero Result Card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    border-radius: 14px; padding: 1.8rem; border: 1.5px solid {theme_color}55;
                    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4); margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <span style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">
                        Overall ATS Readiness Score
                    </span>
                    <div style="display: flex; align-items: baseline; gap: 0.8rem; margin-top: 0.3rem;">
                        <span style="color: {theme_color}; font-size: 3.4rem; font-weight: 800; line-height: 1;">
                            {overall_score:.1f}
                        </span>
                        <span style="color: #64748b; font-size: 1.5rem; font-weight: 500;">/ 100</span>
                        <span style="background: {theme_color}22; color: {theme_color}; border: 1px solid {theme_color};
                                     padding: 0.3rem 0.9rem; border-radius: 9999px; font-size: 1.1rem; font-weight: 700; margin-left: 0.5rem;">
                            Grade: {grade}
                        </span>
                    </div>
                    <div style="color: #e2e8f0; font-size: 1.05rem; font-weight: 500; margin-top: 0.6rem;">
                        🎯 Assessment Tier: <strong style="color: {theme_color};">{tier}</strong> — {status_label}
                    </div>
                </div>
                <div style="text-align: right; background: #0b1120; padding: 1rem 1.4rem; border-radius: 10px; border: 1px solid #334155;">
                    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Target Parameters</div>
                    <div style="color: #f8fafc; font-size: 0.95rem; font-weight: 600; margin-top: 0.3rem;">🏢 {result['industry']}</div>
                    <div style="color: #38bdf8; font-size: 0.85rem; font-weight: 500; margin-top: 0.2rem;">💼 {result['career_level']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Quick Metric Cards
    verbs = result["verbs_audit"]
    quant = result["quantification_audit"]
    readability = result["readability_audit"]
    comps = result["component_scores"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="⚡ Action Verb Density",
            value=f"{verbs['action_verb_density_pct']}%",
            delta=f"{verbs['total_unique_action_verbs']} power verbs",
            help="Percentage of bullet points starting with high-impact action verbs.",
        )
    with m2:
        st.metric(
            label="📊 Quantified Impact",
            value=f"{quant['quantification_pct']}%",
            delta=f"{len(quant['extracted_metrics'])} metrics found",
            help="Percentage of bullets with measurable outcomes, percentages, or dollar figures.",
        )
    with m3:
        st.metric(
            label="🏛️ Structure Completeness",
            value=f"{comps['structural_completeness']}%",
            delta="6 Core Sections",
            help="Coverage of essential ATS resume sections.",
        )
    with m4:
        st.metric(
            label="📖 Word Count & Length",
            value=f"{readability['word_count']} words",
            delta=f"~{readability['estimated_pages']} pages",
            help="Estimated length and page density.",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Detailed Multi-Tab Diagnostic Deep-Dive
    tabs = st.tabs([
        "📊 Score Breakdown",
        "⚡ Power Verbs & Impact",
        "🎯 Industry Taxonomy",
        "💡 Actionable Recommendations",
        "📄 Parsed Content & Contacts",
    ])

    # Tab 1: Component Breakdown
    with tabs[0]:
        st.markdown("#### 🔬 Component Score Analysis")
        col_bars, col_sections = st.columns([1.2, 1.0], gap="large")

        with col_bars:
            st.markdown("##### Sub-Dimension Scores")
            for comp_name, comp_val in comps.items():
                label_formatted = comp_name.replace("_", " ").title()
                st.write(f"**{label_formatted}** ({comp_val}/100)")
                st.progress(min(max(comp_val / 100.0, 0.0), 1.0))

        with col_sections:
            st.markdown("##### Section Presence Audit")
            secs = result["sections_audit"]
            for sec_key, sec_data in secs.items():
                is_present = sec_data["found"]
                icon = "✅" if is_present else "❌"
                status_text = f"Found ({sec_data['word_count']} words)" if is_present else "Missing / Not Detected"
                badge_bg = "#14532d" if is_present else "#7f1d1d"
                badge_fg = "#86efac" if is_present else "#fca5a5"

                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center;
                                padding: 0.5rem 0.8rem; background: #0f172a; border-radius: 6px;
                                margin-bottom: 0.4rem; border: 1px solid #1e293b;">
                        <span style="color: #f1f5f9; font-weight: 500;">{icon} {sec_key.title()}</span>
                        <span style="background: {badge_bg}; color: {badge_fg}; font-size: 0.75rem;
                                     padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600;">
                            {status_text}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Tab 2: Action Verbs & Impact
    with tabs[1]:
        st.markdown("#### ⚡ Power Verbs & Metric Quantification")

        c_v1, c_v2 = st.columns(2, gap="large")
        with c_v1:
            st.markdown("##### 🚀 Strong Action Verbs Identified")
            cat_verbs = verbs["categorized_verbs"]
            has_any_verbs = False
            for group, v_list in cat_verbs.items():
                if v_list:
                    has_any_verbs = True
                    chips = " ".join([f"`{v}`" for v in v_list])
                    st.markdown(f"**{group}:** {chips}")
            if not has_any_verbs:
                st.warning("No strong action verbs were identified. Start each bullet point with high-impact verbs.")

            if verbs["weak_count"] > 0:
                st.markdown("##### ⚠️ Passive & Cliché Phrases Flagged")
                st.error(f"Found {verbs['weak_count']} passive or unimpactful phrases:")
                for item in verbs["improvement_advice"]:
                    alts = ", ".join(f"**{a}**" for a in item["alternatives"])
                    st.markdown(f"- ❌ Avoid: `{item['weak_phrase']}` ➔ ✨ Consider: {alts}")
            else:
                st.success("✅ Excellent! No passive clichés or weak phrases were detected.")

        with c_v2:
            st.markdown("##### 📈 Quantified Achievements Detected")
            if quant["extracted_metrics"]:
                st.markdown("**Sample Metrics Detected:**")
                for m in quant["extracted_metrics"][:8]:
                    st.markdown(f"- 🎯 `{m}`")
            else:
                st.warning("No explicit numerical achievements (%, $, numbers) were found.")

            if quant["quantified_samples"]:
                st.markdown("**Top Impact Bullet Points:**")
                for s in quant["quantified_samples"][:3]:
                    st.info(f"💡 \"{s}\"")

    # Tab 3: Industry Taxonomy
    with tabs[2]:
        ind_audit = result["industry_audit"]
        st.markdown(f"#### 🎯 {ind_audit['industry']} Skill Coverage")

        col_ind1, col_ind2 = st.columns(2, gap="large")
        with col_ind1:
            st.markdown(f"##### ✅ Matched Skills ({ind_audit['matched_count']} / {ind_audit['total_taxonomy_skills']})")
            if ind_audit["matched_skills"]:
                chips = " ".join([f"`{s}`" for s in ind_audit["matched_skills"]])
                st.markdown(chips)
            else:
                st.warning("No core industry skills matched this target sector.")

        with col_ind2:
            st.markdown("##### 📌 High-Priority Keywords to Consider Adding")
            if ind_audit["missing_recommendations"]:
                chips = " ".join([f"`{s}`" for s in ind_audit["missing_recommendations"][:12]])
                st.markdown(chips)
                st.caption("Naturally include applicable competencies that align with your genuine background.")
            else:
                st.success("Comprehensive skill coverage across target industry taxonomy!")

    # Tab 4: Prioritized Recommendations
    with tabs[3]:
        st.markdown("#### 💡 Prioritized Optimization Checklist")
        recs = result["recommendations"]

        if not recs:
            st.success("🎉 Outstanding resume! No high-priority structural or content issues found.")
        else:
            for r in recs:
                p = r["priority"]
                color_p = "#ef4444" if p == "Critical" else ("#f59e0b" if p == "High" else "#38bdf8")
                st.markdown(
                    f"""
                    <div style="background: #0f172a; border-left: 4px solid {color_p};
                                padding: 0.9rem 1.2rem; border-radius: 6px; margin-bottom: 0.8rem;
                                border-top: 1px solid #1e293b; border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="color: #f8fafc; font-size: 1rem;">{r['title']}</strong>
                            <span style="color: {color_p}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">
                                [{p} Priority] • {r['category']}
                            </span>
                        </div>
                        <p style="color: #94a3b8; margin: 0.35rem 0 0 0; font-size: 0.9rem;">
                            {r['detail']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Tab 5: Parsed Content & Contacts
    with tabs[4]:
        st.markdown("#### 👤 Extracted Contact Details & Cleaned Text")
        contact_data = result["contact_audit"]["fields"]

        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown(f"- **Email:** `{contact_data.get('email') or 'Not Found'}`")
            st.markdown(f"- **Phone:** `{contact_data.get('phone') or 'Not Found'}`")
            st.markdown(f"- **Location:** `{contact_data.get('location') or 'Not Found'}`")
        with c_info2:
            st.markdown(f"- **LinkedIn:** `{contact_data.get('linkedin') or 'Not Found'}`")
            st.markdown(f"- **GitHub:** `{contact_data.get('github') or 'Not Found'}`")
            st.markdown(f"- **Portfolio:** `{contact_data.get('portfolio') or 'Not Found'}`")

        st.markdown("---")
        st.markdown("##### 📄 Segmented Text Preview")
        for sec_name, s_data in result["sections_audit"].items():
            if s_data["found"] and s_data["content"]:
                with st.expander(f"{sec_name.title()} ({s_data['word_count']} words)"):
                    st.text(s_data["content"])

    # 7. Ethical AI Disclaimer
    render_disclaimer(
        custom_message="<strong>TalentBridge AI Diagnostics:</strong> ATS compatibility scores and action-verb metrics "
        "are automated natural language processing indicators designed to optimize resume readability and keyword discoverability. "
        "Scores do not guarantee interviews or employment offers. Final recruitment decisions are made by human hiring authorities."
    )
