from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime
import random

# Simulated database for demonstration purposes
# In a real implementation, these would be API calls to backend systems
class HRDatabase:
    def __init__(self):
        # Sample employee data
        self.employees = {
            "EMP001": {
                "name": "Sarah Johnson",
                "department": "Engineering",
                "manager": "Alex Chen",
                "leave_balance": {
                    "annual": 15,
                    "sick": 10,
                    "personal": 3
                },
                "onboarding": {
                    "progress": ["Welcome email received", "IT accounts created"],
                    "pending": ["Complete tax forms", "Enroll in benefits", "Complete security training"]
                }
            },
            "EMP002": {
                "name": "Michael Brown",
                "department": "Marketing",
                "manager": "Jennifer Lee",
                "leave_balance": {
                    "annual": 12,
                    "sick": 7,
                    "personal": 2
                },
                "onboarding": {
                    "progress": ["All tasks completed"],
                    "pending": []
                }
            }
        }
        
        # Sample policies database
        self.policies = {
            "remote work": "Employees may work remotely up to 3 days per week with manager approval. Remote work requests should be submitted at least 48 hours in advance through the HR portal.",
            "sick leave": "Full-time employees receive 10 paid sick days annually, accrued at a rate of 0.83 days per month. Up to 5 unused sick days may roll over to the following year.",
            "annual leave": "Full-time employees receive 15 paid annual leave days per year, accrued at a rate of 1.25 days per month. Unused annual leave may roll over with a maximum cap of 30 days.",
            "benefits": "Full-time employees are eligible for health insurance (medical, dental, vision), 401(k) with 4% company match, life insurance, and wellness program. Enrollment must be completed within 30 days of start date.",
            "expense": "Expenses must be submitted within 30 days of incurring them. Receipts are required for all expenses over $25. Manager approval is needed for expenses over $100."
        }
        
        # Sample job openings
        self.job_openings = [
            {
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "location": "New York",
                "requirements": "5+ years experience in software development, expertise in Python and JavaScript",
                "deadline": "April 30, 2025"
            },
            {
                "title": "Marketing Specialist",
                "department": "Marketing",
                "location": "Remote",
                "requirements": "3+ years of digital marketing experience, SEO knowledge",
                "deadline": "May 15, 2025"
            },
            {
                "title": "HR Coordinator",
                "department": "Human Resources",
                "location": "Chicago",
                "requirements": "2+ years of HR experience, proficiency in HR systems",
                "deadline": "April 20, 2025"
            }
        ]
        
        # Required documents by role and location
        self.required_documents = {
            "Software Developer": {
                "India": ["ID proof (Aadhaar or passport)", "Address proof", "PAN card", "Previous employment certificate", "Educational certificates"],
                "USA": ["Government-issued ID", "Social Security Number", "I-9 documentation", "Educational certificates"]
            },
            "Marketing Specialist": {
                "India": ["ID proof (Aadhaar or passport)", "Address proof", "PAN card", "Portfolio", "Previous employment certificate"],
                "USA": ["Government-issued ID", "Social Security Number", "I-9 documentation", "Portfolio"]
            }
        }

    def get_employee(self, employee_id):
        return self.employees.get(employee_id, None)

    def get_leave_balance(self, employee_id):
        employee = self.get_employee(employee_id)
        if employee:
            return employee["leave_balance"]
        return None

    def submit_leave_request(self, employee_id, leave_type, start_date, end_date, reason):
        # In a real implementation, this would update a database or call an API
        return {
            "status": "submitted",
            "leave_id": f"LR{random.randint(1000, 9999)}",
            "approval_status": "pending"
        }

    def get_onboarding_status(self, employee_id):
        employee = self.get_employee(employee_id)
        if employee:
            return employee["onboarding"]
        return None

    def update_onboarding_task(self, employee_id, task):
        employee = self.get_employee(employee_id)
        if employee and task in employee["onboarding"]["pending"]:
            employee["onboarding"]["pending"].remove(task)
            employee["onboarding"]["progress"].append(task)
            return True
        return False

    def get_policy(self, policy_topic):
        # Simplified policy lookup - in a real RAG implementation, 
        # this would use vector search against policy documents
        for key, value in self.policies.items():
            if policy_topic and policy_topic.lower() in key:
                return value
        return "I couldn't find specific information on that policy. Please contact HR for more details."

    def search_jobs(self, title=None, department=None, location=None):
        results = []
        for job in self.job_openings:
            match = True
            if title and title.lower() not in job["title"].lower():
                match = False
            if department and department.lower() not in job["department"].lower():
                match = False
            if location and location.lower() not in job["location"].lower():
                match = False
            
            if match:
                results.append(job)
        
        return results

