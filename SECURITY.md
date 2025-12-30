# Security Policy

## 🔒 Security Overview

This document outlines security considerations, best practices, and known security issues for the ElevatR platform.

## 🚨 Critical Security Issues Identified

### 1. ✅ FIXED: API Key Exposure (CRITICAL)
**Status**: Fixed in this PR  
**Issue**: Google API key was previously exposed in client-side JavaScript in `student_profile.html`  
**Impact**: API key could be extracted from the browser and misused, leading to unauthorized API usage and potential costs  
**Fix**: Moved API calls to server-side endpoint `/api/generate_improvement_plan`

### 2. ⚠️ Default Secret Key (HIGH PRIORITY)
**Status**: Needs immediate attention in production  
**Location**: `app.py` line 67  
**Issue**: 
```python
app.secret_key = os.getenv("SECRET_KEY", "your_super_secret_key_bput")
```
**Impact**: If `SECRET_KEY` environment variable is not set, a default hardcoded key is used, which compromises session security  
**Recommendation**: 
- **ALWAYS** set a strong, random `SECRET_KEY` in your `.env` file before deploying
- Generate a secure key using: `python -c "import secrets; print(secrets.token_hex(32))"`
- Never use the default value in production
- Consider failing to start if `SECRET_KEY` is not set in production environments

### 3. ⚠️ Test Credentials in Database Population Script (MEDIUM)
**Status**: Acceptable for development only  
**Location**: `populate_db.py` line 90  
**Issue**: Hardcoded password `'pass1234'` used for dummy company accounts  
**Impact**: Development/test databases may have predictable passwords  
**Recommendation**: 
- Only use `populate_db.py` for development/testing
- Never run this script in production
- If you need test data in production-like environments, use environment variables for credentials

## 🛡️ Security Best Practices

### Environment Variables
All sensitive configuration should be stored in environment variables, never hardcoded:

✅ **Required Environment Variables** (must be set):
- `SECRET_KEY` - Flask session secret (generate with `secrets.token_hex(32)`)
- `DB_PASSWORD` - Database password
- `GOOGLE_API_KEY` - Google Gemini API key
- `WHEREBY_API_KEY` - Whereby video conferencing API key

✅ **Optional Environment Variables** (with safe defaults):
- `DB_USERNAME` (default: "root")
- `DB_HOST` (default: "localhost")
- `DB_NAME` (default: "bput15")

### File Upload Security
The application implements several upload security measures:
- File extension validation (only PNG, JPG, JPEG, GIF allowed)
- Secure filename generation using `werkzeug.utils.secure_filename`
- Files stored in `static/uploads/` with controlled access

**Best Practice**: Ensure the `static/uploads/` directory has appropriate permissions and is regularly monitored.

### Password Security
- All passwords are hashed using Werkzeug's `generate_password_hash`
- Password verification uses `check_password_hash`
- No plaintext passwords are stored in the database

### Session Security
- Session-based authentication with role-based access control
- User roles: student, company, college, university
- Session data includes: `user_id`, `role`, `logged_in` flag

### Database Security
- Uses SQLAlchemy ORM to prevent SQL injection
- Parameterized queries throughout the application
- Database credentials stored in environment variables

### API Security
- Google Gemini API key protected on server-side only
- Whereby API key used server-side for video room creation
- API endpoints check user authentication and authorization

## 📋 Security Checklist for Deployment

Before deploying to production, ensure:

- [ ] `.env` file is created with all required variables
- [ ] `SECRET_KEY` is set to a strong, random value (not the default)
- [ ] `DB_PASSWORD` is set to a strong database password
- [ ] All API keys (`GOOGLE_API_KEY`, `WHEREBY_API_KEY`) are valid and properly restricted
- [ ] `.env` file is NOT committed to version control (verified in `.gitignore`)
- [ ] Database backups are configured
- [ ] File upload directory permissions are properly set
- [ ] Flask debug mode is disabled (`debug=False` in production)
- [ ] HTTPS is enabled for all traffic
- [ ] Regular security updates are scheduled for dependencies

## 🔍 Security Audit Results

### What Was Checked:
✅ Git history for leaked secrets (none found)  
✅ Hardcoded API keys in source code (fixed)  
✅ Environment variable usage (properly implemented)  
✅ Password storage (using secure hashing)  
✅ SQL injection vulnerabilities (protected by ORM)  
✅ File upload security (extension validation in place)  
✅ Session management (implemented correctly)  
✅ `.gitignore` configuration (`.env` properly excluded)  

### Sensitive Files Found in Uploads:
The `static/uploads/` directory contains user-uploaded images and certificates. This is expected behavior. These files:
- Are not sensitive system files
- Are user-generated content (profile photos, company logos, certificates)
- Should be regularly backed up
- Should have appropriate access controls in production

## 🚨 Reporting Security Issues

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Contact the repository owner directly via GitHub
3. Provide detailed information about the vulnerability
4. Allow reasonable time for the issue to be addressed

## 📝 Security Updates

### Version History
- **2025-12-06**: Initial security audit completed
  - Fixed API key exposure in client-side code
  - Documented default secret key issue
  - Created comprehensive security documentation

## 🔗 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## 📧 Support

For security-related questions, please open a GitHub issue (for non-sensitive topics) or contact the maintainers directly.

---

**Last Updated**: December 6, 2025  
**Next Review**: Recommended quarterly security reviews
