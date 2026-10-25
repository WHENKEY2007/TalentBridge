"""
Training and artifact serialization script for Resume–Job Matching.
Fits an enterprise TF-IDF vectorizer across a diverse multi-domain software engineering corpus.
"""

import sys
from pathlib import Path

# Add project root to path if executed standalone
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.resume_job_matching.config import (
    ARTIFACTS_DIR,
    JOB_PRESETS,
    MODEL_PATH,
    SAMPLE_RESUME,
)
from modules.resume_job_matching.model import ResumeJobMatcher

# Multi-domain seed corpus for IDF weight calibration
EXPANDED_SEED_CORPUS = [
    # 1. Base samples and presets
    SAMPLE_RESUME,
    JOB_PRESETS["Senior Python Backend Engineer"],
    JOB_PRESETS["Machine Learning & AI Engineer"],
    JOB_PRESETS["Full-Stack React & Node Engineer"],
    JOB_PRESETS["Cloud DevOps & Platform Engineer"],
    JOB_PRESETS["Data Platform & ETL Engineer"],
    JOB_PRESETS["Mobile Software Engineer (iOS / Android)"],

    # 2. Python Backend & Distributed Systems
    """Senior Python Developer: Extensive background in Python 3, FastAPI, Django, Flask,
    asynchronous programming with asyncio, Celery task queues, Redis caching, PostgreSQL database
    design, SQLAlchemy ORM, microservices architecture, RabbitMQ message brokers, gRPC protocols,
    pytest test coverage, Docker containerization, AWS ECS deployments, and RESTful API development.""",

    """Backend Software Engineer: Built high-concurrency web services handling 10k RPS in Python
    and Go. Experience with MySQL sharding, Redis cluster, Apache Kafka event streams, Elasticsearch
    for distributed logging, Docker containers, Kubernetes orchestration, and GitLab CI/CD pipelines.""",

    # 3. Modern Frontend & Web
    """Senior Frontend Engineer: Expert in TypeScript, JavaScript (ES6+), React 18, Next.js,
    state management with Redux Toolkit and Zustand, styling with Tailwind CSS, HTML5, CSS3,
    component libraries, Webpack and Vite bundling, unit testing with Jest and React Testing Library,
    end-to-end testing with Cypress, responsive mobile-first UI development, and Web Vitals optimization.""",

    """UI/UX Full-Stack Developer: Experience building dynamic web apps using Vue.js, Nuxt.js,
    Node.js, Express, Tailwind CSS, GraphQL Apollo client, REST APIs, MongoDB, PostgreSQL,
    Webpack, Figma to code conversion, accessibility (a11y) standards, and Vercel cloud deployments.""",

    # 4. Cloud, DevOps, and Site Reliability
    """Staff DevOps & Platform Engineer: Infrastructure as Code with Terraform and Ansible.
    Cloud automation on AWS (EKS, VPC, IAM, RDS, S3, CloudFront) and GCP (GKE, Cloud Run).
    Container orchestration with Kubernetes, Helm charts, service mesh with Istio, CI/CD with
    GitHub Actions and ArgoCD, observability with Prometheus, Grafana, Datadog, and Linux kernel tuning.""",

    """Site Reliability Engineer (SRE): Ensuring 99.99% service availability, SLO/SLI tracking,
    incident management, automated alerting with PagerDuty and Opsgenie, Docker container runtime,
    Kubernetes pod lifecycle, Linux system administration, Bash and Python scripting, chaos engineering,
    and cloud networking security.""",

    # 5. Data Engineering & Big Data
    """Lead Data Engineer: Architected distributed ETL and ELT data pipelines using Apache Spark,
    Databricks, Apache Airflow, dbt (data build tool), Kafka real-time streaming, and Delta Lake.
    Designed columnar data warehouses in Snowflake, Google BigQuery, and Amazon Redshift.
    Proficient in advanced SQL, Python, PySpark, data governance, and schema modeling.""",

    """Data Infrastructure Specialist: Built batch and streaming pipelines processing 500GB daily
    using Python, Scala, Spark, Kafka, AWS Kinesis, Athena, S3 data lakes, PostgreSQL, and Cassandra.
    Managed Airflow DAG workflows and implemented automated data quality checks with Great Expectations.""",

    # 6. Machine Learning, NLP, and AI Engineering
    """Senior Machine Learning Engineer: Designed, fine-tuned, and deployed LLMs and transformer models
    using PyTorch, Hugging Face transformers, LangChain, LlamaIndex, vLLM, and ONNX Runtime.
    Experience with vector databases (Pinecone, Weaviate, Milvus, Qdrant), retrieval-augmented generation (RAG),
    Dockerized FastAPI inference microservices on AWS SageMaker, Scikit-learn, Pandas, and MLflow tracking.""",

    """Data Scientist / AI Specialist: Statistical modeling, hypothesis testing, predictive analytics,
    feature engineering with Scikit-learn, XGBoost, LightGBM, TensorFlow, PyTorch, natural language processing (NLP),
    computer vision with OpenCV, convolutional neural networks, data visualization with Matplotlib, Seaborn, Tableau,
    and business stakeholder reporting.""",

    # 7. Mobile Development
    """Lead Mobile Developer: iOS and Android native and cross-platform development with React Native,
    TypeScript, Swift, SwiftUI, Kotlin, and Jetpack Compose. Integrated RESTful and GraphQL APIs,
    offline-first SQLite caching, push notifications with Firebase FCM, App Store deployment, and CI/CD with Fastlane.""",

    # 8. Cybersecurity & Cloud Sec
    """DevSecOps & Cloud Security Engineer: Implemented vulnerability scanning with Snyk, Trivy, and SonarQube.
    Hardened Kubernetes clusters, managed IAM roles and policies on AWS, secret management with HashiCorp Vault,
    OWASP Top 10 mitigation, pen testing, TLS/SSL certificate lifecycle, and SOC2 compliance automation.""",

    # 9. Systems, Embedded & High Performance
    """Systems Software Engineer: Low-level systems programming in Rust, C++, and C.
    High-throughput network programming, memory management, multi-threading, concurrency, POSIX sockets,
    Linux eBPF kernel tracing, performance profiling with perf and valgrind, and WebAssembly (Wasm).""",

    # 10. Engineering Leadership & Agile Methodologies
    """Technical Lead & Engineering Manager: Spearheaded cross-functional squads of 12 software engineers.
    Facilitated Agile, Scrum, Kanban sprints, JIRA roadmapping, PR reviews, architectural design records (ADRs),
    mentorship, stakeholder communication, hiring technical talent, and aligning delivery with product KPIs.""",
]


def train_and_save_vectorizer(output_path: Path = MODEL_PATH) -> Path:
    """
    Fits the ResumeJobMatcher vectorizer on the expanded corpus and saves the artifact.
    """
    print(f"[Training] Initializing TF-IDF Vectorizer with {len(EXPANDED_SEED_CORPUS)} domain documents...")
    matcher = ResumeJobMatcher()
    matcher.fit(EXPANDED_SEED_CORPUS)

    saved_path = matcher.save(output_path)
    print(f"[Artifact Saved] Model successfully serialized to: {saved_path}")
    return saved_path


if __name__ == "__main__":
    train_and_save_vectorizer()