# Initialize the simulated database
hr_db = HRDatabase()

class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_name = tracker.get_slot("user_name")
        
        if user_name:
            dispatcher.utter_message(text=f"Hello {user_name}!")
        else:
            dispatcher.utter_message(text=f"Welcome to HR Connect!")
        
        return []


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, FollowupAction

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Initialize the session
        events = [SessionStarted()]

        employee_id = tracker.get_slot("employee_id")
        
        if employee_id:
            employee = hr_db.get_employee(employee_id)
            if employee:
                events += [SlotSet("user_name", employee["name"]), 
                        SlotSet("department", employee["department"]),
                        SlotSet("manager", employee["manager"])]
        
        # Set initial slot values
        # events.append(SlotSet("user_name", "Sarah Johnson"))
        # events.append(SlotSet("employee_id", "EMP001"))
        # events.append(SlotSet("department", "EMP001"))
        
        # Optional: Send a welcome message
        dispatcher.utter_message(text="Welcome to HR Connect! 😊")
        
        # Trigger the greeting flow as followup action
        # events.append(FollowupAction("action_greet_user"))
        
        return events



class ActionGetLeaveBalance(Action):
    def name(self) -> Text:
        return "action_get_leave_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        
        if not employee_id:
            dispatcher.utter_message(text="I need your employee ID to check your leave balance. Could you please provide it?")
            return []
        
        leave_balance = hr_db.get_leave_balance(employee_id)
        
        if leave_balance:
            balance_text = f"Your current leave balances are:\n- Annual Leave: {leave_balance['annual']} days\n- Sick Leave: {leave_balance['sick']} days\n- Personal Leave: {leave_balance['personal']} days"
            dispatcher.utter_message(text=balance_text)
            return [SlotSet("leave_balance", balance_text)]
        else:
            dispatcher.utter_message(text="I couldn't find your leave balance information. Please contact HR for assistance.")
            
        return []

class ActionSubmitLeaveRequest(Action):
    def name(self) -> Text:
        return "action_submit_leave_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        leave_type = tracker.get_slot("leave_type")
        leave_start_date = tracker.get_slot("leave_start_date")
        leave_end_date = tracker.get_slot("leave_end_date")
        leave_reason = tracker.get_slot("leave_reason")
        
        if not all([employee_id, leave_type, leave_start_date, leave_end_date, leave_reason]):
            missing = []
            if not employee_id:
                missing.append("employee ID")
            if not leave_type:
                missing.append("leave type")
            if not leave_start_date:
                missing.append("start date")
            if not leave_end_date:
                missing.append("end date")
            if not leave_reason:
                missing.append("reason")
                
            dispatcher.utter_message(text=f"I need your {', '.join(missing)} to submit your leave request.")
            return []
        
        # Submit the leave request to the backend
        result = hr_db.submit_leave_request(employee_id, leave_type, leave_start_date, leave_end_date, leave_reason)
        
        if result["status"] == "submitted":
            return [SlotSet("leave_status", "pending")]
        else:
            dispatcher.utter_message(text="There was an issue submitting your leave request. Please try again later.")
            
        return []

class ActionGetPolicyInformation(Action):
    def name(self) -> Text:
        return "action_get_policy_information"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract the policy topic from the conversation
        last_message = tracker.latest_message.get("text", "")
        
        # In a real RAG implementation, this would:
        # 1. Convert the user query to embeddings
        # 2. Search a vector DB of policy documents
        # 3. Retrieve relevant passages
        # 4. Use an LLM to generate a response based on those passages
        
        # Simple keyword detection for demo
        policy_topics = ["remote work", "sick leave", "annual leave", "benefits", "expense"]
        detected_topic = None
        
        for topic in policy_topics:
            if topic in last_message.lower():
                detected_topic = topic
                break
        
        policy_answer = hr_db.get_policy(detected_topic if detected_topic else last_message)
        
        return [SlotSet("policy_answer", policy_answer)]

