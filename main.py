import fnmatch
import os

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime as dt

# TODO: Create admin ability to set up groups and see group results.
# TODO: Create admin ability to read through all exports, consolidate to one file, and delete individual files.
# TODO: Add documentation to sidebar.
# TODO: Create ability to export your results to your desktop.

st.set_page_config(layout='wide')

st.title('Becoming a Calibrated Estimator Workshop')
st.sidebar.write('Welcome to the "Becoming a Calibrated Estimator Workshop."')


####################
# Internal Functions
####################
# Callback functions
def init_form_callback():
	st.session_state['user_name'] = st.session_state['init_name']
	st.session_state['group_id'] = st.session_state['init_group_id']
	if len(st.session_state['user_name']) == 0:
		st.warning('You must supply a Name to take this Quiz')
		del st.session_state['session_status']
	else:
		st.session_state['session_status'] = 'init_form_submitted'


def display_admin_screen():
	st.session_state['session_status'] = 'admin_options'


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
							   st.session_state['quiz_datetime'],
							   str(question_row['Question']),
							   str(question_row['AnswerFormat']),
							   str(got_answer_correct),
							   str(question_row['Solution']),
							   str(st.session_state['answer_lower_bound']),
							   str(st.session_state['answer_upper_bound'])]],
							 columns=['UserName', 'GroupID', 'QuizDateTime', 'Question', 'AnswerFormat',
									  'CorrectAnswer', 'Solution', 'LowerBound', 'UpperBound'])
	st.session_state['answers_df'] = pd.concat([st.session_state['answers_df'], answer_df], ignore_index=True)
	if st.session_state['current_index'] >= st.session_state['max_index']:
		st.session_state['session_status'] = 'quiz_finished'
	else:
		st.session_state['current_index'] += 1


# helper functions
def reset_to_start():
	for key in st.session_state.keys():
		del st.session_state[key]


def search_for_files():
	master_file_name = 'Files/MasterResults.csv'
	exports_dir = 'Files/Exports'
	st.session_state['export_result_file_names'] = []
	st.session_state['export_summary_file_names'] = []
	files = os.scandir(exports_dir)
	for filename in files:
		print(f'checking: {filename}')
		if fnmatch.fnmatch(name=filename.name, pat='*Results.csv'):
			st.session_state['export_result_file_names'].append(exports_dir + '/' + filename.name)
		if fnmatch.fnmatch(name=filename.name, pat='*Summary.csv'):
			st.session_state['export_summary_file_names'].append(exports_dir + '/' + filename.name)


def add_to_master_record():
	# TODO: Check if master record exists (Excel file).
	# TODO: Read in any existing master record and create one dataframe for summary and one for results.
	# TODO: Append new summary and new results.
	# TODO: Write out new Excel master record file.
	# TODO: Delete individual files.
	pass


def calculate_90_ci_results():
	answers_df = st.session_state['answers_df']
	bounds_mask = answers_df['AnswerFormat'] != 'Binary'
	bounds_questions = answers_df.loc[bounds_mask]
	bounds_questions.reset_index(drop=True, inplace=True)
	total_num_questions = len(bounds_questions)
	st.session_state['num_90_ci_questions'] = total_num_questions
	st.session_state['num_90_ci_correct'] = 0
	if total_num_questions == 0:
		return
	correct_mask = bounds_questions['CorrectAnswer'] == 'True'
	correct_questions = bounds_questions.loc[correct_mask]
	num_of_correct_questions = len(correct_questions)
	st.session_state['num_90_ci_correct'] = num_of_correct_questions
	percent_of_correct_questions = num_of_correct_questions/total_num_questions

	st.subheader('90% Confidence Questions Results:')
	st.write(f'You got {num_of_correct_questions} out of {total_num_questions} "90% Confidence" questions correct.')
	if percent_of_correct_questions > 0.6:
		st.write('Based on your answers, you MAY be a calibrated estimator or you MAY be under-confident '
				 '(i.e. You made your range of answers very large).')
	elif (percent_of_correct_questions > 0.3) and (percent_of_correct_questions <= 0.6):
		st.write('Based on your answers, there is only a 1.3% chance that you are a calibrated estimator. '
				 'You are likely over-confident in your estimates.')
	elif percent_of_correct_questions <= 0.3:
		st.write('Based on your answers, there is only a 1 in 100,000 chance that you are a calibrated estimator. '
				 'You are likely over-confident in your estimates.')


