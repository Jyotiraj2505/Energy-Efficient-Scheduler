# =============================================================================
# MODULE 1 — INTELLIGENT SCHEDULER CORE (BASIC STRUCTURE)
# =============================================================================
# This is the initial structure of the scheduler.
# It defines the Process class and SchedulerCore skeleton.
# Logic will be added in later commits.
# =============================================================================


# -------------------------------
# PROCESS CLASS
# -------------------------------
class Process:
    def __init__(self, pid, burst_time, priority, arrival_time):
        self.pid = pid
        self.burst_time = burst_time
        self.priority = priority
        self.arrival_time = arrival_time

        # Will be calculated later
        self.energy_score = 0
        self.energy_label = ""

    def __repr__(self):
        return f"Process({self.pid}, Burst={self.burst_time}, Priority={self.priority})"


# -------------------------------
# SCHEDULER CORE (EMPTY FOR NOW)
# -------------------------------
class SchedulerCore:
    def __init__(self):
        self.process_list = []
        self.ready_queue = []
        self.current_time = 0

    def add_process(self, process):
        self.process_list.append(process)


# -------------------------------
# TEST RUN (BASIC)
# -------------------------------
if __name__ == "__main__":
    scheduler = SchedulerCore()

    p1 = Process("P1", 5, 3, 0)
    p2 = Process("P2", 2, 1, 1)

    scheduler.add_process(p1)
    scheduler.add_process(p2)

    print("Processes added:")
    for p in scheduler.process_list:
        print(p)