class ActionGetOnboardingStatus(Action):
    def name(self) -> Text:
        return "action_get_onboarding_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        
        if not employee_id:
            dispatcher.utter_message(text="I need your employee ID to check your onboarding status. Could you please provide it?")
            return []
        
        onboarding_status = hr_db.get_onboarding_status(employee_id)
        
        if onboarding_status:
            # Format the progress and pending tasks
            completed = ", ".join(onboarding_status["progress"])
            pending = ", ".join(onboarding_status["pending"])
            
            if pending:
                next_task = onboarding_status["pending"][0] if onboarding_status["pending"] else "All tasks completed"
                progress_text = f"Completed tasks: {completed}\nPending tasks: {pending}\nNext task to focus on: {next_task}"
                return [
                    SlotSet("onboarding_progress", progress_text),
                    SlotSet("onboarding_next_task", next_task)
                ]
            else:
                progress_text = f"Congratulations! You have completed all onboarding tasks: {completed}"
                return [
                    SlotSet("onboarding_progress", progress_text),
                    SlotSet("onboarding_next_task", "All tasks completed")
                ]
        else:
            dispatcher.utter_message(text="I couldn't find your onboarding information. Please contact HR for assistance.")
            
        return []

class ActionUpdateOnboardingTask(Action):
    def name(self) -> Text:
        return "action_update_onboarding_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        task = tracker.get_slot("onboarding_next_task")
        
        if not employee_id or not task:
            dispatcher.utter_message(text="I need both your employee ID and the task you completed to update your progress.")
            return []
        
        # Update the task status
        success = hr_db.update_onboarding_task(employee_id, task)
        
        if success:
            dispatcher.utter_message(text=f"Great job! I've marked '{task}' as completed.")
            
            # Get the updated status to find the next task
            onboarding_status = hr_db.get_onboarding_status(employee_id)
            if onboarding_status and onboarding_status["pending"]:
                next_task = onboarding_status["pending"][0]
                dispatcher.utter_message(text=f"Your next task is: {next_task}")
                return [SlotSet("onboarding_next_task", next_task)]
            else:
                dispatcher.utter_message(text="Congratulations! You have completed all onboarding tasks.")
                return [SlotSet("onboarding_next_task", "All tasks completed")]
        else:
            dispatcher.utter_message(text=f"I couldn't update your task status. Please ensure you're providing the correct task name.")
            
        return []

class ActionGetBenefitsInformation(Action):
    def name(self) -> Text:
        return "action_get_benefits_information"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        selected_benefit = tracker.get_slot("selected_benefit")
        
        benefit_details = {
            "health insurance": "Our health insurance plans include three options (Basic, Standard, Premium) with varying coverage levels and premiums. All plans include medical, dental, and vision coverage with different deductibles and co-pays.",
            "401k": "Our 401(k) plan includes a 4% company match. You can contribute up to the annual IRS limit, and are fully vested in company contributions after 3 years of service.",
            "life insurance": "All full-time employees receive basic life insurance coverage equal to one year's salary at no cost. Additional voluntary coverage can be purchased for yourself and dependents.",
            "wellness program": "Our wellness program includes gym membership discounts, wellness challenges with rewards, and annual health screenings. Participation can earn you up to $500 in health insurance premium discounts."
        }
        
        if selected_benefit and selected_benefit.lower() in benefit_details:
            dispatcher.utter_message(text=benefit_details[selected_benefit.lower()])
        elif not selected_benefit:
            dispatcher.utter_message(text="Please select a specific benefit you'd like to learn more about, such as health insurance, 401(k), life insurance, or wellness program.")
        else:
            dispatcher.utter_message(text="I don't have specific information about that benefit. Please contact HR for more details.")
            
        return []

