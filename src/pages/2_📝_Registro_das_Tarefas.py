import time
from datetime import datetime

import pandas as pd
import streamlit as st

from utils import check_password
from database import YouthFormDataRepository, TasksFormDataRepository, CompiledFormDataRepository


st.set_page_config(page_title="Registros das Tarefas", page_icon="📝")


if not check_password():
    st.stop()


st.title("Registrar Dados Compilados")


def refresh_youth_and_task_entries():
	youth_entries = YouthFormDataRepository.get_all()
	task_entries = TasksFormDataRepository.get_all()
	youth_options = {y.id: y.name for y in youth_entries}
	task_options = {t.id: t.tasks for t in task_entries}
	return youth_entries, task_entries, youth_options, task_options

youth_entries, task_entries, youth_options, task_options = refresh_youth_and_task_entries()
task_by_id = {t.id: t for t in task_entries}

with st.form("compiled_form"):
	selected_youth_id = st.selectbox("Selecionar Jovem", options=list(youth_options.keys()), format_func=lambda x: youth_options[x] if x in youth_options else "")
	selected_task_id = st.selectbox("Selecionar Tarefa", options=list(task_options.keys()), format_func=lambda x: task_options[x] if x in task_options else "")
	quantity = st.number_input("Quantidade", min_value=1, step=1)
	bonus = st.number_input("Bônus", min_value=0, step=1)
	submitted = st.form_submit_button("Registrar Entrada")

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
		st.success("Entrada registrada e pontuação total do jovem atualizada!")
		st.rerun()


# Display stored compiled entries
st.header("Entradas Compiladas Salvas")
compiled_entries = CompiledFormDataRepository.get_all()
if compiled_entries:
	def get_name_by_id(id_):
		return youth_options.get(id_, str(id_))
	def get_task_by_id(id_):
		return task_options.get(id_, str(id_))

	df_compiled = pd.DataFrame([
		{
			"Jovem": get_name_by_id(e.youth_id),
			"Tarefa": get_task_by_id(e.task_id),
			"Data": datetime.fromtimestamp(e.timestamp).strftime("%d/%m/%Y"),
			"Quantidade": e.quantity,
			"Bônus": e.bonus,
			"Pontuação Total": e.quantity * (task_by_id.get(e.task_id).points if task_by_id.get(e.task_id) else 0) + e.bonus # type: ignore
		} for e in compiled_entries
	])
	st.dataframe(df_compiled, hide_index=True)
else:
	st.info("Nenhuma entrada compilada salva ainda.")
