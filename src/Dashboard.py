# Page: Dashboard
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from database import YouthFormDataRepository, TasksFormDataRepository, CompiledFormDataRepository


st.set_page_config(page_title="Dashboard", page_icon="📊")


st.title("Painel de Jovens Missionários")


# Table: YouthFormData ordered by highest total points
youth_entries = YouthFormDataRepository.get_all()
filtered_youth = [y for y in youth_entries if y.total_points > 0]
sorted_youth = sorted(filtered_youth, key=lambda y: y.total_points, reverse=True)

st.header("Ranking dos Jovens por Pontuação Total")
if sorted_youth:
    st.table([
        {
            "Nome": y.name,
            "Idade": y.age,
            "Organização": y.organization,
            "Pontuação Total": y.total_points
        } for y in sorted_youth
    ])
else:
    st.info("Nenhum jovem cadastrado ainda.")

# Pie chart: Most pointed task
compiled_entries = CompiledFormDataRepository.get_all()
task_entries = TasksFormDataRepository.get_all()
task_points = {}
task_dict = {t.id: t for t in task_entries}
task_points = {}
for entry in compiled_entries:
    task = task_dict.get(entry.task_id)
    if task:
        points = task.points * entry.quantity + entry.bonus
        task_points[task.tasks] = task_points.get(task.tasks, 0) + points

if task_points:
    st.header("Tarefas Mais Pontuadas")
    df = pd.DataFrame({"Tarefa": list(task_points.keys()), "Pontuação": list(task_points.values())})
    fig = go.Figure(data=[go.Pie(labels=df["Tarefa"], values=df["Pontuação"], title="Pontuação por Tarefa")])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma pontuação de tarefa disponível.")