def calculate_binary_results():
	st.session_state['num_binary_correct'] = 0
	st.session_state['num_binary_100_confidence'] = 0
	st.session_state['num_binary_100_confidence_correct'] = 0
	st.session_state['num_binary_expected_confidence_correct'] = 0
	answers_df = st.session_state['answers_df']
	bounds_mask = answers_df['AnswerFormat'] == 'Binary'
	bounds_questions = answers_df.loc[bounds_mask]
	bounds_questions.reset_index(drop=True, inplace=True)
	total_num_questions = len(bounds_questions)
	st.session_state['num_binary_questions'] = total_num_questions
	if total_num_questions == 0:
		return
	correct_mask = bounds_questions['CorrectAnswer'] == 'True'
	correct_questions = bounds_questions.loc[correct_mask]
	num_of_correct_questions = len(correct_questions)
	st.session_state['num_binary_correct'] = num_of_correct_questions

	complete_confidence_mask = bounds_questions['UpperBound'] == '100'
	num_of_complete_confidence = len(bounds_questions.loc[complete_confidence_mask])
	st.session_state['num_binary_100_confidence'] = num_of_complete_confidence
	complete_confidence_correct_mask = correct_questions['UpperBound'] == '100'
	num_of_correct_complete_confidence = len(correct_questions.loc[complete_confidence_correct_mask])
	st.session_state['num_binary_100_confidence_correct'] = num_of_correct_complete_confidence

	confidence_series = bounds_questions['UpperBound'].astype(int)
	expected_num_correct = (confidence_series.sum())/100
	st.session_state['num_binary_expected_confidence_correct'] = expected_num_correct

	st.subheader('True/False Questions Results:')
	st.write(f'Based on your confidence ratings, you expected to get {expected_num_correct} True/False questions correct.')
	st.write(f'You actually got {num_of_correct_questions} out of {total_num_questions} True/False questions correct.')
	if num_of_complete_confidence == num_of_correct_complete_confidence:
		st.write(f'You got all {num_of_correct_complete_confidence} questions which you gave 100% confidence correct.')
	else:
		st.write(f'Of the {num_of_complete_confidence} questions you marked with 100% confidence, you only got '
				 f'{num_of_correct_complete_confidence} questions correct.')


def write_results_to_csv():
	export_file_name = f'Files/Exports/' + st.session_state['user_name'] + ' Results.csv'
	export_file = Path(export_file_name)
	if export_file.is_file():
		answer_csv = pd.read_csv(export_file_name)
		concat_df = pd.concat([st.session_state['answers_df'], answer_csv], ignore_index=True)
		concat_df.to_csv(export_file_name, index=False)
	else:
		st.session_state['answers_df'].to_csv(export_file_name, index=False)


def write_summary_to_csv():
	st.session_state['summary_df'] = pd.DataFrame([[st.session_state['user_name'],
								st.session_state['group_id'],
								st.session_state['quiz_name'],
								st.session_state['quiz_datetime'],
								st.session_state['num_90_ci_questions'],
								st.session_state['num_90_ci_correct'],
								st.session_state['num_binary_questions'],
								st.session_state['num_binary_correct'],
								st.session_state['num_binary_expected_confidence_correct'],
								st.session_state['num_binary_100_confidence'],
								st.session_state['num_binary_100_confidence_correct']]],
							  columns=['UserName', 'GroupID', 'QuizName', 'DateTime',
									   'Num90CIQuestions', 'Num90CICorrect',
									   'NumBinaryQuestions', 'NumBinaryCorrect',
									   'ExpectedBinaryCorrect', 'Binary100PctConfidence',
									   'Binary100PctConfidenceCorrect'])
	export_file_name = f'Files/Exports/' + st.session_state['user_name'] + ' Summary.csv'
	export_file = Path(export_file_name)
	if export_file.is_file():
		summary_csv = pd.read_csv(export_file_name)
		concat_df = pd.concat([st.session_state['summary_df'], summary_csv], ignore_index=True)
		concat_df.to_csv(export_file_name, index=False)
	else:
		st.session_state['summary_df'].to_csv(export_file_name, index=False)


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


