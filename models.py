from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    power_profile: float  # Power multiplier conceptually (e.g. 1.0 is normal, 1.5 is heavy)
    
    # State tracking mutable fields
    remaining_time: int = field(init=False)
    state: str = "New" # New, Ready, Running, Completed
    completion_time: Optional[int] = None
    start_time: Optional[int] = None
    turnaround_time: Optional[int] = None
    waiting_time: Optional[int] = None
    
    def __post_init__(self):
        self.remaining_time = self.burst_time

@dataclass
class Core:
    core_id: int
    frequency_mhz: float = 2400.0
    voltage_v: float = 1.0
    temperature_c: float = 40.0
    current_process: Optional[Process] = None
    
    # Thresholds
    TEMP_THRESHOLD: float = 75.0
    CRITICAL_TEMP: float = 85.0
    BASE_TEMP: float = 40.0
    
    def update_temperature(self, time_delta: float):
        if self.current_process:
            # Heat up based on power profile and frequency
            heat_generated = (self.frequency_mhz / 2400.0) * self.voltage_v * self.current_process.power_profile * 2.0
            self.temperature_c = min(self.CRITICAL_TEMP, self.temperature_c + heat_generated)
        else:
            # Cool down
            self.temperature_c = max(self.BASE_TEMP, self.temperature_c - 1.5)

    def apply_dvfs(self, load="normal"):
        if load == "high_temp":
            self.frequency_mhz = 1200.0
            self.voltage_v = 0.8
        elif load == "heavy":
            self.frequency_mhz = 3200.0
            self.voltage_v = 1.2
        else:
            self.frequency_mhz = 2400.0
            self.voltage_v = 1.0

@dataclass
class SimulatorState:
    time: int
    ready_queue: List[int] # List of PIDs
    scheduled_processes: Dict[int, Optional[int]] # Core ID -> PID
    core_temperatures: Dict[int, float]
    core_frequencies: Dict[int, float]
    completed_processes: List[int]
    notes: List[str] # To hold "cut" or "shift" event messages

    def clone(self):
        return SimulatorState(
            time=self.time,
            ready_queue=list(self.ready_queue),
            scheduled_processes=dict(self.scheduled_processes),
            core_temperatures=dict(self.core_temperatures),
            core_frequencies=dict(self.core_frequencies),
            completed_processes=list(self.completed_processes),
            notes=list(self.notes)
        )
