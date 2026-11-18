from datetime import datetime, timedelta, timezone

import streamlit as st

from core.database import init_db
from services.demo import DEMO_CUT, DEMO_NAME, seed_demo
from services.indicadores import task_rows
from services.obra import create_project, list_rows
from ui.plano import import_view, plan_view, submit
from ui.resumen import backups, dashboard, gantt, history, matrix, metrics, reports

st.set_page_config(page_title="PlantaControl", page_icon="🏗️", layout="wide")


@st.cache_resource
def initialize():
    init_db()


def today():
    return datetime.now(timezone(timedelta(hours=-5))).date()


def project_controls():
    user = st.sidebar.text_input("Responsable del registro", value="Equipo de obra").strip()
    with st.sidebar.expander("Nueva obra"):
        with st.form("nueva-obra"):
            name = st.text_input("Nombre")
            start = st.date_input("Inicio", today())
            end = st.date_input("Término", today() + timedelta(days=60))
            if st.form_submit_button("Crear obra"):
                project_id = submit(lambda: create_project(name, start, end, user), "Obra creada.")
                if project_id:
                    st.session_state.pending_project = project_id
                    st.rerun()
    if st.sidebar.button("Abrir demo de Briones Luco", width="stretch"):
        project_id = seed_demo()
        st.session_state.pending_project = project_id
        st.session_state[f"corte-{project_id}"] = DEMO_CUT
        st.rerun()
    return user


def main():
    initialize()
    st.sidebar.header("PlantaControl")
    user = project_controls()
    st.title("PlantaControl")
    if notice := st.session_state.pop("notice", None):
        st.success(notice)
    projects = {row["id"]: row for row in list_rows("SELECT * FROM obras ORDER BY id")}
    if not projects:
        st.info("Crea una obra, abre la demo o restaura un respaldo.")
        backups()
        return
    pending = st.session_state.pop("pending_project", None)
    if pending in projects:
        st.session_state["obra"] = pending
    project_id = st.sidebar.selectbox("Obra", projects, format_func=lambda k: projects[k]["nombre"], key="obra")
    project = projects[project_id]
    if not user:
        st.warning("Escribe el nombre del responsable para continuar.")
        return
    plans = {p["id"]: p for p in list_rows(
        "SELECT id, ruta_archivo, version FROM planos WHERE obra_id=? ORDER BY version DESC", (project_id,)
    )}
    pending_plan = st.session_state.pop(f"nuevo-plano-{project_id}", None)
    if pending_plan in plans:
        st.session_state[f"plan-{project_id}"] = pending_plan
    plan_id = st.sidebar.selectbox("Versión del plano", plans, format_func=lambda k:
                                   f'v{plans[k]["version"]} · {plans[k]["ruta_archivo"]}',
                                   key=f"plan-{project_id}") if plans else None
    st.session_state.setdefault(f"corte-{project_id}", DEMO_CUT if project["nombre"] == DEMO_NAME else today())
    cut = st.sidebar.date_input("Fecha de corte",
                                key=f"corte-{project_id}")
    tolerance = st.sidebar.number_input("Tolerancia de atraso (pp)", 0.0, 100.0, 5.0, step=1.0)
    section = st.radio("Vista", ["Plano interactivo", "Dashboard", "Matriz", "Historial", "Carta Gantt",
                               "Informes", "Respaldo"], horizontal=True, label_visibility="collapsed")
    active_plan = plan_id
    if section != "Plano interactivo" and len(plans) > 1:
        if st.sidebar.checkbox("Incluir todas las versiones"):
            active_plan = None
    rows = task_rows(project_id, cut, tolerance, active_plan)
    st.caption(f'{project["nombre"]} · Corte al {cut:%d/%m/%Y}')
    if section != "Respaldo":
        metrics(rows)
    if section == "Plano interactivo":
        selected = list_rows("SELECT * FROM planos WHERE id=?", (plan_id,)) if plan_id else []
        plan_view(project, next(iter(selected), None), rows, cut, user)
        import_view(project_id, user)
    elif section == "Dashboard":
        dashboard(rows)
    elif section == "Matriz":
        matrix(rows)
    elif section == "Historial":
        history(project_id, active_plan, cut, tolerance)
    elif section == "Carta Gantt":
        gantt(rows, cut)
    elif section == "Informes":
        reports(project, active_plan, rows, cut)
    else:
        backups()


main()

