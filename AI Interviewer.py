import os
import random
from streamlit_option_menu import option_menu
import google.generativeai as genai
import PyPDF2
import pandas as pd
import hashlib
import json
from datetime import datetime
import re
import streamlit as st



# Configure Google Gemini AI
os.environ["API_KEY"] = 'AIzaSyBdj4P28uwm9oOHLYRBAzEF7k4I1r3zh3s'
genai.configure(api_key=os.environ["API_KEY"])

# User authentication functions
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def validate_user_input(input_text, input_type):
    """Validate user input with specific rules"""
    if not input_text.strip():
        return False, f"{input_type} cannot be empty"
    
    if ' ' in input_text:
        return False, f"{input_type} cannot contain spaces"
    
    if input_type == "Username" and len(input_text) < 3:
        return False, "Username must be at least 3 characters long"
    
    if input_type == "Password" and len(input_text) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, "Input validated successfully"

def handle_user_authentication(username, password, action):
    """Handle user authentication with enhanced security"""
    try:
        users = load_users()
        
        if action == "login":
            if username not in users:
                return False, "Username not found"
            
            if users[username]['password'] != password:
                return False, "Incorrect password"
            
            return True, "Login successful"
        
        elif action == "register":
            if username in users:
                return False, "Username already exists"
            
            users[username] = {
                'password': password,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': None,
                'interview_history': []
            }
            
            save_users(users)
            return True, "Account created successfully"
        
        return False, "Invalid action"
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Show login page if not logged in
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .login-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 2rem auto;
        max-width: 500px;
    }
    .login-title {
        color: #2c3e50;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .login-subtitle {
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-title">🎯 AI Interviewer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Your personal interview preparation assistant</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.subheader("Welcome Back!")
        login_username = st.text_input("Username", placeholder="Enter your username", help="No spaces allowed", key="login_username")
        login_password = st.text_input("Password", type="password", placeholder="Enter your password", help="No spaces allowed", key="login_password")
        
        if st.button("Login", key="login_btn"):
            success, message = handle_user_authentication(login_username, login_password, "login")
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username", placeholder="Create a username", help="No spaces allowed, minimum 3 characters", key="new_username")
        new_password = st.text_input("Choose Password", type="password", placeholder="Create a password", help="No spaces allowed, minimum 6 characters", key="new_password")
        
        if st.button("Create Account", key="register_btn"):
            success, message = handle_user_authentication(new_username, new_password, "register")
            if success:
                st.success(message)
            else:
                st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# If logged in, show the main application
if st.session_state.logged_in:
    st.sidebar.write(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# CSS Styling
st.markdown("""
<style>
.st-emotion-cache-1jicfl2 { padding-top: 2rem !important; }
body { background-color: #333; }
.main { background-color: #111; }
.sidebar .sidebar-content { background-color: #333333; color: white; }
.sidebar .sidebar-content a { color: #61dafb; }
.button-style {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    display: inline-block;
    font-size: 16px;
    margin: 10px 2px;
    cursor: pointer;
    border-radius: 8px;
}
.title-style {
    font-size: 36px;
    color: #4CAF50;
    text-align: center;
    font-weight: bold;
}
.subtitle-style {
    font-size: 24px;
    color: #f5f5f5;
    text-align: center;
    margin-bottom: 20px;
}
.circular-button {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 10px;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background-color: white;
    text-align: center;
    line-height: 150px;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
    border: 2px solid #4CAF50;
}
.flex-container {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
}
</style>
""", unsafe_allow_html=True)

# Feature Functions
def login_access():
    st.write("Login feature is under development.")

def navigation_buttons(current_question, total_questions):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", disabled=(current_question == 0)):
            return current_question - 1
    with col2:
        if st.button("Next", disabled=(current_question == total_questions - 1)):
            return current_question + 1
    return current_question

def progress_tracking(current_question, total_questions):
    st.progress((current_question + 1) / total_questions)

def question_timer():
    st.write("Timer feature is under development.")

def bookmark_question(bookmarked_questions, current_question):
    if st.button("Bookmark Question"):
        bookmarked_questions.add(current_question)
    return bookmarked_questions

def feedback_system():
    feedback = st.text_area("Provide your feedback:")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

def leaderboard():
    st.write("Leaderboard feature is under development.")

def question_categories(categories):
    selected_category = st.selectbox("Select a category:", categories)
    return selected_category

def detailed_analytics():
    st.write("Analytics feature is under development.")

def custom_question_sets():
    st.write("Custom question sets feature is under development.")

# Utility Functions
def generate_ai_response(prompt, model_name='gemini-1.5-flash-latest'):
    """Generic function to generate AI responses"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):
            st.error("API quota exceeded. Please try again later or check your API usage.")
        else:
            st.error(f"Error generating response: {e}")
        return "Error generating response. Please try again."

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return " ".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text(file):
    """Extract text from uploaded file"""
    if file is None:
        return ""
    
    file_type = file.type.lower()
    if "pdf" in file_type:
        return extract_text_from_pdf(file)
    elif "plain" in file_type:
        return file.getvalue().decode("utf-8")
    else:
        st.error("Unsupported file type. Please upload a PDF or TXT file.")
        return ""

def evaluate_answer(user_answer, ideal_answer=""):
    """Evaluate user's answer"""
    if not user_answer.strip():
        return 0
    
    # Check answer length - penalize very long answers
    answer_length = len(user_answer.split())
    if answer_length > 100:  # If answer is too long
        return 5  # Base score for long answers
    
    if ideal_answer:
        # Use ideal answer comparison if available
        # Normalize both answers to lowercase and remove extra spaces
        user_words = set(user_answer.lower().split())
        ideal_words = set(ideal_answer.lower().split())
        
        # Calculate word overlap
        overlap = len(user_words.intersection(ideal_words))
        total_unique_words = len(ideal_words)
        
        # Base score on word overlap
        score = (overlap / total_unique_words) * 10
        
        # Bonus for conciseness (shorter answers get a small bonus)
        if answer_length < 50:
            score += 1
            
        return round(min(10, score), 2)
    else:
        # Use key terms evaluation if no ideal answer
        score = min(10, len(user_answer.split()) / 20)
        key_terms = ['experience', 'project', 'team', 'solution', 'challenge', 'success', 'learn', 'improve']
        score += sum(2 for term in key_terms if term.lower() in user_answer.lower())
        return min(10, score)

def load_questions(company):
    """Load and select random questions based on company and difficulty levels."""
    try:
        if company == "TCS":
            file_path = "tcs1.csv"
            question_col = "Question"
        elif company == "Amazon":
            file_path = "amazon1.csv"
            question_col = "Question"
        elif company == "Accenture":
            file_path = "acc.csv"
            question_col = "questions"
        elif company == "Microsoft":
            file_path = "micro.csv"
            question_col = "Question"
        else:
            st.error(f"Unknown company: {company}")
            return None, None
            
        # Load the CSV file
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            st.error(f"Error reading {file_path}: {str(e)}")
            return None, None
            
        # Check if the question column exists
        if question_col not in df.columns:
            st.error(f"Column '{question_col}' not found in {file_path}. Available columns: {', '.join(df.columns)}")
            return None, None
            
        # Extract difficulty and clean question text
        try:
            df['difficulty'] = df[question_col].str.extract(r'\((.*?)\)$', expand=False)
            df['question'] = df[question_col].str.replace(r'\(.*?\)$', '', regex=True)
        except Exception as e:
            st.error(f"Error extracting difficulty from questions: {str(e)}")
            return None, None
        
        # Clean and standardize difficulty values
        df['difficulty'] = df['difficulty'].str.lower().str.strip()
        
        # Handle empty difficulty values
        empty_difficulty = df['difficulty'].isna().sum()
        if empty_difficulty > 0:
            st.warning(f"Found {empty_difficulty} questions without difficulty level in {company} file. These will be excluded.")
        
        # Remove any empty rows and reset index
        df = df.dropna(subset=['question', 'difficulty']).reset_index(drop=True)
        
        # Count questions by difficulty
        difficulty_counts = df['difficulty'].value_counts()
        st.info(f"Found questions by difficulty in {company} file:\n" + 
                "\n".join([f"{diff}: {count}" for diff, count in difficulty_counts.items()]))
        
        try:
            # Get questions by difficulty
            low_questions = df[df['difficulty'] == 'low']
            medium_questions = df[df['difficulty'] == 'medium']
            high_questions = df[df['difficulty'] == 'high']
            
            # Check if we have enough questions of each difficulty
            required = {'low': 3, 'medium': 4, 'high': 3}
            for difficulty, required_count in required.items():
                actual_count = len(df[df['difficulty'] == difficulty])
                if actual_count < required_count:
                    st.error(f"Not enough {difficulty} difficulty questions in {company} file.\n" +
                            f"Found: {actual_count}, Required: {required_count}\n" +
                            f"Please make sure questions have proper difficulty markers like (low), (medium), or (high)")
                    return None, None
            
            # Generate random seed based on current timestamp
            current_seed = int(datetime.now().timestamp())
            
            # Select random questions for each difficulty using the current timestamp as seed
            selected_low = low_questions.sample(n=3, random_state=current_seed)
            selected_medium = medium_questions.sample(n=4, random_state=current_seed)
            selected_high = high_questions.sample(n=3, random_state=current_seed)
            
            # Combine questions in specific order: low -> medium -> high
            selected_questions = pd.concat([
                selected_low,      # 3 low difficulty questions
                selected_medium,   # 4 medium difficulty questions
                selected_high      # 3 high difficulty questions
            ]).reset_index(drop=True)
            
            # Verify we have exactly 10 questions
            if len(selected_questions) != 10:
                st.error(f"Error: Selected {len(selected_questions)} questions instead of 10.")
                return None, None
            
            return selected_questions, 'question'
            
        except Exception as e:
            st.error(f"Error selecting questions: {str(e)}")
            return None, None
        
    except Exception as e:
        st.error(f"Error loading questions for {company}: {str(e)}")
        return None, None

def create_sample_questions():
    """Create a DataFrame with sample questions when the main questions can't be loaded."""
    sample_questions = [
        # Low difficulty questions
        {
            'question': 'Tell me about your understanding of Accenture and its services.',
            'difficulty': 'low'
        },
        {
            'question': 'What interests you about working at Accenture?',
            'difficulty': 'low'
        },
        {
            'question': 'How do you stay updated with current technology trends?',
            'difficulty': 'low'
        },
        
        # Medium difficulty questions
        {
            'question': 'Describe a challenging project you worked on and how you handled it.',
            'difficulty': 'medium'
        },
        {
            'question': 'How do you handle working with diverse teams across different time zones?',
            'difficulty': 'medium'
        },
        {
            'question': 'What methodologies do you use for project management?',
            'difficulty': 'medium'
        },
        {
            'question': 'How do you ensure quality in your deliverables?',
            'difficulty': 'medium'
        },
        
        # High difficulty questions
        {
            'question': 'Describe a situation where you had to lead a complex technical implementation.',
            'difficulty': 'high'
        },
        {
            'question': 'How would you handle a project that is behind schedule and over budget?',
            'difficulty': 'high'
        },
        {
            'question': 'Explain how you would implement a digital transformation strategy for a client.',
            'difficulty': 'high'
        }
    ]
    
    return pd.DataFrame(sample_questions)

def generate_company_answer(question, company):
    """Generate an ideal answer for company-specific questions"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""Provide a concise, professional answer for this {company} interview question. 
        Keep it brief (2-3 sentences) and focused, considering {company}'s work culture and values:
        Question: {question}"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "Error generating answer. Please try again."

def generate_questions(question_type, context="", num_questions=5):
    """Generate questions based on type"""
    prompts = {
        'behavioral': [
            "Generate a behavioral question about problem-solving.",
            "Create a question about teamwork experience.",
            "Ask about handling workplace challenges.",
            "Generate a question about leadership experience.",
            "Ask about time management and prioritization."
        ],
        'professional': [
            "Generate a technical question about project challenges.",
            "Create a question about system design decisions.",
            "Ask about coding best practices.",
            "Generate a question about debugging approaches.",
            "Ask about technology adoption decisions."
        ],
        'resume': [
            f"Based on this resume:\n{context}\nGenerate a question about the candidate's experience.",
            f"Based on this resume:\n{context}\nAsk about a specific project mentioned.",
            f"Based on this resume:\n{context}\nQuestion about technical skills listed.",
            f"Based on this resume:\n{context}\nAsk about role responsibilities.",
            f"Based on this resume:\n{context}\nGenerate a question about achievements."
        ]
    }

    questions = []
    selected_prompts = prompts.get(question_type, prompts['behavioral'])
    for _ in range(num_questions):
        prompt = random.choice(selected_prompts)
        question = generate_ai_response(prompt)
        questions.append(question)
    return questions

def company_interview_screen():
    """Company-specific interview screen"""
    st.write("### Choose your company to start the interview:")
    
    # Initialize session state variables if not exists
    if 'company_questions' not in st.session_state:
        st.session_state.company_questions = None
    if 'company_current' not in st.session_state:
        st.session_state.company_current = 0
    if 'company_scores' not in st.session_state:
        st.session_state.company_scores = []
    if 'company_answers' not in st.session_state:
        st.session_state.company_answers = []
    if 'company_started' not in st.session_state:
        st.session_state.company_started = False

    # Company selection buttons in three columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("TCS Interview"):
            questions_df, column_name = load_questions("TCS")
            if questions_df is not None:
                st.session_state.company = "TCS"
                st.session_state.company_questions = questions_df
                st.session_state.column_name = column_name
                st.session_state.company_started = True
                st.session_state.company_current = 0
                st.session_state.company_scores = []
                st.session_state.company_answers = []
                st.session_state.show_question = True
    
    with col2:
        if st.button("Accenture Interview"):
            questions_df, column_name = load_questions("Accenture")
            if questions_df is not None:
                st.session_state.company = "Accenture"
                st.session_state.company_questions = questions_df
                st.session_state.column_name = column_name
                st.session_state.company_started = True
                st.session_state.company_current = 0
                st.session_state.company_scores = []
                st.session_state.company_answers = []
                st.session_state.show_question = True
    
    with col3:
        if st.button("Amazon Interview"):
            questions_df, column_name = load_questions("Amazon")
            if questions_df is not None:
                st.session_state.company = "Amazon"
                st.session_state.company_questions = questions_df
                st.session_state.column_name = column_name
                st.session_state.company_started = True
                st.session_state.company_current = 0
                st.session_state.company_scores = []
                st.session_state.company_answers = []
                st.session_state.show_question = True

    # Initialize show_question in session state if not exists
    if 'show_question' not in st.session_state:
        st.session_state.show_question = False

    if st.session_state.company_started and st.session_state.company_questions is not None and st.session_state.show_question:
        current_idx = st.session_state.company_current
        questions_df = st.session_state.company_questions
        
        # Display progress
        st.progress((current_idx + 1) / 10)
        st.write(f"Question {current_idx + 1} of 10")
        
        # Get current question and its difficulty
        current_question = questions_df.iloc[current_idx]
        difficulty = current_question['difficulty'].lower()
        
        # Display difficulty with color
        difficulty_color = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red'
        }
        st.markdown(f"**Difficulty:** <span style='color: {difficulty_color[difficulty]}'>{difficulty.upper()}</span>", 
                    unsafe_allow_html=True)
        
        # Display question
        st.write(f"**Question:** {current_question[st.session_state.column_name]}")
        
        # Answer input
        answer = st.text_area("Your Answer:", key=f"company_answer_{current_idx}", height=150)
        
        col1, col2, col3 = st.columns([1,2,1])
        
        with col1:
            if current_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.company_current -= 1
                    st.rerun()
        
        with col2:
            if st.button("Submit Answer"):
                if answer.strip():
                    with st.spinner("Evaluating..."):
                        ideal_answer = generate_company_answer(
                            current_question[st.session_state.column_name],
                            st.session_state.company
                        )
                        score = evaluate_answer(answer, ideal_answer)
                        
                        # Store results
                        st.session_state.company_scores.append(score)
                        st.session_state.company_answers.append(answer)
                        
                        # Show brief feedback
                        st.success(f"Score: {score}/10")
                        st.info(f"Quick tip: {ideal_answer[:100]}...")
                        
                        if len(st.session_state.company_scores) == 10:
                            show_company_final_results()
                        else:
                            st.session_state.company_current += 1
                else:
                    st.warning("Please provide an answer before submitting.")
        
        with col3:
            if current_idx < 9 and len(st.session_state.company_scores) > current_idx:
                if st.button("➡️ Next"):
                    st.session_state.company_current += 1
                    st.rerun()

def show_company_final_results():
    """Display final results for company interview"""
    st.balloons()
    
    total_score = sum(st.session_state.company_scores)
    avg_score = total_score / 10
    
    st.markdown("## 🎉 Interview Completed!")
    st.markdown(f"### Total Score: {total_score}/100")
    st.markdown(f"### Average Score: {avg_score:.1f}/10")
    
    # Generate medium-sized feedback
    feedback_prompt = f"""
    Provide a medium-sized feedback (about 150-200 words) for this {st.session_state.company} interview:
    Total Score: {total_score}/100
    
    Focus on:
    1. Overall performance for {st.session_state.company} specific questions
    2. Key strengths demonstrated (2-3 points)
    3. Areas for improvement (2-3 points)
    4. Quick tips for future {st.session_state.company} interviews
    """
    
    feedback = generate_ai_response(feedback_prompt)
    
    st.markdown("### 📝 Interview Feedback")
    st.write(feedback)
    
    if st.button("Start New Company Interview"):
        for key in list(st.session_state.keys()):
            if key.startswith('company_'):
                del st.session_state[key]
        st.rerun()

def interview_screen(interview_type):
    """Generic interview screen for behavioral and professional interviews"""
    st.markdown(f'<h1 class="title-style">{interview_type.title()} Interview</h1>', unsafe_allow_html=True)
    
    # Initialize session state variables
    if f'{interview_type}_started' not in st.session_state:
        st.session_state[f'{interview_type}_started'] = False
        st.session_state[f'{interview_type}_questions'] = []
        st.session_state[f'{interview_type}_current'] = 0
        st.session_state[f'{interview_type}_scores'] = []
        st.session_state[f'{interview_type}_answers'] = []
        st.session_state[f'{interview_type}_ideal_answers'] = []
        st.session_state[f'{interview_type}_show_evaluation'] = False

    # Start interview button
    if not st.session_state[f'{interview_type}_started']:
        st.write(f"Welcome to the {interview_type.title()} Interview! Click below to begin.")
        if st.button(f"Start {interview_type.title()} Interview"):
            st.session_state[f'{interview_type}_started'] = True
            st.session_state[f'{interview_type}_questions'] = generate_questions(interview_type, num_questions=10)
            st.rerun()

    # Interview in progress
    if st.session_state[f'{interview_type}_started']:
        current_idx = st.session_state[f'{interview_type}_current']
        questions = st.session_state[f'{interview_type}_questions']
        
        if current_idx < len(questions):
            # Navigation buttons with arrows
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            
            with nav_col1:
                if current_idx > 0:
                    if st.button("⬅️", key=f"prev_{interview_type}_btn", help="Previous Question"):
                        st.session_state[f'{interview_type}_current'] -= 1
                        st.session_state[f'{interview_type}_show_evaluation'] = False
                        st.rerun()
            
            with nav_col2:
                # Display progress
                st.write(f"Question {current_idx + 1} of {len(questions)}")
                progress_tracking(current_idx, len(questions))
                
                # Display current question
                st.write(f"**Question:** {questions[current_idx]}")
            
            with nav_col3:
                if current_idx < len(questions) - 1:
                    if st.button("➡️", key=f"next_{interview_type}_btn", help="Next Question"):
                        st.session_state[f'{interview_type}_current'] += 1
                        st.session_state[f'{interview_type}_show_evaluation'] = False
                        st.rerun()

            answer = st.text_area(
                "Your Answer:", 
                key=f"{interview_type}_answer_{current_idx}",
                height=150
            )

            # Submit button
            if st.button("Submit Answer", key=f"submit_{interview_type}_{current_idx}"):
                if answer.strip():
                    # Generate ideal answer
                    ideal_answer = generate_ai_response(
                        f"Provide a concise, 2-3 sentence answer for this {interview_type} interview question. "
                        f"Focus on key points and be specific but brief: {questions[current_idx]}"
                    )
                    
                    # Calculate score
                    score = evaluate_answer(answer, ideal_answer)
                    
                    # Store results
                    st.session_state[f'{interview_type}_scores'].append(score)
                    st.session_state[f'{interview_type}_answers'].append(answer)
                    st.session_state[f'{interview_type}_ideal_answers'].append(ideal_answer)
                    st.session_state[f'{interview_type}_show_evaluation'] = True
                    st.rerun()

            # Show evaluation after submission
            if st.session_state[f'{interview_type}_show_evaluation'] and len(st.session_state[f'{interview_type}_scores']) > current_idx:
                st.write("### Your Score:")
                st.write(f"**{st.session_state[f'{interview_type}_scores'][current_idx]}/10**")
                
                st.write("### Ideal Answer:")
                st.info(st.session_state[f'{interview_type}_ideal_answers'][current_idx])

                # Next question button
                if st.button("Next Question", key=f"next_{interview_type}_{current_idx}"):
                    st.session_state[f'{interview_type}_current'] += 1
                    st.session_state[f'{interview_type}_show_evaluation'] = False
                    st.rerun()
        else:
            show_interview_results(interview_type)

def generate_resume_questions(resume_text):
    """Generate exactly 10 questions covering all resume aspects"""
    question_distribution = [
        {
            "topic": "Technical Skills",
            "count": 2,
            "prompt": "Based on the technical skills mentioned in the resume, generate specific questions about their practical application and proficiency level."
        },
        {
            "topic": "Internships/Work Experience",
            "count": 2,
            "prompt": "Looking at the internship/work experience section, ask about specific responsibilities, challenges faced, and solutions implemented."
        },
        {
            "topic": "Projects",
            "count": 2,
            "prompt": "Regarding the projects mentioned in the resume, ask about technical implementation, role, and impact."
        },
        {
            "topic": "Certifications",
            "count": 2,
            "prompt": "Based on the certifications listed, ask about their relevance to the role and practical application of learned skills."
        },
        {
            "topic": "Achievements",
            "count": 2,
            "prompt": "Looking at achievements and accomplishments, ask about the impact, metrics, and process of achieving these results."
        }
    ]
    
    all_questions = []
    
    try:
        for category in question_distribution:
            prompt = f"""
            Based on this resume content: {resume_text}
            
            Generate exactly {category['count']} questions about the candidate's {category['topic']}.
            {category['prompt']}
            
            Requirements:
            - Questions should be specific to the content in the resume
            - Focus on practical experience and implementation
            - Ask about concrete examples and results
            - Questions should require detailed responses
            """
            
            response = generate_ai_response(prompt)
            questions = [q.strip() for q in response.split('\n') if '?' in q][:category['count']]
            
            # If we didn't get enough questions for this category, generate generic ones
            while len(questions) < category['count']:
                generic_q = f"Tell me about your experience with {category['topic'].lower()}?"
                questions.append(generic_q)
            
            all_questions.extend(questions)
    
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        # Provide backup questions if generation fails
        all_questions = [
            "Describe your most relevant technical skills for this position.",
            "Tell me about your most challenging project.",
            "What was your most significant achievement in your last role?",
            "How have you applied your certifications in practical scenarios?",
            "Describe your role in your most recent internship.",
            "What technical challenges did you face in your projects?",
            "How do you keep your technical skills updated?",
            "Tell me about a situation where you used your technical expertise to solve a problem.",
            "What was your most impactful contribution in your previous role?",
            "How have your certifications helped you in your career development?"
        ]
    
    return all_questions[:10]  # Ensure exactly 10 questions

def resume_screen():
    """Resume-based interview screen with concise feedback and final summary"""
    st.markdown('<h1 class="title-style">Resume-based Interview</h1>', unsafe_allow_html=True)
    
    # Initialize session state variables
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    if 'resume_started' not in st.session_state:
        st.session_state.resume_started = False
    if 'resume_current' not in st.session_state:
        st.session_state.resume_current = 0
    if 'resume_scores' not in st.session_state:
        st.session_state.resume_scores = []
    if 'resume_answers' not in st.session_state:
        st.session_state.resume_answers = []
    if 'resume_questions' not in st.session_state:
        st.session_state.resume_questions = []
    if 'resume_completed' not in st.session_state:
        st.session_state.resume_completed = False

    if not st.session_state.resume_started:
        st.write("### Upload Your Resume")
        st.write("Please upload your resume in PDF or TXT format.")
        resume_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
        
        if resume_file:
            try:
                with st.spinner("Processing your resume..."):
                    resume_text = extract_text(resume_file)
                    if resume_text.strip():
                        st.session_state.resume_text = resume_text
                        st.success("✅ Resume processed successfully!")
                        
                        if st.button("Start Interview"):
                            with st.spinner("Generating questions..."):
                                # Generate 10 questions covering different resume aspects
                                questions = generate_resume_questions(resume_text)
                                st.session_state.resume_questions = questions
                                st.session_state.resume_started = True
                                st.rerun()
                    else:
                        st.error("Could not extract text from the uploaded file.")
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")

    if st.session_state.resume_started and not st.session_state.resume_completed:
        current_idx = st.session_state.resume_current
        
        # Display progress
        st.progress((current_idx + 1) / 10)
        st.write(f"Question {current_idx + 1} of 10")
        
        # Display current question
        st.write(f"**Question:** {st.session_state.resume_questions[current_idx]}")
        
        # Answer input
        answer = st.text_area("Your Answer:", key=f"resume_answer_{current_idx}", height=150)
        
        col1, col2, col3 = st.columns([1,2,1])
        
        with col1:
            if current_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.resume_current -= 1
                    st.rerun()
        
        with col2:
            if st.button("Submit Answer"):
                if answer.strip():
                    with st.spinner("Evaluating..."):
                        ideal_answer = generate_ai_response(
                            f"Based on this resume:\n{st.session_state.resume_text}\n\n"
                            f"Provide a very brief (max 2 sentences) focused answer for: {st.session_state.resume_questions[current_idx]}"
                        )
                        score = evaluate_answer(answer, ideal_answer)
                        
                        # Store results including ideal answer
                        st.session_state.resume_scores.append(score)
                        st.session_state.resume_answers.append(answer)
                        if 'resume_ideal_answers' not in st.session_state:
                            st.session_state.resume_ideal_answers = []
                        st.session_state.resume_ideal_answers.append(ideal_answer)  # Store ideal answer
                        
                        # Show brief feedback
                        st.success(f"Score: {score}/10")
                        st.markdown("### Ideal Answer:")
                        st.info(ideal_answer)
                        
                        if len(st.session_state.resume_scores) == 10:
                            st.session_state.resume_completed = True
                            st.rerun()
                        else:
                            if st.button("Next Question ➡️"):
                                st.session_state.resume_current += 1
                                st.rerun()
                else:
                    st.warning("Please provide an answer before submitting.")
        
        with col3:
            if current_idx < 9 and len(st.session_state.resume_scores) > current_idx:
                if st.button("➡️ Next"):
                    st.session_state.resume_current += 1
                    st.rerun()

    # Show final results after completing all questions
    if st.session_state.resume_completed:
        st.balloons()
        
        # Calculate total score
        total_score = sum(st.session_state.resume_scores)
        avg_score = total_score / 10
        
        # Display overall score
        st.markdown("## 🎉 Interview Completed!")
        st.markdown(f"### Total Score: {total_score}/100")
        st.markdown(f"### Average Score: {avg_score:.1f}/10")
        
        # Generate medium-sized feedback
        feedback_prompt = f"""
        Provide a medium-sized feedback (about 150-200 words) for this resume-based interview:
        Total Score: {total_score}/100
        
        Focus on:
        1. Overall performance in presenting resume experience
        2. Strengths in communicating achievements (2-3 points)
        3. Areas for improvement in presenting experience (2-3 points)
        4. Quick tips for future resume-based interviews
        
        Keep the feedback concise but specific to the candidate's resume and responses.
        """
        
        feedback = generate_ai_response(feedback_prompt)
        
        # Display feedback in a clean format
        st.markdown("### 📝 Interview Feedback")
        st.write(feedback)
        
        # Add option to restart
        if st.button("Start New Resume Interview"):
            for key in list(st.session_state.keys()):
                if key.startswith('resume_'):
                    del st.session_state[key]
            st.rerun()

        # Save interview data
        if st.session_state.get('logged_in') and st.session_state.get('username'):
            save_interview_data(
                st.session_state.username,
                'resume',
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_score': total_score,
                    'average_score': avg_score,
                    'questions': st.session_state.resume_questions,
                    'answers': st.session_state.resume_answers,
                    'scores': st.session_state.resume_scores,
                    'feedback': feedback,
                    'ideal_answers': st.session_state.get('resume_ideal_answers', [])  # Add this line
                }
            )
            st.success("✅ Interview results saved!")

def show_interview_results(interview_type):
    """Display comprehensive interview results with detailed feedback"""
    st.balloons()
    st.markdown("<h1 style='text-align: center;'>🎉 Interview Completed!</h1>", unsafe_allow_html=True)
    
    try:
        # Get interview data
        scores = st.session_state.get(f'{interview_type}_scores', [])
        questions = st.session_state.get(f'{interview_type}_questions', []) if interview_type != 'resume' else st.session_state.get('resume_questions_history', [])
        answers = st.session_state.get(f'{interview_type}_answers', [])
        ideal_answers = st.session_state.get(f'{interview_type}_ideal_answers', [])
        
        # Check if there are any completed questions
        if not scores or not answers:
            st.error("No answers found. Please complete at least one question.")
            return
        
        # Calculate scores
        total_score = sum(scores)
        num_questions = len(scores)
        average_score = total_score / num_questions if num_questions > 0 else 0
        
        # Display overall score with enhanced styling
        st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #1a1a1a; border-radius: 10px; margin: 20px 0; color: white;'>
                <h2 style='color: #4CAF50;'>Final Score: {total_score}/{num_questions * 10}</h2>
                <p style='color: #ffffff;'>Average Score per Question: {average_score:.2f}/10</p>
            </div>
        """, unsafe_allow_html=True)

        # Generate immediate feedback
        with st.spinner("Generating comprehensive feedback..."):
            # Create a detailed analysis of all answered questions
            question_analysis = []
            for i in range(num_questions):
                question_analysis.append(f"""
                Question {i+1}: {questions[i] if i < len(questions) else 'Custom Question'}
                Your Answer: {answers[i]}
                Ideal Answer: {ideal_answers[i]}
                Score: {scores[i]}/10
                """)
            
            feedback_prompt = f"""
            Analyze this {interview_type} interview performance:

            Summary:
            - Questions Attempted: {num_questions}
            - Total Score: {total_score}/{num_questions * 10}
            - Average Score: {average_score:.2f}/10

            Detailed Analysis:
            {' '.join(question_analysis)}

            Please provide a comprehensive analysis covering:

            1. OVERALL PERFORMANCE:
            - Overall evaluation
            - Key strengths shown
            - Areas for improvement

            2. TECHNICAL PROFICIENCY:
            - Knowledge demonstration
            - Understanding of concepts
            - Application of knowledge

            3. COMMUNICATION SKILLS:
            - Clarity of responses
            - Structure and organization
            - Professional language use

            4. ACTIONABLE RECOMMENDATIONS:
            - Specific improvement steps
            - Study resources
            - Practice suggestions
            """

            feedback = generate_ai_response(feedback_prompt)
            
            # Display feedback sections with custom styling
            st.markdown("### 📊 Detailed Performance Analysis")
            sections = feedback.split('\n\n')
            for section in sections:
                if section.strip():
                    title = section.split('\n')[0].strip()
                    content = '\n'.join(section.split('\n')[1:])
                    with st.expander(title, expanded=True):
                        st.markdown(f"""
                            <div style='background-color: #2b2b2b; padding: 15px; border-radius: 5px;'>
                                {content}
                            </div>
                        """, unsafe_allow_html=True)

        # Question-by-question analysis
        st.markdown("### 📝 Question Analysis")
        for i in range(num_questions):
            with st.expander(f"Question {i+1} - Score: {scores[i]}/10 🎯", expanded=True):
                st.markdown("""
                    <style>
                    .question-box { background-color: #2b2b2b; padding: 10px; border-radius: 5px; margin: 5px 0; }
                    .answer-box { background-color: #1a1a1a; padding: 10px; border-radius: 5px; margin: 5px 0; }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown("<div class='question-box'>", unsafe_allow_html=True)
                st.markdown("**📋 Question:**")
                st.write(questions[i] if i < len(questions) else "Custom Question")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='answer-box'>", unsafe_allow_html=True)
                st.markdown("**✍️ Your Answer:**")
                st.write(answers[i])
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='answer-box'>", unsafe_allow_html=True)
                st.markdown("**💡 Ideal Answer:**")
                st.write(ideal_answers[i])
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Generate specific feedback for each answer
                specific_feedback = generate_ai_response(f"""
                Analyze this specific answer:
                Question: {questions[i] if i < len(questions) else 'Custom Question'}
                Given Answer: {answers[i]}
                Ideal Answer: {ideal_answers[i]}
                Score: {scores[i]}/10

                Provide specific feedback in this format:
                STRENGTHS:
                - Key strong points in the answer
                
                AREAS FOR IMPROVEMENT:
                - Specific points that could be better
                
                TIPS FOR NEXT TIME:
                - Actionable advice for similar questions
                """)
                
                st.markdown("<div class='answer-box'>", unsafe_allow_html=True)
                st.markdown("**🎯 Specific Feedback:**")
                st.write(specific_feedback)
                st.markdown("</div>", unsafe_allow_html=True)

        # Save interview data if logged in
        if st.session_state.get('logged_in') and st.session_state.get('username'):
            save_interview_data(
                st.session_state.username,
                interview_type,
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_score': total_score,
                    'average_score': average_score,
                    'questions': questions[:num_questions],
                    'answers': answers,
                    'ideal_answers': ideal_answers,
                    'scores': scores,
                    'feedback': feedback
                }
            )
            st.success("✅ Interview results saved!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try again or contact support if the issue persists.")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Interview", key="new_interview"):
            for key in list(st.session_state.keys()):
                if key.startswith(f'{interview_type}_'):
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 View Interview History", key="view_history"):
            st.session_state.show_history = True
            st.rerun()

def get_role_specific_questions(role):
    """Generate role-specific interview questions"""
    role_prompts = {
        "Software Developer": [
            "Generate a technical question about software design patterns",
            "Ask about experience with agile development methodologies",
            "Create a question about debugging complex issues",
            "Ask about code optimization and performance",
            "Generate a question about version control and collaboration"
        ],
        "Data Scientist": [
            "Ask about experience with machine learning algorithms",
            "Generate a question about data preprocessing techniques",
            "Create a question about statistical analysis methods",
            "Ask about big data technologies",
            "Generate a question about model evaluation metrics"
        ],
        "DevOps Engineer": [
            "Ask about CI/CD pipeline implementation",
            "Generate a question about container orchestration",
            "Create a question about infrastructure automation",
            "Ask about monitoring and logging solutions",
            "Generate a question about cloud services"
        ],
        "Frontend Developer": [
            "Ask about modern JavaScript frameworks",
            "Generate a question about responsive design",
            "Create a question about web performance optimization",
            "Ask about state management in web applications",
            "Generate a question about UI/UX best practices"
        ],
        "Backend Developer": [
            "Ask about API design and implementation",
            "Generate a question about database optimization",
            "Create a question about scalability solutions",
            "Ask about microservices architecture",
            "Generate a question about server security"
        ]
    }
    
    questions = []
    prompts = role_prompts.get(role, role_prompts["Software Developer"])
    for prompt in prompts:
        question = generate_ai_response(f"{prompt} for a {role} position. Make the question specific and technical.")
        questions.append(question)
    
    # Generate 5 more behavioral questions specific to the role
    behavioral_prompt = f"Generate a behavioral interview question for a {role} position that focuses on real work scenarios"
    for _ in range(5):
        question = generate_ai_response(behavioral_prompt)
        questions.append(question)
    
    return questions

def professional_screen():
    """Professional interview screen with concise ideal answers"""
    st.markdown('<h1 class="title-style">Professional Interview</h1>', unsafe_allow_html=True)
    
    # Initialize session state variables
    if 'professional_role' not in st.session_state:
        st.session_state.professional_role = None
    if 'professional_started' not in st.session_state:
        st.session_state.professional_started = False
    if 'professional_current' not in st.session_state:
        st.session_state.professional_current = 0
    if 'professional_scores' not in st.session_state:
        st.session_state.professional_scores = []
    if 'professional_answers' not in st.session_state:
        st.session_state.professional_answers = []
    if 'professional_questions' not in st.session_state:
        st.session_state.professional_questions = []
    if 'professional_completed' not in st.session_state:
        st.session_state.professional_completed = False

    # Role selection if not started
    if not st.session_state.professional_started:
        st.write("### Select Your Role")
        roles = [
            "Software Developer",
            "Data Scientist",
            "DevOps Engineer",
            "Frontend Developer",
            "Backend Developer"
        ]
        selected_role = st.selectbox("Choose your role:", roles)
        
        if st.button("Start Professional Interview"):
            st.session_state.professional_role = selected_role
            st.session_state.professional_questions = get_role_specific_questions(selected_role)[:10]  # Ensure 10 questions
            st.session_state.professional_started = True
            st.rerun()
        return

    if st.session_state.professional_started and not st.session_state.professional_completed:
        current_idx = st.session_state.professional_current
        
        # Display progress
        st.progress((current_idx + 1) / 10)
        st.write(f"Question {current_idx + 1} of 10")
        
        # Display current question
        st.write(f"**Question:** {st.session_state.professional_questions[current_idx]}")
        
        # Answer input
        answer = st.text_area("Your Answer:", key=f"professional_answer_{current_idx}", height=150)
        
        col1, col2, col3 = st.columns([1,2,1])
        
        with col1:
            if current_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.professional_current -= 1
                    st.rerun()
        
        with col2:
            if st.button("Submit Answer"):
                if answer.strip():
                    with st.spinner("Evaluating..."):
                        ideal_answer = generate_ai_response(
                            f"""Provide a concise but complete technical answer for this {st.session_state.professional_role} question:
                            Question: {st.session_state.professional_questions[current_idx]}
                            
                            Requirements:
                            - Focus on key technical points
                            - Include one practical example or implementation detail
                            - Keep it clear and precise
                            - Maximum 3-4 sentences
                            - Highlight best practices
                            
                            Make it specific to {st.session_state.professional_role} role."""
                        )
                        
                        score = evaluate_answer(answer, ideal_answer)
                        
                        # Store results including ideal answer
                        st.session_state.professional_scores.append(score)
                        st.session_state.professional_answers.append(answer)
                        if 'professional_ideal_answers' not in st.session_state:
                            st.session_state.professional_ideal_answers = []
                        st.session_state.professional_ideal_answers.append(ideal_answer)  # Store ideal answer
                        
                        # Show score and ideal answer
                        st.success(f"Score: {score}/10")
                        st.markdown("### Ideal Answer:")
                        st.info(ideal_answer)
                        
                        if len(st.session_state.professional_scores) == 10:
                            st.session_state.professional_completed = True
                            st.rerun()
                else:
                    st.warning("Please provide an answer before submitting.")
        
        with col3:
            if current_idx < 9 and len(st.session_state.professional_scores) > current_idx:
                if st.button("➡️ Next"):
                    st.session_state.professional_current += 1
                    st.rerun()

    # Show final results after completion
    if st.session_state.professional_completed:
        st.balloons()
        
        # Calculate total score
        total_score = sum(st.session_state.professional_scores)
        avg_score = total_score / 10
        
        # Display overall score
        st.markdown("## 🎉 Interview Completed!")
        st.markdown(f"### Total Score: {total_score}/100")
        st.markdown(f"### Average Score: {avg_score:.1f}/10")
        
        # Generate medium-sized feedback
        feedback_prompt = f"""
        Provide a medium-sized feedback (about 150-200 words) for this {st.session_state.professional_role} interview:
        Total Score: {total_score}/100
        Average Score: {avg_score}/10
        
        Focus on:
        1. Technical proficiency assessment
        2. Key strengths in {st.session_state.professional_role} role
        3. Areas for technical improvement
        4. Specific recommendations for future technical interviews
        """
        
        feedback = generate_ai_response(feedback_prompt)
        
        # Display feedback
        st.markdown("### 📝 Interview Feedback")
        st.write(feedback)
        
        # Add restart button
        if st.button("Start New Professional Interview"):
            for key in list(st.session_state.keys()):
                if key.startswith('professional_'):
                    del st.session_state[key]
            st.rerun()

        # Save interview data
        if st.session_state.get('logged_in') and st.session_state.get('username'):
            save_interview_data(
                st.session_state.username,
                'professional',
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_score': total_score,
                    'average_score': avg_score,
                    'questions': st.session_state.professional_questions,
                    'answers': st.session_state.professional_answers,
                    'scores': st.session_state.professional_scores,
                    'feedback': feedback,
                    'role': st.session_state.professional_role,
                    'ideal_answers': st.session_state.get('professional_ideal_answers', [])  # Make sure this is included
                }
            )
            st.success("✅ Interview results saved!")

def behavioral_screen():
    """Behavioral interview screen with simplified navigation"""
    # Initialize session state variables
    if 'behavioral_questions' not in st.session_state:
        st.session_state.behavioral_questions = [
            "Tell me about a time when you had to work with a difficult team member.",
            "Describe a situation where you had to meet a tight deadline.",
            "Share an experience where you had to handle multiple priorities.",
            "Tell me about a time when you demonstrated leadership skills.",
            "Describe a situation where you had to resolve a conflict.",
            "Share an example of how you dealt with failure.",
            "Tell me about a time when you went above and beyond.",
            "Describe a situation where you had to learn something quickly.",
            "Share an experience where you had to make a difficult decision.",
            "Tell me about a time when you showed initiative."
        ]
    
    if 'behavioral_started' not in st.session_state:
        st.session_state.behavioral_started = False
    if 'behavioral_current' not in st.session_state:
        st.session_state.behavioral_current = 0
    if 'behavioral_scores' not in st.session_state:
        st.session_state.behavioral_scores = []
    if 'behavioral_answers' not in st.session_state:
        st.session_state.behavioral_answers = []
    if 'behavioral_completed' not in st.session_state:
        st.session_state.behavioral_completed = False

    st.markdown('<h1 class="title-style">Behavioral Interview</h1>', unsafe_allow_html=True)

    if not st.session_state.behavioral_started:
        if st.button("Start Behavioral Interview"):
            st.session_state.behavioral_started = True
            st.rerun()
        return

    if st.session_state.behavioral_started and not st.session_state.behavioral_completed:
        current_idx = st.session_state.behavioral_current
        
        # Display progress
        st.progress((current_idx + 1) / 10)
        st.write(f"Question {current_idx + 1} of 10")
        
        # Display current question
        st.write(f"**Question:** {st.session_state.behavioral_questions[current_idx]}")
        
        # Answer input
        answer = st.text_area("Your Answer:", key=f"behavioral_answer_{current_idx}", height=150)
        
        col1, col2, col3 = st.columns([1,2,1])
        
        with col1:
            if current_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.behavioral_current -= 1
                    st.rerun()
        
        with col2:
            if st.button("Submit Answer"):
                if answer.strip():
                    with st.spinner("Evaluating..."):
                        # Generate ideal answer using STAR method
                        ideal_answer = generate_ai_response(
                            f"""Provide a brief but effective STAR method answer for this behavioral question:
                            Question: {st.session_state.behavioral_questions[current_idx]}
                            
                            Requirements:
                            - One short sentence each for Situation, Task, Action, and Result
                            - Focus on key points only
                            - Be specific and measurable
                            - Maximum 4 sentences total
                            - Highlight the impact
                            
                            Format:
                            S: [brief situation]
                            T: [clear task]
                            A: [specific action]
                            R: [measurable result]"""
                        )
                        
                        score = evaluate_answer(answer, ideal_answer)
                        
                        # Store results including ideal answer
                        st.session_state.behavioral_scores.append(score)
                        st.session_state.behavioral_answers.append(answer)
                        if 'behavioral_ideal_answers' not in st.session_state:
                            st.session_state.behavioral_ideal_answers = []
                        st.session_state.behavioral_ideal_answers.append(ideal_answer)  # Store ideal answer
                        
                        # Show score and ideal answer
                        st.success(f"Score: {score}/10")
                        st.markdown("### Ideal Answer:")
                        st.info(ideal_answer)
                        
                        # Check if all questions are answered
                        if len(st.session_state.behavioral_scores) == 10:
                            st.session_state.behavioral_completed = True
                            st.rerun()
                else:
                    st.warning("Please provide an answer before submitting.")
        
        with col3:
            # Show Next button only if question has been answered
            if current_idx < 9 and len(st.session_state.behavioral_scores) > current_idx:
                if st.button("➡️ Next"):
                    st.session_state.behavioral_current += 1
                    st.rerun()

    # Show final results after completion
    if st.session_state.behavioral_completed:
        st.balloons()
        
        # Calculate total score
        total_score = sum(st.session_state.behavioral_scores)
        avg_score = total_score / 10
        
        # Display overall score
        st.markdown("## 🎉 Interview Completed!")
        st.markdown(f"### Total Score: {total_score}/100")
        st.markdown(f"### Average Score: {avg_score:.1f}/10")
        
        # Generate medium-sized feedback
        feedback_prompt = f"""
        Provide a medium-sized feedback (about 150-200 words) for this behavioral interview:
        Total Score: {total_score}/100
        Average Score: {avg_score}/10
        
        Focus on:
        1. Overall performance assessment
        2. STAR method usage
        3. Key strengths demonstrated (2-3 points)
        4. Areas for improvement (2-3 points)
        5. Specific recommendations for future behavioral interviews
        """
        
        feedback = generate_ai_response(feedback_prompt)
        
        # Display feedback
        st.markdown("### 📝 Interview Feedback")
        st.write(feedback)
        
        # Save interview data
        if st.session_state.get('logged_in') and st.session_state.get('username'):
            save_interview_data(
                st.session_state.username,
                'behavioral',
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_score': total_score,
                    'average_score': avg_score,
                    'questions': st.session_state.behavioral_questions,
                    'answers': st.session_state.behavioral_answers,
                    'scores': st.session_state.behavioral_scores,
                    'feedback': feedback,
                    'ideal_answers': st.session_state.get('behavioral_ideal_answers', [])  # Make sure this is included
                }
            )
            st.success("✅ Interview results saved!")
        
        # Add restart button
        if st.button("Start New Behavioral Interview"):
            for key in list(st.session_state.keys()):
                if key.startswith('behavioral_'):
                    del st.session_state[key]
            st.rerun()

def homepage():
    # Initialize session state variables if not exists
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'company' not in st.session_state:
        st.session_state.company = None
    if 'column_name' not in st.session_state:
        st.session_state.column_name = None
    if 'total_score' not in st.session_state:
        st.session_state.total_score = 0
    if 'show_evaluation' not in st.session_state:
        st.session_state.show_evaluation = False
    if 'current_answer' not in st.session_state:
        st.session_state.current_answer = ""
    if 'current_score' not in st.session_state:
        st.session_state.current_score = 0
    if 'current_ideal_answer' not in st.session_state:
        st.session_state.current_ideal_answer = ""

    st.markdown('<h1 class="title-style">AI Interviewer Beta</h1>', unsafe_allow_html=True)
    st.write("""
    𝕋𝕙𝕚𝕤 𝕥𝕠𝕠𝕝 𝕙𝕖𝕝𝕡𝕤 𝕪𝕠𝕦 𝕡𝕣𝕖𝕡𝕒𝕣𝕖 𝕗𝕠𝕣 𝕚𝕟𝕥𝕖𝕣𝕚𝕖𝕨𝕤 𝕓𝕪 𝕘𝕖𝕟𝕖𝕣𝕒𝕥𝕚𝕟𝕘 𝕛𝕠𝕓-𝕤𝕡𝕖𝕔𝕚𝕗𝕚𝕔 𝕢𝕦𝕖𝕤𝕥𝕚𝕠𝕕𝕤.
    """)

    # Company selection buttons in four columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='circular-button' style='background: linear-gradient(45deg, #0066cc, #0099ff);'>
            <h3 style='color: white; margin: 0;'>TCS</h3>
        </div>
        """, unsafe_allow_html=True)
        tcs_button = st.button("TCS Interview", key="tcs-btn")
    
    with col2:
        st.markdown("""
        <div class='circular-button' style='background: linear-gradient(45deg, #a100ff, #7700ff);'>
            <h3 style='color: white; margin: 0;'>Accenture</h3>
        </div>
        """, unsafe_allow_html=True)
        accenture_button = st.button("Accenture Interview", key="accenture-btn")
    
    with col3:
        st.markdown("""
        <div class='circular-button' style='background: linear-gradient(45deg, #ff9900, #ffad33);'>
            <h3 style='color: white; margin: 0;'>Amazon</h3>
        </div>
        """, unsafe_allow_html=True)
        amazon_button = st.button("Amazon Interview", key="amazon-btn")
        
    with col4:
        st.markdown("""
        <div class='circular-button' style='background: linear-gradient(45deg, #00a4ef, #0078d4);'>
            <h3 style='color: white; margin: 0;'>Microsoft</h3>
        </div>
        """, unsafe_allow_html=True)
        microsoft_button = st.button("Microsoft Interview", key="microsoft-btn")

    # Handle button clicks
    if tcs_button or accenture_button or amazon_button or microsoft_button:
        if tcs_button:
            company = "TCS"
        elif accenture_button:
            company = "Accenture"
        elif amazon_button:
            company = "Amazon"
        else:
            company = "Microsoft"
            
        questions_df, column_name = load_questions(company)
        st.session_state.questions = questions_df
        st.session_state.column_name = column_name
        st.session_state.current_question = 0
        st.session_state.company = company
        st.session_state.total_score = 0
        st.session_state.show_evaluation = False
        st.session_state.current_answer = ""
        st.session_state.current_score = 0
        st.session_state.current_ideal_answer = ""
        st.rerun()

    # Display interview questions if company is selected and questions are loaded
    if st.session_state.company is not None and st.session_state.questions is not None:
        st.write(f"## {st.session_state.company} Interview")
        
        # Navigation buttons with arrows
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        
        with nav_col1:
            if st.session_state.current_question > 0:
                if st.button("⬅️", key="prev_company_btn", help="Previous Question"):
                    st.session_state.current_question -= 1
                    st.session_state.show_evaluation = False
                    st.session_state.current_answer = ""
                    st.session_state.current_score = 0
                    st.session_state.current_ideal_answer = ""
                    st.rerun()
        
        with nav_col2:
            st.write(f"Question {st.session_state.current_question + 1} of 10")
            try:
                current_row = st.session_state.questions.iloc[st.session_state.current_question]
                current_q = current_row[st.session_state.column_name]
            except Exception as e:
                st.error("Error loading questions. Please try selecting a company again.")
                return
            
            # Display difficulty for all companies
            difficulty = current_row['difficulty'].lower()
            difficulty_color = {
                'low': 'green',
                'medium': 'orange',
                'high': 'red'
            }
            st.markdown(f"**Difficulty:** <span style='color: {difficulty_color[difficulty]}'>{difficulty.upper()}</span>", 
                        unsafe_allow_html=True)
            
            st.write(f"**Question:** {current_q}")
        
        with nav_col3:
            if st.session_state.current_question < 9:
                if st.button("➡️", key="next_company_btn", help="Next Question"):
                    st.session_state.current_question += 1
                    st.session_state.show_evaluation = False
                    st.session_state.current_answer = ""
                    st.session_state.current_score = 0
                    st.session_state.current_ideal_answer = ""
                    st.rerun()

        answer = st.text_area("Your Answer:", value=st.session_state.current_answer, height=150, 
                            key=f"answer_{st.session_state.current_question}")

        if st.button("Submit Answer"):
            if answer.strip():
                ideal_answer = generate_company_answer(current_q, st.session_state.company)
                score = evaluate_answer(answer, ideal_answer)
                
                # Store results including ideal answer
                st.session_state.current_score = score
                st.session_state.current_ideal_answer = ideal_answer
                st.session_state.total_score += score
                st.session_state.current_answer = answer
                if f'ideal_answer_{st.session_state.current_question}' not in st.session_state:
                    st.session_state[f'ideal_answer_{st.session_state.current_question}'] = ideal_answer
                st.session_state.show_evaluation = True

        if st.session_state.show_evaluation:
            st.write("### Your Score:")
            st.write(f"**{st.session_state.current_score}/10**")
            
            st.write("### Ideal Answer:")
            st.info(st.session_state.current_ideal_answer)

            if st.button("Next Question"):
                if st.session_state.current_question < 9:
                    st.session_state.current_question += 1
                    st.session_state.show_evaluation = False
                    st.session_state.current_answer = ""
                    st.session_state.current_score = 0
                    st.session_state.current_ideal_answer = ""
                    st.rerun()
                else:
                    st.write("## 🎉 Interview Completed!")
                    st.write(f"### Final Score: {st.session_state.total_score}/100")
                    
                    # Generate comprehensive feedback immediately
                    

                    detailed_analysis = ''.join([
                        f"Q{i+1}: {question}\nYour Answer: {answer}\nIdeal Answer: {ideal_answer}\nScore: {score}/10\n\n"
                        for i, (question, answer, ideal_answer, score) in enumerate(zip(
                            [st.session_state.questions.iloc[i][st.session_state.column_name] for i in range(10)],
                            [st.session_state.get(f'answer_{i}', '') for i in range(10)],
                            [st.session_state.get(f'ideal_answer_{i}', '') for i in range(10)],
                            [st.session_state.get(f'score_{i}', 0) for i in range(10)]
                        ))
                    ])
                    feedback_prompt = f"""
Analyze this company interview performance for {st.session_state.company}:

                    Please provide a comprehensive analysis covering:

                    1. OVERALL PERFORMANCE ASSESSMENT
                    - Evaluate overall interview performance
                    - Score interpretation
                    - Key strengths and areas of concern

                    2. COMPANY-SPECIFIC FEEDBACK
                    - Alignment with {st.session_state.company}'s values and culture
                    - Understanding of company requirements
                    - Areas that need company-specific improvement

                    3. TECHNICAL PROFICIENCY
                    - Knowledge demonstration
                    - Problem-solving approach
                    - Technical communication skills

                    4. COMMUNICATION SKILLS
                    - Clarity and structure of responses
                    - Professional language usage
                    - Ability to articulate complex ideas

                    5. ACTIONABLE RECOMMENDATIONS
                    - Specific areas to improve
                    - Preparation strategies
                    - Resources for further learning
                    """

                    with st.spinner("Generating comprehensive feedback..."):
                        feedback = generate_ai_response(feedback_prompt)
                        
                        # Display feedback sections
                        st.markdown("### 📊 Detailed Performance Analysis")
                        sections = feedback.split('\n\n')
                        for section in sections:
                            if section.strip():
                                title = section.split('\n')[0].strip()
                                content = '\n'.join(section.split('\n')[1:])
                                with st.expander(title, expanded=True):
                                    st.write(content)

                        # Save interview data if logged in
                        if st.session_state.get('logged_in') and st.session_state.get('username'):
                            save_interview_data(
                                st.session_state.username,
                                'company',
                                {
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'company': st.session_state.company,
                                    'total_score': st.session_state.total_score,
                                    'average_score': st.session_state.total_score/10,
                                    'questions': [st.session_state.questions.iloc[i][st.session_state.column_name] for i in range(10)],
                                    'answers': [st.session_state.get(f'answer_{i}', '') for i in range(10)],
                                    'ideal_answers': [st.session_state.get(f'ideal_answer_{i}', '') for i in range(10)],  # Make sure this is included
                                    'scores': [st.session_state.get(f'score_{i}', 0) for i in range(10)],
                                    'feedback': feedback
                                }
                            )

                    if st.button("Start New Interview"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()

def save_interview_data(username, interview_type, data):
    """
    Save interview data for a user.
    
    Args:
        username (str): The username of the person who completed the interview
        interview_type (str): Type of interview (company, behavioral, professional, resume)
        data (dict): Interview data including scores, answers, and feedback
    """
    try:
        # Create interview_data directory if it doesn't exist
        if not os.path.exists('interview_data'):
            os.makedirs('interview_data')
        
        # Construct the file path
        file_path = os.path.join('interview_data', f'{username}_history.json')
        
        # Load existing history or create new
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                history = json.load(f)
        else:
            history = {
                'company': [],
                'behavioral': [],
                'professional': [],
                'resume': []
            }
        
        # Ensure the interview type exists in history
        if interview_type not in history:
            history[interview_type] = []
        
        # Create interview entry with proper ideal answers handling
        interview_entry = {
            'timestamp': data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'total_score': data.get('total_score', 0),
            'average_score': data.get('average_score', 0),
            'questions': data.get('questions', []),
            'answers': data.get('answers', []),
            'scores': data.get('scores', []),
            'feedback': data.get('feedback', ''),
            'ideal_answers': data.get('ideal_answers', []) if data.get('ideal_answers') else []  # Ensure ideal_answers is always a list
        }
        
        # Validate that all lists have the same length
        list_lengths = [
            len(interview_entry['questions']),
            len(interview_entry['answers']),
            len(interview_entry['scores']),
            len(interview_entry['ideal_answers'])
        ]
        
        if len(set(list_lengths)) > 1:
            st.warning("Warning: Inconsistent data lengths detected. Some data may be missing.")
            # Pad shorter lists with None to match the longest length
            max_length = max(list_lengths)
            interview_entry['questions'] += [None] * (max_length - len(interview_entry['questions']))
            interview_entry['answers'] += [None] * (max_length - len(interview_entry['answers']))
            interview_entry['scores'] += [0] * (max_length - len(interview_entry['scores']))
            interview_entry['ideal_answers'] += [None] * (max_length - len(interview_entry['ideal_answers']))
        
        # Add company name if it's a company interview
        if interview_type == 'company' and 'company' in data:
            interview_entry['company'] = data['company']
        elif interview_type == 'company' and 'company' in st.session_state:
            interview_entry['company'] = st.session_state.company
        
        # Add role if it's a professional interview
        if interview_type == 'professional' and 'role' in data:
            interview_entry['role'] = data['role']
        elif interview_type == 'professional' and 'professional_role' in st.session_state:
            interview_entry['role'] = st.session_state.professional_role
        
        # Add the new interview to history
        history[interview_type].append(interview_entry)
        
        # Save updated history
        with open(file_path, 'w') as f:
            json.dump(history, f, indent=4)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving interview data: {str(e)}")
        return False

def show_feedback_and_score(score, ideal_answer):
    """Display immediate feedback and score after each question submission"""
    # Create a container for the feedback
    feedback_container = st.container()
    
    with feedback_container:
        # Display score with appropriate color and styling
        if score >= 8:
            st.success(f"Score: {score}/10 🌟")
        elif score >= 6:
            st.warning(f"Score: {score}/10 👍")
        else:
            st.error(f"Score: {score}/10 💪")
        
        # Display ideal answer section
        st.write("**Quick Feedback:**")
        with st.expander("View Ideal Response", expanded=True):
            # Truncate ideal answer if too long
            display_answer = ideal_answer[:200] + "..." if len(ideal_answer) > 200 else ideal_answer
            st.info(display_answer)
        
        # Add tips based on score
        if score < 8:
            st.write("**Tips for improvement:**")
            if score < 6:
                st.write("• Be more specific in your response")
                st.write("• Include concrete examples")
                st.write("• Structure your answer clearly")
            else:
                st.write("• Add more details to strengthen your answer")
                st.write("• Quantify your achievements where possible")

def create_interview_section(section_type, questions, current_idx):
    """Common interview section layout with proper feedback and navigation"""
    # Display progress
    st.progress((current_idx + 1) / 10)
    st.write(f"Question {current_idx + 1} of 10")
    
    # Display current question
    st.write(f"**Question:** {questions[current_idx]}")
    
    # Answer input
    answer = st.text_area("Your Answer:", key=f"{section_type}_answer_{current_idx}", height=150)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state[f"{section_type}_current"] -= 1
                st.rerun()
    
    with col2:
        if st.button("Submit Answer"):
            if answer.strip():
                with st.spinner("Evaluating..."):
                    ideal_answer = generate_ai_response(
                        f"Provide a concise answer for: {questions[current_idx]}"
                    )
                    score = evaluate_answer(answer, ideal_answer)
                    
                    # Store the results
                    st.session_state[f"{section_type}_scores"].append(score)
                    st.session_state[f"{section_type}_answers"].append(answer)
                    st.session_state[f"{section_type}_ideal_answers"].append(ideal_answer)
                    
                    # Show immediate feedback
                    show_feedback_and_score(score, ideal_answer)
                    
                    # Check if all questions are answered
                    if len(st.session_state[f"{section_type}_scores"]) == 10:
                        st.session_state[f"{section_type}_completed"] = True
                        show_final_results(section_type)
                    else:
                        # Show next button after submission
                        if st.button("Next Question ➡️"):
                            st.session_state[f"{section_type}_current"] += 1
                            st.rerun()
            else:
                st.warning("Please provide an answer before submitting.")
    
    with col3:
        if current_idx < 9 and len(st.session_state[f"{section_type}_scores"]) > current_idx:
            if st.button("➡️ Next"):
                st.session_state[f"{section_type}_current"] += 1
                st.rerun()

def show_final_results(interview_type):
    """Display comprehensive final results and feedback"""
    st.balloons()
    
    scores = st.session_state[f"{interview_type}_scores"]
    answers = st.session_state[f"{interview_type}_answers"]
    questions = st.session_state[f"{interview_type}_questions"]
    
    total_score = sum(scores)
    avg_score = total_score / len(scores)
    
    # Display overall score
    st.markdown("## 🎉 Interview Completed!")
    st.markdown(f"### Total Score: {total_score}/100")
    st.markdown(f"### Average Score: {avg_score:.2f}/10")
    
    # Generate comprehensive feedback
    qa_details = ''.join([
    f"Q{i+1}: {q}\nA: {a}\n"
    for i, (q, a) in enumerate(zip(questions, answers))
])
    feedback_prompt = f"""
    Analyze this {interview_type} interview performance:
    Total Score: {total_score}/100
    Average Score: {avg_score}/10
    
    Questions and Answers:
    {qa_details}
    
    Provide detailed feedback covering:
    1. Overall performance assessment
    2. Key strengths demonstrated
    3. Areas for improvement
    4. Specific recommendations
    5. Next steps for preparation
    """
    
    feedback = generate_ai_response(feedback_prompt)
    
    # Display feedback in sections
    st.markdown("### 📝 Detailed Feedback")
    with st.expander("View Complete Analysis", expanded=True):
        st.write(feedback)
    
    # Question-by-question review
    st.markdown("### 📋 Question Review")
    for idx, (question, answer, score) in enumerate(zip(questions, answers, scores)):
        with st.expander(f"Question {idx + 1} - Score: {score}/10"):
            st.write(f"**Question:** {question}")
            st.write("**Your Answer:**")
            st.write(answer)
            if interview_type in ['professional', 'resume']:
                st.write("**Ideal Answer:**")
                st.info(st.session_state[f"{interview_type}_ideal_answers"][idx])
    
    # Add restart button
    if st.button(f"Start New {interview_type.title()} Interview"):
        for key in list(st.session_state.keys()):
            if key.startswith(f"{interview_type}_"):
                del st.session_state[key]
        st.rerun()

def main():
    with st.sidebar:
        selected = option_menu(
            "Navigation Options",
            ["🏠 Company Interview", "📝 Behavioral Screen", "💼 Professional Screen", "📄 Resume Screen", "📊 History"],
            icons=["building", "chat-left-dots", "briefcase", "file-earmark-person", "clock-history"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"background-color": "#333333"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {"font-size": "18px", "color": "white", "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "#4CAF50"},
            }
        )

    if selected == "🏠 Company Interview":
        homepage()
    elif selected == "📝 Behavioral Screen":
        behavioral_screen()
    elif selected == "💼 Professional Screen":
        professional_screen()
    elif selected == "📄 Resume Screen":
        resume_screen()
    elif selected == "📊 History":
        display_interview_history()

    st.markdown("""
    <hr style="border:2px solid #4CAF50">
    <p style="text-align:center; color: #f5f5f5;">© 2024 AI Interviewer | Powered by Gemini AI</p>
    """, unsafe_allow_html=True)

def display_interview_history():
    """Display user's interview history with filtering and sorting options"""
    if not st.session_state.get('logged_in'):
        st.warning("Please log in to view your interview history.")
        return

    st.title("📊 Interview History")
    
    # Get user's interview history
    username = st.session_state.username
    
    try:
        # Create filters in the sidebar
        st.sidebar.markdown("### Filter Options")
        interview_types = ["All", "Company", "Behavioral", "Professional", "Resume"]
        selected_type = st.sidebar.selectbox("Interview Type", interview_types)
        
        # Date range filter
        st.sidebar.markdown("### Date Range")
        start_date = st.sidebar.date_input("From")
        end_date = st.sidebar.date_input("To")
        
        # Sort options
        sort_by = st.sidebar.selectbox(
            "Sort by",
            ["Most Recent", "Highest Score", "Lowest Score"]
        )
        
        # Get filtered history
        filtered_history = get_user_interview_history(username)
        
        if not filtered_history:
            st.info("No interview history found. Complete an interview to see your results here!")
            return
        
        # Display summary statistics
        st.markdown("### Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_interviews = len(filtered_history)
            st.metric("Total Interviews", total_interviews)
            
        with col2:
            avg_score = sum(h['total_score'] for h in filtered_history) / total_interviews
            st.metric("Average Score", f"{avg_score:.1f}/100")
            
        with col3:
            best_score = max(h['total_score'] for h in filtered_history)
            st.metric("Best Score", f"{best_score}/100")
        
        # Display detailed history
        st.markdown("### Interview Details")
        
        for record in filtered_history:
            with st.expander(f"Interview on {record['timestamp']} - Score: {record['total_score']}/100"):
                # Interview metadata
                st.markdown(f"""
                **Type:** {record.get('interview_type', 'N/A')}  
                **Date:** {record['timestamp']}  
                **Total Score:** {record['total_score']}/100  
                **Average Score:** {record['average_score']:.1f}/10
                """)
                
                # If it's a company interview, show company name
                if 'company' in record:
                    st.markdown(f"**Company:** {record['company']}")
                
                # If it's a professional interview, show role
                if 'role' in record:
                    st.markdown(f"**Role:** {record['role']}")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["Summary", "Detailed View"])
                
                with tab1:
                    # Show feedback summary
                    st.markdown("#### Feedback Summary")
                    st.markdown(record.get('feedback', 'No feedback available'))
                    
                    # Show performance chart
                    scores = record.get('scores', [])
                    if scores:
                        st.markdown("#### Performance Chart")
                        chart_data = pd.DataFrame({
                            'Question': [f"Q{i+1}" for i in range(len(scores))],
                            'Score': scores
                        })
                        st.bar_chart(chart_data.set_index('Question'))
                
                with tab2:
                    # Show detailed question/answer view
                    st.markdown("#### Questions and Answers")
                    questions = record.get('questions', [])
                    answers = record.get('answers', [])
                    ideal_answers = record.get('ideal_answers', [])  # Get ideal answers
                    scores = record.get('scores', [])
                    
                    # Ensure all lists have the same length by using the shortest length
                    min_length = min(
                        len(questions), 
                        len(answers), 
                        len(scores),
                        len(ideal_answers) if ideal_answers else len(questions)  # Include ideal_answers in length check
                    )
                    
                    for i in range(min_length):
                        st.markdown(f"""
                        **Question {i+1}** (Score: {scores[i]}/10)
                        
                        **Q:** {questions[i]}
                        
                        **Your Answer:**  
                        {answers[i]}
                        """)
                        
                        # Display ideal answer with improved handling
                        if ideal_answers and i < len(ideal_answers):
                            ideal_answer = ideal_answers[i]
                            if ideal_answer and isinstance(ideal_answer, str) and ideal_answer.strip():
                                st.markdown(f"""
                                **Ideal Answer:**  
                                {ideal_answer}
                                """)
                            else:
                                st.info("No ideal answer recorded for this question.")
                        else:
                            st.info("No ideal answer recorded for this question.")
                        
                        st.markdown("---")
        
    except Exception as e:
        st.error(f"Error loading interview history: {str(e)}")
        st.write("Please try again or contact support if the issue persists.")

def get_user_interview_history(username):
    """
    Retrieve interview history for a user from the JSON file.
    """
    try:
        # Construct the file path
        file_path = os.path.join('interview_data', f'{username}_history.json')
        
        # Check if history file exists
        if not os.path.exists(file_path):
            return []
        
        # Load the history file
        with open(file_path, 'r') as f:
            history = json.load(f)
        
        # Combine all interview types into a single list
        all_interviews = []
        for interview_type, interviews in history.items():
            for interview in interviews:
                # Add interview type to each record if not already present
                if 'interview_type' not in interview:
                    interview['interview_type'] = interview_type
                all_interviews.append(interview)
        
        # Sort interviews by timestamp (most recent first)
        all_interviews.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_interviews
        
    except Exception as e:
        st.error(f"Error retrieving interview history: {str(e)}")
        return []

if __name__ == "__main__":
    main()