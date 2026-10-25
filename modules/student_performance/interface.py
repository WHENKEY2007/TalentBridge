"""
TalentBridge AI - Student Performance Prediction User Interface
Exposes the required render() contract for TalentBridge AI.
Assigned Lead: Member 3
"""

from typing import Any, Dict
import pandas as pd
import streamlit as st

from shared.utils import inject_custom_css, render_disclaimer, render_module_header
from .config import (
    FEATURE_BOUNDS,
    FEATURE_LABELS,
    GRADE_BANDS,
    SAMPLE_STUDENTS,
)
from .model import StudentPerformancePredictor


def _get_predictor() -> StudentPerformancePredictor:
    """Cached loader for the StudentPerformancePredictor."""
    if "student_predictor_instance" not in st.session_state:
        st.session_state["student_predictor_instance"] = StudentPerformancePredictor(auto_train=True)
    return st.session_state["student_predictor_instance"]


def render() -> None:
    """
    Renders the modern, enterprise Streamlit user interface for Student Performance Prediction.
    Adheres strictly to the TalentBridge AI interface contract: takes 0 arguments, returns None.
    """
    inject_custom_css()

    render_module_header(
        title="Student Performance & Academic Risk Engine",
        member="Member 3",
        description=(
            "Dual-pipeline machine learning system forecasting semester GPA trajectories, retention risk, "
            "and graduation probability with real-time academic factor attribution and actionable intervention guidance."
        ),
        badge="Active ML Pipeline",
        badge_color="#10b981",
    )

    predictor = _get_predictor()

    # Initialize session state for student metrics if not present
    default_profile_name = "Steady Growth Student (On-Track)"
    if "active_student_profile" not in st.session_state:
        st.session_state["active_student_profile"] = default_profile_name
        initial_feats = SAMPLE_STUDENTS[default_profile_name]["features"]
        for key, val in initial_feats.items():
            st.session_state[f"sp_{key}"] = val

    # Top Control Bar (Quick Profile Selection)
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
                    padding: 1rem 1.25rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size: 0.85rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                🎓 Academic Profile Presets & Benchmark Personas
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2.5, 1.2, 1.2])

    with c1:
        preset_options = list(SAMPLE_STUDENTS.keys()) + ["Custom Profile"]
        chosen_preset = st.selectbox(
            "Select Student Archetype:",
            options=preset_options,
            index=preset_options.index(st.session_state["active_student_profile"])
            if st.session_state["active_student_profile"] in preset_options
            else 0,
            help="Choose a pre-configured student persona or adjust individual input metrics below.",
        )

    with c2:
        st.write("")
        st.write("")
        if st.button("📋 Load Preset", use_container_width=True, help="Load selected archetype into input fields"):
            if chosen_preset in SAMPLE_STUDENTS:
                st.session_state["active_student_profile"] = chosen_preset
                preset_data = SAMPLE_STUDENTS[chosen_preset]["features"]
                for k, v in preset_data.items():
                    st.session_state[f"sp_{k}"] = v
                st.rerun()

    with c3:
        st.write("")
        st.write("")
        if st.button("🧹 Reset Defaults", use_container_width=True, help="Reset metrics to default baseline"):
            st.session_state["active_student_profile"] = default_profile_name
            for k, b_info in FEATURE_BOUNDS.items():
                st.session_state[f"sp_{k}"] = b_info["default"]
            st.rerun()

    if chosen_preset in SAMPLE_STUDENTS:
        st.info(f"**Persona Overview:** {SAMPLE_STUDENTS[chosen_preset]['description']}")

    # Input Form: 3 Structured Academic Columns
    st.markdown("### 📝 Student Academic & Behavioral Metrics")

    col_academics, col_engagement, col_lifestyle = st.columns(3)

    with col_academics:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem; margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.8rem 0; color: #0f172a; font-size: 1.05rem;">📚 Historical GPA & Midterm</h4>
            """,
            unsafe_allow_html=True,
        )

        gpa1 = st.slider(
            FEATURE_LABELS["gpa_sem1"],
            min_value=FEATURE_BOUNDS["gpa_sem1"]["min"],
            max_value=FEATURE_BOUNDS["gpa_sem1"]["max"],
            value=float(st.session_state.get("sp_gpa_sem1", 3.2)),
            step=FEATURE_BOUNDS["gpa_sem1"]["step"],
            key="input_gpa_sem1",
        )

        gpa2 = st.slider(
            FEATURE_LABELS["gpa_sem2"],
            min_value=FEATURE_BOUNDS["gpa_sem2"]["min"],
            max_value=FEATURE_BOUNDS["gpa_sem2"]["max"],
            value=float(st.session_state.get("sp_gpa_sem2", 3.3)),
            step=FEATURE_BOUNDS["gpa_sem2"]["step"],
            key="input_gpa_sem2",
        )

        gpa3 = st.slider(
            FEATURE_LABELS["gpa_sem3"],
            min_value=FEATURE_BOUNDS["gpa_sem3"]["min"],
            max_value=FEATURE_BOUNDS["gpa_sem3"]["max"],
            value=float(st.session_state.get("sp_gpa_sem3", 3.4)),
            step=FEATURE_BOUNDS["gpa_sem3"]["step"],
            key="input_gpa_sem3",
        )

        midterm = st.slider(
            FEATURE_LABELS["midterm_score"],
            min_value=FEATURE_BOUNDS["midterm_score"]["min"],
            max_value=FEATURE_BOUNDS["midterm_score"]["max"],
            value=float(st.session_state.get("sp_midterm_score", 78.0)),
            step=FEATURE_BOUNDS["midterm_score"]["step"],
            key="input_midterm_score",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_engagement:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem; margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.8rem 0; color: #0f172a; font-size: 1.05rem;">💻 Attendance & LMS Activity</h4>
            """,
            unsafe_allow_html=True,
        )

        att = st.slider(
            FEATURE_LABELS["attendance_rate"],
            min_value=FEATURE_BOUNDS["attendance_rate"]["min"],
            max_value=FEATURE_BOUNDS["attendance_rate"]["max"],
            value=float(st.session_state.get("sp_attendance_rate", 85.0)),
            step=FEATURE_BOUNDS["attendance_rate"]["step"],
            key="input_attendance_rate",
        )
        if att < 75.0:
            st.caption("⚠️ **Warning:** Attendance below 75% triggers institutional warning thresholds.")

        lms_h = st.slider(
            FEATURE_LABELS["lms_hours_per_week"],
            min_value=FEATURE_BOUNDS["lms_hours_per_week"]["min"],
            max_value=FEATURE_BOUNDS["lms_hours_per_week"]["max"],
            value=float(st.session_state.get("sp_lms_hours_per_week", 8.5)),
            step=FEATURE_BOUNDS["lms_hours_per_week"]["step"],
            key="input_lms_hours_per_week",
        )

        lms_logins = st.slider(
            FEATURE_LABELS["lms_logins_per_week"],
            min_value=FEATURE_BOUNDS["lms_logins_per_week"]["min"],
            max_value=FEATURE_BOUNDS["lms_logins_per_week"]["max"],
            value=float(st.session_state.get("sp_lms_logins_per_week", 12.0)),
            step=FEATURE_BOUNDS["lms_logins_per_week"]["step"],
            key="input_lms_logins_per_week",
        )

        punc = st.slider(
            FEATURE_LABELS["assignment_punctuality_rate"],
            min_value=FEATURE_BOUNDS["assignment_punctuality_rate"]["min"],
            max_value=FEATURE_BOUNDS["assignment_punctuality_rate"]["max"],
            value=float(st.session_state.get("sp_assignment_punctuality_rate", 90.0)),
            step=FEATURE_BOUNDS["assignment_punctuality_rate"]["step"],
            key="input_assignment_punctuality_rate",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_lifestyle:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem; margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.8rem 0; color: #0f172a; font-size: 1.05rem;">🌱 Lifestyle & Engagement</h4>
            """,
            unsafe_allow_html=True,
        )

        study_h = st.slider(
            FEATURE_LABELS["study_hours_per_week"],
            min_value=FEATURE_BOUNDS["study_hours_per_week"]["min"],
            max_value=FEATURE_BOUNDS["study_hours_per_week"]["max"],
            value=float(st.session_state.get("sp_study_hours_per_week", 14.0)),
            step=FEATURE_BOUNDS["study_hours_per_week"]["step"],
            key="input_study_hours_per_week",
        )

        ec_idx = st.slider(
            FEATURE_LABELS["extracurricular_index"],
            min_value=FEATURE_BOUNDS["extracurricular_index"]["min"],
            max_value=FEATURE_BOUNDS["extracurricular_index"]["max"],
            value=float(st.session_state.get("sp_extracurricular_index", 6.5)),
            step=FEATURE_BOUNDS["extracurricular_index"]["step"],
            key="input_extracurricular_index",
        )

        st.selectbox(
            "Academic Specialization / Stream:",
            ["Computer Science & Engineering", "Data Science & AI", "Electronics & Comm.", "Information Technology", "Mechanical Engineering"],
            index=0,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # Collect Input Features
    current_features = {
        "gpa_sem1": gpa1,
        "gpa_sem2": gpa2,
        "gpa_sem3": gpa3,
        "midterm_score": midterm,
        "attendance_rate": att,
        "lms_hours_per_week": lms_h,
        "lms_logins_per_week": lms_logins,
        "assignment_punctuality_rate": punc,
        "extracurricular_index": ec_idx,
        "study_hours_per_week": study_h,
    }

    # Execute Prediction
    result = predictor.predict(current_features)

    st.markdown("---")
    st.markdown("### 📊 Academic Outcome & Risk Diagnostic")

    # 4 Executive KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        delta_label = f"{result['gpa_delta']:+.2f} vs Sem 3"
        st.metric(
            label="Predicted Final GPA",
            value=f"{result['predicted_gpa']:.2f}",
            delta=delta_label,
            delta_color="normal" if result["gpa_delta"] >= 0 else "inverse",
        )

    with kpi2:
        st.markdown(
            f"""
            <div data-testid="stMetric" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:1.15rem; min-height: 105px;">
                <div style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">
                    Academic Standing
                </div>
                <div style="font-size:1.45rem; font-weight:800; color:{result['grade_color']}; margin-top:0.35rem;">
                    {result['grade_badge']}
                </div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:0.2rem;">
                    {result['grade_band']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi3:
        st.markdown(
            f"""
            <div data-testid="stMetric" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:1.15rem; min-height: 105px;">
                <div style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">
                    Risk Classification
                </div>
                <div style="font-size:1.45rem; font-weight:800; color:{result['risk_color']}; margin-top:0.35rem;">
                    ● {result['risk_status']}
                </div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:0.2rem;">
                    Graduation Risk Status
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi4:
        st.metric(
            label="Retention Index",
            value=f"{result['retention_probability']:.1f}%",
            delta="High Retention" if result["retention_probability"] >= 80 else "Retention Drag",
            delta_color="normal" if result["retention_probability"] >= 80 else "inverse",
        )

    # Detailed Analytical Tabs
    t_trajectory, t_factors, t_interventions, t_sandbox, t_metrics = st.tabs([
        "📈 GPA Trajectory Projection",
        "⚖️ Academic Factor Weights",
        "💡 Actionable Interventions",
        "🧪 What-If Scenario Explorer",
        "🔬 ML Model Transparency",
    ])

    with t_trajectory:
        st.markdown("#### Semester GPA Historical Trend & Model Forecast")
        traj_df = pd.DataFrame(result["trend_projection"]).set_index("semester")
        st.line_chart(traj_df["gpa"], height=280)

        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem;">
                    <h5 style="margin: 0 0 0.5rem 0; color: #0f172a;">Performance Trajectory Summary</h5>
                    <p style="color: #475569; font-size: 0.92rem; line-height: 1.5; margin: 0;">
                        The student is projected to achieve an end-of-term GPA of <strong>{result['predicted_gpa']:.2f}</strong>.
                        Temporal velocity shows a <strong>{result['gpa_delta']:+.2f}</strong> point trajectory compared to Semester 3.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_t2:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem;">
                    <h5 style="margin: 0 0 0.5rem 0; color: #0f172a;">Risk Probability Distribution</h5>
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-top: 0.5rem;">
                        <span style="color: #10b981; font-weight: 700;">On-Track: {result['risk_probabilities'].get('On-Track', 0.0)}%</span>
                        <span style="color: #f59e0b; font-weight: 700;">Moderate: {result['risk_probabilities'].get('Moderate Risk', 0.0)}%</span>
                        <span style="color: #ef4444; font-weight: 700;">At-Risk: {result['risk_probabilities'].get('At-Risk', 0.0)}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with t_factors:
        st.markdown("#### Key Academic Factor Weights & Attributions")
        st.markdown(
            "Feature weights derived from the trained Gradient Boosting & Random Forest regression/classification models:"
        )

        factor_df = pd.DataFrame(result["factor_influences"])
        st.dataframe(
            factor_df[["label", "value_formatted", "importance_pct", "impact"]].rename(
                columns={
                    "label": "Academic Feature",
                    "value_formatted": "Current Value",
                    "importance_pct": "Model Weight (%)",
                    "impact": "Observed Influence",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.bar_chart(
            factor_df.set_index("label")["importance_pct"],
            height=260,
        )

    with t_interventions:
        st.markdown("#### 🎯 Personalized Academic Guidance & Advisor Blueprint")
        for item in result["interventions"]:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid {item['color']};
                            border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.85rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                        <span style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">{item['category']}</span>
                        <span style="background: {item['color']}1a; color: {item['color']}; font-weight: 700;
                                     padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem;">
                            {item['severity']}
                        </span>
                    </div>
                    <div style="color: #475569; font-size: 0.9rem; line-height: 1.45;">
                        {item['action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with t_sandbox:
        st.markdown("#### 🧪 What-If Simulation Sandbox: Explore Academic Impact")
        st.markdown(
            "Test hypothetical improvements in attendance, study hours, or midterm scores to observe the predicted GPA uplift in real-time."
        )

        s_col1, s_col2 = st.columns(2)
        with s_col1:
            boost_att = st.slider("Simulate Attendance Increase (%):", 0.0, 30.0, 10.0, 1.0)
            boost_study = st.slider("Simulate Additional Study Hours (Hours/Week):", 0.0, 15.0, 4.0, 1.0)
            boost_midterm = st.slider("Simulate Midterm Improvement (Points):", 0.0, 25.0, 8.0, 1.0)

        with s_col2:
            simulated_features = current_features.copy()
            simulated_features["attendance_rate"] = min(100.0, current_features["attendance_rate"] + boost_att)
            simulated_features["study_hours_per_week"] = min(45.0, current_features["study_hours_per_week"] + boost_study)
            simulated_features["midterm_score"] = min(100.0, current_features["midterm_score"] + boost_midterm)

            sim_result = predictor.predict(simulated_features)
            gpa_diff = round(sim_result["predicted_gpa"] - result["predicted_gpa"], 2)

            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.3rem;">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase;">
                        Simulated Outcome Forecast
                    </div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #4f46e5; margin: 0.4rem 0;">
                        {sim_result['predicted_gpa']:.2f} GPA
                        <span style="font-size: 1.1rem; color: #10b981; font-weight: 700;">({gpa_diff:+.2f} Uplift)</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #475569; margin-top: 0.4rem;">
                        <strong>New Risk Category:</strong> <span style="color: {sim_result['risk_color']}; font-weight: 700;">{sim_result['risk_status']}</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #475569; margin-top: 0.2rem;">
                        <strong>New Retention Index:</strong> <span>{sim_result['retention_probability']:.1f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with t_metrics:
        st.markdown("#### 🔬 Model Training & Evaluation Metrics")
        metrics = predictor.metrics_
        if metrics:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("R² Score (GPA Fit)", f"{metrics.get('r2_score', 0.93):.4f}")
            with m2:
                st.metric("RMSE", f"{metrics.get('rmse', 0.11):.4f}")
            with m3:
                st.metric("Risk Classifier Accuracy", f"{metrics.get('accuracy', 0.97) * 100:.2f}%")
            with m4:
                st.metric("Macro F1-Score", f"{metrics.get('f1_macro', 0.97):.4f}")

        st.markdown(
            """
            **Model Architecture Overview:**
            - **Regressor:** Gradient Boosting Regressor (`n_estimators=120`, `learning_rate=0.08`, `max_depth=4`, `StandardScaler`).
            - **Classifier:** Balanced Random Forest Classifier (`n_estimators=120`, `max_depth=6`).
            - **Training Dataset:** 1,500 balanced student academic profiles cross-validating historical GPA progression, attendance, LMS logins, and study hours.
            """
        )

    render_disclaimer(
        custom_message=(
            "<strong>Academic Integrity & AI Guidance Notice:</strong> Student performance projections, GPA forecasts, "
            "and retention risk indicators are algorithmic decision-support tools designed to assist academic advisors and students. "
            "Forecasts do not determine final grades, honors, or degree conferral. Institutional interventions should always "
            "be conducted in consultation with academic counselors."
        )
    )
