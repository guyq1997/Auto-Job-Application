#!/usr/bin/env python3
"""
Prompt Templates for Job Application Automation
"""

from typing import Dict, List


class JobApplicationPrompts:
    """Prompt template class for job applications"""
    
    @staticmethod
    def get_navigation_prompt(job_url: str) -> str:
        """Create navigation instruction prompt"""
        return f"""
Your task is to help me find and navigate to the job application form.

First, please navigate to this job link: {job_url}

Please follow these steps:

1. **Find the Apply Button**: 
   - Look for "Apply", "Apply Now", "申请", "Bewerben", "Jetzt bewerben" or similar application buttons
   - The button may be in different locations on the page, please look carefully
   - The button could be a link, button, or other clickable element

2. **Click the Apply Button**:
   - Click the apply button immediately after finding it
   - If there are multiple apply buttons, choose the most obvious or primary one

3. **Handle Possible Redirects**:
   - After clicking, you may be redirected to a new page or a new tab may open
   - If redirected to an external website (like company website), continue looking for the application form
   - If redirected to job platforms (like LinkedIn, Indeed, etc.), please continue as well

4. **Handle Login Requirements (Optional)**:
   - If login is required, find the username and password input fields and enter credentials
   - Click the login button and wait for successful login

5. **Confirm Arrival at Application Form**:
   - Confirm the page contains an application form (with input fields like name, email, etc.)
   - If it's just a job description page, continue looking for application methods
   - The form may include personal information, resume upload, cover letter fields, etc.

Important Reminders:
- Only handle navigation and finding the form, do not fill in any information
- If you encounter captcha or other obstacles, please stop and report
- Focus on finding the actual job application form, not simple "contact us" forms
- If the page has multiple application options, choose the most direct manual application method (manually apply)
"""
    
    @staticmethod
    def get_form_filling_prompt(job_data: Dict, personal_data: Dict) -> str:
        """Create form filling instruction prompt"""
        personal_info = personal_data.get("personal_info", {})
        work_experience = personal_data.get("work_experience", [])
        education = personal_data.get("education", [])
        
        # Build work experience information
        experience_text = ""
        if work_experience:
            current_job = work_experience[0]  # Assume the first one is the latest job
            experience_text = f"""
Current Work Experience:
- Company: {current_job.get('company', '')}
- Position: {current_job.get('position', '')}
- Start Date: {current_job.get('start_date', '')}
- End Date: {current_job.get('end_date', 'Present')}
- Location: {current_job.get('location', '')}
- Key Skills: {', '.join(current_job.get('technologies', []))}
"""
        
        # Build education background information
        education_text = ""
        if education:
            latest_education = education[0]  # Assume the first one is the highest degree
            education_text = f"""
Education Background:
- Institution: {latest_education.get('institution', '')}
- Degree: {latest_education.get('degree', '')}
- Field of Study: {latest_education.get('field_of_study', '')}
- Graduation Date: {latest_education.get('end_date', '')}
- GPA: {latest_education.get('gpa', '')}
"""
        
        return f"""
You have completed the navigation task, now I need you to help me fill out the form, upload files and submit.

# Task Description
Your task is to fill out the job application form, upload files and submit. I have navigated to the application form page, now I need you to help me fill in all necessary information.

# Required Information
Below I will provide you with all the information needed to fill out the form, please fill out the form according to this information.

**My Personal Information**

- Last Name: {personal_info.get('name', '')}
- First Name: {personal_info.get('name', '')}
- Date of Birth: {personal_info.get('birth_date', '')}
- Email: {personal_info.get('email', '')}
- Phone: {personal_info.get('phone', '')}
- Address: {personal_info.get('address', '')}
- LinkedIn: {personal_info.get('linkedin_profile', '')}
- GitHub: {personal_info.get('github_profile', '')}
- Nationality: {personal_info.get('nationality', '')}
- Notice Period: {personal_info.get('notice_period', '')}
- Expected Salary: {personal_info.get('expected_salary', '')}
- Expected Work Location: {personal_info.get('expected_location', '')}
- Expected Work Type: {personal_info.get('expected_work_type', '')}
- My Skills: {personal_info.get('skills', '')}

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
- Why did you choose this position: {personal_info.get('reason', '')}

For other open-ended questions (such as "Why do you want to join our company"), provide brief professional answers.

# How to Fill Out the Form

Next, please fill out the form according to the form prompts, upload materials and submit the application form.

- Carefully read the requirements and labels for each field
- Prioritize filling in fields marked as required (*)
- For uncertain fields, you can skip them or choose the most appropriate option
- If you encounter captcha or other verification steps, please stop and report
- Ensure information accuracy
- If the form has multiple steps/pages, complete them step by step
- If there are confirmation boxes or terms agreements, please check them (such as: data protection statements, etc.)
- Do not subscribe to any emails
- Finally click the submit button

"""


class PromptTemplates:
    """General prompt template class"""
    
    @staticmethod
    def get_error_handling_prompt() -> str:
        """Get error handling prompt"""
        return """
If you encounter the following situations during execution, please stop the operation and report:

1. **Login Requirements**: Page requires login or registration
2. **Captcha**: Image captcha or other verification steps appear
3. **Page Errors**: 404, 500 or other error pages
4. **Network Issues**: Page loading failure or timeout
5. **Permission Issues**: Access denied or special permissions required
6. **Technical Issues**: JavaScript errors or page functionality problems

Please describe the encountered problems in detail for manual intervention.
"""
    
    @staticmethod
    def get_success_criteria_prompt() -> str:
        """获取成功标准提示"""
        return """
任务成功的标准:

1. **导航成功**: 成功找到并点击申请按钮，到达申请表单页面
2. **表单识别**: 正确识别表单字段和必填项
3. **信息填写**: 准确填写所有可填写的字段
4. **提交完成**: 成功提交表单并收到确认信息

如果无法满足以上任一标准，请报告具体原因。
"""
