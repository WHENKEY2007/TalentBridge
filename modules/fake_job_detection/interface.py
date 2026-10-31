"""
TalentBridge AI - Fake Job Posting Detection & Job Authenticity Scanner
Provides live document/text scanning (PDF/DOCX/TXT), fraud risk scoring,
and historical job screening.
Assigned Lead: Member 2
"""

import io
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st
from shared.utils import render_disclaimer

from .analyzer import audit_job_posting_security, parse_job_document
from .model import DATA_PATH, MODEL_PATH, FakeJobDetector

SAMPLE_PRESETS = {
    "🚨 Scam: Internship Training & Certificate Fee ($120)": {
        "title": "AI & Machine Learning Virtual Intern",
        "company": "EduSkills Tech Innovations",
        "text": (
            "Congratulations! Your profile has been selected for our 8-week Remote AI & ML Internship program.\n\n"
            "Roles & Benefits:\n"
            "- Work on live projects and receive an industry-recognized completion certificate & LOR.\n"
            "- Flexible working hours for college students.\n\n"
            "Important Notice for Selected Students:\n"
            "To confirm your seat, issue your verified offer letter, and access our proprietary training kit, "
            "every student intern is required to pay a mandatory internship registration fee of $120 (refundable upon "
            "completion). Please wire the processing charge directly to registrar-eduskills@gmail.com or send via "
            "CashApp. Candidates who do not pay within 24 hours will forfeit their offer letter and certificate."
        ),
    },
    "✅ Legitimate: Senior Python / Cloud Engineer": {
        "title": "Senior Python Backend Engineer",
        "company": "CloudScale Systems Inc.",
        "text": (
            "CloudScale Systems is an enterprise cloud computing and analytics provider "
            "with over 1,200 employees worldwide. We are looking for an experienced Senior "
            "Python Engineer with 5+ years of experience in Django, PostgreSQL, Docker, and AWS.\n\n"
            "Responsibilities:\n"
            "- Architect resilient microservices and distributed APIs.\n"
            "- Participate in peer code reviews, sprint planning, and architecture RFCs.\n"
            "- Optimize query execution plans and ensure 99.9% uptime SLA.\n\n"
            "Qualifications:\n"
            "- Bachelor's or Master's degree in Computer Science or equivalent.\n"
            "- Strong background in REST APIs, relational databases, and CI/CD pipelines.\n\n"
            "Compensation & Benefits:\n"
            "- Base salary $135,000 - $165,000 DOE with annual performance bonus.\n"
            "- Comprehensive health, dental, and vision insurance premiums covered 100%.\n"
            "- 401(k) matching up to 5%, flexible PTO, and home office stipend."
        ),
    },
    "🚨 Scam: Telegram Work-From-Home Data Entry ($50/hr)": {
        "title": "Data Entry Specialist - Immediate Start",
        "company": "Apex Global Career Services LLC",
        "text": (
            "URGENT HIRING: We are seeking 25 remote data entry assistants to start immediately! "
            "Earn $50 per hour working just 2 hours daily from your computer or smartphone. "
            "No prior experience, degree, or technical skills required.\n\n"
            "Do NOT apply through this portal. To secure your interview and immediate placement, "
            "message our Global HR Director Mr. David on Telegram directly at @Global_Recruiter_247 "
            "or contact us via WhatsApp at +1-800-FAKE-JOB.\n\n"
            "Candidates must send their full name, date of birth, SSN, and a photo of their driver's "
            "license to hr-immediate-careers@gmail.com to receive daily payouts via CashApp or Zelle."
        ),
    },
    "🚨 Scam: Advance-Fee Cashier's Check & Equipment Scam": {
        "title": "Virtual Personal Assistant ($900/Week)",
        "company": "FastTrack Global Ventures",
        "text": (
            "We are hiring a dedicated Personal Assistant for remote administrative duties. "
            "You will earn $900 weekly for flexible part-time errands.\n\n"
            "Upon acceptance, our accounting department will courier an official cashier's check "
            "for $4,200 to your home address. You will deposit this check into your personal bank account, "
            "deduct your first week's pay of $900, and immediately wire the remaining balance to our "
            "approved equipment vendor via Western Union, MoneyGram, or Bitcoin ATM to deliver your "
            "home office laptop and software package.\n\n"
            "Immediate hiring — no formal interview needed!"
        ),
    },
}


