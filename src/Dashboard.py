from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from database import (
    CompiledFormDataRepository,
    TasksFormDataRepository,
    YouthFormDataRepository,
)

st.set_page_config(page_title="Dashboard", page_icon="📊")


st.title("Painel de Jovens Missionários")


# Helper function to calculate last Sunday
def get_last_sunday():
    today = datetime.now()
    days_since_sunday = (
        today.weekday() + 1
    )  # Monday = 1, Tuesday = 2, ..., Sunday = 7
    last_sunday = today - timedelta(days=days_since_sunday)
    # Set to beginning of Sunday
    return last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)


# Calculate totals for specific missionary activities
def calculate_task_totals():
    compiled_entries = CompiledFormDataRepository.get_all()
    task_entries = TasksFormDataRepository.get_all()
    task_dict = {t.id: t for t in task_entries}

    # Define the specific tasks we want to track with Portuguese display names
    target_tasks = {
        "Entregar Livro de Mórmon + foto + relato no grupo": (
            "Livros de Mórmon entregues"
        ),
        "Levar amigo à sacramental": "Pessoas levadas à igreja",
        "Dar contato (tel/endereço) às Sisteres": "Referências",
        "Visitar com as Sisteres": "Lições",
        "Postar mensagem do evangelho nas redes sociais + print": (
            "Posts nas redes sociais"
        ),
        "Fazer noite familiar com pesquisador": "Sessões de noite familiar",
    }

    # Calculate totals and deltas since last Sunday
    # (week runs Sunday to Saturday)
    totals = dict.fromkeys(target_tasks.values(), 0)
    deltas = dict.fromkeys(target_tasks.values(), 0)

    last_sunday = get_last_sunday()
    # Week starts on Sunday, not Monday after Sunday
    sunday_timestamp = last_sunday.timestamp()

    for entry in compiled_entries:
        task = task_dict.get(entry.task_id)
        if task and task.tasks in target_tasks:
            display_name = target_tasks[task.tasks]
            totals[display_name] += entry.quantity

            # Count activities since last Sunday (current week)
            if entry.timestamp >= sunday_timestamp:
                deltas[display_name] += entry.quantity

    return totals, deltas


