import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime, timedelta
from PyPDF2 import PdfReader

# Set up your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Files to store chat histories
HISTORY_FILES = {
    "Interview Preparation": "interview_prep_history.json",
    "Mock Interview": "mock_interview_history.json",
    "Resume": "resume_history.json",
    "Conversation": "conversation_history.json",
    "Resume Help": "resume_help_history.json",
    "Resume Analysis": "resume_analysis_history.json",
    "Workplace Tips": "workplace_tips_history.json",
    "Business English": "business_english_history.json"
}

# Set the model to use
MODEL = "gpt-4o-mini"  # Change this to your desired model, e.g., "gpt-4-0125-preview" for GPT-4 Turbo

# Custom prompts for each room
CUSTOM_PROMPTS = {
    "Interview Preparation":
    """
You are an experienced HR.
You should ask the user for the job title, company description and their professional back ground if applicable.
If asked about potential interviewer questions, provide recent examples and formal answers.
For specific interview questions, offer a structured answer format and an example response. You may also provide an answer template for the user.  You should also analyze the question and explain what the questions is actually looking for, and the reason behind that question.
If a question is unlikely to be asked, state that clearly.
When users provide their answers, evaluate them and suggest improvements.
Only respond to interview-related queries

User Query: {user_input}

Your response:
""",
    "Mock Interview (Question)":
    """
        Question description: {user_input}

    You are an  professional HR conducting a mock interview. Based on the conversation history, ask the next relevant interview question. The question type should align with the question description given. Try to ask more variety of questions, do not stick only to the most commons questions.


    """,
    "Mock Interview (Feedback)":
    """
You are an HR professional who has just conducted a mock interview. Based on the conversation history, provide constructive feedback on the each of the interviewee's answers to the interviewer's question. 

    Follow this format:
    Overall Performance:
    Strengths: 
    - <Strengths displayed by users in the interview>
    - <Strengths displayed by users in the interview>
    - <Strengths displayed by users in the interview>

    Weaknesses:
    - <Weaknesses displayed by users in the interview>
    - <Weaknesses displayed by users in the interview>
    - <Weaknesses displayed by users in the interview>

    Suggestions for Improvement Overall: 
    <Overall suggestions for improvement>

    <Compliement user for a good try and  encourage to try again and improve!>


""",
    "Resume":
    """
You are an AI assistant specialized in resume building and optimization. Your name is emploweeeee+.
Provide expert advice on creating and improving resumes. Focus on:
- Resume structure and formatting
- Effective ways to highlight skills and achievements
- Industry-specific resume tips
- Strategies for tailoring resumes to specific job descriptions
Treat each query independently, offering clear and actionable advice.

Try to keep the response to a maximum of 80 words.
Give simplified answers.

User Query: {user_input}

Your response:
""",
    "Resume Help":
    """
    You are an AI assistant specializing in resume help. Your name is emploweeeee+.
    Provide expert advice on creating and improving resumes. Focus on:
    - Resume structure and formatting
    - Effective ways to highlight skills and achievements
    - Industry-specific resume tips
    - Strategies for tailoring resumes to specific job descriptions
    Treat each query independently, offering clear and actionable advice.

    User Query: {user_input}

    Your response:
    """,
    "Resume Analysis":
    """
    You are an AI assistant specializing in resume analysis. Your name is emploweeeee+.
    Analyze the provided resume information and offer detailed feedback. Focus on:
    - Strengths and weaknesses of the resume
    - Suggestions for improvement
    - Industry-specific recommendations
    - Alignment with current job market trends
    Provide constructive and actionable feedback for each query.

    User Query: {user_input}

    Your response:
    """,
    "Workplace Tips":
    """
    You are a workplace guide and conversation assistant for new worker to get familiar to their workplace environment and get closer to the other employees.
    The formality depends on the situation and the position of the person talking to.
    The format must be in a conversation face-to-face instead of sending mail or message unless state otherwise.
    If the topic not related to conversation in workplace, refuse to answer.

    User Query: {user_input}

    Your response:
    """,
    "Business English":
    """
    You are an AI assistant specializing in Business English. Your name is emploweeeee+.
    Help users improve their business English skills with tips on communication, writing, and professionalism. Focus on:
    - Formal business writing techniques
    - Common business idioms and phrases
    - Email etiquette
    - Presentation and public speaking tips
    Offer clear explanations and examples for each query.

    User Query: {user_input}

    Your response:
    """
}

