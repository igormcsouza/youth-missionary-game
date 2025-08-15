import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from database import YouthFormDataRepository, TasksFormDataRepository, CompiledFormDataRepository


st.set_page_config(page_title="Dashboard", page_icon="📊")


st.title("Painel de Jovens Missionários")


# Calculate totals for specific missionary activities
def calculate_task_totals():
    compiled_entries = CompiledFormDataRepository.get_all()
    task_entries = TasksFormDataRepository.get_all()
    task_dict = {t.id: t for t in task_entries}
    
    # Define the specific tasks we want to track
    target_tasks = {
        "Entregar Livro de Mórmon + foto + relato no grupo": "Book of Mormon",
        "Levar amigo à sacramental": "People brought to church",
        "Ajudar alguém a se batizar": "Baptisms",
        "Postar mensagem do evangelho nas redes sociais + print": "Social media posts",
        "Fazer noite familiar com pesquisador": "FHE sessions"
    }
    
    # Calculate totals
    totals = {display_name: 0 for display_name in target_tasks.values()}
    
    for entry in compiled_entries:
        task = task_dict.get(entry.task_id)
        if task and task.tasks in target_tasks:
            display_name = target_tasks[task.tasks]
            totals[display_name] += entry.quantity
    
    return totals

# Display missionary activity totals as cards
activity_totals = calculate_task_totals()
if any(total > 0 for total in activity_totals.values()):
    st.header("Totais das Atividades Missionárias")
    
    # Create columns for the cards
    cols = st.columns(5)
    
    activities = [
        ("Book of Mormon", "📖", activity_totals["Book of Mormon"]),
        ("People brought to church", "⛪", activity_totals["People brought to church"]),
        ("Baptisms", "🛁", activity_totals["Baptisms"]),
        ("Social media posts", "📱", activity_totals["Social media posts"]),
        ("FHE sessions", "🏠", activity_totals["FHE sessions"])
    ]
    
    for i, (name, icon, total) in enumerate(activities):
        with cols[i]:
            st.metric(
                label=f"{icon} {name}",
                value=str(total)
            )


# Table: YouthFormData ordered by highest total points
youth_entries = YouthFormDataRepository.get_all()
filtered_youth = [y for y in youth_entries if y.total_points > 0]
sorted_youth = sorted(filtered_youth, key=lambda y: y.total_points, reverse=True)

st.header("Ranking dos Jovens por Pontuação Total")
if sorted_youth:
    df = pd.DataFrame([
        {
            "Ranking": idx + 1,
            "Nome": y.name,
            "Idade": y.age,
            "Organização": y.organization,
            "Pontuação Total": y.total_points
        } for idx, y in enumerate(sorted_youth)
    ])
    st.dataframe(df, hide_index=True)
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

# Bar chart: Total points for Young Man and Young Woman
young_man_points = sum(y.total_points for y in youth_entries if y.organization == "Rapazes")
young_woman_points = sum(y.total_points for y in youth_entries if y.organization == "Moças")
COLOR_YOUNG_MAN, COLOR_YOUNG_WOMAN = ["#1f77b4", "#e75480"]

if young_man_points == 0 and young_woman_points == 0:
    st.info("Nenhuma pontuação total disponível para Rapazes e Moças.")
else:
    st.header("Pontuação Total por Organização")
    bar_df = pd.DataFrame({
        "Organização": ["Rapazes", "Moças"],
        "Pontuação Total": [young_man_points, young_woman_points]
    })
    bar_fig = go.Figure(data=[go.Bar(x=bar_df["Organização"], y=bar_df["Pontuação Total"], marker_color=[COLOR_YOUNG_MAN, COLOR_YOUNG_WOMAN] )])
    bar_fig.update_layout(yaxis_title="Pontuação Total", xaxis_title="Organização")
    st.plotly_chart(bar_fig, use_container_width=True)