####################
# Display Flow
####################
# display the initialization form
if 'session_status' not in st.session_state:
	init_form = st.form('init_form')
	init_form.text_input('Please enter your name', key='init_name')
	init_form.text_input('If you are with a group, please enter group ID below (otherwise leave blank)',
										 key='init_group_id')
	init_form.form_submit_button(label='Start Workshop', on_click=init_form_callback)
	st.button(label='Admin', on_click=display_admin_screen)
	st.session_state['session_status'] = 'init_displaying'

if st.session_state['session_status'] == 'admin_options':
	st.button(label='Back to Start Page', on_click=reset_to_start)
	search_for_files()
	if len(st.session_state['export_result_file_names']) > 0:
		st.write(f'There is {len(st.session_state["export_result_file_names"])} new file(s). '
				 f'Would you like to add this data to the master record?')

# display the quiz selection form
if st.session_state['session_status'] == 'init_form_submitted':
	question_file = pd.read_csv('Files/QuizList.csv')
	st.header("Which test would you like to take?")
	quiz_form = st.form('quiz')
	quiz_form.selectbox('Quiz:', question_file['FileName'], key='init_quiz_name')
	quiz_form.form_submit_button(label='Begin', on_click=quiz_form_callback)
	quiz_form.form_submit_button(label='Start Over', on_click=reset_to_start)
	st.session_state['session_status'] = 'quiz_form_displaying'

# initial quiz setup
if st.session_state['session_status'] == 'quiz_form_submitted':
	quiz_name = "Files/" + st.session_state['quiz_name'] + ".csv"
	questions = pd.read_csv(quiz_name)
	questions['Solution'] = questions['Solution'].astype(str)
	st.session_state['questions'] = questions
	st.session_state['current_index'] = 0
	st.session_state['max_index'] = len(questions) - 1
	st.session_state['answers_df'] = pd.DataFrame(columns=['UserName', 'GroupID', 'QuizDateTime', 'Question',
														   'AnswerFormat', 'CorrectAnswer', 'Solution',
														   'LowerBound', 'UpperBound'])
	st.session_state['quiz_datetime'] = dt.today().strftime('%Y-%m-%d %H:%M')
	st.session_state['session_status'] = 'quiz_underway'

# display one quiz question
if st.session_state['session_status'] == 'quiz_underway':
	quest_num = st.session_state['current_index']
	question_row = st.session_state['questions'].iloc[quest_num]
	question = question_row['Question']
	answer_format = question_row['AnswerFormat']
	st.write(f'Taking "{st.session_state["quiz_name"]}" quiz')
	st.button(label='Start Over', on_click=reset_to_start)
	st.header(question)
	with st.form('question'):
		# st.form_submit_button(label='Start Over', on_click=reset_to_start)
		if answer_format == 'Number':
			col1, col2 = st.columns(2)
			with col1:
				st.number_input(label='Lower Bound', value=0, key='answer_lower_bound')
			with col2:
				st.number_input(label='Upper Bound', value=0, key='answer_upper_bound')
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
	write_results_to_csv()
	write_summary_to_csv()
	st.dataframe(st.session_state['summary_df'])
	st.dataframe(st.session_state['answers_df'])
	st.subheader('To take another quiz, click the button below')
	st.button(label='Take again', on_click=reset_to_start)


# st.write(st.session_state)
