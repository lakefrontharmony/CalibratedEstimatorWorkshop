import streamlit as st
import pandas as pd

st.set_page_config(layout='wide')

st.title('Becoming a Calibrated Estimator Workshop')
st.sidebar.write('Welcome to the "Becoming a Calibrated Estimator Workshop."')


def init_form_callback():
	st.session_state['session_status'] = 'init_form_submitted'


def quiz_form_callback():
	st.session_state['session_status'] = 'quiz_form_submitted'


if 'session_status' not in st.session_state:
	init_form = st.form('init_form')
	init_form.text_input('Please enter your name', key='init_name')
	init_form.text_input('If you are with a group, please enter group ID below (otherwise leave blank)',
										 key='init_group_id')
	init_form.form_submit_button(label='Start Workshop', on_click=init_form_callback)
	st.session_state['session_status'] = 'init_displaying'

if st.session_state['session_status'] == 'init_form_submitted':
	question_file = pd.read_csv('Files/QuizList.csv')
	st.header("Which test would you like to take?")
	quiz_form = st.form('quiz')
	quiz_form.selectbox('Quiz:', question_file['FileName'], key='quiz_name')
	quiz_form.form_submit_button(label='Begin', on_click=quiz_form_callback)
	st.session_state['session_status'] = 'quiz_form_displaying'

if st.session_state['session_status'] == 'quiz_form_submitted':
	quiz_name = "Files/" + st.session_state['quiz_name'] + ".csv"
	question_file = pd.read_csv(quiz_name)
	st.write(question_file)

st.write(st.session_state)
