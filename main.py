import numpy

import streamlit as st
import pandas as pd

# TODO: Save results DF to csv file
# TODO: Add documentation to sidebar
# TODO: Create admin ability to set up groups and see group results
# TODO: Create file for logging who took tests, when, and with what groups

st.set_page_config(layout='wide')

st.title('Becoming a Calibrated Estimator Workshop')
st.sidebar.write('Welcome to the "Becoming a Calibrated Estimator Workshop."')


# Callback functions
def init_form_callback():
	st.session_state['user_name'] = st.session_state['init_name']
	st.session_state['group_id'] = st.session_state['init_group_id']
	st.session_state['session_status'] = 'init_form_submitted'


def quiz_form_callback():
	st.session_state['quiz_name'] = st.session_state['init_quiz_name']
	st.session_state['session_status'] = 'quiz_form_submitted'


def quiz_answer_callback():
	got_answer_correct = check_for_correct_answer(question_row['AnswerFormat'],
												  question_row['Solution'],
												  st.session_state['answer_lower_bound'],
												  st.session_state['answer_upper_bound'])
	answer_df = pd.DataFrame([[st.session_state['user_name'],
							   st.session_state['group_id'],
							   str(question_row['Question']),
							   str(question_row['Solution']),
							   str(question_row['AnswerFormat']),
							   str(got_answer_correct),
							   str(st.session_state['answer_lower_bound']),
							   str(st.session_state['answer_upper_bound'])]], columns=['UserName', 'GroupID',
																					   'Question', 'Solution',
																					   'AnswerFormat', 'CorrectAnswer',
																					   'LowerBound', 'UpperBound'])
	st.session_state['answers_df'] = pd.concat([st.session_state['answers_df'], answer_df], ignore_index=True)
	if st.session_state['current_index'] >= st.session_state['max_index']:
		st.session_state['session_status'] = 'quiz_finished'
	else:
		st.session_state['current_index'] += 1

	st.dataframe(st.session_state['answers_df'])


def reset_to_start():
	for key in st.session_state.keys():
		del st.session_state[key]


def calculate_90_ci_results():
	answers_df = st.session_state['answers_df']
	bounds_mask = answers_df['AnswerFormat'] != 'Binary'
	bounds_questions = answers_df.loc[bounds_mask]
	bounds_questions.reset_index(drop=True, inplace=True)
	total_num_questions = len(bounds_questions)
	if total_num_questions == 0:
		return
	correct_mask = bounds_questions['CorrectAnswer'] == 'True'
	correct_questions = bounds_questions.loc[correct_mask]
	num_of_correct_questions = len(correct_questions)
	percent_of_correct_questions = num_of_correct_questions/total_num_questions

	st.subheader('90% Confidence Questions Results:')
	st.write(f'You got {num_of_correct_questions} out of {total_num_questions} "90% Confidence" questions correct.')
	if percent_of_correct_questions > 0.6:
		st.write('Based on your answers, you MAY be a calibrated estimator.')
	elif (percent_of_correct_questions > 0.3) and (percent_of_correct_questions <= 0.6):
		st.write('Based on your answers, there is only a 1.3% chance that you are a calibrated estimator. '
				 'You are likely over-confident in your estimates.')
	elif percent_of_correct_questions <= 0.3:
		st.write('Based on your answers, there is only a 1 in 100,000 chance that you are a calibrated estimator. '
				 'You are likely over-confident in your estimates.')


def calculate_binary_results():
	answers_df = st.session_state['answers_df']
	bounds_mask = answers_df['AnswerFormat'] == 'Binary'
	bounds_questions = answers_df.loc[bounds_mask]
	bounds_questions.reset_index(drop=True, inplace=True)
	total_num_questions = len(bounds_questions)
	if total_num_questions == 0:
		return
	correct_mask = bounds_questions['CorrectAnswer'] == 'True'
	correct_questions = bounds_questions.loc[correct_mask]
	num_of_correct_questions = len(correct_questions)

	complete_confidence_mask = bounds_questions['UpperBound'] == '100'
	num_of_complete_confidence = len(bounds_questions.loc[complete_confidence_mask])
	complete_confidence_correct_mask = correct_questions['UpperBound'] == '100'
	num_of_correct_complete_confidence = len(correct_questions.loc[complete_confidence_correct_mask])

	confidence_series = bounds_questions['UpperBound'].astype(int)
	expected_num_correct = (confidence_series.sum())/100

	st.subheader('True/False Questions Results:')
	st.write(f'Based on your confidence ratings, you expected to get {expected_num_correct} True/False questions correct.')
	st.write(f'You actually got {num_of_correct_questions} out of {total_num_questions} True/False questions correct.')
	if num_of_complete_confidence == num_of_correct_complete_confidence:
		st.write(f'You got all {num_of_correct_complete_confidence} questions which you gave 100% confidence correct.')
	else:
		st.write(f'Of the {num_of_complete_confidence} questions you marked with 100% confidence, you only got '
				 f'{num_of_correct_complete_confidence} questions correct.')


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
	quiz_form.selectbox('Quiz:', question_file['FileName'], key='init_quiz_name')
	quiz_form.form_submit_button(label='Begin', on_click=quiz_form_callback)
	st.session_state['session_status'] = 'quiz_form_displaying'

