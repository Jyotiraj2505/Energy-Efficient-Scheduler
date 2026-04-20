import streamlit as st
import pandas as pd
from models import Process
from algorithms import run_eesa, run_round_robin
import time

# --- Configuration ---
st.set_page_config(page_title="EESA Simulator", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for "simple, not screaming AI" look
st.markdown("""
<style>
    /* Hide sidebar completely */
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 15px;
        text-align: center;
        font-family: monospace;
    }
    
    .event-log-container {
        border-left: 2px solid #007bff;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    
    .queue-box {
        display: inline-block;
        border: 1px solid #28a745;
        background-color: #e8f5e9;
        padding: 5px 10px;
        border-radius: 4px;
        margin: 2px;
        font-weight: bold;
    }
    
    .core-box {
        display: inline-block;
        border: 1px solid #17a2b8;
        background-color: #e0f7fa;
        padding: 5px 10px;
        border-radius: 4px;
        margin: 2px;
    }
    
    .shift-note {
        color: #d32f2f;
        font-weight: bold;
        background-color: #ffebee;
        padding: 4px;
        border-radius: 3px;
    }
    
    .normal-note {
        color: #555;
        font-style: italic;
    }
    
    .arrow {
        font-size: 20px;
        margin: 0 10px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'processes' not in st.session_state:
    st.session_state.processes = [
        Process(pid=1, arrival_time=0, burst_time=5, power_profile=1.5),
        Process(pid=2, arrival_time=1, burst_time=8, power_profile=1.2),
        Process(pid=3, arrival_time=2, burst_time=4, power_profile=2.0), # Heavy
        Process(pid=4, arrival_time=4, burst_time=6, power_profile=1.0)
    ]
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False

# --- Header ---
st.title("CPU Scheduling Simulator")
st.markdown("Energy-Efficient Scheduling Algorithm (EESA) vs Round Robin.")
st.divider()

# --- Process Input Section ---
st.subheader("Process Configuration")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    new_pid = st.number_input("PID", min_value=1, step=1, value=len(st.session_state.processes)+1)
with col2:
    new_arrival = st.number_input("Arrival Time", min_value=0, step=1, value=0)
with col3:
    new_burst = st.number_input("Burst Time", min_value=1, step=1, value=5)
with col4:
    new_power = st.number_input("Power Profile multiplier", min_value=0.5, step=0.1, value=1.0)
with col5:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Add Process", on_click=lambda: st.session_state.processes.append(Process(new_pid, new_arrival, new_burst, new_power))):
        pass

if st.button("Clear Processes"):
    st.session_state.processes = []
    st.session_state.simulation_run = False

if st.session_state.processes:
    st.dataframe(pd.DataFrame([{
        "PID": p.pid, 
        "Arrival Time": p.arrival_time, 
        "Burst Time": p.burst_time, 
        "Power Profile": p.power_profile
    } for p in st.session_state.processes]), use_container_width=True)
else:
    st.info("No processes added yet.")

# --- Simulation Execution ---
st.divider()
col_run, _, _ = st.columns([1, 2, 2])
with col_run:
    if st.button("Run Simulation", type="primary"):
        if not st.session_state.processes:
            st.error("Add at least one process to run the simulation.")
        else:
            with st.spinner("Simulating..."):
                # Run EESA
                eesa_states, eesa_completed, eesa_energy, eesa_wait = run_eesa(st.session_state.processes, num_cores=2, quantum=2)
                # Run RR
                rr_states, rr_completed, rr_energy, rr_wait = run_round_robin(st.session_state.processes, num_cores=2, quantum=2)
                
                st.session_state.eesa_results = (eesa_states, eesa_completed, eesa_energy, eesa_wait)
                st.session_state.rr_results = (rr_states, rr_completed, rr_energy, rr_wait)
                st.session_state.simulation_run = True

# --- Results Dashboard ---
if st.session_state.simulation_run:
    eesa_states, eesa_completed, eesa_energy, eesa_wait = st.session_state.eesa_results
    rr_states, rr_completed, rr_energy, rr_wait = st.session_state.rr_results
    
    st.subheader("Performance Comparison")
    
    # EESA Metrics
    met_col1, met_col2 = st.columns(2)
    with met_col1:
        st.markdown(f"""
<div class="metric-card">
    <h4>EESA (Energy-Efficient)</h4>
    <h2>Total Energy: {eesa_energy:.2f} U</h2>
    <h4>Avg Wait Time: {eesa_wait:.2f} t</h4>
</div>
""", unsafe_allow_html=True)
        
    with met_col2:
        st.markdown(f"""
<div class="metric-card">
    <h4>Round Robin (Baseline)</h4>
    <h2>Total Energy: {rr_energy:.2f} U</h2>
    <h4>Avg Wait Time: {rr_wait:.2f} t</h4>
</div>
""", unsafe_allow_html=True)
        
    st.divider()
    
    # --- True Gantt Chart visualization ---
    st.subheader("Execution Gantt Chart")
    
    # We will build an interval-based timeline
    def build_timeline(states, num_cores=2):
        if not states:
             return []
        
        intervals = []
        curr = {
            'start': states[0].time,
            'ready': list(states[0].ready_queue),
            'cores': dict(states[0].scheduled_processes),
            'temps': dict(states[0].core_temperatures),
            'freqs': dict(states[0].core_frequencies),
            'notes': list(states[0].notes)
        }
        
        for state in states[1:]:
            # Only split interval if scheduling on cores changes or ready queue changes (so we don't stretch wrong ready queue)
            # Actually, the user wants the Gantt block to represent process runs.
            # We will generate blocks where EITHER running processes change OR we reached end.
            if state.scheduled_processes != curr['cores']:
                curr['end'] = state.time
                intervals.append(curr)
                curr = {
                    'start': state.time,
                    'ready': list(state.ready_queue),
                    'cores': dict(state.scheduled_processes),
                    'temps': dict(state.core_temperatures),
                    'freqs': dict(state.core_frequencies),
                    'notes': list(state.notes)
                }
            else:
                curr['notes'].extend(state.notes)
                curr['temps'] = dict(state.core_temperatures)
                curr['freqs'] = dict(state.core_frequencies)
                
        curr['end'] = states[-1].time + 1
        intervals.append(curr)
        return intervals

    eesa_intervals = build_timeline(eesa_states)
    total_time = eesa_intervals[-1]['end'] if eesa_intervals else 1
    
    # Custom CSS for the Gantt Chart matching the reference
    st.markdown("""
<style>
.gantt-wrapper {
    margin-bottom: 40px;
    font-family: Arial, sans-serif;
}
.gantt-title {
    text-align: center;
    font-weight: bold;
    color: #444;
    margin-bottom: 5px;
    font-size: 14px;
    text-transform: uppercase;
}
.gantt-sub-title {
    color: #666;
    margin-bottom: 5px;
    font-size: 14px;
}
.gantt-row {
    position: relative;
    height: 40px;
    border-top: 1px solid #777;
    border-bottom: 1px solid #777;
    background-color: #fafafa;
    margin-bottom: 2px;
}
.gantt-box {
    position: absolute;
    height: 100%;
    border-left: 1px solid #777;
    border-right: 1px solid #777;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: bold;
    color: #333;
    overflow: hidden;
    white-space: nowrap;
}
.ready-box {
    background-color: #ccffcc; /* light green like image */
}
.core-box {
    background-color: #ffffff; /* white like image */
}
.idle-box {
    background-color: transparent;
    border: none;
}
.axis-row {
    position: relative;
    height: 20px;
    margin-bottom: 10px;
}
.axis-tick {
    position: absolute;
    transform: translateX(-50%);
    font-size: 11px;
    color: #333;
    top: 2px;
}
.axis-tick::before {
    content: '';
    position: absolute;
    top: -4px;
    left: 50%;
    width: 1px;
    height: 4px;
    background-color: #777;
}
.processor-label {
    display: inline-block;
    background-color: #7b68ee;
    color: white;
    padding: 5px 15px;
    border-radius: 5px;
    font-size: 12px;
    font-weight: bold;
    margin-left: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

    html_out = ["<div class='gantt-wrapper'>"]
    
    # 1. Ready Queue
    html_out.append("<div class='gantt-title'>READY QUEUE</div>")
    html_out.append("<div class='gantt-row'>")
    for interval in eesa_intervals:
        t1 = interval['start']
        t2 = interval['end']
        width_pct = ((t2 - t1) / total_time) * 100
        left_pct = (t1 / total_time) * 100
        rq_str = " ".join([f"P{p}" for p in interval['ready']])
        if rq_str:
            html_out.append(f"<div class='gantt-box ready-box' style='left:{left_pct}%; width:{width_pct}%;'>{rq_str}</div>")
    html_out.append("</div>") # end ready queue row
    html_out.append("<div style='height:20px;'></div>") # spacer
    
    # 2. Processors
    for c_id in [0, 1]:
        html_out.append(f"<div class='gantt-sub-title'>Gantt Chart of processor {c_id+1} <span class='processor-label'>Processor {c_id+1}</span></div>")
        html_out.append("<div class='gantt-row'>")
        
        ticks_set = set()
        ticks_html = []
        
        for interval in eesa_intervals:
            t1 = interval['start']
            t2 = interval['end']
            width_pct = ((t2 - t1) / total_time) * 100
            left_pct = (t1 / total_time) * 100
            p_id = interval['cores'].get(c_id)
            
            # ticks
            if t1 not in ticks_set:
                ticks_html.append(f"<div class='axis-tick' style='left:{left_pct}%;'>{t1}</div>")
                ticks_set.add(t1)
                
            if p_id is not None:
                temp = interval['temps'].get(c_id, 40.0)
                freq = interval['freqs'].get(c_id, 2400.0)
                box_content = f"P{p_id}<br><span style='font-size:10px; font-weight:normal; color:#555;'>{temp:.1f}°C | {freq}MHz</span>"
                html_out.append(f"<div class='gantt-box core-box' style='left:{left_pct}%; width:{width_pct}%; flex-direction:column; line-height:1.2; text-align:center;'>{box_content}</div>")
            else:
                html_out.append(f"<div class='gantt-box idle-box' style='left:{left_pct}%; width:{width_pct}%; border:none;'></div>")
                
        # Final tick
        if total_time not in ticks_set:
            ticks_html.append(f"<div class='axis-tick' style='left:100%;'>{total_time}</div>")
            
        html_out.append("</div>") # end core row
        
        # Axis row
        html_out.append("<div class='axis-row'>")
        html_out.append("".join(ticks_html))
        html_out.append("</div>")

    # Display Thermal and DVFS Events
    html_out.append("<div style='margin-top: 20px; font-size: 13px; background-color: #fff3f3; padding: 10px; border-left: 3px solid #d32f2f;'>")
    html_out.append("<b>🔥 Thermal & DVFS Event Log:</b><ul style='margin-top: 5px; margin-bottom: 0px;'>")
    events_found = False
    for interval in eesa_intervals:
        for note in interval['notes']:
            if "Thermal Shift" in note or "DVFS" in note:
                events_found = True
                html_out.append(f"<li><b>[Time {interval['start']}]</b> {note}</li>")
    if not events_found:
        html_out.append("<li>No thermal shifts or heavy DVFS scaling occurred during this run.</li>")
    html_out.append("</ul></div>")

    html_out.append("</div>") # end wrapper
    
    st.markdown("".join(html_out), unsafe_allow_html=True)


