import pandas as pd
import streamlit as st

from database import (
    CompiledFormDataRepository,
    TasksFormDataRepository,
    YouthFormDataRepository,
)
from utils import check_password

st.set_page_config(page_title="Dados dos Jovens e Tarefas", page_icon="📁")


if not check_password():
    st.stop()


st.title("Cadastro de Jovens")


with st.expander("Adicionar Cadastro", expanded=True):
    with st.form("entry_form"):
        name = st.text_input("Nome")
        age = st.number_input("Idade", min_value=0, max_value=120, step=1)
        organization = st.selectbox("Organização", ["Rapazes", "Moças"])
        total_points = 0  # Not editable
        submitted = st.form_submit_button("Adicionar Cadastro")

        if submitted:
            result = YouthFormDataRepository.store(
                name, age, organization, total_points
            )
            if result is not None:
                st.success("Cadastro adicionado!")
            # Error message is handled by the repository method


col1, col2 = st.columns([4, 1])
with col1:
    st.header("Cadastros Salvos")
with col2:
    if st.button("Atualizar Pontuação Total"):
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
    df = pd.DataFrame(
        [
            {
                "Nome": e.name,
                "Idade": e.age,
                "Organização": e.organization,
                "Pontuação Total": e.total_points,
            }
            for e in entries
        ]
    )
    st.dataframe(df, hide_index=True)
else:
    st.info("Nenhum cadastro salvo ainda.")


st.title("Cadastro de Tarefas")


with st.expander("Adicionar Nova Tarefa", expanded=True):
    with st.form("task_entry_form"):
        tasks = st.text_input("Nome da Tarefa")
        points = st.number_input("Pontuação", min_value=0, step=1)
        repeatable = st.checkbox("Repetível")
        submitted_task = st.form_submit_button("Adicionar Tarefa")

        if submitted_task:
            result = TasksFormDataRepository.store(tasks, points, repeatable)
            if result is not None:
                st.success("Tarefa adicionada!")
            # Error message is handled by the repository method


st.header("Tarefas Salvas")
task_entries = TasksFormDataRepository.get_all()
if task_entries:
    df_tasks = pd.DataFrame(
        [
            {
                "Tarefa": t.tasks,
                "Pontuação": t.points,
                "Repetível": "Sim" if t.repeatable else "Não",
            }
            for t in task_entries
        ]
    )
    st.dataframe(df_tasks, hide_index=True)
else:
    st.info("Nenhuma tarefa salva ainda.")
