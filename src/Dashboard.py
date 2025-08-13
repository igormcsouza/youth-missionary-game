import os
import sys

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from database import YouthFormDataRepository, TasksFormDataRepository, CompiledFormDataRepository


st.title("Youth Missionary Dashboard")

# Table: YouthFormData ordered by highest total points
youth_entries = YouthFormDataRepository.get_all()
sorted_youth = sorted(youth_entries, key=lambda y: y.total_points, reverse=True)
st.header("Youth Ranking by Total Points")
if sorted_youth:
    st.table([
        {
            "Name": y.name,
            "Age": y.age,
            "Organization": y.organization,
            "Total Points": y.total_points
        } for y in sorted_youth
    ])
else:
    st.info("No youth entries stored yet.")

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
    st.header("Most Pointed Tasks")
    df = pd.DataFrame({"Task": list(task_points.keys()), "Points": list(task_points.values())})
    fig = go.Figure(data=[go.Pie(labels=df["Task"], values=df["Points"], title="Points by Task")])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No task points data available.")