ROOM_DESCRIPTIONS = {
    "Interview Preparation":
    "Get expert advice on common interview questions, strategies, and tips to ace your next job interview.",
    "Mock Interview":
    "Practice your interview skills with our AI interviewer and receive personalized feedback to improve your performance.",
    "Resume Help":
    "Get assistance on creating and optimizing your resume to increase your chances of landing an interview.",
    "Resume Analysis":
    "Upload your resume and receive detailed feedback and suggestions for improvement.",
    "Workplace Tips":
    "Get valuable insights and advice on workplace dynamics and professional relationships.",
    "Business English":
    "Improve your business English skills with tips on communication, writing, and professionalism."
}


@st.cache_data
def load_chat_history(room):
    if room == "Mock Interview":
        return st.session_state.get('mock_interview_history', [])
    elif os.path.exists(HISTORY_FILES.get(room, "")):
        with open(HISTORY_FILES[room], "r") as f:
            return json.load(f)
    return []


def save_chat_history(history, room):
    if room == "Mock Interview":
        st.session_state['mock_interview_history'] = history
    else:
        with open(HISTORY_FILES[room], "w") as f:
            json.dump(history, f)


def generate_response(prompt, room):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "system",
                "content": CUSTOM_PROMPTS[room].format(user_input=prompt)
            }],
            temperature=1.2)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return e


def export_chat_history(history):
    content = "Chat History:\n\n"
    for message in history:
        content += f"{message['role'].capitalize()}: {message['content']}\n\n"
    return content


def import_chat_history(content):
    history = []
    current_role = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith("User: "):
            if current_role:
                history.append({
                    "role": current_role,
                    "content": " ".join(current_content)
                })
            current_role = "user"
            current_content = [line[6:]]
        elif line.startswith("Assistant: "):
            if current_role:
                history.append({
                    "role": current_role,
                    "content": " ".join(current_content)
                })
            current_role = "assistant"
            current_content = [line[11:]]
        elif line.strip() == "":
            continue
        else:
            current_content.append(line)

    if current_role:
        history.append({
            "role": current_role,
            "content": " ".join(current_content)
        })

    return history


def check_appropriate(input):
    response = client.chat.completions.create(model=MODEL,
                                              messages=[{
                                                  "role":
                                                  "system",
                                                  "content":
                                                  """
            You are a interview supervisor.Youare to checks if the user's answer is appropriate or not in terms of rudeness, innapropriate topics mentioned, use of profanity or anything that is unacceptable in an interview. Examples

             1. **Curse Words**: Identify and flag any explicit language (e.g., f***, s***, etc.).
             2. **Criminal Behavior**: Look for phrases that imply illegal activities (e.g., theft, drug use).
             3. **Disrespectful Speech**: Highlight language that is derogatory or demeaning toward individuals or groups.
             ...
             ...

             Do not flag phrases that may have negative connotations but are not explicitly harmful or offensive, such as "pulling all-nighters" or similar expressions, unless they directly indicate disrespect or negativity toward others.

              If the input is appropriate, respond with 'True'. If the input is not appropriate, respond with 'False'.
             """
                                              }, {
                                                  "role": "user",
                                                  "content": input
                                              }])
    return response.choices[0].message.content


def extreme_warning(input):
    response = client.chat.completions.create(model=MODEL,
                                              messages=[{
                                                  "role":
                                                  "system",
                                                  "content":
                                                  """
             You are a strict disciplinary teacher who specializes in interviews. You are to warn and scold user based on their innapropriate inputs.

             You should reply in the format of: 

             <warning emoji>MOCK TEST STOPPED!!!

             Reason~
             <Reason for stopping the mock test, due to users' behaviour>

             WARNING:
             <Give warning to users about the use of extreme words, innapropriate topics, etc.>

             <Explain possible consequences>

             <Explain how to avoid the same behaviour in the future>
            """
                                              }, {
                                                  "role": "user",
                                                  "content": input
                                              }])
    return response.choices[0].message.content