class ActionSubmitExpense(Action):
    def name(self) -> Text:
        return "action_submit_expense"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        expense_amount = tracker.get_slot("expense_amount")
        expense_category = tracker.get_slot("expense_category")
        expense_date = tracker.get_slot("expense_date")
        expense_description = tracker.get_slot("expense_description")
        
        if not all([employee_id, expense_amount, expense_category]):
            missing = []
            if not employee_id:
                missing.append("employee ID")
            if not expense_amount:
                missing.append("expense amount")
            if not expense_category:
                missing.append("expense category")
                
            dispatcher.utter_message(text=f"I need your {', '.join(missing)} to submit your expense claim.")
            return []
        
        # Determine if manager approval is needed (for expenses over $100)
        needs_approval = float(expense_amount) > 100
        
        if needs_approval:
            employee = hr_db.get_employee(employee_id)
            manager = employee["manager"] if employee else "your manager"
            dispatcher.utter_message(text=f"Your expense claim of ${expense_amount} for {expense_category} has been submitted. It requires approval from {manager}.")
        else:
            dispatcher.utter_message(text=f"Your expense claim of ${expense_amount} for {expense_category} has been successfully submitted and auto-approved.")
            
        return []

class ActionVerifyDocuments(Action):
    def name(self) -> Text:
        return "action_verify_documents"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        document_type = tracker.get_slot("document_type")
        
        if not document_type:
            dispatcher.utter_message(text="Please specify what type of document you're uploading.")
            return []
        
        # Simulate document verification
        dispatcher.utter_message(text=f"I've verified your {document_type}. The document appears to be in the correct format and is complete.")
        
        return [SlotSet("document_status", "verified")]

class ActionGetPayslip(Action):
    def name(self) -> Text:
        return "action_get_payslip"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        
        if not employee_id:
            dispatcher.utter_message(text="I need your employee ID to retrieve your payslip information. Could you please provide it?")
            return []
        
        # In a real implementation, this would securely retrieve payslip data from a payroll system
        employee = hr_db.get_employee(employee_id)
        if employee:
            current_month = datetime.datetime.now().strftime("%B %Y")
            dispatcher.utter_message(text=f"I've located your payslip for {current_month}. For security reasons, I can only provide limited information here. Your net pay has been transferred to your registered bank account. You can view your full payslip with all deductions and calculations by logging into the payroll portal at payroll.techcorp.com.")
        else:
            dispatcher.utter_message(text="I couldn't find your payslip information. Please contact HR or Payroll for assistance.")
            
        return []

class ActionSearchJobs(Action):
    def name(self) -> Text:
        return "action_search_jobs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        job_title = tracker.get_slot("job_title")
        job_location = tracker.get_slot("job_location")
        job_department = tracker.get_slot("job_department")
        
        # Search for matching jobs
        jobs = hr_db.search_jobs(job_title, job_department, job_location)
        
        if jobs:
            response = "I found the following job openings that match your criteria:\n\n"
            for job in jobs:
                response += f"**{job['title']}** - {job['department']}\n"
                response += f"Location: {job['location']}\n"
                response += f"Requirements: {job['requirements']}\n"
                response += f"Application Deadline: {job['deadline']}\n\n"
                
            response += "To apply, please visit careers.techcorp.com and search for these positions."
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="I couldn't find any job openings matching your criteria. Try broadening your search parameters or check back later as new positions are posted regularly.")
            
        return []

class ActionITSupport(Action):
    def name(self) -> Text:
        return "action_it_support"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the latest user message to determine what IT support is needed
        last_message = tracker.latest_message.get("text", "").lower()
        
        # Check for specific IT setup needs
        if "email" in last_message or "mail" in last_message:
            dispatcher.utter_message(text="To set up your email: 1) Visit portal.techcorp.com, 2) Use your employee ID as your username and the temporary password from your welcome email, 3) Follow the prompts to create a permanent password.")
        elif "vpn" in last_message:
            dispatcher.utter_message(text="To set up VPN access: 1) Download the TechCorp VPN client from it.techcorp.com/downloads, 2) Install the software, 3) Launch the application, 4) Log in with your email credentials, 5) Use the verification code sent to your registered mobile number.")
        elif "multi-factor" in last_message or "mfa" in last_message or "authentication" in last_message:
            dispatcher.utter_message(text="To set up multi-factor authentication: 1) Download the TechCorp Authenticator app from your device's app store, 2) Open the app and scan the QR code from portal.techcorp.com/mfa, 3) Enter the verification code on the portal to complete setup.")
        else:
            # Create a general IT support ticket
            dispatcher.utter_message(text="I've created an IT support ticket for your issue. An IT support specialist will contact you within 24 hours. Your ticket number is IT-" + str(random.randint(10000, 99999)) + ".")
            
        return []
