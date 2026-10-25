
"""TalentBridge AI - Fake Job Posting Detection and Job Browser."""

import pandas as pd
import streamlit as st

from .model import FakeJobDetector, DATA_PATH, MODEL_PATH


@st.cache_resource
def load_detector() -> FakeJobDetector:
    """Load the trained detector, training it only when needed."""
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
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. "
            "Place fake_job_postings.csv in the module data folder."
        )

    return pd.read_csv(DATA_PATH)


@st.cache_data(show_spinner="Screening job listings...")
def get_screened_jobs() -> pd.DataFrame:
    """Return listings classified as legitimate by the model."""
    detector = load_detector()
    return detector.screen_jobs(load_historical_jobs())


def render() -> None:
    """Display searchable job listings with trust scores."""
    st.title("Job Listings")
    st.caption("TalentBridge AI · Fake Job Posting Detection")

    st.info(
        "Only postings predicted as legitimate by our ML model are shown. "
        "Trust scores are estimates and do not guarantee authenticity."
    )

    try:
        jobs = get_screened_jobs()
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        st.error(f"Unable to load screened job listings: {exc}")
        return

    if jobs.empty:
        st.warning("No listings passed the model's screening.")
        return

    search = st.text_input(
        "Search jobs",
        placeholder="Enter a job title, company, or keyword",
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

    # Styling for a single job row and the Apply button.
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
        div[data-testid="stButton"] button[kind="secondary"]:disabled {
            background-color: #111827;
            color: #FFFFFF;
            border: 1px solid #111827;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for listing_index, (_, job) in enumerate(
        filtered.head(100).iterrows()
    ):
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
        company = (
            str(raw_company).strip()
            if pd.notna(raw_company)
            else ""
        )

        raw_score = job.get("trust_score", 0.0)
        trust_score = (
            float(raw_score) if pd.notna(raw_score) else 0.0
        )

        # One unified row with the title and score inside the same border.
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

        # Expandable details appear directly below the unified row.
        with st.expander(
            f"View details for {title}",
            key=f"details_{listing_index}",
        ):
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
