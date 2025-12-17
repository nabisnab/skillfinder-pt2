import streamlit as st
import re
from collections import Counter
from typing import Dict, List, Tuple
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Scanner - SkillFinder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .score-high {
        color: #09ab3b;
        font-weight: bold;
    }
    .score-medium {
        color: #ff9500;
        font-weight: bold;
    }
    .score-low {
        color: #ff2b2b;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def extract_skills(text: str) -> List[str]:
    """Extract technical skills and keywords from text."""
    # Convert to lowercase for processing
    text = text.lower()
    
    # Common tech skills, frameworks, and tools
    common_skills = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell',
        
        # Web Technologies
        'html', 'css', 'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask',
        'fastapi', 'spring', 'asp.net', 'laravel', 'rails', 'webpack', 'tailwind',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'firebase', 'elasticsearch', 'redis',
        'dynamodb', 'cassandra', 'oracle', 'sqlite', 'neo4j', 'graphql',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github',
        'terraform', 'ansible', 'ci/cd', 'devops', 'microservices',
        
        # Data & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'apache spark', 'hadoop',
        'data science', 'nlp', 'computer vision', 'ai', 'neural networks',
        
        # Other Technologies
        'git', 'rest api', 'graphql', 'soap', 'mqtt', 'grpc', 'json', 'xml',
        'linux', 'windows', 'macos', 'jira', 'confluence', 'slack'
    ]
    
    # Find skills in text
    found_skills = []
    for skill in common_skills:
        if skill in text:
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates

def extract_experience_years(text: str) -> float:
    """Estimate years of experience from resume text."""
    text_lower = text.lower()
    
    # Look for experience patterns like "5 years", "10+ years", etc.
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:professional|industry|it)',
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            return float(matches[0])
    
    # Count job entries as rough estimate (1 year per position)
    job_keywords = ['senior', 'lead', 'manager', 'developer', 'engineer', 'architect']
    job_count = sum(1 for keyword in job_keywords if keyword in text_lower)
    
    return float(job_count) if job_count > 0 else 0.0

def calculate_match_score(resume_skills: List[str], job_skills: List[str]) -> Tuple[float, Dict]:
    """Calculate match score between resume and job description."""
    if not job_skills:
        return 0.0, {"matched": [], "missing": [], "extra": []}
    
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    # Find matched skills
    matched = [skill for skill in job_skills if skill.lower() in resume_skills_lower]
    
    # Find missing skills
    missing = [skill for skill in job_skills if skill.lower() not in resume_skills_lower]
    
    # Find extra skills in resume
    extra = [skill for skill in resume_skills if skill.lower() not in job_skills_lower]
    
    # Calculate match percentage
    match_percentage = (len(matched) / len(job_skills)) * 100 if job_skills else 0
    
    return match_percentage, {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_count": len(matched),
        "total_required": len(job_skills)
    }

def calculate_keyword_frequency(text: str) -> Dict[str, int]:
    """Calculate frequency of important keywords."""
    text_lower = text.lower()
    
    # Important keywords to track
    keywords = [
        'team', 'leadership', 'communication', 'problem solving', 'analytical',
        'agile', 'scrum', 'project', 'management', 'api', 'integration',
        'performance', 'optimization', 'security', 'testing', 'qa',
        'ux', 'ui', 'design', 'architecture', 'scalability'
    ]
    
    freq = {}
    for keyword in keywords:
        count = text_lower.count(keyword.lower())
        if count > 0:
            freq[keyword.title()] = count
    
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

def generate_detailed_analysis(resume_text: str, job_text: str) -> Dict:
    """Generate comprehensive analysis of resume vs job description."""
    
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    
    match_score, match_details = calculate_match_score(resume_skills, job_skills)
    
    resume_experience = extract_experience_years(resume_text)
    job_experience = extract_experience_years(job_text)
    
    experience_match = min((resume_experience / job_experience * 100), 100) if job_experience > 0 else 0
    
    resume_keywords = calculate_keyword_frequency(resume_text)
    job_keywords = calculate_keyword_frequency(job_text)
    
    # Calculate overall score (weighted)
    overall_score = (match_score * 0.6) + (experience_match * 0.4)
    
    return {
        "skill_match_score": match_score,
        "experience_match_score": experience_match,
        "overall_score": overall_score,
        "match_details": match_details,
        "resume_experience": resume_experience,
        "job_experience": job_experience,
        "resume_keywords": resume_keywords,
        "job_keywords": job_keywords,
        "resume_skills": resume_skills,
        "job_skills": job_skills
    }

def get_score_color(score: float) -> str:
    """Return color class based on score."""
    if score >= 75:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    else:
        return "score-low"

def get_recommendation(score: float) -> str:
    """Generate recommendation based on overall score."""
    if score >= 85:
        return "🟢 Excellent Match! Strong candidate for this position."
    elif score >= 70:
        return "🟡 Good Match! Candidate has most required skills with potential to grow."
    elif score >= 50:
        return "🟠 Moderate Match! Candidate has foundational skills but needs development in key areas."
    else:
        return "🔴 Weak Match! Significant skill gaps exist. Further training recommended."

