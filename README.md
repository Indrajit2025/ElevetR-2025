# 🚀 ElevatR: Intelligent Campus Placement Ecosystem
### Biju Patnaik University of Technology (BPUT) Specialized Recruitment Portal

<p align="center">
  <img src="static/favicon.svg" width="120" alt="ElevatR Logo" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Backend-Flask-black?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Database-MySQL-4479A1?style=for-the-badge&logo=mysql" />
  <img src="https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn" />
  <img src="https://img.shields.io/badge/API-Google_Gemini-blue?style=for-the-badge&logo=google-gemini" />
</p>

---

## 📖 Executive Overview
**ElevatR** is a comprehensive, AI-driven placement management system built to modernize recruitment for **BPUT** colleges. It replaces legacy processes with a unified platform that connects students, recruiters, and university administration through automated workflows and intelligent matching.

## 🏗️ System Architecture
```mermaid
graph TD
    A[Student] -->|Uploads Certificate| B(Gemini AI Skill Extractor)
    B -->|Populates| C[(MySQL DB)]
    D[Company] -->|Posts Job| E(ML Recommendation Engine)
    C --> E
    E -->|Calculates Fit Score| A
    D -->|Accepted Applicant| F[Whereby Video Interview]
    G[University Admin] -->|Verifies| D
