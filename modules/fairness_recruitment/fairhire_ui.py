
import io
import pandas as pd
import streamlit as st

from fairhire_core import (
    FACTORS,
    analyze,
    find_skills,
    make_scorer,
    parse_resume
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("⚖️ FairHire AI")

st.caption(
    "Upload resumes and a job description. The system selects "
    "candidates and explains every decision, testing gender, "
    "college, age and career gap one at a time."
)


# --------------------------------------------------
# FILE READER
# --------------------------------------------------

def read_file(f):
    name = f.name.lower()

    if name.endswith(".pdf"):
        from pypdf import PdfReader

        return "\n".join(
            page.extract_text() or ""
            for page in PdfReader(io.BytesIO(f.read())).pages
        )

    if name.endswith(".docx"):
        from docx import Document

        return "\n".join(
            paragraph.text
            for paragraph in Document(io.BytesIO(f.read())).paragraphs
        )

    return f.read().decode("utf-8", errors="ignore")


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

with st.expander("⚙️ Settings", expanded=True):

    st.header("Settings")

    mode = st.radio(
        "Scoring model",
        [
            "Skills match (no bias)",
            "Simulated biased model (demo)",
            "LLM (Gemini / OpenAI)"
        ]
    )

    strength = (
        st.slider(
            "Simulated bias strength",
            0.0, 2.0, 1.0, 0.1
        )
        if mode.startswith("Simulated")
        else 1.0
    )

    provider = key = model = ""

    if mode.startswith("LLM"):

        provider = st.selectbox(
            "Provider",
            ["Gemini", "OpenAI"]
        )

        key = st.text_input(
            "API key",
            type="password"
        )

        model = st.text_input(
            "Model name",
            "gemini-2.0-flash"
            if provider == "Gemini"
            else "gpt-4o-mini"
        )

    top_n = st.number_input(
        "How many to shortlist",
        1, 50, 3
    )

    threshold = st.slider(
        "Bias threshold (avg score change, points)",
        0.5, 10.0, 2.0, 0.5
    )


# --------------------------------------------------
# RESUME AND JOB DESCRIPTION UPLOAD
# --------------------------------------------------

st.subheader("📄 Upload Candidate Resumes")

c1, c2 = st.columns(2)

resumes = c1.file_uploader(
    "Resumes (PDF, DOCX or TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

jd_file = c2.file_uploader(
    "Job description (optional file)",
    type=["pdf", "docx", "txt"]
)

jd = c2.text_area(
    "...or paste the job description",
    height=130
)


# --------------------------------------------------
# CANDIDATE SELECTION
# --------------------------------------------------

if st.button("🚀 Select candidates", type="primary"):

    if jd_file:
        jd = read_file(jd_file)

    required = find_skills(jd)

    if len(resumes) < 2 or not jd.strip():

        st.error(
            "Upload at least 2 resumes and give a job description."
        )

    elif not required:

        st.error(
            "No known skills found in the job description. "
            "Mention skills like Python, SQL, machine learning."
        )

    else:

        try:

            cands = [
                parse_resume(read_file(f), f.name)
                for f in resumes
            ]

            kind = (
                "biased"
                if mode.startswith("Simulated")
                else "llm"
                if mode.startswith("LLM")
                else "skills"
            )

            scorer = make_scorer(
                kind,
                jd,
                required,
                strength,
                provider,
                key,
                model
            )

            st.session_state["res"] = analyze(
                cands,
                scorer,
                required,
                int(top_n),
                threshold
            )

            st.session_state["cands"] = cands
            st.session_state["req"] = required

        except Exception as e:

            st.error(f"Could not run: {e}")


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

res = st.session_state.get("res")

if res:

    # SECTION 1: RESUME ANALYSIS

    st.subheader("1. What the system read")

    st.write(
        "Required skills from the job: "
        + ", ".join(st.session_state["req"])
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state["cands"]
        ).drop(columns="file").rename(
            columns={
                "name": "Name",
                "institution": "College",
                "age": "Age",
                "gap": "Career gap (yrs)",
                "exp": "Experience (yrs)",
                "skills": "Skills found"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


    # SECTION 2: BIAS TEST

    st.subheader(
        "2. Bias test: one factor changed at a time"
    )

    cols = st.columns(len(res["factors"]))

    for col, (f, r) in zip(
        cols,
        res["factors"].items()
    ):

        col.metric(
            f,
            "BIAS FOUND" if r["biased"] else "No effect",
            f"avg change {r['mean_abs_delta']:.1f} pts",
            delta_color="inverse" if r["biased"] else "off"
        )

        col.caption(
            f"Rank changed for {r['flip_rate']:.0%} of candidates"
        )

    if res["skipped"]:

        st.info(
            "Not tested (not found in resumes): "
            + ", ".join(res["skipped"])
        )


    # SECTION 3: FINAL DECISION

    st.subheader("3. Final decision")

    out = pd.DataFrame(
        res["rows"]
    ).sort_values("Fair_rank")

    if res["flagged"]:

        st.warning(
            f"Bias found in: {', '.join(res['flagged'])}. "
            f"Ranking corrected; {res['changed']} decision(s) changed."
        )

    else:

        st.success(
            "No factor affected the ranking. "
            "The original ranking is kept."
        )

    st.dataframe(
        out.drop(columns="Reason"),
        use_container_width=True,
        hide_index=True
    )


    # SECTION 4: EXPLANATIONS

    st.subheader(
        "4. Why each candidate was selected or rejected"
    )

    for _, r in out.iterrows():

        icon = (
            "✅"
            if r.Decision == "Selected"
            else "❌"
        )

        with st.expander(
            f"{icon} #{r.Fair_rank}  {r.Candidate}",
            expanded=True
        ):

            st.write(r.Reason)


    # SECTION 5: DOWNLOAD

    st.download_button(
        "📥 Download decisions (CSV)",
        out.to_csv(index=False),
        "fair_decisions.csv"
    )
