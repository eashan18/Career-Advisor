import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from open_ai_chatbot import extract_career_info
import datetime
import pandas as pd

# ==================== Job Matching Data ====================
def match_jobs(location):
    job_data = {
        "bangalore": [
            {"title": "AI Developer - Google", "lat": 12.9716, "lon": 77.5946},
            {"title": "Data Analyst - Infosys", "lat": 12.9750, "lon": 77.6050}
        ],
        "delhi": [
            {"title": "ML Intern - Microsoft", "lat": 28.6139, "lon": 77.2090}
        ],
        "remote": [
            {"title": "Prompt Engineer - OpenAI", "lat": 0.0, "lon": 0.0}
        ]
    }
    return job_data.get(location.lower(), [])

# ==================== Salary Data ====================
salary_data = {
    "ai developer": "₹8–15 LPA",
    "data analyst": "₹5–8 LPA",
    "full stack developer": "₹6–12 LPA",
    "prompt engineer": "₹10–18 LPA"
}

# ==================== Firebase Init ====================
if not firebase_admin._apps:
    # yeh secrets Streamlit Cloud ke secrets.toml me rakha hoga
    firebase_config = st.secrets["firebase"]  
    
    # dict ko directly Certificate me pass kar sakte hain
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# ==================== UI Header ====================
st.markdown("## 💼 Career & Skills Advisor – AI Powered Job Finder")

# ==================== User Input ====================
user_input = st.text_area(
    "✍️ Tell us about your career goals!\n\nExample: I am a Python developer with prompt engineering skills, aiming to become an AI Developer. I have internship experience in backend development and prefer remote or Bangalore-based opportunities.",
    placeholder="Describe your skills, career goal, experience level, and preferred job location here...",
    key="unique_input"
)

# ==================== Submit Button ====================
if st.button("Submit", key="submit_button"):
    if user_input.strip() != "":
        # Save raw input
        doc_ref = db.collection("career_profiles").document()
        doc_ref.set({
            "description": user_input,
            "timestamp": datetime.datetime.now()
        })

        try:
            # Extract AI structured career info
            career_info = extract_career_info(user_input)
            doc_ref.update({"structured_data": career_info})

            location = career_info.get("preferred_location", "").strip()
            career_goal = career_info.get("career_goal", "").lower()
            skills = career_info.get("skills", [])

            # ===== 1. Show Matching Jobs =====
            matched_jobs = match_jobs(location)
            if matched_jobs:
                st.success("✅ Found nearby jobs & internships:")
                for job in matched_jobs:
                    st.write(f"- **{job['title']}**")

                st.markdown("### 📍 Nearby Jobs & Internships on Map")
                job_df = pd.DataFrame(matched_jobs)
                job_df = job_df.rename(columns={"lat": "latitude", "lon": "longitude"})
                st.map(job_df)
            else:
                st.warning("❌ No jobs or internships found for this location.")

            # ===== 2. AI Career Growth Roadmap =====
            st.markdown("### 🚀 Your AI-Generated Career Roadmap")
            roadmap_steps = [
                "Complete advanced training in your core skills",
                "Build 2–3 portfolio projects",
                "Network on LinkedIn and attend meetups",
                "Apply to 10+ targeted job opportunities",
                "Prepare for interviews with mock tests"
            ]
            for step in roadmap_steps:
                st.write(f"✅ {step}")

            # ===== 3. Skills Gap Analysis =====
            st.markdown("### 📊 Skills Gap Analysis")
            required_skills = {
                "ai developer": ["Python", "Machine Learning", "Deep Learning", "Docker"],
                "data analyst": ["SQL", "Excel", "Power BI", "Data Visualization"],
                "full stack developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
                "prompt engineer": ["Prompt Engineering", "LLM APIs", "Python", "LangChain"]
            }
            if career_goal in required_skills:
                missing_skills = [s for s in required_skills[career_goal] if s not in skills]
                if missing_skills:
                    st.write("You need to work on:")
                    for ms in missing_skills:
                        st.write(f"- {ms}")
                else:
                    st.write("🎯 You already have all the key skills for this role!")

            # ===== 4. Salary Insights =====
            st.markdown("### 💰 Salary Insights")
            if career_goal in salary_data:
                st.write(f"Average Salary for **{career_goal.title()}** in India: {salary_data[career_goal]}")
            else:
                st.write("No salary data available for this role yet.")

            # ===== 5. AI Quick Tips =====
            st.markdown("### 💡 Quick Career Tips")
            quick_tips = [
                "Showcase your projects on GitHub",
                "Write LinkedIn posts about your learning journey",
                "Contribute to open-source related to your field"
            ]
            for tip in quick_tips:
                st.write(f"💡 {tip}")

            # ===== Show Extracted Info =====
            st.markdown("### 🤖 AI-Powered Career Info Extraction")
            st.json(career_info)

        except Exception as e:
            st.error(f" Error occurred: {e}")
    else:
        st.warning("⚠️ Please enter some input.")
