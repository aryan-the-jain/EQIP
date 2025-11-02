# Streamlit Cloud Deployment Guide - Eqip.ai

## 🚀 **Quick Deployment Steps**

### **1. Prepare Your Repository**

First, ensure your code is in a GitHub repository:

```bash
# If not already a git repo
git init
git add .
git commit -m "Initial Eqip.ai complete pipeline"

# Push to GitHub
git remote add origin https://github.com/yourusername/eqip-ai.git
git branch -M main
git push -u origin main
```

### **2. Deploy to Streamlit Cloud**

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Repository**: Select your Eqip.ai repository
5. **Branch**: main
6. **Main file path**: `streamlit_app.py`
7. **Click "Deploy!"**

### **3. Configure Secrets (Important!)**

In your Streamlit Cloud app dashboard:

1. **Go to**: App settings → Secrets
2. **Add these secrets**:

```toml
# Demo Mode (set to false when you have a backend)
DEMO_MODE = "true"

# Backend API (when available)
API_BASE = "https://your-backend-api.herokuapp.com"

# OpenAI API Key (for RAG functionality)
OPENAI_API_KEY = "your-openai-api-key-here"

# Database (when using cloud database)
DATABASE_URL = "postgresql://user:pass@host:port/db"

# Vector Database
VECTOR_DB_URL = "https://your-qdrant-instance.qdrant.tech"
```

---

## 🎭 **Demo Mode Features**

Your app includes a **Demo Mode** that works without a backend:

### **What Works in Demo Mode:**
- ✅ **Complete UI**: All 5 pipeline stages functional
- ✅ **Mock Data**: Realistic sample responses
- ✅ **Full Flow**: Users can test the entire pipeline
- ✅ **Visualizations**: Charts and tables with demo data
- ✅ **Contract Generation**: Sample contracts with realistic content
- ✅ **License Recommendations**: Real license analysis
- ✅ **Export Functions**: JSON and text report downloads

### **Demo Mode Responses:**
- **IP Options**: UK-focused copyright, trademark, and design rights advice
- **Attribution**: Equal distribution among contributors
- **Ownership**: Proportional share allocation
- **Contracts**: Sample legal agreements (NDA, IP Assignment, etc.)
- **Licenses**: MIT and Apache 2.0 recommendations

---

## 🔧 **Production Deployment Options**

### **Option 1: Frontend-Only (Recommended for Demo)**
- **Deploy**: Just the Streamlit app with demo mode
- **Benefits**: Quick deployment, no backend complexity
- **Use Case**: Demonstrations, prototyping, user testing

### **Option 2: Full Stack Deployment**
- **Backend**: Deploy FastAPI to Heroku/Railway/DigitalOcean
- **Database**: PostgreSQL on Heroku/Supabase/Neon
- **Vector DB**: Qdrant Cloud
- **Frontend**: Streamlit Cloud
- **Benefits**: Full functionality with real RAG

---

## 📁 **Files for Deployment**

### **Required Files:**
- ✅ `streamlit_app.py` - Main entry point with demo mode
- ✅ `frontend/streamlit_app_enhanced.py` - Enhanced UI functionality
- ✅ `requirements_streamlit.txt` - Minimal dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml` - Environment variables template

### **Optional Files (for full stack):**
- `backend/` - FastAPI backend code
- `requirements.txt` - Full dependencies
- `docker-compose.yml` - Local development
- `Dockerfile` - Container deployment

---

## 🎯 **Deployment Checklist**

### **Pre-Deployment:**
- [ ] Code pushed to GitHub repository
- [ ] `streamlit_app.py` in root directory
- [ ] `requirements_streamlit.txt` configured
- [ ] `.streamlit/config.toml` created

### **Streamlit Cloud Setup:**
- [ ] App created on share.streamlit.io
- [ ] Repository connected
- [ ] Main file path set to `streamlit_app.py`
- [ ] Secrets configured (at minimum `DEMO_MODE = "true"`)

### **Post-Deployment:**
- [ ] App loads without errors
- [ ] All 5 pipeline stages accessible
- [ ] Demo functionality working
- [ ] Export features functional

---

## 🔗 **Backend Deployment (Optional)**

If you want full functionality, deploy the backend separately:

### **Heroku Deployment:**
```bash
# Install Heroku CLI, then:
heroku create your-eqip-backend
heroku addons:create heroku-postgresql:mini
heroku config:set OPENAI_API_KEY=your-key-here
git subtree push --prefix=backend heroku main
```

### **Railway Deployment:**
1. Connect your GitHub repo to Railway
2. Select the `backend` folder
3. Add environment variables
4. Deploy automatically

### **Update Streamlit Secrets:**
```toml
DEMO_MODE = "false"
API_BASE = "https://your-backend-url.herokuapp.com"
```

---

## 🎨 **Customization for Production**

### **Branding:**
- Update the gradient title colors in CSS
- Modify the color scheme in `.streamlit/config.toml`
- Add your company logo and branding

### **Features:**
- Enable/disable demo mode via secrets
- Configure default jurisdictions
- Customize contract templates
- Add additional license types

---

## 🚨 **Important Notes**

### **Demo Mode Limitations:**
- No persistent data storage
- Mock API responses only
- No real RAG functionality
- Contracts are templates only

### **Production Requirements:**
- OpenAI API key for RAG
- PostgreSQL database for data persistence
- Vector database for document search
- File storage for contract documents

---

## 📞 **Support**

### **Common Issues:**
1. **App won't start**: Check `requirements_streamlit.txt` and main file path
2. **Secrets not working**: Verify secrets.toml format in Streamlit Cloud
3. **API errors**: Ensure `DEMO_MODE = "true"` for frontend-only deployment

### **Deployment URLs:**
- **Streamlit Cloud**: https://share.streamlit.io/
- **GitHub**: https://github.com/yourusername/eqip-ai
- **Your App**: https://yourusername-eqip-ai-streamlit-app-main.streamlit.app/

---

**🎉 Your Eqip.ai system is ready for cloud deployment!**

*Deployment guide created on November 2, 2025*
