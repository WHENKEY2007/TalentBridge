"""
Configuration, constants, taxonomies, and presets for AI Resume Analysis.
Assigned to Member 10.
"""

from pathlib import Path
from typing import Dict, List, Set

# Base Paths
MODULE_DIR = Path(__file__).resolve().parent
DATA_DIR = MODULE_DIR / "data"
ARTIFACTS_DIR = MODULE_DIR / "artifacts"
TRAINING_DATA_PATH = DATA_DIR / "resume_benchmark_data.csv"
MODEL_PATH = ARTIFACTS_DIR / "resume_analyzer_model.joblib"

# Supported Career Levels
CAREER_LEVELS = ["Entry-Level / Graduate", "Mid-Level Professional", "Senior / Executive Lead"]

# Supported Target Industries
TARGET_INDUSTRIES = [
    "Software & Technology",
    "Data Science & AI",
    "Cloud & DevOps",
    "Finance & Banking",
    "Healthcare & Biotechnology",
    "Product & Marketing",
]

# Section Headers for Structure Audit
SECTION_PATTERNS: Dict[str, List[str]] = {
    "contact": [
        r"(?:contact|personal details|contact information|get in touch)",
    ],
    "summary": [
        r"(?:professional summary|summary|profile|about me|executive summary|career objective|objective)",
    ],
    "experience": [
        r"(?:work experience|professional experience|experience|employment history|work history|career background)",
    ],
    "education": [
        r"(?:education|academic background|academic qualifications|degrees|qualifications)",
    ],
    "skills": [
        r"(?:technical skills|skills & expertise|skills|core competencies|technologies|proficiencies|tools & skills)",
    ],
    "projects": [
        r"(?:projects|key projects|academic projects|personal projects|selected projects)",
    ],
    "certifications": [
        r"(?:certifications|certificates|licenses & certifications|credentials|professional development)",
    ],
    "awards": [
        r"(?:awards|honors|achievements|accolades|recognition)",
    ],
}

# Strong High-Impact Action Verbs (Categorized)
ACTION_VERBS: Dict[str, Set[str]] = {
    "Leadership & Direction": {
        "directed", "spearheaded", "orchestrated", "championed", "mentored", "governed",
        "supervised", "mobilized", "guided", "steered", "empowered", "founded", "pioneered",
        "presided", "facilitated", "orchestrated", "transformed", "unified"
    },
    "Execution & Engineering": {
        "architected", "engineered", "built", "implemented", "developed", "deployed",
        "constructed", "refactored", "integrated", "programmed", "automated", "configured",
        "designed", "devised", "operationalized", "migrated", "synthesized", "formulated"
    },
    "Optimization & Metrics": {
        "maximized", "minimized", "accelerated", "optimized", "amplified", "scaled",
        "boosted", "reduced", "decreased", "expanded", "outperformed", "enhanced",
        "doubled", "tripled", "standardized", "upgraded", "streamlined", "overhauled"
    },
    "Analysis & Research": {
        "analyzed", "evaluated", "diagnosed", "audited", "quantified", "modeled",
        "investigated", "benchmarked", "mapped", "identified", "calculated", "discovered",
        "forecasted", "surveyed", "tested", "validated", "monitored"
    },
    "Collaboration & Stakeholder": {
        "partnered", "negotiated", "liaised", "collaborated", "aligned", "advocated",
        "presented", "influenced", "secured", "delivered", "coordinated", "resolved"
    },
}

# Flat Set of All Strong Verbs
ALL_ACTION_VERBS: Set[str] = {verb for group in ACTION_VERBS.values() for verb in group}

# Weak, Passive, or Cliché Phrases to Avoid in Resumes
WEAK_PATTERNS: List[str] = [
    r"\bresponsible for\b",
    r"\bduties included\b",
    r"\bhelped with\b",
    r"\bworked on\b",
    r"\btasked with\b",
    r"\bassisted in\b",
    r"\bassisted with\b",
    r"\bparticipated in\b",
    r"\bhandled\b",
    r"\bhard-working\b",
    r"\bdetail-oriented\b",
    r"\bteam player\b",
    r"\bgo-getter\b",
    r"\bself-starter\b",
    r"\bthink outside the box\b",
    r"\bgood communication skills\b",
]