def get_next_interview_question(num, history):
    if num == 0:
        prompt = "Greet the user and Ask user about what profession/industry he is working towards and the position he wishes to apply for in the company"
    elif num == 1:
        prompt = "Ask user some relevant general questions to test user's observation, creativity and self-awareness."
    elif num <= 2:
        prompt = "ask user some relevant industry specific questions  to  test user knowledge and skills in that industry"
    elif num == 3:
        prompt = "Ask user a compeltely random question that tests user quick and critical thinking"
    elif num <= 6:
        prompt = "Ask user some relevant behavioural questions to test user's problem solving skills in different scenarios"
    else:
        prompt = "Ask user some cultural/motivation/Future goals questions"

    return generate_response(prompt, "Mock Interview (Question)")


def get_interview_feedback(history):
    prompt = "Provide constructive feedback on the interviewee's performance."
    return generate_response(prompt, "Mock Interview (Feedback)")


# Functions from resumeconst.py
def readpdf(pdf_file):
    """Read PDF file and extract text"""
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += str(page.extract_text())
    return text


def analyze_with_openai(messages):
    """Generic function to interact with OpenAI API"""
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                  messages=messages,
                                                  max_tokens=1000)
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error communicating with OpenAI: {str(e)}")
        return None


def analyze_job_requirements(job_description):
    """Analyze job description and extract requirements"""
    messages = [{
        "role":
        "system",
        "content":
        """
        As a professional HR Manager with 20 years of experience:
        Analyze this job description and extract job requirements.
        If the description is minimal, generate appropriate general requirements.
        Return the job position name and requirements only.
        """
    }, {
        "role": "user",
        "content": f"Job Description:\n{job_description}"
    }]
    return analyze_with_openai(messages)


def analyze_resume(resume_text, job_requirements):
    """Analyze resume against job requirements"""
    if len(resume_text) < 100:
        return "The File is not in ATS format, Please provide an ATS format resume"

    messages = [{
        "role":
        "system",
        "content":
        """
        As a professional HR Manager with 20 years of experience:
        Analyze this Resume and confirm if it is a resume.
        If yes, analyze it against the Job Requirements.
        Respond in the following strict format:

        1. *Resume Analysis*: [Provide analysis of the resume]
        2. *Suggestions to Improve*: [Suggestions to improve the resume for the specific job.]
        3. *ATS Reformatting*: [Reformatting suggestions to improve ATS readability of the Resume.]
        4. *Updated Resume*: [Provide the updated resume in ATS format.]
        SCORE:[A number range from 0 to 100, or 0 if the resume is not relevant.]
        If it is not a Resume, just output it is not a resume.
        """
    }, {
        "role":
        "user",
        "content":
        f"Resume:\n{resume_text}\n\nJob Requirements:\n{job_requirements}"
    }]
    return analyze_with_openai(messages)


def extract_score(analyze_result):
    """Extract numerical score from analysis result"""
    try:
        for line in analyze_result.split('\n'):
            if line.startswith('SCORE:'):
                score_str = line.replace('SCORE:', '').strip()
                return float(score_str)
        return 0
    except:
        return 0


def extract_suggestions(analyze_result):
    """Extract suggestions removing the score line"""
    return '\n'.join(line for line in analyze_result.split('\n')
                     if not line.startswith('SCORE:'))


