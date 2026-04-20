from models import Process, Core, SimulatorState
import copy

def calculate_energy(states, cores_count=2):
    total_energy = 0.0
    for state in states:
        for core_id in range(cores_count):
            freq = state.core_frequencies.get(core_id, 2400.0)
            # Power is roughly proportional to V^2 * f. Assuming V is proportional to f for simplicity here.
            # Simplified static + dynamic power calculation
            power = (freq / 2400.0)**3 if freq > 0 else 0.1 # idle power
            total_energy += power * 1.0 # 1 time unit
    return total_energy

def run_eesa(processes_input, num_cores=2, quantum=2):
    processes = copy.deepcopy(processes_input)
    cores = [Core(core_id=i) for i in range(num_cores)]
    
    time = 0
    ready_queue = []
    completed = []
    states = []
    
    # Sort by arrival time initially
    processes.sort(key=lambda p: p.arrival_time)
    process_dict = {p.pid: p for p in processes}
    
    # Time quantum tracking per core
    core_quantum = {i: 0 for i in range(num_cores)}

    while len(completed) < len(processes):
        notes = []
        
        # 1. Check arrivals
        for p in processes:
            if p.arrival_time == time and p.state == "New":
                p.state = "Ready"
                ready_queue.append(p)
                notes.append(f"Process {p.pid} arrived into Ready Queue.")
                
        # 2. Process currently running
        for core in cores:
            p = core.current_process
            if p:
                p.remaining_time -= 1
                core_quantum[core.core_id] += 1
                core.update_temperature(1.0)
                
                if p.remaining_time == 0:
                    p.state = "Completed"
                    p.completion_time = time + 1
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    completed.append(p)
                    core.current_process = None
                    core_quantum[core.core_id] = 0
                    notes.append(f"Process {p.pid} completed on Core {core.core_id}.")
                elif core_quantum[core.core_id] >= quantum:
                    p.state = "Ready"
                    ready_queue.append(p)
                    core.current_process = None
                    core_quantum[core.core_id] = 0
                    notes.append(f"Process {p.pid} quantum expired.")
                else:
                    # Thermal Check & Steering
                    if core.temperature_c >= core.TEMP_THRESHOLD:
                        # Apply DVFS temporarily or shift
                        cooler_cores = [c for c in cores if c.temperature_c < core.TEMP_THRESHOLD and c.current_process is None]
                        if cooler_cores:
                            # Shift to another core
                            target_core = min(cooler_cores, key=lambda c: c.temperature_c)
                            target_core.current_process = p
                            core.current_process = None
                            core_quantum[target_core.core_id] = core_quantum[core.core_id]
                            core_quantum[core.core_id] = 0
                            notes.append(f"Thermal Shift: Process {p.pid} moved from Core {core.core_id} ({core.temperature_c:.1f}°C) to Core {target_core.core_id} ({target_core.temperature_c:.1f}°C).")
                        else:
                            # Apply DVFS
                            core.apply_dvfs("high_temp")
                            notes.append(f"DVFS Applied: Core {core.core_id} scaled down (Temp {core.temperature_c:.1f}°C).")
                    else:
                        # Normal DVFS if heavy
                        if p.power_profile > 1.2:
                           core.apply_dvfs("heavy")
                        else:
                           core.apply_dvfs("normal")
            else:
                 core.update_temperature(1.0) # Idle cooling
                 core.apply_dvfs("normal")
                 
        # 3. Schedule from ready queue
        # Find idle cores
        idle_cores = [c for c in cores if c.current_process is None]
        # Sort cores by temperature (coolest first) for EESA
        idle_cores.sort(key=lambda c: c.temperature_c)
        
        for core in idle_cores:
            if ready_queue:
                # EESA might prioritize based on energy profile, but keep it simple FIFO for the ready queue here
                p = ready_queue.pop(0)
                p.state = "Running"
                if p.start_time is None:
                    p.start_time = time
                core.current_process = p
                core_quantum[core.core_id] = 0
                
                # Apply initial DVFS based on process profile
                if p.power_profile > 1.2:
                    core.apply_dvfs("heavy")
                else:
                    core.apply_dvfs("normal")
                    
                notes.append(f"Scheduled: Process {p.pid} → Core {core.core_id}.")

        # 4. Record State
        state = SimulatorState(
            time=time,
            ready_queue=[p.pid for p in ready_queue],
            scheduled_processes={c.core_id: (c.current_process.pid if c.current_process else None) for c in cores},
            core_temperatures={c.core_id: c.temperature_c for c in cores},
            core_frequencies={c.core_id: c.frequency_mhz for c in cores},
            completed_processes=[p.pid for p in completed],
            notes=notes
        )
        states.append(state)
        
        time += 1
        # Failsafe
        if time > 1000:
            break
            
    energy = calculate_energy(states, num_cores)
    avg_wait = sum(p.waiting_time for p in completed) / len(completed) if completed else 0
    return states, completed, energy, avg_wait


def run_round_robin(processes_input, num_cores=2, quantum=2):
    processes = copy.deepcopy(processes_input)
    cores = [Core(core_id=i) for i in range(num_cores)]
    
    time = 0
    ready_queue = []
    completed = []
    states = []
    
    processes.sort(key=lambda p: p.arrival_time)
    process_dict = {p.pid: p for p in processes}
    core_quantum = {i: 0 for i in range(num_cores)}

    while len(completed) < len(processes):
        notes = []
        
        for p in processes:
            if p.arrival_time == time and p.state == "New":
                p.state = "Ready"
                ready_queue.append(p)
                
        for core in cores:
            p = core.current_process
            if p:
                p.remaining_time -= 1
                core_quantum[core.core_id] += 1
                core.update_temperature(1.0)
                
                if p.remaining_time == 0:
                    p.state = "Completed"
                    p.completion_time = time + 1
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    completed.append(p)
                    core.current_process = None
                    core_quantum[core.core_id] = 0
                elif core_quantum[core.core_id] >= quantum:
                    p.state = "Ready"
                    ready_queue.append(p)
                    core.current_process = None
                    core_quantum[core.core_id] = 0
            else:
                 core.update_temperature(1.0)
        
        # Round Robin Scheduling: Just pick the first idle core
        idle_cores = [c for c in cores if c.current_process is None]
        for core in idle_cores:
            if ready_queue:
                p = ready_queue.pop(0)
                p.state = "Running"
                if p.start_time is None:
                    p.start_time = time
                core.current_process = p
                core_quantum[core.core_id] = 0

        state = SimulatorState(
            time=time,
            ready_queue=[p.pid for p in ready_queue],
            scheduled_processes={c.core_id: (c.current_process.pid if c.current_process else None) for c in cores},
            core_temperatures={c.core_id: c.temperature_c for c in cores},
            core_frequencies={c.core_id: c.frequency_mhz for c in cores}, # Fixed 2400 for RR implicitly since no apply_dvfs called
            completed_processes=[p.pid for p in completed],
            notes=notes
        )
        states.append(state)
        
        time += 1
        if time > 1000:
            break
            
    energy = calculate_energy(states, num_cores)
    avg_wait = sum(p.waiting_time for p in completed) / len(completed) if completed else 0
    return states, completed, energy, avg_wait
