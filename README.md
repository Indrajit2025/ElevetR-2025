# 🚀 ElevatR: BPUT Smart Placement Portal

**ElevatR** is an intelligent, AI-powered placement management system designed specifically for the **BPUT** (Biju Patnaik University of Technology) ecosystem. It bridges the gap between students, recruiters, and academic administrators through automated workflows and career intelligence.

---

## 🗺️ System Architecture

graph TD
    A[Student Profile] -->|ML Processing| B(AI Recommendation Engine)
    B -->|TF-IDF + Cosine Similarity| C{Job Matching}
    C -->|Fits| D[Student Dash: Top Jobs]
    C -->|Gaps| E[AI Roadmap: Learning Links]
    
    F[Company] -->|MCA Verification| G(University Admin)
    G -->|Approved| H[Job Posting Enabled]
    
    I[Gemini AI Chatbot] <-->|Career Help| A
    H -->|Video Interview| J[Whereby Integration]
