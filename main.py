import streamlit as st
import PyPDF2
import requests
import json

# Set page configuration
st.set_page_config(page_title="Resume Analyzer", layout="wide")

# Add title and description
st.title("Resume Analysis Tool")
st.write("Upload your resume and enter the job description to get personalized analysis and recommendations.")

# Create two columns for inputs
col1, col2 = st.columns(2)

# Resume upload section
with col1:
    st.subheader("Upload Resume")
    resume_file = st.file_uploader("Upload your resume (PDF format)", type=['pdf'])
    
# Job description section
with col2:
    st.subheader("Job Description")
    job_description = st.text_area("Paste the job description here", height=200)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to call Groq API
def analyze_resume(resume_text, job_desc):
    import groq
    
    # Initialize Groq client
    client = groq.Groq(
        api_key=os.environ["GROQ_API_KEY"]
    )
    
    prompt = f"""
    Analyze the following resume against the job description:
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_desc}
    
    Please provide:
    1. Key strengths matching the job requirements
    2. Areas of improvement or missing skills
    3. Specific suggestions to improve the resume
    """
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        response_text = completion.choices[0].message.content
        return {
            "strengths": response_text.split("1.")[1].split("2.")[0].strip(),
            "weaknesses": response_text.split("2.")[1].split("3.")[0].strip(),
            "suggestions": response_text.split("3.")[1].strip()
        }
    except Exception as e:
        return str(e)

# Create analyze button
if st.button("Analyze Resume"):
    if resume_file is not None and job_description:
        with st.spinner("Analyzing your resume..."):
            # Extract text from resume
            resume_text = extract_text_from_pdf(resume_file)
            
            # Get analysis from API
            analysis = analyze_resume(resume_text, job_description)
            
            # Display results
            st.subheader("Analysis Results")
            
            # Create three columns for results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🎯 Key Strengths")
                st.write(analysis.get("strengths", "No strengths found"))
                
            with col2:
                st.markdown("### 🎯 Areas for Improvement")
                st.write(analysis.get("weaknesses", "No areas of improvement found"))
                
            with col3:
                st.markdown("### 💡 Suggestions")
                st.write(analysis.get("suggestions", "No suggestions available"))
                
    else:
        st.error("Please upload a resume and enter a job description to proceed.")

# Add footer
st.markdown("---")
st.markdown("### How to use this tool")
st.write("""
1. Upload your resume in PDF format
2. Paste the job description you're interested in
3. Click 'Analyze Resume' to get personalized insights
4. Review the analysis to improve your application
""")
