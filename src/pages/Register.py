import streamlit as st
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import YouthFormDataRepository, TasksFormDataRepository, CompiledFormDataRepository

st.title("Register Compiled Form Data")


def refresh_youth_and_task_entries():
	youth_entries = YouthFormDataRepository.get_all()
	task_entries = TasksFormDataRepository.get_all()
	youth_options = {y.id: y.name for y in youth_entries}
	task_options = {t.id: t.tasks for t in task_entries}
	return youth_entries, task_entries, youth_options, task_options

youth_entries, task_entries, youth_options, task_options = refresh_youth_and_task_entries()
task_by_id = {t.id: t for t in task_entries}

with st.form("compiled_form"):
	selected_youth_id = st.selectbox("Select Youth", options=list(youth_options.keys()), format_func=lambda x: youth_options[x] if x in youth_options else "")
	selected_task_id = st.selectbox("Select Task", options=list(task_options.keys()), format_func=lambda x: task_options[x] if x in task_options else "")
	quantity = st.number_input("Quantity", min_value=1, step=1)
	bonus = st.number_input("Bonus", min_value=0, step=1)
	submitted = st.form_submit_button("Register Entry")

	if submitted and selected_youth_id and selected_task_id:
		CompiledFormDataRepository.store(
			youth_id=selected_youth_id,
			task_id=selected_task_id,
			timestamp=time.time(),
			quantity=quantity,
			bonus=bonus
		)
		# Recalculate total points for the selected youth
		compiled_entries = CompiledFormDataRepository.get_all()
		total_points = 0
		for entry in compiled_entries:
			if entry.youth_id == selected_youth_id:
				task = task_by_id.get(entry.task_id)
				if task:
					total_points += task.points * entry.quantity + entry.bonus
		YouthFormDataRepository.update_total_points(selected_youth_id, total_points)
		st.success("Compiled entry registered and youth total points updated!")
		# Refresh youth_entries for display
		youth_entries, task_entries, youth_options, task_options = refresh_youth_and_task_entries()


# Display stored compiled entries
st.header("Stored Compiled Entries")
compiled_entries = CompiledFormDataRepository.get_all()
if compiled_entries:
	def get_name_by_id(id_):
		return youth_options.get(id_, str(id_))
	def get_task_by_id(id_):
		return task_options.get(id_, str(id_))
	from datetime import datetime
	st.table([
		{
			"Youth": get_name_by_id(e.youth_id),
			"Task": get_task_by_id(e.task_id),
			"Date": datetime.fromtimestamp(e.timestamp).strftime("%d/%m/%Y"),
			"Quantity": e.quantity,
			"Bonus": e.bonus
		} for e in compiled_entries
	])
else:
	st.info("No compiled entries stored yet.")
