import streamlit as st
import pandas as pd

st.set_page_config(layout='wide')

st.title('Becoming a Calibrated Estimator Workshop')
st.sidebar.write('Welcome to the "Becoming a Calibrated Estimator Workshop."')


# Callback functions
def init_form_callback():
	st.session_state['session_status'] = 'init_form_submitted'


def quiz_form_callback():
	st.session_state['session_status'] = 'quiz_form_submitted'


def quiz_answer_callback():
	answer_df = pd.DataFrame([[question_row['Question'],
							  question_row['CorrectAnswer'],
							  st.session_state['answer_lower_bound'],
							  st.session_state['answer_upper_bound']]], columns=['Question', 'CorrectAnswer',
																				'LowerBound', 'UpperBound'])
	st.session_state['answers_df'] = pd.concat([st.session_state['answers_df'], answer_df], ignore_index=True)
	st.session_state['current_index'] += 1

# display the initialization form
if 'session_status' not in st.session_state:
	init_form = st.form('init_form')
	init_form.text_input('Please enter your name', key='init_name')
	init_form.text_input('If you are with a group, please enter group ID below (otherwise leave blank)',
										 key='init_group_id')
	init_form.form_submit_button(label='Start Workshop', on_click=init_form_callback)
	st.session_state['session_status'] = 'init_displaying'

# display the quiz selection form
if st.session_state['session_status'] == 'init_form_submitted':
	question_file = pd.read_csv('Files/QuizList.csv')
	st.header("Which test would you like to take?")
	quiz_form = st.form('quiz')
	quiz_form.selectbox('Quiz:', question_file['FileName'], key='quiz_name')
	quiz_form.form_submit_button(label='Begin', on_click=quiz_form_callback)
	st.session_state['session_status'] = 'quiz_form_displaying'

# initial quiz setup
if st.session_state['session_status'] == 'quiz_form_submitted':
	quiz_name = "Files/" + st.session_state['quiz_name'] + ".csv"
	questions = pd.read_csv(quiz_name)
	st.session_state['questions'] = questions
	st.session_state['current_index'] = 0
	st.session_state['max_index'] = len(questions) - 1
	st.session_state['answers_df'] = pd.DataFrame(columns=['Question', 'CorrectAnswer', 'LowerBound', 'UpperBound'])
	st.session_state['session_status'] = 'quiz_underway'

# display one quiz question
if st.session_state['session_status'] == 'quiz_underway':
	quest_num = st.session_state['current_index']
	question_row = st.session_state['questions'].iloc[quest_num]
	question = question_row['Question']
	answer_format = question_row['AnswerFormat']
	correct_answer = question_row['CorrectAnswer']

	st.header(question)
	question_form = st.form('question')
	if answer_format == 'Number':
		question_form.number_input(label='Lower Bound', key='answer_lower_bound')
		question_form.number_input(label='Upper Bound', key='answer_upper_bound')
	elif answer_format == 'Year':
		question_form.number_input(label='Lower Year', format='%u', step=1, key='answer_lower_bound')
		question_form.number_input(label='Upper Year', format='%u', step=1, key='answer_upper_bound')
	elif answer_format == 'Percentage':
		question_form.slider(label='Lower %', min_value=0, max_value=100, value=0, key='answer_lower_bound')
		question_form.slider(label='Upper %', min_value=0, max_value=100, value=100, key='answer_upper_bound')
	elif answer_format == 'Binary':
		question_form.radio(label='Is this True or False?', options=('True', 'False'), key='answer_lower_bound')
		question_form.radio(label='How confident are you?', options=(50, 60, 70, 80, 90, 100),
							 key='answer_upper_bound')
	question_form.form_submit_button(label='Next', on_click=quiz_answer_callback)


st.write(st.session_state)