# Calculate weekly points for each youth
def calculate_weekly_youth_points():
    """Calculate points earned by each youth this week (Sunday to Saturday)"""
    compiled_entries = CompiledFormDataRepository.get_all()
    task_entries = TasksFormDataRepository.get_all()
    youth_entries = YouthFormDataRepository.get_all()

    task_dict = {t.id: t for t in task_entries}
    youth_dict = {y.id: y for y in youth_entries}

    last_sunday = get_last_sunday()
    sunday_timestamp = last_sunday.timestamp()

    # Calculate current total points for each youth (all time)
    current_total_points = {}
    for youth in youth_entries:
        current_total_points[youth.id] = {
            "name": youth.name,
            "organization": youth.organization,
            "points": youth.total_points,
        }

    # Calculate total points as of last Saturday
    # (excluding this week's entries)
    last_saturday_points = {}
    for youth in youth_entries:
        last_saturday_points[youth.id] = {
            "name": youth.name,
            "organization": youth.organization,
            "points": 0,
        }

    # Add up all points except those from this week (Sunday onwards)
    for entry in compiled_entries:
        if entry.timestamp < sunday_timestamp:  # Before this week
            task = task_dict.get(entry.task_id)
            youth = youth_dict.get(entry.youth_id)
            if task and youth:
                points = task.points * entry.quantity + entry.bonus
                last_saturday_points[youth.id]["points"] += points

    # Create ranking for current totals (position 1 = highest points)
    current_ranking = sorted(
        [
            (youth_id, data["points"])
            for youth_id, data in current_total_points.items()
            if data["points"] > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    current_positions = {
        youth_id: idx + 1 for idx, (youth_id, _) in enumerate(current_ranking)
    }

    # Create ranking for last Saturday (position 1 = highest points)
    last_saturday_ranking = sorted(
        [
            (youth_id, data["points"])
            for youth_id, data in last_saturday_points.items()
            if data["points"] > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    last_saturday_positions = {
        youth_id: idx + 1
        for idx, (youth_id, _) in enumerate(last_saturday_ranking)
    }

    # Calculate weekly points and position changes
    weekly_points = {}
    for entry in compiled_entries:
        if entry.timestamp >= sunday_timestamp:  # This week
            task = task_dict.get(entry.task_id)
            youth = youth_dict.get(entry.youth_id)
            if task and youth:
                points = task.points * entry.quantity + entry.bonus
                if youth.id not in weekly_points:
                    current_pos = current_positions.get(youth.id, 0)
                    last_saturday_pos = last_saturday_positions.get(
                        youth.id, 0
                    )

                    # Calculate delta: negative means moved up (good)
                    # If youth wasn't ranked last Saturday, consider them as
                    # having moved up
                    if last_saturday_pos == 0:
                        delta = (
                            -(current_pos - len(last_saturday_positions) - 1)
                            if current_pos > 0
                            else 0
                        )
                    else:
                        delta = last_saturday_pos - current_pos

                    weekly_points[youth.id] = {
                        "name": youth.name,
                        "organization": youth.organization,
                        "points": 0,
                        "delta": delta,
                    }
                weekly_points[youth.id]["points"] += points

    return weekly_points


# Calculate weekly "Livros de Mórmon" deliveries
def calculate_weekly_book_deliveries():
    """Calculate weekly deliveries of 'Livros de Mórmon'
    since competition start"""
    compiled_entries = CompiledFormDataRepository.get_all()
    task_entries = TasksFormDataRepository.get_all()

    # Find the "Livros de Mórmon" task
    book_task = None
    for task in task_entries:
        if "Livro de Mórmon" in task.tasks:
            book_task = task
            break

    if not book_task:
        return {}

    # Group deliveries by week
    weekly_deliveries = {}

    # Find the earliest entry to establish week 1
    earliest_timestamp = min(
        [entry.timestamp for entry in compiled_entries],
        default=datetime.now().timestamp(),
    )
    earliest_date = datetime.fromtimestamp(earliest_timestamp)

    # Find the Sunday of the first week
    days_since_sunday = earliest_date.weekday() + 1
    first_sunday = earliest_date - timedelta(days=days_since_sunday)
    first_sunday = first_sunday.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    for entry in compiled_entries:
        if entry.task_id == book_task.id:
            entry_date = datetime.fromtimestamp(entry.timestamp)

            # Calculate which week this entry belongs to
            days_since_first = (entry_date - first_sunday).days
            week_number = (days_since_first // 7) + 1

            if week_number not in weekly_deliveries:
                weekly_deliveries[week_number] = 0
            weekly_deliveries[week_number] += entry.quantity

    return weekly_deliveries


# Calculate days until October 31, 2025
def calculate_countdown():
    """Calculate days remaining until October 31, 2025"""
    end_date = datetime(2025, 10, 31)
    current_date = datetime.now()
    days_remaining = (end_date - current_date).days
    return max(0, days_remaining)  # Don't show negative days


# Display missionary activity totals as cards
activity_totals, activity_deltas = calculate_task_totals()
if any(total > 0 for total in activity_totals.values()):
    st.header("Totais das Atividades Missionárias")

    # Create columns for the cards
    cols = st.columns(5)

    activities = [
        (
            "Livros de Mórmon",
            "📖",
            activity_totals["Livros de Mórmon entregues"],
            activity_deltas["Livros de Mórmon entregues"],
        ),
        (
            "Referências",
            "📞",
            activity_totals["Referências"],
            activity_deltas["Referências"],
        ),
        ("Lições", "👥", activity_totals["Lições"], activity_deltas["Lições"]),
        (
            "Posts",
            "📱",
            activity_totals["Posts nas redes sociais"],
            activity_deltas["Posts nas redes sociais"],
        ),
        (
            "Noites familiares",
            "🏠",
            activity_totals["Sessões de noite familiar"],
            activity_deltas["Sessões de noite familiar"],
        ),
    ]

    for i, (name, icon, total, delta) in enumerate(activities):
        with cols[i]:
            st.metric(
                label=f"{icon} {name}",
                value=str(total),
                delta=f"+{delta} novos" if delta > 0 else None,
            )


# Table: YouthFormData ordered by highest total points
youth_entries = YouthFormDataRepository.get_all()
filtered_youth = [y for y in youth_entries if y.total_points > 0]
sorted_youth = sorted(
    filtered_youth, key=lambda y: y.total_points, reverse=True
)

# Top 5 da Semana (pontos semanais)
st.header("Top 5 da Semana")
st.caption("Pontos obtidos na semana atual (domingo a sábado)")

if sorted_youth:
    # Get weekly points for each youth
    weekly_points_data = calculate_weekly_youth_points()

    # Create Top 5 based on total ranking but show weekly points
    top_5_youth = sorted_youth[:5]

    # Check if any of the top 5 have weekly points
    has_weekly_activity = any(
        weekly_points_data.get(youth.id, {}).get("points", 0) > 0
        for youth in top_5_youth
    )

    if top_5_youth and has_weekly_activity:
        # Display in a single row using columns
        cols = st.columns(5)

        for idx, youth in enumerate(top_5_youth):
            weekly_points = weekly_points_data.get(youth.id, {}).get(
                "points", 0
            )
            position_delta = weekly_points_data.get(youth.id, {}).get(
                "delta", 0
            )

            with cols[idx]:
                st.metric(
                    label=f"#{idx + 1} {youth.name}",
                    value=f"{weekly_points} pts",
                    delta=f"{position_delta} posição",
                )
    else:
        st.info("Nenhuma pontuação desta semana ainda.")
else:
    st.info("Nenhum jovem cadastrado ainda.")

st.header("Ranking dos Jovens por Pontuação Total")
if sorted_youth:
    df = pd.DataFrame(
        [
            {
                "Ranking": idx + 1,
                "Nome": y.name,
                "Idade": y.age,
                "Organização": y.organization,
                "Pontuação Total": y.total_points,
            }
            for idx, y in enumerate(sorted_youth)
        ]
    )
    st.dataframe(df, hide_index=True)
else:
    st.info("Nenhum jovem cadastrado ainda.")

# Weekly Graph: "Livros de Mórmon" Delivered
weekly_books = calculate_weekly_book_deliveries()
if weekly_books:
    st.header("Entregas Semanais de Livros de Mórmon")

    # Prepare data for chart
    weeks = sorted(weekly_books.keys())
    deliveries = [weekly_books[week] for week in weeks]
    week_labels = [f"Semana {week}" for week in weeks]

    # Create line chart
    fig = px.line(
        x=week_labels,
        y=deliveries,
        title="Livros de Mórmon Entregues por Semana",
        labels={"x": "Semana", "y": "Quantidade Entregue"},
    )
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma entrega de Livro de Mórmon registrada ainda.")

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
    df = pd.DataFrame(
        {
            "Tarefa": list(task_points.keys()),
            "Pontuação": list(task_points.values()),
        }
    )
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["Tarefa"],
                values=df["Pontuação"],
                title="Pontuação por Tarefa",
            )
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma pontuação de tarefa disponível.")

# Bar chart: Total points for Young Man and Young Woman
young_man_points = sum(
    y.total_points for y in youth_entries if y.organization == "Rapazes"
)
young_woman_points = sum(
    y.total_points for y in youth_entries if y.organization == "Moças"
)
COLOR_YOUNG_MAN, COLOR_YOUNG_WOMAN = ["#1f77b4", "#e75480"]

if young_man_points == 0 and young_woman_points == 0:
    st.info("Nenhuma pontuação total disponível para Rapazes e Moças.")
else:
    st.header("Pontuação Total por Organização")
    bar_df = pd.DataFrame(
        {
            "Organização": ["Rapazes", "Moças"],
            "Pontuação Total": [young_man_points, young_woman_points],
        }
    )
    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=bar_df["Organização"],
                y=bar_df["Pontuação Total"],
                marker_color=[COLOR_YOUNG_MAN, COLOR_YOUNG_WOMAN],
            )
        ]
    )
    bar_fig.update_layout(
        yaxis_title="Pontuação Total", xaxis_title="Organização"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

# Countdown to End of Game
days_remaining = calculate_countdown()
st.markdown("---")
st.markdown(
    f"**Ainda faltam {days_remaining} dias para o fim da gincana!**",
    help="A gincana termina em 31 de outubro de 2025",
)
