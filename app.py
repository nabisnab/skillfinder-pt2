import streamlit as st
import re
import PyPDF2
from groq import Groq
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json

# Download required NLTK data
try:      
    nltk.data.find('tokenizers/punkt')
except LookupError:  
    nltk.download('punkt')

try:  
    nltk.data.find('corpora/stopwords')
except LookupError:  
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:  
    nltk.download('wordnet')

# ===== GROQ API KEY =====
GROQ_API_KEY = "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"
# ===========================

# Page Configuration
st.set_page_config(
    page_title="SkillFinder - Resume Scanner Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    : root {
        --primary-color: #0066cc;
        --secondary-color: #00d4ff;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
    }

    .main {
        background:  linear-gradient(135deg, #0f172a 0%, #1a2a4a 100%);
    }

    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border-bottom: 1px solid #334155;
        margin-bottom: 2rem;
        border-radius: 0 0 12px 12px;
        position: sticky;
        top: 0;
        z-index:  100;
    }

    .logo-container {
        font-size: 1.8rem;
        font-weight:  800;
    }

    .logo-skill {
        color: #0066cc;
    }

    .logo-finder {
        color: #cbd5e1;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        color: #cbd5e1;
        font-weight: 600;
    }

    .header-container {
        background: linear-gradient(135deg, #0066cc 0%, #00d4ff 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 102, 204, 0.3);
    }

    .header-container h1 {
        color:  white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
    }

    .header-container p {
        color: rgba(255, 255, 255, 0.9);
        margin:  0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    .position-card {
        background: linear-gradient(135deg, #0066cc 0%, #00d4ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }

    .position-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
    }

    .position-card p {
        margin:  0;
        opacity: 0.9;
    }

    .metric-card {
        background: #1e293b;
        border:  2px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: #0066cc;
        background: #334155;
    }

    . metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #00d4ff;
        margin: 0.5rem 0;
    }

    . metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    . stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #00d4ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 102, 204, 0.4);
    }

    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin:  0.25rem;
        font-size: 0.85rem;
        font-weight:  600;
    }

    .skill-rank {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1e293b;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
    }

    .ai-response {
        background: #1e293b;
        border-left: 4px solid #0066cc;
        padding: 1rem;
        border-radius:  8px;
        margin:  1rem 0;
    }

    .score-bar {
        width: 100%;
        height: 8px;
        background: #334155;
        border-radius:  4px;
        overflow:  hidden;
        margin-top: 0.5rem;
    }

    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #0066cc 0%, #00d4ff 100%);
    }

    .position-input-container {
        background: #1e293b;
        border: 2px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .shortlist-card {
        background: #0f172a;
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        margin:  0.5rem 0;
    }

    .rejected-card {
        background: #0f172a;
        border:  2px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'preferred_position' not in st.session_state:
    st.session_state.preferred_position = None
if 'job_description' not in st.session_state:
    st.session_state.job_description = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'ats_results' not in st. session_state:
    st. session_state.ats_results = None

# Initialize NLTK
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords. words('english'))

# Top Navigation Bar
st.markdown("""
<div class="top-nav">
    <div class="logo-container">
        <span class="logo-skill">Skill</span><span class="logo-finder">Finder</span>
    </div>
    <div class="nav-links">
        <span>Home</span>
        <span>About</span>
        <span>How it works</span>
        <span>Contact</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# ========== ATS LOGIC ==========

# Define skill keywords for different positions
POSITION_KEYWORDS = {
    "data scientist": {
        "required": ["python", "machine learning", "sql", "pandas", "scikit-learn", "data analysis"],
        "nice_to_have": ["tensorflow", "spark", "deep learning", "statistics", "tableau", "power bi"],
    },
    "software engineer": {
        "required":  ["python", "java", "javascript", "git", "oop", "api"],
        "nice_to_have": ["docker", "kubernetes", "aws", "ci/cd", "microservices", "react"],
    },
    "ux designer": {
        "required": ["figma", "user research", "wireframing", "prototyping", "ui/ux", "design thinking"],
        "nice_to_have": ["adobe xd", "sketch", "user testing", "accessibility", "interaction design"],
    },
    "product manager": {
        "required":  ["product strategy", "roadmap", "stakeholder management", "market analysis", "metrics"],
        "nice_to_have": ["agile", "jira", "analytics", "a/b testing", "user interviews"],
    },
    "devops engineer": {
        "required": ["docker", "kubernetes", "ci/cd", "linux", "aws", "infrastructure"],
        "nice_to_have": ["terraform", "ansible", "prometheus", "jenkins", "git"],
    },
}

def extract_keywords(resume_text:  str) -> List[str]:
    """Extract keywords from resume"""
    resume_lower = resume_text.lower()
    words = word_tokenize(resume_lower)
    keywords = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
    return keywords

def calculate_keyword_match(resume_text: str, position:  str) -> Dict: 
    """Calculate keyword matching score"""
    resume_lower = resume_text.lower()
    
    # Get position keywords
    position_lower = position.lower()
    keywords = POSITION_KEYWORDS.get(position_lower, {}).get("required", [])
    nice_keywords = POSITION_KEYWORDS.get(position_lower, {}).get("nice_to_have", [])
    
    # Find matches
    required_matches = [k for k in keywords if k in resume_lower]
    nice_matches = [k for k in nice_keywords if k in resume_lower]
    
    # Calculate score
    required_score = (len(required_matches) / len(keywords) * 100) if keywords else 0
    nice_score = (len(nice_matches) / len(nice_keywords) * 100) if nice_keywords else 0
    
    keyword_match_score = (required_score * 0.7) + (nice_score * 0.3)
    
    return {
        "keyword_match_score": keyword_match_score,
        "required_matches": required_matches,
        "missing_keywords": [k for k in keywords if k not in resume_lower],
        "nice_to_have_matches": nice_matches,
    }

def calculate_ats_score(resume_text:  str, position: str, ai_analysis: Dict) -> Dict:
    """
    Calculate ATS Score with weighted criteria: 
    - Keyword Match:  40%
    - AI Overall Score: 30%
    - Skill Match: 20%
    - Experience Alignment: 10%
    """
    keyword_match = calculate_keyword_match(resume_text, position)
    
    ai_overall = ai_analysis.get('overall_score', 0)
    skill_match = ai_analysis.get('skill_match_percentage', 0)
    experience = ai_analysis.get('experience_alignment', 0)
    
    # Weighted ATS score
    ats_score = (
        (keyword_match['keyword_match_score'] * 0.40) +
        (ai_overall * 0.30) +
        (skill_match * 0.20) +
        (experience * 0.10)
    )
    
    return {
        "ats_score": min(100, ats_score),
        "keyword_match":  keyword_match,
        "breakdown": {
            "keyword_weight": keyword_match['keyword_match_score'] * 0.40,
            "ai_overall_weight": ai_overall * 0.30,
            "skill_match_weight": skill_match * 0.20,
            "experience_weight": experience * 0.10,
        }
    }

def shortlist_candidate(ats_score: float, threshold: float = 60.0) -> Dict:
    """
    Determine if candidate should be shortlisted
    Threshold: 60+ = Shortlist, Below 60 = Reject
    """
    if ats_score >= threshold:
        return {
            "status": "SHORTLISTED ✅",
            "color": "#10b981",
            "recommendation": "Recommended for next round",
            "reasoning": "Meets minimum criteria for position"
        }
    else: 
        return {
            "status":  "REJECTED ❌",
            "color": "#ef4444",
            "recommendation": "Does not meet minimum criteria",
            "reasoning": "Score below threshold"
        }

# Groq AI - MAIN ANALYSIS ENGINE
def analyze_with_groq_main(resume_text: str, preferred_position: str, job_description: str) -> Dict:
    """
    MAIN AI ANALYSIS - Groq analyzes resume for the preferred position
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""Analyze this resume for the {preferred_position} position and ONLY respond with valid JSON. 

RESUME: 
{resume_text[: 2500]}

PREFERRED POSITION: {preferred_position}

JOB DESCRIPTION:  {job_description if job_description else "General fit analysis"}

Return ONLY this JSON structure (no markdown, no extra text):
{{
    "position_title": "{preferred_position}",
    "overall_score": 85,
    "skill_match_percentage": 80,
    "experience_alignment": 75,
    "strengths_for_position": ["strength1", "strength2", "strength3", "strength4"],
    "gaps_for_position": ["gap1", "gap2", "gap3", "gap4"],
    "specific_recommendations": ["rec1", "rec2", "rec3", "rec4", "rec5", "rec6"],
    "ats_score": 80,
    "hiring_probability": 75,
    "years_experience_match": "5+ years required, 3 years found",
    "detailed_feedback": "Overall feedback text here"
}}"""
        
        message = client.chat.completions. create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=800,
        )
        
        response_text = message.choices[0].message.content. strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text. split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        response_text = response_text.strip()
        
        # Extract JSON from curly braces
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            st.error("❌ Model did not return valid JSON format")
            return None
        
        json_str = response_text[json_start:json_end]
        
        # Try to parse
        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON parsing error: {str(e)}")
            st.write(f"Attempted to parse: {json_str[: 200]}...")
            return None
    
    except Exception as e: 
        st.error(f"❌ Error with Groq AI: {str(e)}")
        return None

# Main Header
st.markdown("""
<div class="header-container">
    <h1>📄 Resume Scanner Pro</h1>
    <p>Powered by Groq AI + ATS Filtering - Advanced Resume Analysis & Position Matching</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Resume", "💼 Position Analysis", "🤖 ATS & Shortlisting", "🏆 Results"])

with tab1:
    st.markdown("### 📤 Upload Your Resume")
    st.markdown("**Drag and drop** your resume file below or click to browse")
    
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, TXT)",
        type=['pdf', 'txt'],
        label_visibility="collapsed",
        help="Upload your resume in PDF or TXT format"
    )
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_ext = file_name.split('.')[-1].lower()
        
        try:
            if file_ext == 'pdf':
                resume_text = extract_text_from_pdf(uploaded_file)
            elif file_ext == 'txt': 
                resume_text = uploaded_file.read().decode('utf-8')
            else:
                resume_text = None
            
            if resume_text:
                st.session_state.resume_data = resume_text
                st.success(f"✅ **{file_name}** uploaded successfully!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st. metric("📄 File Type", file_ext. upper())
                with col2:
                    st.metric("📝 Characters", len(resume_text))
                with col3:
                    st.metric("📋 Words", len(resume_text.split()))
                
                with st.expander("👀 Preview Resume", expanded=False):
                    st.text_area(
                        "Resume Content",
                        value=resume_text[: 500] + "..." if len(resume_text) > 500 else resume_text,
                        height=200,
                        disabled=True
                    )
        
        except Exception as e: 
            st.error(f"❌ Error processing file: {str(e)}")

with tab2:
    if st.session_state.resume_data:
        st.markdown("### 💼 Target Position & Job Details")
        
        st.markdown("#### What position are you targeting?")
        preferred_position = st.text_input(
            "Preferred Position:",
            placeholder="e.g., Data Scientist, Software Engineer, UX Designer",
            key="position_input",
            help="Enter the exact job title you're aiming for"
        )
        
        st.markdown("#### (Optional) Paste the Job Description")
        st.markdown("Leave empty to analyze for general fit")
        
        job_description = st.text_area(
            "Job Description:",
            height=250,
            placeholder="Role description here.. .",
            key="job_input"
        )
        
        if st.button("🤖 Analyze for Position", use_container_width=True, type="primary"):
            if preferred_position: 
                st.markdown(f"""
                <div class="position-card">
                    <h3>🎯 Target Position</h3>
                    <p>{preferred_position}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st. session_state.preferred_position = preferred_position
                st.session_state.job_description = job_description
                
                with st.spinner(f"🤖 Analyzing your fit for {preferred_position}..."):
                    analysis = analyze_with_groq_main(
                        st.session_state.resume_data,
                        preferred_position,
                        job_description
                    )
                
                if analysis:
                    st.session_state.analysis_results = analysis
                    
                    st.markdown("---")
                    st.subheader(f"📊 Your Fit for {preferred_position}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Overall Score", f"{analysis. get('overall_score', 0)}")
                    with col2:
                        st.metric("Skill Match", f"{analysis.get('skill_match_percentage', 0)}%")
                    with col3:
                        st.metric("Experience", f"{analysis.get('experience_alignment', 0)}%")
                    with col4:
                        st.metric("Hiring Prob.", f"{analysis.get('hiring_probability', 0)}%")
                    
                    st.markdown("---")
                    st.markdown("#### 📅 Experience Match")
                    st.info(f"📌 {analysis.get('years_experience_match', 'N/A')}")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### ✅ Strengths")
                        for strength in analysis.get('strengths_for_position', []):
                            st.success(f"✓ {strength}")
                    with col2:
                        st.markdown("#### 🎯 Gaps")
                        for gap in analysis.get('gaps_for_position', []):
                            st.warning(f"→ {gap}")
                    
                    st.markdown("---")
                    st.markdown("#### 📝 Feedback")
                    st.info(analysis.get('detailed_feedback', 'No feedback'))
                    
                    st. markdown("---")
                    st.markdown("#### 🚀 Recommendations")
                    for i, rec in enumerate(analysis.get('specific_recommendations', []), 1):
                        st.info(f"**{i}. ** {rec}")
            else:
                st.error("❌ Please enter your preferred position")
    else:
        st.info("👉 Upload a resume first")

with tab3:
    if st.session_state.analysis_results and st.session_state.resume_data:
        st.markdown("### 🤖 ATS Filtering & Shortlisting")
        
        analysis = st.session_state.analysis_results
        position = st.session_state.preferred_position or "Target Position"
        
        ats_results = calculate_ats_score(
            st.session_state.resume_data,
            position,
            analysis
        )
        st.session_state.ats_results = ats_results
        
        st.markdown("#### 📊 ATS Score Breakdown")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Final ATS", f"{ats_results['ats_score']:.1f}")
        with col2:
            st.metric("Keywords", f"{ats_results['breakdown']['keyword_weight']:.1f}")
        with col3:
            st.metric("AI Score", f"{ats_results['breakdown']['ai_overall_weight']:.1f}")
        with col4:
            st.metric("Skills", f"{ats_results['breakdown']['skill_match_weight']:.1f}")
        with col5:
            st.metric("Experience", f"{ats_results['breakdown']['experience_weight']:.1f}")
        
        st.markdown("---")
        st.markdown("#### 🔍 Keyword Analysis")
        
        keyword_info = ats_results['keyword_match']
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Found Keywords:**")
            if keyword_info['required_matches']:
                for skill in keyword_info['required_matches']: 
                    st.write(f"• {skill. title()}")
            else:
                st.warning("No keywords found")
        
        with col2:
            st.markdown("**❌ Missing Keywords:**")
            if keyword_info['missing_keywords']:
                for skill in keyword_info['missing_keywords']:
                    st.write(f"• {skill.title()}")
            else:
                st.success("All keywords present!")
        
        st.markdown("---")
        st.markdown("#### 🎁 Nice-to-Have Skills:")
        if keyword_info['nice_to_have_matches']:
            for skill in keyword_info['nice_to_have_matches']:
                st. write(f"• {skill. title()}")
        else:
            st.info("None found")
        
        st. markdown("---")
        st.markdown("#### 📋 Shortlisting Decision")
        shortlist = shortlist_candidate(ats_results['ats_score'])
        
        status_color = shortlist['color']
        status_text = shortlist['status']
        recommendation = shortlist['recommendation']
        
        st.markdown(f"""
        <div style="background:  #1e293b; border:  3px solid {status_color}; padding: 1. 5rem; border-radius: 12px;">
            <h3 style="color: {status_color}; margin:  0;">{status_text}</h3>
            <p style="color:  #cbd5e1; margin: 0. 5rem 0 0 0;"><strong>{recommendation}</strong></p>
            <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.9rem;">{shortlist['reasoning']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👉 Complete analysis first")

with tab4:
    if st. session_state.analysis_results and st.session_state. ats_results:
        analysis = st.session_state.analysis_results
        position = st. session_state.preferred_position or "Target Position"
        ats_results = st.session_state.ats_results
        
        st.markdown(f"### 🏆 Complete Summary for {position}")
        
        st.markdown("#### 📊 All Scores")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ATS Score", f"{ats_results['ats_score']:.1f}")
        with col2:
            st.metric("AI Overall", f"{analysis. get('overall_score', 0)}")
        with col3:
            st.metric("Hiring Prob.", f"{analysis.get('hiring_probability', 0)}%")
        with col4:
            st.metric("Skill Match", f"{analysis.get('skill_match_percentage', 0)}%")
        
        st.markdown("---")
        st.markdown("#### ✅ Strengths")
        for strength in analysis.get('strengths_for_position', []):
            st.success(f"• {strength}")
        
        st.markdown("---")
        st.markdown("#### 🎯 Areas to Improve")
        for gap in analysis.get('gaps_for_position', []):
            st.warning(f"• {gap}")
        
        st. markdown("---")
        st.markdown("#### 📈 Detailed Feedback")
        st.info(analysis.get('detailed_feedback', 'No feedback'))
        
        st.markdown("---")
        st.markdown("#### 🚀 Recommendations")
        for i, rec in enumerate(analysis.get('specific_recommendations', []), 1):
            st.info(f"**{i}.** {rec}")
    else:
        st.info("👉 Complete all steps")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 2rem 0;'>
    <p>🚀 SkillFinder • Powered by Groq AI + ATS Logic</p>
    <p style='font-size: 0.85rem;'>Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
</div>
""", unsafe_allow_html=True)