# Industry Specific Competency Taxonomies
INDUSTRY_TAXONOMY: Dict[str, Set[str]] = {
    "Software & Technology": {
        "python", "java", "c++", "c#", "javascript", "typescript", "golang", "rust",
        "react", "angular", "vue", "node.js", "django", "fastapi", "spring boot",
        "sql", "postgresql", "mongodb", "docker", "kubernetes", "git", "ci/cd",
        "microservices", "rest api", "graphql", "system design", "data structures",
        "algorithms", "linux", "unit testing", "agile", "tdd"
    },
    "Data Science & AI": {
        "python", "r", "sql", "machine learning", "deep learning", "nlp", "llm",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "data visualization", "tableau", "power bi", "feature engineering", "stats",
        "statistics", "regression", "classification", "clustering", "xgboost",
        "transformers", "hugging face", "opencv", "spark", "hadoop", "eda"
    },
    "Cloud & DevOps": {
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "ci/cd", "helm", "prometheus", "grafana", "linux", "bash",
        "cloudformation", "gitops", "argocd", "networking", "vpc", "iam",
        "site reliability", "sre", "serverless", "lambda", "nginx", "load balancing"
    },
    "Finance & Banking": {
        "financial modeling", "dcf", "valuation", "excel", "bloomberg", "sql",
        "risk management", "portfolio management", "forecasting", "auditing",
        "compliance", "financial analysis", "sec filings", "p&l", "budgeting",
        "derivatives", "equities", "fixed income", "capital markets", "m&a", "python"
    },
    "Healthcare & Biotechnology": {
        "clinical research", "bioinformatics", "fda regulations", "gcp", "glp",
        "molecular biology", "data analysis", "python", "r", "biostatistics",
        "genomics", "pharmaceuticals", "clinical trials", "hipaa", "cell culture",
        "pcr", "spectrometry", "drug discovery", "regulatory compliance"
    },
    "Product & Marketing": {
        "product management", "roadmapping", "agile", "scrum", "user research",
        "wireframing", "figma", "kpis", "a/b testing", "google analytics", "seo",
        "sem", "content marketing", "crm", "salesforce", "hubspot", "customer acquisition",
        "retention", "cac", "ltv", "go-to-market", "competitive analysis"
    },
}

# Career Level Benchmark Expectations
CAREER_LEVEL_BENCHMARKS = {
    "Entry-Level / Graduate": {
        "min_words": 250,
        "max_words": 600,
        "ideal_pages": 1,
        "min_strong_verbs": 5,
        "min_quantified_bullets": 2,
        "required_sections": ["contact", "education", "skills", "projects"],
        "bonus_sections": ["experience", "certifications"],
    },
    "Mid-Level Professional": {
        "min_words": 400,
        "max_words": 850,
        "ideal_pages": 1.5,
        "min_strong_verbs": 10,
        "min_quantified_bullets": 4,
        "required_sections": ["contact", "summary", "experience", "education", "skills"],
        "bonus_sections": ["projects", "certifications", "awards"],
    },
    "Senior / Executive Lead": {
        "min_words": 600,
        "max_words": 1200,
        "ideal_pages": 2,
        "min_strong_verbs": 15,
        "min_quantified_bullets": 7,
        "required_sections": ["contact", "summary", "experience", "skills", "education"],
        "bonus_sections": ["certifications", "awards", "projects"],
    },
}

