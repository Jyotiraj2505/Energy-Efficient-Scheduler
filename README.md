# Energy-Efficient-Scheduler
Not everything needs to run at full speed all the time. This project is about knowing when it should run at full speed.

# The Main Idea of project is that
Most of the systems today chase performance : faster execution, quicker response, more power.
But at what cost??
-That extra performance often comes with:
  unnecessary energy usage,
  heat buildup,
  reduced efficiency over time
So instead of asking “How fast can we go?”, we ask: “What’s the smartest way to run tasks without wasting energy?”

# What We’re Trying to Do is 
We’re building a CPU scheduling approach that:
  adapts to the current workload
  avoids running at full power when it’s not needed
  keeps performance stable without overconsumption
  stays aware of system temperature


# The system makes decisions based on:
Workload → How heavy are the tasks?
CPU State → Is the system idle or busy?
Temperature → Is it heating up?
Based on this, it adjusts how the CPU behaves instead of keeping it constant all the time.

# Why This Actually Matters
This isn’t just theory.
Energy-aware scheduling is important in:
mobile devices (battery life matters)
laptops (heat + performance balance)
embedded systems
large-scale servers (huge power savings)
Even small improvements can make a big real-world impact.


# About Us
This project is built by two developers working together with a simple goal:
Make something that is not just functional, but actually thoughtful.
No unnecessary complexity.
No over-engineering.
Just a clean idea executed properly.


# NOTE:
This is a work in progress — and that’s intentional.
We’re focusing on understanding the problem deeply and building a solution step by step, instead of rushing to make it look “complete”.


# Progress Update

- Created basic structure of scheduler core
- Implemented Process class
- Initialized SchedulerCore class

# Progress Update

- Implemented energy score calculation
- Added energy classification (HIGH, MEDIUM, LOW)
- Integrated energy profiling into scheduler