def main():
    st.set_page_config(layout="wide")

    # Custom CSS for chat bubbles, layout, buttons, and timer
    st.markdown("""
            <style>
            ::selection {
                background-color: #FFD700; /* Highlight color */
                color: #000000; /* Text color when highlighted */
            }
            .stApp {
                background-color: #FAFAFA; 
            }
            .chat-bubble {
                padding: 10px;
                border-radius: 15px;
                margin-bottom: 10px;
                max-width: 80%;
                display: flex;
                align-items: flex-start;
            }
            .user-bubble {
                background-color: #E0E0E0; 
                color: #212121; 
                margin-left: auto;
            }
            .assistant-bubble {
                background-color: #F5F5F5; 
                color: #424242;
            }
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 10px;
            }
            .message-content {
                flex-grow: 1;
            }
            .stButton > button {
                background-color: #00897B;
                color: white;
                width: 100%;
                height: 50px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px; 
            }
            .stButton > button:hover {
                color:#FFC300;
                border: 1px solid;
                border-color: #FFC300;
            }
            .timer {
                font-size: 24px;
                font-weight: bold;
                color: #00897B; 
                text-align: center;
                padding: 10px;
                background-color: #E0F2F1; 
                border-radius: 10px;
                margin-bottom: 20px;
            }
        </style>
    """,
                unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; align-items: center;">
        <img src="https://static.thenounproject.com/png/1610456-200.png" alt="Logo" width="50" style="margin-right: 10px;">
        <h2 style="margin: 0; color:black">emploweeeee+</h2>
        <br>
    </div>
    <h4 style="color:black">. ݁₊ ⊹ . ݁˖ . ݁Your Unproblematic Coworker. ݁₊ ⊹ . ݁˖ . ݁</h4>
    """,
                unsafe_allow_html=True)

    def formal_translator(prompt):
        system_prompt = """
      Transform a informal or casual sentences into 3 professional language suitable for workplace communication.

      - Focus on maintaining professionalism and clarity in the revised sentences.
      - Avoid using slang, overly casual language, or ambiguous phrases.
      - Ensure that the core message of the original sentence is preserved.
      - Ensure that any sensitive or culturally specific terms are treated with respect and professionalism.
      - Maintain the formality level consistent with typical workplace communication guidelines.

      # Steps
      1. Analyze the provided sentence to understand its core message.
      2. Identify any informal or casual language that needs to be transformed.
      3. Rewrite the sentence using professional language, ensuring clarity and appropriateness for a workplace setting.
      4. Review the transformed sentence to ensure the core message is intact, simple and professional.
      5. Convert negative sentences to positive messages

      # Output Format
      - The output should be 3 single, professionally rewritten sentences each separated by an empty line.
      - Maintain clarity and conciseness in the revised sentence.

      Example:
      
      (1) <alternative 1>
      
      (2) <alternative 2>
      
      (3) <alternative 3>

      
      """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": "Give this to John?"
            }, {
                "role":
                "assistant",
                "content":
                """
                  (1) Could you please kindly help me to hand the documents to John? <br>
                  (2) Please pass this document to John. <br>
                  (3) Please hand this over to John. <br>
                  """
            }, {
                "role": "user",
                "content": "I need that report, like, yesterday!"
            }, {
                "role":
                "assistant",
                "content":
                """
                  (1) Could you please prioritize and send me the report as soon as possible? <br>
                  (2) I would greatly appreciate it if you could provide that report at your earliest convenience. <br>
                  (3) I would appreciate it if you could expedite the delivery of that report. Thank you for your prompt attention to this matter. <br>
                  """
            }, {
                "role": "user",
                "content": "That idea sounds kinda off."
            }, {
                "role":
                "assistant",
                "content":
                """
                  (1) I have some reservations about that idea, but we can have a try on it. <br>
                  (2) It may be beneficial to reconsider that idea for improved alignment with our objectives. <br>
                  (3) I believe we should explore alternative approaches, as this idea may not fully meet our expectations.
                  """
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=1.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content

    # Navigation buttons
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if st.button("Interview Help"):
            st.session_state.room = "Interview Preparation"
    with col2:
        if st.button("Mock Interview"):
            st.session_state.room = "Mock Interview"
    with col3:
        if st.button("Resume Help"):
            st.session_state.room = "Resume Help"
    with col4:
        if st.button("Resume Analysis"):
            st.session_state.room = "Resume Analysis"
    with col5:
        if st.button("Workplace Tips"):
            st.session_state.room = "Workplace Tips"
    with col6:
        if st.button("Business English"):
            st.session_state.room = "Business English"

    # Initialize room if not set
    if 'room' not in st.session_state:
        st.session_state.room = "Interview Preparation"

    room = st.session_state.room
    st.markdown(f"""
    <h2 style="color:black"> Current Room: {room} </h2>
    <h4 style="color:coral">Chat clears as you refresh the page. Please download a copy of your chat history before refreshing.</h4>
    """,
                unsafe_allow_html=True)

    st.markdown(f"""
        <div style='background-color: #E0F7FA; padding: 10px; border-radius: 8px; border: 1px solid #B2EBF2; margin-bottom: 20px;'>
            <p style='color:black; margin: 0;'>{ROOM_DESCRIPTIONS[room]}</p>
        </div>
    """,
                unsafe_allow_html=True)

    # Initialize session state for chat histories if they don't exist
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {
            r: load_chat_history(r)
            for r in HISTORY_FILES.keys()
        }

    # Initialize mock interview state
    if 'mock_interview_state' not in st.session_state:
        st.session_state.mock_interview_state = {
            'started': False,
            'end_time': None,
            'question_count': 0,
            'max_questions': 5,
            'feedback_given': False
        }
    if 'mock_interview_history' not in st.session_state:
        st.session_state.mock_interview_history = []

    # Sidebar for utility functions
    with st.sidebar:
        st.header("Chat Utilities")

        if st.download_button(
                label="Download Chat History",
                data=export_chat_history(
                    st.session_state.mock_interview_history if room ==
                    "Mock Interview" else st.session_state.chat_histories[room]
                ),
                file_name=f"{room.lower().replace(' ', '_')}_chat_history.txt",
                mime="text/plain",
                key="download_chat_history"):
            st.success("Chat history downloaded!")

        if st.button("Clear Chat History"):
            if room == "Mock Interview":
                st.session_state.mock_interview_history = []
            else:
                st.session_state.chat_histories[room] = []
                save_chat_history([], room)
            st.success("Chat history cleared!")
            st.rerun()

        uploaded_file = st.file_uploader("Import Chat History", type="txt")
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            imported_history = import_chat_history(content)
            if st.button("Restore Imported Chat History"):
                st.session_state.chat_histories[room] = imported_history
                save_chat_history(imported_history, room)
                st.success("Chat history restored!")
                st.rerun()

    # User input and chat logic
    if room == "Mock Interview":
        # Display chat history for Mock Interview
        for message in st.session_state.mock_interview_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class='chat-bubble user-bubble'>
                    <img src='https://brandeps.com/icon-download/U/User-icon-21.png' class='avatar'>
                    <div class='message-content'>{message['content']}</div>
                </div>
                """,
                            unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-bubble assistant-bubble'>
                    <img src='https://static.thenounproject.com/png/1610456-200.png' class='avatar'>
                    <div class='message-content'>{message['content']}</div>
                </div>
                """,
                            unsafe_allow_html=True)

        if not st.session_state.mock_interview_state['started']:
            if st.button("Start New Mock Interview"):
                st.session_state.mock_interview_history = []
                st.session_state.mock_interview_state = {
                    'started': True,
                    'end_time': datetime.now() + timedelta(minutes=20),
                    'question_count': 0,
                    'max_questions': 4,
                    'feedback_given': False
                }
                question = get_next_interview_question(
                    st.session_state.mock_interview_state["question_count"],
                    [])
                st.session_state.mock_interview_history.append({
                    "role":
                    "assistant",
                    "content":
                    question
                })
                st.session_state.mock_interview_state['question_count'] += 1
                st.rerun()

        if st.session_state.mock_interview_state['started']:
            # Display timer
            remaining_time = st.session_state.mock_interview_state[
                'end_time'] - datetime.now()
            if remaining_time.total_seconds() > 0:
                minutes, seconds = divmod(remaining_time.seconds, 60)
                st.markdown(
                    f"<div class='timer'>Time Remaining: {minutes:02d}:{seconds:02d}</div>",
                    unsafe_allow_html=True)
            else:
                st.markdown("<div class='timer'>Time's Up!</div>",
                            unsafe_allow_html=True)
                st.session_state.mock_interview_state['started'] = False

        # Chat input for the mock interview
        user_input = st.chat_input("Your answer here...")

        if user_input and st.session_state.mock_interview_state['started']:
            st.session_state.mock_interview_history.append({
                "role":
                "user",
                "content":
                user_input
            })

            if check_appropriate(user_input) != "True":
                st.session_state.mock_interview_history.append({
                    "role":
                    "assistant",
                    "content":
                    extreme_warning(user_input)
                })
                st.session_state.mock_interview_state['feedback_given'] = True
                st.session_state.mock_interview_state['started'] = False

            elif st.session_state.mock_interview_state[
                    'question_count'] < st.session_state.mock_interview_state[
                        'max_questions']:
                next_question = get_next_interview_question(
                    st.session_state.mock_interview_state["question_count"],
                    st.session_state.mock_interview_history)
                st.session_state.mock_interview_history.append({
                    "role":
                    "assistant",
                    "content":
                    next_question
                })
                st.session_state.mock_interview_state['question_count'] += 1
            elif not st.session_state.mock_interview_state['feedback_given']:
                feedback = get_interview_feedback(
                    st.session_state.mock_interview_history)
                st.session_state.mock_interview_history.append({
                    "role":
                    "assistant",
                    "content":
                    "Thank you for completing the mock interview. Here's your feedback:\n\n"
                    + feedback
                })
                st.session_state.mock_interview_state['feedback_given'] = True
                st.session_state.mock_interview_state['started'] = False

            save_chat_history(st.session_state.mock_interview_history,
                              'Mock Interview')
            st.rerun()

    elif room == "Business English":
        st.markdown(
            f"<h5 style='color: black; padding:0px;margin:0px;'><b>Enter A Sentence:</h5>",
            unsafe_allow_html=True)
        sentence = st.text_input("")
        if st.button("Translate"):
            formal = formal_translator(sentence)
            st.markdown(
                f"<div style='color: black'><b><u>Alternative sentence</u></b><br>{formal}</div>",
                unsafe_allow_html=True)

    elif room == "Resume Analysis":
        st.markdown(
            f"<h5 style='color: black; padding:0px;margin:0px;'><b>Enter the Job Description:</b></h5>",
            unsafe_allow_html=True)
        job_description = st.text_area('', height=150)

        st.markdown(
            f"<h5 style='color: black; padding:0px;margin:0px;'><b>Upload Your Resume (Text-based PDF):</b></h5>",
            unsafe_allow_html=True)
        uploaded_file = st.file_uploader('', type=['pdf'])

        if st.button('Analyze Resume'):
            if not job_description:
                st.error("Please enter a job description")
            elif not uploaded_file:
                st.error("Please upload a resume file")
            else:
                try:
                    with st.spinner('Analyzing your resume...'):
                        resume_text = readpdf(uploaded_file)
                        job_summary = analyze_job_requirements(job_description)
                        analyze_result = analyze_resume(
                            resume_text, job_summary)

                        score = extract_score(analyze_result)
                        suggestions = extract_suggestions(analyze_result)

                        st.markdown(
                            f"<h3 style='color: black;'>Resume Match Score:</h3>",
                            unsafe_allow_html=True)
                        st.markdown(
                            f"<h1 style='color: black;'>{int(score)}%</h1>",
                            unsafe_allow_html=True)
                        st.progress(score / 100)
                        st.markdown(
                            f"<h5 style='color: black;'>{suggestions}</h5>",
                            unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Display chat history for other rooms
        for message in st.session_state.chat_histories[room]:
            if message["role"] == "user":
                st.markdown(f"""
                <div class='chat-bubble user-bubble'>
                    <img src='https://brandeps.com/icon-download/U/User-icon-21.png' class='avatar'>
                    <div class='message-content'>{message['content']}</div>
                </div>
                """,
                            unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-bubble assistant-bubble'>
                    <img src='https://static.thenounproject.com/png/1610456-200.png' class='avatar'>
                    <div class='message-content'>{message['content']}</div>
                </div>
                """,
                            unsafe_allow_html=True)

        # General chat input for other rooms
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Store the user input in the chat history
            st.session_state.chat_histories[room].append({
                "role": "user",
                "content": user_input
            })
            response = generate_response(user_input, room)
            st.session_state.chat_histories[room].append({
                "role": "assistant",
                "content": response
            })
            save_chat_history(st.session_state.chat_histories[room], room)
            st.rerun()


if __name__ == "__main__":
    main()
