# 🚀 ElevatR: Intelligent Campus Placement Ecosystem
### Biju Patnaik University of Technology (BPUT) Specialized Recruitment Portal

<p align="center">
  <img src="static/favicon.svg" width="120" alt="ElevatR Logo" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Backend-Flask-black?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Database-MySQL-4479A1?style=for-the-badge&logo=mysql" />
  <img src="https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn" />
  <img src="https://img.shields.io/badge/AI-Google_Gemini-blue?style=for-the-badge&logo=google-gemini" />
  <img src="https://img.shields.io/badge/Frontend-Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css" />
</p>

---

## 📖 Executive Overview
**ElevatR** is an enterprise-grade, AI-driven placement management system engineered to modernize the recruitment lifecycle for the **BPUT** ecosystem. By integrating **Generative AI** and **Machine Learning**, the platform automates the bridge between student potential and industry requirements, replacing fragmented legacy processes with a high-performance, unified portal.

---

## 🏗️ System Architecture & Workflow

```mermaid
graph TD
    subgraph "Data Ingestion"
    A[Student] -->|Uploads Certificate| B(Gemini AI Vision)
    B -->|Skills Extraction| C[(MySQL Database)]
    end

    subgraph "Intelligence Layer"
    C -->|Profile Data| D(Scikit-Learn Engine)
    E[Company] -->|Job Requirements| D
    D -->|TF-IDF + Cosine Similarity| F{Fit Score}
    end

    subgraph "Execution"
    F -->|Personalized Recommendations| A
    E -->|Acceptance| G[Whereby Video API]
    H[BPUT University] -->|Compliance Check| E
    end
🧠 Advanced Technical Features
1. Generative AI & Natural Language Processing
Skill Extraction Engine: Utilizes Google Gemini (2.0 Flash/1.5 Flash) to analyze uploaded certificates (JPG/PNG) and autonomously update student profiles with verified technical skills.

Conversational Assistant: An integrated AI Chatbot provides 24/7 career guidance and platform navigation support for students.

Automated Resume Generation: Leverages xhtml2pdf to transform complex database profiles into professional, recruiter-ready PDF documents.

2. Machine Learning Recommendation Logic
Vectorization: Job descriptions and student project summaries are processed using TF-IDF (Term Frequency-Inverse Document Frequency).

Similarity Scoring: Matches are calculated via Cosine Similarity, ensuring students see opportunities that mathematically align with their demonstrated expertise.

3. Integrated Video Communication
Whereby Embedded: Upon applicant acceptance, the system automatically triggers the Whereby API to generate unique, secure video conference rooms for interviews, eliminating the need for external meeting links.

🛠️ Tech Stack Deep Dive
Component	Technology	Role
Backend Core	Python / Flask	Manages routing, session handling, and server-side logic.
ORM	Flask-SQLAlchemy	Facilitates secure database transactions and relational mapping.
Database	MySQL (bput15)	High-concurrency relational storage for profiles, jobs, and apps.
AI Vision	Google Gemini API	Real-time OCR and semantic analysis of certificates.
ML Libraries	Scikit-learn / Pandas	Power the recommendation engine and data manipulation.
NLP	spaCy	Advanced language processing for text-based analysis.
Frontend	Tailwind CSS / JS	Responsive, utility-first design with AOS and Lottie animations.

Export to Sheets

🔒 Security & Compliance
ElevatR is built with a "Security First" philosophy to protect sensitive student and corporate data:

Cryptographic Hashing: All passwords undergo PBKDF2 hashing via Werkzeug before storage.

Verification Protocol: Companies must undergo MCA, CIN, and GSTIN validation by University admins before gaining posting privileges.

Environment Isolation: Sensitive API keys and database credentials are managed exclusively through encrypted .env variables.

Session Security: Implements secure, server-side session management to prevent unauthorized profile access.

🚀 Installation & Deployment
Prerequisites
Python 3.8+

MySQL Server 5.7+

Active Google Gemini API Key

Deployment Steps
Clone the Environment:

Bash

git clone [https://github.com/Indrajit2025/ElevetR-2025.git](https://github.com/Indrajit2025/ElevetR-2025.git)
cd ElevetR-2025
Dependency Management:

Bash

pip install -r requirements.txt
python -m spacy download en_core_web_sm
Database Initialization:

Bash

# Create 'bput15' database in MySQL
python populate_db.py 
Execution:

Bash

python app.py
<div align="center"> <p><b>Designed & Developed with ❤️ by Indrajit Mondal</b></p> <p><i>Technical Head @ REC Hackathon Club | BPUT Excellence in Innovation</i></p> <a href="https://www.google.com/search?q=https://portfolio.indrajit.in.net">Personal Portfolio</a> • <a href="https://www.google.com/search?q=https://www.linkedin.com/in/indrajit-mondal-32613a35b/">LinkedIn</a> </div>
