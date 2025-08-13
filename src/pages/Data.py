# import streamlit and database functions
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import YouthFormDataRepository, TasksFormDataRepository
from database import CompiledFormDataRepository

st.title("Youth Form Data")

with st.expander("Add New Entry", expanded=True):
	with st.form("entry_form"):
		name = st.text_input("Name")
		age = st.number_input("Age", min_value=0, max_value=120, step=1)
		organization = st.selectbox("Organization", ["Young Man", "Young Woman"])
		total_points = 0  # Not editable by user
		submitted = st.form_submit_button("Add Entry")

		if submitted:
			YouthFormDataRepository.store(name, age, organization, total_points)
			st.success("Entry added!")

# Display stored entries
col1, col2 = st.columns([4,1])
with col1:
	st.header("Stored Entries")
with col2:
	if st.button("Update Total Points"):
		compiled_entries = CompiledFormDataRepository.get_all()

		task_by_id = {t.id: t for t in TasksFormDataRepository.get_all()}
		for youth in YouthFormDataRepository.get_all():
			total_points = 0
			for entry in compiled_entries:
				if entry.youth_id == youth.id:
					task = task_by_id.get(entry.task_id)
					if task:
						total_points += task.points * entry.quantity + entry.bonus
			if youth.id:
				YouthFormDataRepository.update_total_points(youth.id, total_points)
		st.rerun()
entries = YouthFormDataRepository.get_all()
if entries:
	st.table([
		{
			"Name": e.name,
			"Age": e.age,
			"Organization": e.organization,
			"Total Points": e.total_points
		} for e in entries
	])
else:
	st.info("No entries stored yet.")

# Tasks Form Data
st.title("Tasks Form Data")

# Form for adding tasks
with st.expander("Add New Task", expanded=True):
	with st.form("task_entry_form"):
		tasks = st.text_input("Task Name")
		points = st.number_input("Points", min_value=0, step=1)
		repeatable = st.checkbox("Repeatable")
		submitted_task = st.form_submit_button("Add Task")

		if submitted_task:
			TasksFormDataRepository.store(tasks, points, repeatable)
			st.success("Task added!")

# Display stored tasks
st.header("Stored Tasks")
task_entries = TasksFormDataRepository.get_all()
if task_entries:
	st.table([
		{
			"Task": t.tasks,
			"Points": t.points,
			"Repeatable": t.repeatable
		} for t in task_entries
	])
else:
	st.info("No tasks stored yet.")
