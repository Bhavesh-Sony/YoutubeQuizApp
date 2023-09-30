import streamlit as st
from helpers.youtube_utils import extract_video_id_from_url, get_transcript_text
from helpers.openai_utils import get_quiz_data
from helpers.quiz_utils import string_to_list, get_randomized_options
from helpers.toast_messages import get_random_toast


st.set_page_config(
    page_title="YoutubeQuizAPP",
    page_icon="🧠",
    layout="centered",
)

# Check if user is new or returning using session state.
# If user is new, show the toast message.
if 'first_time' not in st.session_state:
    message, icon = get_random_toast()
    st.toast(message, icon=icon)
    st.session_state.first_time = False

st.title(":red[Youtube-Quiz] — Explore your YouTube experience in a whole new way with YouTube-Quiz! 📺🧠", anchor=False)
st.write("""
Have you ever wondered how well you've understood a YouTube video's content? Well, here's an exciting twist: Instead of just passively watching videos on YouTube, come on over to **YoutubeQuiz** and put your comprehension to the test!

Wondering how it all works? 🤔

Note: Remember, the video must have English captions for the tool to function effectively.
Once you've provided these details, presto! You'll be presented with a series of tailored questions designed just for you, ensuring that you've truly grasped the video's content. It's time to challenge your knowledge! 🚀


1. Simply paste the URL of the YouTube video you've recently watched.
2. Enter your OpenAI API Key.
 
""")

with st.form("user_input"):
    YOUTUBE_URL = st.text_input("Enter the YouTube video link:", value="https://youtu.be/bcYwiwsDfGE?si=qQ0nvkmKkzHJom2y")
    OPENAI_API_KEY = st.text_input("Enter your OpenAI API Key:", placeholder="sk-XXXX", type='password')
    submitted = st.form_submit_button("Craft my quiz!")

if submitted or ('quiz_data_list' in st.session_state):
    if not YOUTUBE_URL:
        st.info("Please provide a valid YouTube video link. Head over to [YouTube](https://www.youtube.com/) to fetch one.")
        st.stop()
    elif not OPENAI_API_KEY:
        st.info("Please fill out the OpenAI API Key to proceed. If you don't have one, you can obtain it [here](https://platform.openai.com/account/api-keys).")
        st.stop()
        
    with st.spinner("Crafting your quiz...🤓"):
        if submitted:
            video_id = extract_video_id_from_url(YOUTUBE_URL)
            video_transcription = get_transcript_text(video_id)
            quiz_data_str = get_quiz_data(video_transcription, OPENAI_API_KEY)
            st.session_state.quiz_data_list = string_to_list(quiz_data_str)

            if 'user_answers' not in st.session_state:
                st.session_state.user_answers = [None for _ in st.session_state.quiz_data_list]
            if 'correct_answers' not in st.session_state:
                st.session_state.correct_answers = []
            if 'randomized_options' not in st.session_state:
                st.session_state.randomized_options = []

            for q in st.session_state.quiz_data_list:
                options, correct_answer = get_randomized_options(q[1:])
                st.session_state.randomized_options.append(options)
                st.session_state.correct_answers.append(correct_answer)

        with st.form(key='quiz_form'):
            st.subheader("🧠 Quiz Time: Test Your Knowledge!", anchor=False)
            for i, q in enumerate(st.session_state.quiz_data_list):
                options = st.session_state.randomized_options[i]
                default_index = st.session_state.user_answers[i] if st.session_state.user_answers[i] is not None else 0
                response = st.radio(q[0], options, index=default_index)
                user_choice_index = options.index(response)
                st.session_state.user_answers[i] = user_choice_index  # Update the stored answer right after fetching it


            results_submitted = st.form_submit_button(label='Unveil My Score!')
            if results_submitted:
                score = sum([ua == st.session_state.randomized_options[i].index(ca) for i, (ua, ca) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers))])
                st.success(f"Your score: {score}/{len(st.session_state.quiz_data_list)}")

                if score == len(st.session_state.quiz_data_list):  # Check if all answers are correct
                    st.balloons()
                else:
                    incorrect_count = len(st.session_state.quiz_data_list) - score
                    if incorrect_count == 1:
                        st.warning(f"Almost perfect! You got 1 question wrong. Let's review it:")
                    else:
                        st.warning(f"Almost there! You got {incorrect_count} questions wrong. Let's review them:")

                for i, (ua, ca, q, ro) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers, st.session_state.quiz_data_list, st.session_state.randomized_options)):
                    with st.expander(f"Question {i + 1}", expanded=False):
                        if ro[ua] != ca:
                            st.info(f"Question: {q[0]}")
                            st.error(f"Your answer: {ro[ua]}")
                            st.success(f"Correct answer: {ca}")