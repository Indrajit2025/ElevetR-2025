# ElevatR - BPUT Campus Placement Portal

<div align="center">

![ElevatR](static/favicon.svg)

**A comprehensive campus placement management system for BPUT (Biju Patnaik University of Technology) colleges**

[Features](#features) • [Tech Stack](#tech-stack) • [Installation](#installation) • [Usage](#usage) • [Contributing](#contributing)

</div>

---

## 📋 Overview

ElevatR is an intelligent placement portal designed specifically for BPUT colleges to streamline the campus recruitment process. It connects students, companies, colleges, and university administration on a unified platform with AI-powered features for job recommendations, resume generation, and career guidance.

## ✨ Features

### For Students
- **Smart Profile Management**: Create comprehensive profiles with skills, projects, certificates, and academic records
- **AI-Powered Job Recommendations**: Get personalized internship and job suggestions based on your profile using ML algorithms
- **Resume Generator**: Automatically generate professional resumes from your profile data (PDF download)
- **Job Applications**: Apply for internships and full-time positions with one click
- **Application Tracking**: Monitor the status of all your applications in real-time
- **AI Chatbot Assistant**: Get instant help and career guidance powered by Google Gemini AI
- **Progress Analytics**: Track your placement journey with visual dashboards
- **Resource Hub**: Access curated learning resources for skill development
- **Tech News Feed**: Stay updated with the latest technology news
- **Messaging System**: Direct communication with recruiters

### For Companies
- **Company Registration & Verification**: Secure registration with MCA, CIN, and GSTIN validation
- **Job Posting**: Post internship and full-time job opportunities
- **Candidate Search**: Browse and filter student profiles by skills, CGPA, and location
- **Applicant Management**: Review applications, shortlist candidates, and update statuses
- **Video Interview Integration**: Schedule and conduct interviews via integrated Whereby video conferencing
- **Real-time Notifications**: Get notified about new applications and candidate activities
- **Messaging**: Communicate directly with applicants

### For College Administration
- **College Dashboard**: Monitor placement statistics and student progress
- **Student Analytics**: View detailed reports on student performance and placements
- **Placement Reports**: Generate comprehensive placement statistics
- **Profile Completion Tracking**: Encourage students to complete their profiles

### For University (BPUT)
- **Multi-College Management**: Oversee placement activities across all affiliated colleges
- **Company Verification**: Review and approve/deny company registrations
- **University-wide Analytics**: Get insights into placement trends across colleges
- **Compliance Monitoring**: Ensure all companies meet verification requirements

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **MySQL** - Relational database (via PyMySQL)
- **Python 3.x** - Core programming language

### AI & Machine Learning
- **Google Gemini AI** - Conversational AI chatbot
- **Scikit-learn** - Job recommendation engine (TF-IDF, Cosine Similarity)
- **spaCy** - Natural language processing
- **Pandas** - Data analysis and manipulation

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript** - Interactive functionality
- **Particles.js** - Animated backgrounds
- **Lottie** - Animated illustrations
- **AOS (Animate On Scroll)** - Scroll animations

### Additional Technologies
- **xhtml2pdf** - PDF resume generation
- **Pillow (PIL)** - Image processing
- **Werkzeug** - Security utilities (password hashing, file uploads)
- **Whereby API** - Video conferencing integration
- **python-dotenv** - Environment variable management

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Eusa190/ElevetR.git
cd ElevetR
```

### 2. Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install flask flask-sqlalchemy pymysql werkzeug python-dotenv
pip install scikit-learn pandas spacy google-generativeai
pip install xhtml2pdf pillow requests beautifulsoup4
```

### 4. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Set Up MySQL Database

```sql
-- Login to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE bput15;

-- Exit MySQL
exit;
```

### 6. Configure Environment Variables

Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Google AI API Key (Get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_google_api_key_here

# Whereby Video API Key (Get from https://whereby.com/information/embedded/)
WHEREBY_API_KEY=your_whereby_api_key_here

# Flask Secret Key (Generate a random string)
SECRET_KEY=your_flask_secret_key_here

# Database Configuration
DB_USERNAME=root
DB_PASSWORD=your_database_password_here
DB_HOST=localhost
DB_NAME=bput15
```

### 7. Initialize the Database

```bash
python populate_db.py
```

This script will:
- Drop existing tables (if any)
- Create all required tables
- Optionally populate with sample data (if configured)

### 8. Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`

## 📖 Usage

### First-Time Setup

1. **Access the Application**: Open your browser and navigate to `http://localhost:5000`

2. **Register Users**:
   - **Students**: Go to `/student_register` and complete the registration form
   - **Companies**: Go to `/company_register` and provide company details
   - **Colleges**: Go to `/college_register` with college credentials
   - **University**: Go to `/university_register` for BPUT administration

3. **Company Verification**: University admins must approve companies before they can post jobs

4. **Complete Profiles**: Students should complete their profiles with skills, projects, and certificates

### Key Workflows

#### Student Job Application Flow
1. Login → Browse Jobs → View Recommendations → Apply → Track Status → Communicate with Recruiter

#### Company Recruitment Flow
1. Login → Verify Profile → Post Job → Review Applicants → Shortlist → Schedule Interview → Update Status

#### College Administration Flow
1. Login → View Dashboard → Monitor Student Progress → Generate Reports → Track Placements

## 🗂️ Project Structure

```
ElevetR/
├── app.py                      # Main Flask application
├── populate_db.py              # Database initialization script
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   │   ├── script.js
│   │   ├── chatbot.js
│   │   ├── notification.js
│   │   ├── login_register_script.js
│   │   ├── company_login_script.js
│   │   ├── particles-config.js
│   │   └── main.js
│   ├── IMAGES/                 # Image assets
│   ├── uploads/                # User-uploaded files
│   └── favicon.svg             # Site favicon
├── templates/
│   ├── base.html               # Base template
│   ├── landing.html            # Homepage
│   ├── student_*.html          # Student-related pages
│   ├── company_*.html          # Company-related pages
│   ├── college_*.html          # College-related pages
│   ├── university_*.html       # University-related pages
│   ├── chatbot.html            # AI chatbot interface
│   ├── resources.html          # Learning resources
│   ├── tech_feed.html          # Tech news feed
│   └── ...                     # Other templates
└── README.md                   # This file
```

## 🔑 Key Features Explained

### AI Job Recommendation Engine
The system uses TF-IDF vectorization and cosine similarity to match student skills with job requirements, providing personalized job recommendations with fit scores.

### AI Chatbot Assistant
Powered by Google Gemini, the chatbot provides career guidance, answers placement-related questions, and helps students navigate the platform.

### Resume Generator
Automatically converts student profile data into a professionally formatted PDF resume using xhtml2pdf.

### Progress Analytics
Tracks student journey including CGPA, skills acquired, projects completed, certificates earned, and application counts over time.

### Video Interview Integration
Seamlessly integrates with Whereby API to create and manage video interview rooms directly from the application.

## 🔒 Security Features

- Password hashing using Werkzeug security utilities
- Secure file upload with allowed extensions validation
- Session-based authentication
- Environment variable protection for sensitive data
- SQL injection prevention via SQLAlchemy ORM
- Company verification system with MCA, CIN, and GSTIN validation
- Server-side API key management (no keys exposed to client)

### ⚠️ Important Security Notes

**Before deploying to production, you MUST:**

1. **Set a strong SECRET_KEY**: Generate a secure secret key and add it to your `.env` file:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Never use the default value in production.

2. **Secure your API keys**: Ensure all API keys in `.env` are kept secret and never committed to version control.

3. **Review SECURITY.md**: Read the [SECURITY.md](SECURITY.md) file for a complete security audit and recommendations.

4. **Database security**: Use a strong database password and restrict database access.

5. **Enable HTTPS**: Always use HTTPS in production to protect data in transit.

For detailed security information, vulnerability reports, and best practices, see [SECURITY.md](SECURITY.md).

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Write meaningful commit messages
- Test your changes thoroughly before submitting
- Update documentation as needed

## 🐛 Known Issues

- Web scraping feature in `populate_db.py` requires an external data source
- Some AI features require valid Google API key
- Video conferencing requires Whereby API key

## 📝 License

This project is open source and available for educational purposes. Please check with the repository owner for commercial usage rights.

## 👥 Target Users

- **BPUT Students**: From all affiliated engineering colleges
- **Companies**: Looking to recruit from BPUT colleges
- **College TPOs**: Training and Placement Officers
- **University Administration**: BPUT placement coordinators

## 📧 Support

For support, issues, or feature requests, please open an issue on the GitHub repository.

## 🙏 Acknowledgments

- BPUT (Biju Patnaik University of Technology)
- All affiliated colleges in the BPUT network
- Google Gemini AI for conversational AI capabilities
- Whereby for video conferencing integration
- Open source community for various libraries and frameworks

---

<div align="center">

**Made with ❤️ for BPUT Students and Colleges**

⭐ Star this repository if you find it helpful!

</div>
