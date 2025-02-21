# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Configure Gemini API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# class PromptEngine:
#     @staticmethod
#     def generate_job_description(title, skills, location):
#         """
#         Generate a job description using Gemini.
#         """
#         prompt = f"""
#         You are a hiring assistant. Help write a compelling job description for the following role:
#         - Job Title: {title}
#         - Required Skills: {skills}
#         - Location: {location}

#         Provide a detailed job description that includes:
#         1. A brief introduction about the company (use placeholders if needed).
#         2. Key responsibilities.
#         3. Required qualifications and skills.
#         4. Preferred qualifications (if any).
#         5. Benefits and perks.
#         """
#         model = genai.GenerativeModel('gemini-pro')
#         response = model.generate_content(prompt)
#         # return response.text

#     @staticmethod
#     def generate_resume_feedback(resume_text):
#         """
#         Generate feedback for a resume using Gemini.
#         """
#         prompt = f"""
#         You are a career coach. Provide feedback on the following resume:
#         {resume_text}

#         Focus on:
#         1. Formatting and structure.
#         2. Grammar and spelling.
#         3. Highlighting key achievements.
#         4. Tailoring the resume for specific job roles.
#         """
#         model = genai.GenerativeModel('gemini-pro')
#         response = model.generate_content(prompt)
#         # return response.text

#     @staticmethod
#     def generate_issue_response(issue_description):
#         """
#         Generate a response to a user-reported issue using Gemini.
#         """
#         prompt = f"""
#         You are a support assistant. Respond to the following user issue:
#         {issue_description}

#         Provide a professional and helpful response that:
#         1. Acknowledges the issue.
#         2. Offers a solution or next steps.
#         3. Assures the user that their concern is being addressed.
#         """
#         model = genai.GenerativeModel('gemini-pro')
#         response = model.generate_content(prompt)
#         return response.text