# Benchmark Sample Resumes for 1-Click UI Testing
SAMPLE_RESUMES: Dict[str, Dict[str, str]] = {
    "Entry-Level CS Graduate (High Quality)": {
        "industry": "Software & Technology",
        "level": "Entry-Level / Graduate",
        "text": """Alex Morgan
San Francisco, CA | (555) 345-6789 | alex.morgan@email.com
linkedin.com/in/alexmorgan | github.com/alexmorgan-dev

PROFESSIONAL SUMMARY
Motivated Computer Science graduate with hands-on experience in full-stack development, Python, and cloud infrastructure. Seeking a Junior Software Engineer position to leverage problem-solving skills in high-scale web applications.

EDUCATION
University of California, Berkeley
Bachelor of Science in Computer Science | GPA: 3.82/4.00
Graduation: May 2024
Relevant Coursework: Data Structures, Algorithms, Distributed Systems, Database Management.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, C++, SQL, HTML/CSS
Frameworks: React, Node.js, FastAPI, Express, Django
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS (S3, EC2)
Tools: Git, GitHub Actions, Linux, Postman, Jest

SELECTED PROJECTS
CloudTask - Distributed Task Scheduler (FastAPI, Redis, Docker)
- Architected a distributed asynchronous task queuing engine supporting 5,000+ jobs/min with 99.9% uptime.
- Engineered Redis pub/sub pipelines reducing job dispatch latency by 35%.
- Implemented unit and integration test suite with 92% code coverage using pytest.

CodeInsight - Code Review Chrome Extension (React, TypeScript, Node.js)
- Developed an open-source browser extension used by 1,200+ active developers to analyze PR diffs.
- Integrated OpenAI API for automated vulnerability detection, reducing manual review time by 40%.

EXPERIENCE
Software Engineering Intern | TechNova Solutions
June 2023 - August 2023
- Built 6 reusable React UI components that decreased frontend bundle load time by 18%.
- Optimized database indexing in PostgreSQL, reducing query execution time across 500k customer records.
- Collaborated in an Agile team of 8 engineers delivering weekly production releases.

CERTIFICATIONS
- AWS Certified Cloud Practitioner (2024)
""",
    },
    "Senior Tech Lead / Architect (Elite Benchmark)": {
        "industry": "Software & Technology",
        "level": "Senior / Executive Lead",
        "text": """Elena Vance
Seattle, WA | (555) 987-6543 | elena.vance@techlead.org
linkedin.com/in/elenavance | github.com/elenavance

EXECUTIVE SUMMARY
Distinguished Software Architect and Engineering Leader with 10+ years of expertise designing distributed cloud-native platforms, scaling engineering organizations, and steering digital transformations. Spearheaded platform migrations supporting $120M annual revenue with 99.99% availability.

CORE COMPETENCIES
- Architecture: Microservices, Distributed Systems, Event-Driven Architecture, High Availability
- Languages: Go, Python, Java, C++, TypeScript
- Cloud & DevOps: AWS, Kubernetes, Docker, Terraform, Kafka, Prometheus
- Leadership: Technical Strategy, Team Mentorship (team of 35+), Budget Oversight ($4.5M)

PROFESSIONAL EXPERIENCE
Principal Systems Architect | CloudScale Global | Seattle, WA
Jan 2020 - Present
- Spearheaded company-wide architectural overhaul migrating monolithic infrastructure to Kubernetes microservices, cutting infrastructure costs by $1.8M annually.
- Directed an engineering division of 45 engineers across 4 cross-functional teams, reducing production defect rate by 42%.
- Engineered high-throughput Kafka streaming pipelines processing over 3.5B events daily with sub-20ms p99 latency.
- Orchestrated automated CI/CD deployment pipelines on AWS, accelerating release cadence from bi-weekly to 15 deployments per day.

Staff Software Engineer | Nexus Data Systems | San Jose, CA
Mar 2016 - Dec 2019
- Architected multi-region PostgreSQL distributed database clusters handling 85,000 queries per second.
- Reduced API p95 response time by 65% through custom caching tiers built on Redis and Envoy proxy.
- Mentored 14 mid-level engineers, resulting in 8 promotions to senior engineering roles over 3 years.
- Standardized unit testing and security scanning protocols across 20+ microservices, achieving 90%+ branch coverage.

Senior Software Developer | Apex Solutions | San Jose, CA
Aug 2013 - Feb 2016
- Built scalable REST and GraphQL APIs utilizing Go and Python, serving 4M monthly active users.
- Automated deployment scripts reducing server provisioning time from 4 hours to 7 minutes.

EDUCATION
Master of Science in Computer Science | Stanford University | 2013
Bachelor of Science in Computer Engineering | University of Washington | 2011

AWARDS & CERTIFICATIONS
- AWS Certified Solutions Architect - Professional (2023)
- Certified Kubernetes Administrator (CKA)
- Patent: Distributed Event Reconciliation Protocol (US Patent #9,824,112)
""",
    },
    "Unoptimized Resume with Passive Language (Needs Work)": {
        "industry": "Software & Technology",
        "level": "Mid-Level Professional",
        "text": """John Smith
Email: john@gmail.com

ABOUT ME
I am a hard-working and detail-oriented software developer. A team player who is a good communicator and thinks outside the box. Looking for a new role.

WORK
Software Dev at ABC Corp
2021 - 2023
- Responsible for maintaining website.
- Helped with database stuff and fixing bugs.
- Worked on new features for users.
- Duties included attending daily standup meetings.
- Assisted in writing code in JavaScript and HTML.

Dev Intern at SmallBiz
2020 - 2021
- Handled customer feedback.
- Tasked with updating documentation.
- Helped team members when needed.

SKILLS
HTML, CSS, JavaScript, computers, Microsoft Office.
""",
    },
}
