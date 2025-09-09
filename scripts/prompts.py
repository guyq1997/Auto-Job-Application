#!/usr/bin/env python3
"""
Prompt Templates for Job Application Automation
"""

from typing import Dict, List
from datetime import datetime, timedelta

class JobApplicationPrompts:
    """Prompt template class for job applications"""
    
    @staticmethod
    def get_navigation_prompt(job_url: str) -> str:
        """Create navigation instruction prompt"""
        return f"""
Your task is to help me to log in and confirm if the current page is the job application form.

# Task Description: Navigation
First, please navigate to this job link: {job_url}

Please follow these steps:

1. **Handle Login Requirements (Optional)**:
   - If login is required, use the provided Username and Password.
   - Click the login button and wait for successful login
   - If login is unsuccessful, please stop and report

2. **Confirm Arrival at Application Form**:
   - Confirm the page contains an application form (with input fields like name, email, etc.)
   
# Tools Usage Guidelines:
### CAPTCHA Recognition Tools:
**When to use**: Encountered CAPTCHA, verification codes, or security challenges
- **recognize_captcha**: For general CAPTCHA types
- **solve_hcaptcha_slider**: Specifically for hCaptcha slider puzzles


# Important Reminders:
- Do not fill in any information
- If you encounter captcha or other obstacles, please stop and report
"""
    
    @staticmethod
    def get_form_filling_prompt(personal_data: Dict, job_url: str) -> str:
        """Create form filling instruction prompt"""
        personal_info = personal_data.get("personal_info", {})
        work_experience = personal_data.get("work_experience", [])
        education = personal_data.get("education", [])
        
        # Build work experience information
        def format_work_experience(work_exp_list):
            if not work_exp_list:
                return ""
            
            experience_sections = []
            for i, job in enumerate(work_exp_list, 1):
                section = f"""
{i}. **{"Current Position" if job.get('end_date') == 'Present' else f"Position {i}"}:**
   - Company: {job.get('company', '')}
   - Position: {job.get('position', '')}
   - Employment Type: {job.get('employment_type', 'Full-time')}
   - Duration: {job.get('start_date', '')} – {job.get('end_date', 'Present')}
   - Location: {job.get('location', '')}"""
                
                # Add thesis topic if exists
                if job.get('thesis_topic'):
                    section += f"\n   - Thesis Topic: {job.get('thesis_topic')}"
                
                # Add objective if exists
                if job.get('objective'):
                    section += f"\n   - Objective: {job.get('objective')}"
                
                # Add key contributions
                if job.get('key_contributions'):
                    section += "\n   - Key Contributions:"
                    for contrib in job.get('key_contributions', []):
                        section += f"\n     * {contrib}"
                elif job.get('key_contribution'):  # Single contribution
                    section += f"\n   - Key Contribution: {job.get('key_contribution')}"
                
                # Add main works
                if job.get('main_works'):
                    section += "\n   - Main Works:"
                    for work in job.get('main_works', []):
                        section += f"\n     * {work}"
                
                # Add technologies
                if job.get('technologies'):
                    section += f"\n   - Technologies: {', '.join(job.get('technologies', []))}"
                
                experience_sections.append(section)
            
            return "\n".join(experience_sections)
        
        experience_text = format_work_experience(work_experience)
        
        # Build education background information
        def format_education_background(education_list):
            if not education_list:
                return ""
            
            education_sections = []
            for edu in education_list:
                # Determine degree type for better formatting
                degree_type = "Master's Degree" if "Master" in edu.get('degree', '') else "Bachelor's Degree"
                
                section = f"""
- {degree_type}:
  - Institution: "{edu.get('institution', '')}"
  - Degree: "{edu.get('degree', '')}"
  - Field of Study: "{edu.get('field_of_study', '')}"
  - Start Date: "{edu.get('start_date', '')}"
  - End Date: "{edu.get('end_date', '')}"
  - GPA: "{edu.get('gpa', '')}"
"""
                education_sections.append(section)
            
            return "".join(education_sections)
        
        education_text = format_education_background(education)
        
        return f"""
Go To: {job_url}

THEN I need you to help me fill out the form, upload files and submit.

# Task Description: Form Filling
Your task is to fill out the job application form, upload files and submit. I have navigated to the application form page, now I need you to help me fill in all necessary information.

## Available Tools and When to Use Them:

### CAPTCHA Recognition Tools:
**When to use**: Encountered CAPTCHA, verification codes, or security challenges
- **recognize_captcha**: For general CAPTCHA types
- **solve_hcaptcha_slider**: Specifically for hCaptcha slider puzzles

**My Personal Information**

- Anrede: {personal_info.get('Anrede', '')}
- Titel: {personal_info.get('Titel', '')}
- Anredetitel: {personal_info.get('Anredetitel', '')}
- Gender: {personal_info.get('Gender', '')}
- Last Name: {personal_info.get('last_name', '')}
- First Name: {personal_info.get('first_name', '')}
- Date of Birth: {personal_info.get('birth_date', '')}
- Email: {personal_info.get('email', '')}
- Mobile: {personal_info.get('phone', '')}
- Address: {personal_info.get('address', '')}
- LinkedIn: {personal_info.get('linkedin_profile', '')}
- GitHub: {personal_info.get('github_profile', '')}
- Nationality: {personal_info.get('nationality', '')}
- Notice Period: {personal_info.get('notice_period', '')}
- Earliest Start Date: {(datetime.now() + timedelta(weeks=3)).strftime('%Y-%m-%d') + " (While filling the date, use the click_element_by_index tool to click the date picker and select the date. Only use input_text tool if you can not find the date picker!!!)"}
- Expected Salary: {personal_info.get('expected_salary', '')}
- Expected Work Location: {personal_info.get('expected_location', '')}
- Expected Work Type: {personal_info.get('expected_work_type', '')}
- Travel Willingness: {personal_info.get('travel_willingness', '')}
- Driving License: {personal_info.get('driving_license', '')}
- Presence Requirement: {personal_info.get('presence_requirement', '')}
- My Skills: {personal_info.get('skills', '')}
- Languages: {personal_info.get('languages', '')}
- Höchster Schulabschluss: {personal_info.get('highest_school_degree', '')}
- Höchster Bildungsniveau: {personal_info.get('highest_education_level', '')}
- Arbeitserlaubnis: {personal_info.get('work_permit', '')}

**Education Background:**
{education_text}

**Work Experience:**
{experience_text}


**Document File Paths:**
- Resume: {personal_data.get('documents', [])[0].get('file_path', '') if len(personal_data.get('documents', [])) > 0 else ''}
- Cover Letter: {personal_data.get('documents', [])[1].get('file_path', '') if len(personal_data.get('documents', [])) > 1 else ''}
- Master's Degree Certificate: {personal_data.get('documents', [])[2].get('file_path', '') if len(personal_data.get('documents', [])) > 2 else ''}
- Master's Transcript: {personal_data.get('documents', [])[3].get('file_path', '') if len(personal_data.get('documents', [])) > 3 else ''}
- Bachelor's Degree Certificate: {personal_data.get('documents', [])[4].get('file_path', '') if len(personal_data.get('documents', [])) > 4 else ''}
- German C1 Certificate: {personal_data.get('documents', [])[5].get('file_path', '') if len(personal_data.get('documents', [])) > 5 else ''}
If there are restrictions on the number or size of document uploads, please do not upload the master's transcript.

**Additional Information the Platform May Require:**

- Where did you see this position: {personal_info.get('source', '')}
- Data Privacy Declaration: I agree to the data privacy declaration
- only agree to the necessary terms and conditions, which must be agreed. ( often marked with "*")

For other open-ended questions (such as "Why do you want to join our company"), provide brief answers according to the information provided.

## How to Fill Out the Form
Next, please fill out the form according to the form prompts, upload materials and submit the application form.

- Carefully read the requirements and labels for each field
- You must fill in fields marked as required (*)
- For uncertain fields, you can skip them or choose the most appropriate option
- If you encounter captcha or other verification steps, please use the CAPTCHA tool
- Do not subscribe to any email
- Finally click the submit button
- If an error occurs, you should see the error message, go back and correct it.

# Important Notice
- You should submit the application by yourself, you should not stop and report.
- Always choose apply manually, do not apply with LinkedIn or other job platforms.
- Do not apply with LinkedIn or other job platforms!!!
- While filling the date, use the click_element_by_index tool to click the date picker and select the date. Only use input_text tool if you can not find the date picker!!!
- You must agree to the necessary terms and conditions, which must be agreed. (often marked with "*")
"""
