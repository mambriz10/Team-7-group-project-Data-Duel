# 📚 DataDuel Documentation Index

**Last Updated:** November 24, 2025

Welcome to DataDuel! This index helps you navigate all project documentation.

---

## 🚀 Quick Start

**New to the project?**
1. Read [README.md](README.md) - Project overview and setup
2. Follow [DEPLOYMENT.md](DEPLOYMENT.md) - Get it running
3. Review [FEATURES.md](FEATURES.md) - Understand what's built

**Ready to develop?**
4. Check [PROGRESS.md](PROGRESS.md) - Current status and what's next
5. Use [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md) - Test and debug

---

## 📖 Documentation Structure

### 1. [README.md](README.md) - Project Overview
**Purpose:** High-level introduction, setup instructions, and quick start guide

**Contents:**
- Project vision and goals
- Technology stack
- Architecture overview
- Quick setup (5 minutes)
- Core features list
- API endpoints reference
- Project structure

**Read this if:** You're new to the project or need setup instructions

---

### 2. [FEATURES.md](FEATURES.md) - Technical Documentation
**Purpose:** Deep dive into how each feature works

**Contents:**
- Scoring algorithm explained
- Friends system (Supabase)
- Badge & challenge systems
- Route generation
- Data models and structures
- API endpoint details
- Frontend/backend integration

**Read this if:** You need to understand or modify a specific feature

---

### 3. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment Guide
**Purpose:** Complete deployment instructions for production

**Contents:**
- Cloudflare Pages setup
- Backend deployment (Render/Railway/Heroku)
- Supabase configuration
- Environment variables
- Post-deployment checklist
- Troubleshooting deployment issues
- Cost breakdown

**Read this if:** You're deploying to production or debugging deployment

---

### 4. [PROGRESS.md](PROGRESS.md) - Development Status
**Purpose:** Track what's done, what's in progress, and what's next

**Contents:**
- Feature completion status
- Known issues and limitations
- Current sprint tasks
- Team assignments
- Recent changes
- Future roadmap

**Read this if:** You want to know project status or what to work on next

---

### 5. [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md) - Testing & Debug Guide
**Purpose:** How to test features and fix issues

**Contents:**
- Friends system testing (Supabase)
- Backend API testing
- Frontend testing
- Common issues & solutions
- Logging reference
- Debug commands

**Read this if:** You're testing features or debugging issues

---

### 6. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment Guide
**Purpose:** Production deployment instructions

**Contents:**
- Architecture diagrams
- Frontend deployment (Cloudflare Pages)
- Backend deployment (Render/Railway/Heroku)
- Database setup (Supabase)
- Integration checklist
- Security considerations
- Monitoring & debugging

**Read this if:** You're deploying or configuring production environment

---

## 🔗 Quick Links by Task

### "I want to set up the project locally"
→ [README.md](README.md) - Quick Start Guide

### "I want to understand the scoring algorithm"
→ [FEATURES.md](FEATURES.md) - Scoring System section

### "I want to deploy to production"
→ [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide

### "I want to test the friends feature"
→ [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md) - Friends System Testing

### "I want to see what's been completed"
→ [PROGRESS.md](PROGRESS.md) - Current Status section

### "I'm getting an error"
→ [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md) - Common Issues section

### "I want to add a new feature"
→ [FEATURES.md](FEATURES.md) - Understand existing architecture
→ [PROGRESS.md](PROGRESS.md) - See future roadmap

---

## 📁 Additional Resources

### Backend-Specific
- `DataDuel/backend/supabase_stravaDB/migration_friends.sql` - Database schema
- `DataDuel/backend/test_data_flow.py` - Data flow testing
- `DataDuel/backend/test_friends_api.py` - Friends API testing

### Frontend-Specific
- `DataDuel/frontend/config.js` - Environment configuration
- `DataDuel/frontend/_headers` - Cloudflare headers
- `DataDuel/frontend/_redirects` - Cloudflare redirects

### Deployment
- `wrangler.toml` - Cloudflare Pages config (production-ready)
- `Procfile` - Backend startup command
- `requirements.txt` - Python dependencies

---

## 🏗️ Project File Structure

```
Team-7-group-project-Data-Duel/
├── README.md                    ← Start here
├── INDEX.md                     ← You are here
├── FEATURES.md                  ← Technical details
├── DEPLOYMENT.md                ← Deployment guide
├── PROGRESS.md                  ← Status & roadmap
├── TESTING_AND_DEBUGGING.md     ← Testing guide
├── wrangler.toml                ← Cloudflare config
├── requirements.txt             ← Python packages
├── Procfile                     ← Backend startup
│
└── DataDuel/
    ├── backend/
    │   ├── app.py               ← Main Flask server
    │   ├── data_storage.py      ← JSON storage
    │   ├── friends_storage.py   ← Deprecated (use Supabase)
    │   ├── strava_parser.py     ← Activity parser
    │   ├── route_generator.py   ← Route system
    │   ├── supabase_stravaDB/
    │   │   ├── strava_user.py   ← Supabase functions
    │   │   └── migration_friends.sql ← DB schema
    │   └── data/
    │       ├── users.json       ← User profiles
    │       ├── activities.json  ← Strava data
    │       └── scores.json      ← Calculated scores
    │
    ├── frontend/
    │   ├── index.html           ← Home page
    │   ├── profile.html         ← User profile
    │   ├── social.html          ← Friends system
    │   ├── leaderboards.html    ← Rankings
    │   ├── routes.html          ← Route discovery
    │   ├── config.js            ← Environment config
    │   ├── api.js               ← API client
    │   └── styles.css           ← Global styles
    │
    ├── Person.py                ← User data model
    ├── Score.py                 ← Scoring algorithm
    ├── badges.py                ← Badge system
    └── challenges.py            ← Challenge system
```

---

## 🎓 Development Workflow

### For New Features:
1. Check [PROGRESS.md](PROGRESS.md) - See what's planned
2. Read [FEATURES.md](FEATURES.md) - Understand existing code
3. Develop & test locally
4. Update [PROGRESS.md](PROGRESS.md) - Mark complete
5. Test using [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md)
6. Deploy using [DEPLOYMENT.md](DEPLOYMENT.md)

### For Bug Fixes:
1. Check [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md) - Common issues
2. Use logging/debug commands
3. Fix and test
4. Update [PROGRESS.md](PROGRESS.md) - Note the fix

### For Deployment:
1. Test everything locally
2. Follow [DEPLOYMENT.md](DEPLOYMENT.md) step-by-step
3. Update [PROGRESS.md](PROGRESS.md) - Mark deployed
4. Monitor using deployment docs

---

## 📞 Need Help?

**Can't find what you're looking for?**
1. Search this index for keywords
2. Check the relevant main document
3. Use Ctrl+F in individual files
4. Review code comments in source files

**Common Searches:**
- "friends" → FEATURES.md + TESTING_AND_DEBUGGING.md
- "deploy" → DEPLOYMENT.md
- "error" → TESTING_AND_DEBUGGING.md
- "score" → FEATURES.md
- "setup" → README.md
- "status" → PROGRESS.md

---

**Status:** Documentation Organized ✅  
**Team:** CS422 Team 7  
**Project:** DataDuel - Fair Fitness Competition Platform

