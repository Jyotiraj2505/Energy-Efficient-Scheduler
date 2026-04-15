# =============================================================================
# MODULE 1 — INTELLIGENT SCHEDULER CORE (ENERGY PROFILING ADDED)
# =============================================================================
# This version includes:
# - Process class
# - SchedulerCore basic structure
# - Energy score calculation
# - Energy classification (HIGH, MEDIUM, LOW)
# =============================================================================


# -------------------------------
# ENERGY THRESHOLDS
# -------------------------------
HIGH_THRESHOLD = 15
LOW_THRESHOLD = 5


# -------------------------------
# PROCESS CLASS
# -------------------------------
class Process:
    def __init__(self, pid, burst_time, priority, arrival_time):
        self.pid = pid
        self.burst_time = burst_time
        self.priority = priority
        self.arrival_time = arrival_time

        # Energy attributes
        self.energy_score = 0
        self.energy_label = ""

    def __repr__(self):
        return f"Process({self.pid}, Burst={self.burst_time}, Priority={self.priority})"


# -------------------------------
# SCHEDULER CORE
# -------------------------------
class SchedulerCore:
    def __init__(self):
        self.process_list = []
        self.ready_queue = []
        self.current_time = 0

    # -------------------------------
    # ENERGY CALCULATION
    # -------------------------------
    def calculate_energy_score(self, process):
        return process.burst_time * process.priority

    # -------------------------------
    # ENERGY CLASSIFICATION
    # -------------------------------
    def classify_energy(self, score):
        if score >= HIGH_THRESHOLD:
            return "HIGH"
        elif score <= LOW_THRESHOLD:
            return "LOW"
        else:
            return "MEDIUM"

    # -------------------------------
    # ADD PROCESS
    # -------------------------------
    def add_process(self, process):
        process.energy_score = self.calculate_energy_score(process)
        process.energy_label = self.classify_energy(process.energy_score)

        self.process_list.append(process)


# -------------------------------
# TEST RUN
# -------------------------------
if __name__ == "__main__":
    scheduler = SchedulerCore()

    # Sample processes
    p1 = Process("P1", 5, 3, 0)
    p2 = Process("P2", 2, 1, 1)

    scheduler.add_process(p1)
    scheduler.add_process(p2)

    print("Processes with Energy Profiling:")
    for p in scheduler.process_list:
        print(p.pid, "| Score:", p.energy_score, "| Type:", p.energy_label)