# initial quiz setup
if st.session_state['session_status'] == 'quiz_form_submitted':
	quiz_name = "Files/" + st.session_state['quiz_name'] + ".csv"
	questions = pd.read_csv(quiz_name)
	questions['Solution'] = questions['Solution'].astype(str)
	st.session_state['questions'] = questions
	st.session_state['current_index'] = 0
	st.session_state['max_index'] = len(questions) - 1
	st.session_state['answers_df'] = pd.DataFrame(columns=['UserName', 'GroupID',
														   'Question', 'Solution',
														   'AnswerFormat', 'CorrectAnswer',
														   'LowerBound', 'UpperBound'])
	st.session_state['session_status'] = 'quiz_underway'

# display one quiz question
if st.session_state['session_status'] == 'quiz_underway':
	quest_num = st.session_state['current_index']
	question_row = st.session_state['questions'].iloc[quest_num]
	question = question_row['Question']
	answer_format = question_row['AnswerFormat']
	st.subheader(f'Taking "{st.session_state["quiz_name"]}" quiz')
	st.header(question)
	with st.form('question'):
		if answer_format == 'Number':
			col1, col2 = st.columns(2)
			with col1:
				st.number_input(label='Lower Bound', value=0, key='answer_lower_bound')
			with col2:
				st.number_input(label='Upper Bound',value=0, key='answer_upper_bound')
		elif answer_format == 'Year':
			col1, col2 = st.columns(2)
			with col1:
				st.number_input(label='Lower Year', format='%u', step=1, value=0, key='answer_lower_bound')
			with col2:
				st.number_input(label='Upper Year', format='%u', step=1, value=0, key='answer_upper_bound')
		elif answer_format == 'Percentage':
			st.slider(label='Lower %', min_value=0, max_value=100, value=0, key='answer_lower_bound')
			st.slider(label='Upper %', min_value=0, max_value=100, value=100, key='answer_upper_bound')
		elif answer_format == 'Binary':
			st.radio(label='Is this True or False?', options=('True', 'False'), index=0, key='answer_lower_bound')
			st.radio(label='How confident are you?', options=(50, 60, 70, 80, 90, 100), index=0,
								 key='answer_upper_bound')
		else:
			print('Unknown answer format when creating form')

		if st.session_state['current_index'] >= st.session_state['max_index']:
			st.form_submit_button(label='FINISH QUIZ', on_click=quiz_answer_callback)
		else:
			st.form_submit_button(label='Next Question', on_click=quiz_answer_callback)


if st.session_state['session_status'] == 'quiz_finished':
	st.header('Do you feel like a calibrated estimator?')
	calculate_90_ci_results()
	calculate_binary_results()
	st.subheader('To take another quiz, click the button below')
	st.button(label='Take again', on_click=reset_to_start)


####################
# Internal Functions
####################
def check_for_correct_answer(in_answer_format: str, in_solution, in_lower_bound, in_upper_bound) -> bool:
	return_bool = False
	if (in_answer_format == 'Number') or (in_answer_format == 'Year'):
		if (float(in_solution) >= in_lower_bound) and (float(in_solution) <= in_upper_bound):
			return_bool = True

	elif in_answer_format == 'Percentage':
		formatted_solution = float(in_solution.strip('%'))
		if (formatted_solution >= in_lower_bound) and (formatted_solution <= in_upper_bound):
			return_bool = True

	elif in_answer_format == 'Binary':
		solution_bool = False
		if (in_solution == 'TRUE') or (in_solution == 'True'):
			solution_bool = True

		answer_bool = False
		if in_lower_bound == 'True':
			answer_bool = True
		if solution_bool == answer_bool:
			return_bool = True

	else:
		print('Unknown answer format when calculating result')

	return return_bool


st.write(st.session_state)
