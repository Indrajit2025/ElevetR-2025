# 🚀 ElevatR: The Future of Campus Recruitment
### *State-Level Award Winning AI Placement Ecosystem for Biju Patnaik University of Technology (BPUT)*

<div align="center">

  <img src="static/favicon.svg" alt="ElevatR Logo" width="120" height="120" />
  
  <br />
  
  <a href="#">
    <img src="https://img.shields.io/badge/Award-BPUT_Excellence_in_Innovation-FFD700?style=for-the-badge&logo=trophy&logoColor=black" alt="Award Winning" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge" alt="Status" />
  </a>
  <br />
  <img src="https://img.shields.io/badge/AI_Core-Google_Gemini-blue?style=for-the-badge&logo=google-gemini" />
  <img src="https://img.shields.io/badge/Backend-Flask_Enterprise-black?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/ML_Engine-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn" />
  <img src="https://img.shields.io/badge/Database-MySQL_8.0-4479A1?style=for-the-badge&logo=mysql" />

</div>

---

## 🏆 Hall of Fame: Innovation Excellence
**ElevatR** stands as a testament to engineering ingenuity, recognized with the **BPUT Excellence in Innovation Award**. 

Designed to serve the entire **State University Ecosystem**, this platform was engineered to solve the "Skills Gap" crisis. It is not just a job portal; it is an intelligent bridge that uses **Generative AI** to translate student potential into industry success, securing its place as a top-tier project at the university state level.

---

## 📖 Executive Summary
**ElevatR** is an enterprise-grade, AI-driven placement management system engineered to modernize the recruitment lifecycle. By integrating **Generative AI (Gemini)** and **Machine Learning**, the platform automates the bridge between student potential and industry requirements, replacing fragmented legacy processes with a high-performance, unified portal.

### ⚡ Key Differentiators
* **Zero-Manual Verification:** AI verifies certificates instantly.
* **Mathematical Precision:** Job matching based on Cosine Similarity, not keywords.
* **Seamless Interviews:** One-click video interviews via Whereby API integration.

---

## 🏗️ Intelligent Workflow Architecture

The system operates on a **Closed-Loop Intelligence Model**. Data flows from students to the AI Engine, gets processed for vector similarity, and results in hyper-personalized career opportunities.

```mermaid
graph TD
    subgraph "Phase 1: Intelligent Ingestion"
    User[Student] -->|Uploads Certificate| Vision[Gemini AI Vision 2.0]
    Vision -->|Extracts Technical Skills| DB[(MySQL Database)]
    end

    subgraph "Phase 2: The Matching Engine"
    DB -->|Raw Profile Data| ML[Scikit-Learn Vectorizer]
    Company[Recruiter] -->|Posts Job Req| ML
    ML -->|TF-IDF + Cosine Logic| Match{Fit Score %}
    end

    subgraph "Phase 3: Execution & Delivery"
    Match -->|Top 5 Recommendations| User
    Company -->|Accepts Profile| Video[Whereby Video API]
    Video -->|Generates Secure Room| Interview[Live Interview]
    end