# Main Streamlit App
st.title("📄 Resume Scanner - SkillFinder")
st.markdown("Analyze resumes against job descriptions with intelligent skill matching and scoring.")

# Sidebar for instructions
with st.sidebar:
    st.header("ℹ️ Instructions")
    st.markdown("""
    1. **Paste Resume**: Enter the full resume text
    2. **Paste Job Description**: Enter the job posting text
    3. **Analyze**: Click the analyze button
    4. **Review Results**: Check the detailed scoring and recommendations
    
    The app analyzes:
    - Technical skill matching
    - Experience requirements
    - Keyword alignment
    - Overall compatibility
    """)

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Resume")
    resume_text = st.text_area(
        "Paste resume content here:",
        height=300,
        placeholder="John Doe\nSoftware Engineer\n\nExperience:\n- 5 years Python development\n- React and Node.js expertise\n..."
    )

with col2:
    st.subheader("💼 Job Description")
    job_text = st.text_area(
        "Paste job description here:",
        height=300,
        placeholder="Senior Software Engineer\n\nRequired Skills:\n- 5+ years of Python\n- React expertise\n- Docker and Kubernetes..."
    )

# Analyze button
if st.button("🔍 Analyze Match", use_container_width=True, type="primary"):
    if resume_text and job_text:
        with st.spinner("Analyzing resume and job description..."):
            analysis = generate_detailed_analysis(resume_text, job_text)
        
        # Display Overall Score
        st.markdown("---")
        st.subheader("Overall Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Skill Match",
                f"{analysis['skill_match_score']:.1f}%",
                f"{analysis['match_details']['match_count']}/{analysis['match_details']['total_required']} skills"
            )
        
        with col2:
            st.metric(
                "Experience Match",
                f"{analysis['experience_match_score']:.1f}%",
                f"Resume: {analysis['resume_experience']:.0f} yrs | Required: {analysis['job_experience']:.0f} yrs"
            )
        
        with col3:
            overall_color = get_score_color(analysis['overall_score'])
            st.markdown(f"""
            <div class="metric-card">
                <p style="margin: 0; color: gray; font-size: 0.9em;">OVERALL SCORE</p>
                <p class="{overall_color}" style="font-size: 2em; margin: 10px 0;">
                    {analysis['overall_score']:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendation
        st.markdown("---")
        st.info(get_recommendation(analysis['overall_score']))
        
        # Detailed Skill Analysis
        st.markdown("---")
        st.subheader("📊 Skill Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Matched Skills")
            if analysis['match_details']['matched']:
                for skill in analysis['match_details']['matched']:
                    st.success(f"• {skill}")
            else:
                st.warning("No matching skills found")
        
        with col2:
            st.markdown("#### ❌ Missing Skills")
            if analysis['match_details']['missing']:
                for skill in analysis['match_details']['missing']:
                    st.error(f"• {skill}")
            else:
                st.success("All required skills present!")
        
        # Additional Skills
        if analysis['match_details']['extra']:
            st.markdown("---")
            st.markdown("#### ⭐ Additional Skills in Resume")
            col = st.columns(2)
            for idx, skill in enumerate(analysis['match_details']['extra'][:6]):
                col[idx % 2].info(f"• {skill}")
        
        # Keyword Analysis
        st.markdown("---")
        st.subheader("🔑 Keyword Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Job Description Keywords")
            if analysis['job_keywords']:
                df_job = pd.DataFrame(
                    list(analysis['job_keywords'].items()),
                    columns=["Keyword", "Frequency"]
                )
                st.bar_chart(df_job.set_index("Keyword"))
            else:
                st.info("No key keywords found")
        
        with col2:
            st.markdown("#### Resume Keywords")
            if analysis['resume_keywords']:
                df_resume = pd.DataFrame(
                    list(analysis['resume_keywords'].items()),
                    columns=["Keyword", "Frequency"]
                )
                st.bar_chart(df_resume.set_index("Keyword"))
            else:
                st.info("No key keywords found")
        
        # Detailed Skill Lists
        st.markdown("---")
        st.subheader("📝 Complete Skill Lists")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Resume Skills")
            if analysis['resume_skills']:
                resume_df = pd.DataFrame({"Skills": sorted(analysis['resume_skills'])})
                st.dataframe(resume_df, use_container_width=True, hide_index=True)
            else:
                st.info("No skills detected in resume")
        
        with col2:
            st.markdown("#### Required Job Skills")
            if analysis['job_skills']:
                job_df = pd.DataFrame({"Skills": sorted(analysis['job_skills'])})
                st.dataframe(job_df, use_container_width=True, hide_index=True)
            else:
                st.info("No skills found in job description")
    
    else:
        st.warning("⚠️ Please enter both resume and job description to analyze")

# Footer
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: gray; font-size: 0.9em;">
SkillFinder Resume Scanner © 2025 | Powered by Streamlit
</p>
""", unsafe_allow_html=True)
