"""
TalentBridge AI - Production Resume–Job Matching User Interface.
Enterprise-grade UI with document parsing (PDF/DOCX), taxonomy breakdown, and ATS optimization.
"""

import streamlit as st

from shared.utils import inject_custom_css, render_disclaimer, render_module_header
from .config import JOB_PRESETS, SAMPLE_JOB_DESCRIPTION, SAMPLE_RESUME
from .model import ResumeJobMatcher
from .preprocessing import parse_document


def render() -> None:
    """
    Renders the modern, enterprise Streamlit user interface for Resume–Job Matching.
    Adheres strictly to the TalentBridge AI interface contract.
    """
    inject_custom_css()

    render_module_header(
        title="Resume–Job Matching Engine",
        member="Member 1 (Lead Architect)",
        description=(
            "Hybrid talent intelligence engine analyzing multi-format resume documents (PDF, DOCX, TXT), "
            "domain skills taxonomy coverage across 6 technical categories, and actionable ATS readiness diagnostics."
        ),
        badge="Production Ready",
        badge_color="#10b981",
    )

    # Session State Initialization
    if "active_resume_text" not in st.session_state:
        st.session_state["active_resume_text"] = SAMPLE_RESUME
    if "active_job_text" not in st.session_state:
        st.session_state["active_job_text"] = SAMPLE_JOB_DESCRIPTION

    # Top Controls Bar (Clean Card Styling)
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
                    padding: 1rem 1.25rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size: 0.85rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                🎯 Quick Configuration & Presets
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    control_c1, control_c2, control_c3 = st.columns([2.5, 1.2, 1.2])

    with control_c1:
        preset_names = list(JOB_PRESETS.keys()) + ["Custom Job Description"]
        selected_preset = st.selectbox(
            label="Target Job Role Preset:",
            options=preset_names,
            index=0,
            help="Choose a pre-configured technical job description or enter your own custom text."
        )
        if selected_preset in JOB_PRESETS:
            st.session_state["active_job_text"] = JOB_PRESETS[selected_preset]

    with control_c2:
        st.write("")
        st.write("")
        if st.button("📋 Load Sample Data", use_container_width=True, help="Load benchmark sample resume and job posting"):
            st.session_state["active_resume_text"] = SAMPLE_RESUME
            st.session_state["active_job_text"] = JOB_PRESETS["Senior Python Backend Engineer"]
            st.rerun()

    with control_c3:
        st.write("")
        st.write("")
        if st.button("🧹 Clear All", use_container_width=True, help="Reset all text fields"):
            st.session_state["active_resume_text"] = ""
            st.session_state["active_job_text"] = ""
            st.rerun()

    # Input Columns: Document / Resume Ingestion & Target Job Description
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">📄</span>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #0f172a;">
                    Candidate Resume
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_upload, tab_paste = st.tabs(["📁 Upload File (PDF / DOCX / TXT)", "✍️ Paste Resume Text"])

        with tab_upload:
            uploaded_file = st.file_uploader(
                label="Upload a resume file",
                type=["pdf", "docx", "doc", "txt"],
                help="Supports standard PDF, Microsoft Word (.docx), or plain text resume documents."
            )
            if uploaded_file is not None:
                try:
                    with st.spinner("Extracting text and structure from uploaded document..."):
                        extracted_text = parse_document(uploaded_file, uploaded_file.name)
                        if extracted_text:
                            st.session_state["active_resume_text"] = extracted_text
                            st.success(
                                f"✅ Extracted **{len(extracted_text.split())} words** from `{uploaded_file.name}`"
                            )
                        else:
                            st.warning("Uploaded file appeared empty or could not be read.")
                except Exception as exc:
                    st.error(f"Failed to parse document: {str(exc)}")

            if st.session_state["active_resume_text"]:
                with st.expander("👁️ Preview Extracted Resume Text", expanded=False):
                    preview_txt = st.session_state["active_resume_text"][:800]
                    st.text(preview_txt + ("..." if len(st.session_state["active_resume_text"]) > 800 else ""))

        with tab_paste:
            pasted_resume = st.text_area(
                label="Raw Resume Plain Text",
                value=st.session_state["active_resume_text"],
                height=310,
                key="resume_paste_box",
                placeholder="Paste candidate resume, CV sections, or project descriptions here...",
            )
            if pasted_resume != st.session_state["active_resume_text"]:
                st.session_state["active_resume_text"] = pasted_resume

    with col_right:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">💼</span>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #0f172a;">
                    Target Job Description
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        job_text = st.text_area(
            label="Job Requirements & Technical Stack",
            value=st.session_state["active_job_text"],
            height=375,
            key="job_description_box",
            placeholder="Paste vacancy requirements, technical qualifications, and tech stack here...",
        )
        if job_text != st.session_state["active_job_text"]:
            st.session_state["active_job_text"] = job_text

    st.markdown("<br>", unsafe_allow_html=True)
    match_btn = st.button("⚡ Run Resume–Job Matching Analysis", type="primary", use_container_width=True)

    # Execution & Results Presentation
    if match_btn:
        active_resume = st.session_state["active_resume_text"].strip()
        active_job = st.session_state["active_job_text"].strip()

        if not active_resume or not active_job:
            st.warning("⚠️ Please provide both a Resume and a Job Description before matching.")
            return

        with st.spinner("Executing hybrid matching (TF-IDF + Domain Skills Taxonomy + ATS Audit)..."):
            matcher = ResumeJobMatcher.load()
            results = matcher.predict(resume_text=active_resume, job_text=active_job)

        st.markdown("---")
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #0f172a;">
                    📊 Comprehensive Matching Diagnostics
                </h3>
                <span style="color: #64748b; font-size: 0.85rem; font-weight: 600;">
                    Hybrid Scoring: 55% Skills + 45% Contextual
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Top 4 KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(
                label="Overall Match Score",
                value=f"{results['match_percentage']}%",
                help="Composite metric combining technical skills overlap (55%) and TF-IDF similarity (45%)."
            )
        with m2:
            st.metric(
                label="Skills Coverage",
                value=f"{results['skills_overlap_percentage']}%",
                help="Percentage of technical skills required in the job description found on the resume."
            )
        with m3:
            st.metric(
                label="Textual Alignment",
                value=f"{results['textual_similarity_percentage']}%",
                help="Cosine similarity across vocabulary, context, and experience descriptions."
            )
        with m4:
            st.metric(
                label="Classification Tier",
                value=results["match_level"],
                help="High (>=75%), Moderate (45-74%), Low (<45%)"
            )

        # Visual progress bar
        st.progress(float(results["similarity_score"]), text=f"Composite Suitability: {results['match_percentage']}%")

        # Verdict notification banner
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid {results['match_color']};
                        padding: 1rem 1.25rem; border-radius: 12px; margin: 1.25rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
                    <h4 style="margin: 0; color: {results['match_color']}; font-weight: 800; font-size: 1.1rem;">
                        {results['match_level']}
                    </h4>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #64748b;">
                        Candidate Fit Evaluation
                    </span>
                </div>
                <p style="margin: 0; font-size: 0.94rem; color: #334155; line-height: 1.5;">
                    {results['verdict']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabbed Deep-Dive Analytics
        tab_skills, tab_ats, tab_action = st.tabs([
            "🎯 Skills Taxonomy & Gap Breakdown",
            "📝 ATS Readiness & Impact Diagnostics",
            "🚀 Step-by-Step Optimization Plan",
        ])

        # ----------------------------------------------------------------------
        # Tab A: Skills Gap Breakdown
        # ----------------------------------------------------------------------
        with tab_skills:
            st.markdown("#### Technical Competencies by Category")
            category_breakdown = results["category_breakdown"]

            cat_cols = st.columns(3)
            categories = list(category_breakdown.keys())

            for i, cat in enumerate(categories):
                col = cat_cols[i % 3]
                data = category_breakdown[cat]
                cov_color = "#10b981" if data["coverage_percent"] >= 70 else ("#f59e0b" if data["coverage_percent"] >= 40 else "#ef4444")

                with col:
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; background-color: #ffffff; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong style="font-size: 0.92rem; color: #0f172a;">{cat}</strong>
                                <span style="font-size: 0.78rem; font-weight: 700; color: {cov_color}; background: {cov_color}1a; padding: 2px 8px; border-radius: 9999px;">
                                    {data['matched_count']}/{data['required_count']} ({data['coverage_percent']}%)
                                </span>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if data["matched"]:
                        st.caption("✅ Matched: " + ", ".join(data["matched"]))
                    if data["missing"]:
                        st.caption("❌ Missing: " + ", ".join(data["missing"]))
                    if not data["matched"] and not data["missing"]:
                        st.caption("ℹ️ No requirements in this category.")
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            skill_c1, skill_c2 = st.columns(2)

            with skill_c1:
                st.markdown("#### ✅ Matched Required Skills")
                if results["matched_keywords"]:
                    badges = "".join([
                        f"<span style='background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; padding: 4px 10px; "
                        f"border-radius: 12px; font-size: 0.82rem; font-weight: 600; margin: 3px; display: inline-block;'>"
                        f"✓ {s}</span>"
                        for s in results["matched_keywords"]
                    ])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.info("No matching taxonomy skills identified.")

            with skill_c2:
                st.markdown("#### ❌ Critical Skill Gaps (In JD but Not on Resume)")
                if results["missing_keywords"]:
                    badges = "".join([
                        f"<span style='background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; padding: 4px 10px; "
                        f"border-radius: 12px; font-size: 0.82rem; font-weight: 600; margin: 3px; display: inline-block;'>"
                        f"✗ {s}</span>"
                        for s in results["missing_keywords"]
                    ])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.success("🎉 Superb! All technical competencies specified in the job are present on the resume.")

            if results["bonus_skills"]:
                with st.expander("✨ Candidate Additional Skills (Bonus Competencies)", expanded=False):
                    st.markdown(
                        ", ".join(f"`{s}`" for s in results["bonus_skills"][:20])
                        + ("..." if len(results["bonus_skills"]) > 20 else "")
                    )

        # ----------------------------------------------------------------------
        # Tab B: ATS Diagnostics
        # ----------------------------------------------------------------------
        with tab_ats:
            ats = results["ats_audit"]
            st.markdown("#### Applicant Tracking System (ATS) Structural Health")

            ats_c1, ats_c2, ats_c3, ats_c4 = st.columns(4)
            with ats_c1:
                st.metric(label="Resume Word Count", value=f"{ats['word_count']} words", delta=ats["length_status"])
            with ats_c2:
                st.metric(label="Standard Sections", value=f"{len(ats['sections_present'])} / 5 Detected")
            with ats_c3:
                st.metric(label="Action Verbs", value=f"{ats['action_verb_count']} found")
            with ats_c4:
                st.metric(label="Quantified Metrics", value=f"{ats['quantification_count']} metrics")

            st.markdown("---")
            sec_col1, sec_col2 = st.columns(2)

            with sec_col1:
                st.markdown("##### 📑 Section Headers Checklist")
                for sec in ["Contact Info", "Professional Experience", "Education", "Skills", "Projects"]:
                    if sec in ats["sections_present"]:
                        st.markdown(f"- ✅ **{sec}**: Detected")
                    else:
                        st.markdown(f"- ⚠️ **{sec}**: *Missing or non-standard heading*")

            with sec_col2:
                st.markdown("##### 💥 Strong Action Verbs Identified")
                if ats["action_verbs_found"]:
                    st.write(", ".join(f"`{v}`" for v in ats["action_verbs_found"][:15]))
                else:
                    st.warning("Few or no strong action verbs detected. Upgrade passive bullet points.")

        # ----------------------------------------------------------------------
        # Tab C: Action Plan
        # ----------------------------------------------------------------------
        with tab_action:
            st.markdown("#### 🚀 Actionable Strategy to Maximize Match Rate")
            for idx, plan_item in enumerate(results["optimization_plan"], 1):
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
                                padding: 0.9rem 1.15rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                        <strong style="color: #6366f1;">Step {idx}:</strong> {plan_item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Mandatory Ethical AI Guidance
    render_disclaimer(
        custom_message=(
            "<strong>Notice & Ethical AI Guidance:</strong> The Resume–Job Matching score is an analytical "
            "representation of textual alignment and domain skills taxonomy overlap. "
            "<strong>It is NOT a probability of being hired or an employment certification.</strong> "
            "Holistic human evaluation considering cultural values, problem solving, teamwork, and code reviews must always govern talent decisions."
        )
    )