@st.cache_resource
def load_detector() -> FakeJobDetector:
    """Load the trained detector, auto-training on benchmark data if needed."""
    detector = FakeJobDetector()

    if MODEL_PATH.exists():
        detector.load()
    else:
        detector.train()

    return detector


@st.cache_data(show_spinner=False)
def load_historical_jobs() -> pd.DataFrame:
    """Load job postings for screening and browsing."""
    if not DATA_PATH.exists():
        # Ensure model is trained to generate benchmark data if not yet present
        load_detector()

    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)

    return pd.DataFrame()


@st.cache_data(show_spinner="Screening job listings...")
def get_screened_jobs() -> pd.DataFrame:
    """Return listings classified as legitimate by the model."""
    detector = load_detector()
    jobs = load_historical_jobs()
    if jobs.empty:
        return pd.DataFrame()
    return detector.screen_jobs(jobs)


def render_scanner_tab(detector: FakeJobDetector) -> None:
    """Renders the interactive file upload and job text scanner."""
    st.markdown("### 🛡️ Real-Time Job Authenticity Scanner")
    st.markdown(
        "Upload a job posting document (`.pdf`, `.docx`, `.txt`) or paste posting text "
        "to evaluate fraud risk, detect recruiter red flags, and calculate an authenticity trust score."
    )

    # Preset selection
    st.markdown("##### 💡 Or Test with a Realistic Sample Scenario:")
    p_cols = st.columns(len(SAMPLE_PRESETS))
    for idx, (p_name, p_data) in enumerate(SAMPLE_PRESETS.items()):
        if p_cols[idx].button(p_name, key=f"btn_preset_{idx}", use_container_width=True):
            st.session_state["fjd_title"] = p_data["title"]
            st.session_state["fjd_company"] = p_data["company"]
            st.session_state["fjd_text"] = p_data["text"]
            st.rerun()

    # Input method columns: Upload vs Paste
    col_upload, col_meta = st.columns([1, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "📄 Upload Job Posting Document (PDF, DOCX, TXT)",
            type=["pdf", "docx", "doc", "txt"],
            key="fjd_file_upload",
            help="Upload a saved job posting document or recruitment flyer.",
        )

        extracted_file_text = ""
        if uploaded_file is not None:
            extracted_file_text = parse_job_document(uploaded_file, uploaded_file.name)
            if extracted_file_text:
                st.success(f"✅ Extracted {len(extracted_file_text):,} characters from `{uploaded_file.name}`")
            else:
                st.warning("Could not extract readable text from uploaded file. You can paste the text manually below.")

    with col_meta:
        job_title_input = st.text_input(
            "Job Title (Optional)",
            value=st.session_state.get("fjd_title", ""),
            placeholder="e.g., Software Engineer, Data Entry Assistant",
            key="input_fjd_title",
        )
        company_input = st.text_input(
            "Company / Recruiter Name (Optional)",
            value=st.session_state.get("fjd_company", ""),
            placeholder="e.g., Apex Global Corp",
            key="input_fjd_company",
        )

    # Default text area content
    default_text = extracted_file_text or st.session_state.get("fjd_text", "")

    job_text_input = st.text_area(
        "Job Description & Requirements Text",
        value=default_text,
        height=200,
        placeholder="Paste full job description, email correspondence, requirements, and contact instructions here...",
        key="input_fjd_text",
    )

    scan_button = st.button(
        "🔍 Analyze Job Authenticity & Scan Threat Signals",
        type="primary",
        use_container_width=True,
    )

    if scan_button:
        combined_text = f"{job_title_input} {company_input} {job_text_input}".strip()

        if not combined_text:
            st.error("⚠️ Please upload a document or enter job posting text to analyze.")
            return

        with st.spinner("Evaluating linguistic features and auditing fraud threat vectors..."):
            # 1. ML Model Prediction
            features = {
                "title": job_title_input,
                "company_profile": company_input,
                "description": job_text_input,
                "requirements": "",
                "benefits": "",
            }

            try:
                ml_result = detector.predict(features)
                raw_fraud_prob = float(ml_result.get("fraud_probability", 0.0))
            except Exception:
                raw_fraud_prob = 0.5

            # 2. Heuristic Red Flag & Security Audit
            audit_report = audit_job_posting_security(
                text=job_text_input,
                title=job_title_input,
                company=company_input,
                model_fraud_prob=raw_fraud_prob,
            )

        # Display Results
        st.markdown("---")
        st.markdown("### 📊 Authenticity & Threat Audit Report")

        # Top Banner Verdict
        v_color = audit_report["verdict_color"]
        v_icon = audit_report["badge_icon"]
        v_title = audit_report["verdict"]
        v_threat = audit_report["threat_level"]
        t_score = audit_report["composite_trust_score"]
        f_prob = audit_report["adjusted_fraud_probability"]

        st.markdown(
            f"""
            <div style="background: {v_color}15; border: 2px solid {v_color}; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: {v_color};">
                            {v_icon} {v_title}
                        </div>
                        <div style="color: #475569; font-size: 0.92rem; margin-top: 4px;">
                            Threat Assessment: <strong>{v_threat}</strong> · Analyzed {audit_report['character_count']:,} characters
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.75rem; font-weight: 900; color: {v_color};">
                            {t_score:.1f} <span style="font-size: 1rem; color: #64748b;">/ 100</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">COMPOSITE TRUST SCORE</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Trust Score", f"{t_score:.1f}%", help="Higher is safer. Evaluates likelihood of legitimacy.")
        m2.metric("Fraud Probability", f"{f_prob:.1f}%", help="Combined ML and heuristic fraud likelihood.")
        m3.metric("Red Flags Found", f"{len(audit_report['red_flags'])}", delta_color="inverse")
        m4.metric("Trust Signals", f"{len(audit_report['positive_signals'])}")

        # Red Flags Details
        st.markdown("#### 🚩 Threat & Red-Flag Audit")
        if audit_report["red_flags"]:
            for flag in audit_report["red_flags"]:
                sev_color = "#dc2626" if flag["severity"] == "Critical" else "#f59e0b"
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid {sev_color}; background: #fff5f5; padding: 10px 14px; border-radius: 4px 8px 8px 4px; margin-bottom: 8px;">
                        <strong style="color: {sev_color};">[{flag['severity'].upper()}] {flag['title']}</strong><br/>
                        <span style="font-size: 0.88rem; color: #334155;">{flag['description']}</span><br/>
                        <code style="font-size: 0.82rem; background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top: 4px;">
                            Trigger: {flag['matched_snippet']}
                        </code>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ Zero high-severity fraud triggers or scam patterns detected in the text.")

        # Positive Indicators
        if audit_report["positive_signals"]:
            st.markdown("#### 🟢 Verified Corporate Signals")
            for pos in audit_report["positive_signals"]:
                st.markdown(f"- **{pos['title']}** found in posting text.")

        # Safety Checklist
        st.markdown("#### 🛡️ Candidate Safety Recommendations")
        for step in audit_report["safety_steps"]:
            st.markdown(f"- {step}")

        # Download Report
        report_md = f"""# TalentBridge AI — Job Posting Authenticity Audit

- **Analyzed Job Title:** {job_title_input or 'Unspecified'}
- **Company / Recruiter:** {company_input or 'Unspecified'}
- **Verdict:** {v_title} ({v_threat})
- **Composite Trust Score:** {t_score:.1f} / 100
- **Estimated Fraud Probability:** {f_prob:.1f}%
- **Red Flags Detected:** {len(audit_report['red_flags'])}
- **Positive Trust Signals:** {len(audit_report['positive_signals'])}

## Detected Red Flags
""" + "\n".join([f"- **[{f['severity']}] {f['title']}:** {f['description']} (Matched: `{f['matched_snippet']}`)" for f in audit_report['red_flags']]) + """

## Candidate Action Checklist
""" + "\n".join([f"- {s}" for s in audit_report['safety_steps']])

        st.download_button(
            "📥 Download Authenticity Audit Report (.md)",
            data=report_md,
            file_name="job_authenticity_audit.md",
            mime="text/markdown",
            use_container_width=True,
        )


def render_browser_tab(detector: FakeJobDetector) -> None:
    """Renders the historical job browser and CSV batch screening."""
    st.markdown("### 📋 Screened Historical Job Listings")
    st.markdown(
        "Browse verified listings screened by the ML model. "
        "Postings with estimated fraud probability $\\ge 0.5$ are automatically filtered out."
    )

    try:
        jobs = get_screened_jobs()
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        st.error(f"Unable to load screened job listings: {exc}")
        return

    if jobs.empty:
        st.warning("No listings passed the model's screening.")
        return

    # Search Bar
    search = st.text_input(
        "Search jobs",
        placeholder="Enter a job title, company, or keyword",
        key="fjd_browser_search",
    )

    filtered = jobs

    if search.strip():
        searchable_columns = [
            column
            for column in [
                "title",
                "company_profile",
                "description",
                "requirements",
                "industry",
                "function",
                "location",
            ]
            if column in filtered.columns
        ]

        if searchable_columns:
            matches = filtered[searchable_columns].fillna("").astype(str)
            mask = matches.apply(
                lambda column: column.str.contains(
                    search.strip(), case=False, regex=False
                )
            ).any(axis=1)

            filtered = filtered[mask]

    st.write(f"**{len(filtered):,}** screened listings found")

    # Styling for rows
    st.markdown(
        """
        <style>
        .job-listing-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            border: 1px solid #CBD5E1;
            border-radius: 9px;
            padding: 14px 18px;
            margin: 10px 0 0 0;
            background-color: transparent;
        }
        .job-listing-title {
            font-size: 16px;
            font-weight: 600;
            overflow-wrap: anywhere;
        }
        .job-listing-location {
            font-size: 13px;
            opacity: 0.75;
            margin-top: 4px;
        }
        .job-trust-score {
            flex-shrink: 0;
            text-align: right;
            white-space: nowrap;
            font-size: 15px;
            font-weight: 700;
            color: #15803D;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for listing_index, (_, job) in enumerate(filtered.head(100).iterrows()):
        raw_title = job.get("title")
        title = (
            str(raw_title).strip()
            if pd.notna(raw_title) and str(raw_title).strip()
            else "Untitled role"
        ).replace("**", "")

        raw_location = job.get("location")
        location = (
            str(raw_location).strip()
            if pd.notna(raw_location) and str(raw_location).strip()
            else "Location not specified"
        )

        raw_company = job.get("company_profile")
        company = str(raw_company).strip() if pd.notna(raw_company) else ""

        raw_score = job.get("trust_score", 0.0)
        trust_score = float(raw_score) if pd.notna(raw_score) else 0.0

        st.markdown(
            f"""
            <div class="job-listing-row">
                <div>
                    <div class="job-listing-title">{title}</div>
                    <div class="job-listing-location">{location}</div>
                </div>
                <div class="job-trust-score">
                    Trust Score: {trust_score:.1f}/100
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"View details for {title}", key=f"details_{listing_index}"):
            st.write("**Company information**")
            st.write(company or "No company profile provided.")

            for column, label in [
                ("description", "Job description"),
                ("requirements", "Requirements"),
                ("benefits", "Benefits"),
                ("employment_type", "Employment type"),
                ("required_experience", "Experience"),
                ("required_education", "Education"),
                ("industry", "Industry"),
            ]:
                value = job.get(column)
                if pd.notna(value) and str(value).strip():
                    st.write(f"**{label}:**")
                    st.write(str(value))

            st.button(
                "Apply",
                key=f"apply_historical_{listing_index}",
                disabled=True,
                type="secondary",
                help="Application functionality is not available yet.",
                use_container_width=True,
            )

    if len(filtered) > 100:
        st.caption("Showing the first 100 matching listings.")


def render() -> None:
    """Entry point for Fake Job and Internship Posting Detection interface."""
    st.title("🛡️ Fake Job & Internship Posting Detection")
    st.caption("TalentBridge AI · Natural Language Processing & Fraud Threat Auditing (24B11AI134 & 24P31A42D0)")

    render_disclaimer(
        custom_message=(
            "Our AI model screens job postings and estimates their likelihood of being legitimate. "
            "Trust scores are estimates, not proof of authenticity. Always verify employers and job offers "
            "independently before sharing personal information, banking details, or applying."
        )
    )

    detector = load_detector()

    tab_scan, tab_browse = st.tabs([
        "🔍 Check a Job Posting (Upload / Paste)",
        "📋 Browse Screened Job Listings",
    ])

    with tab_scan:
        render_scanner_tab(detector)

    with tab_browse:
        render_browser_tab(detector)
