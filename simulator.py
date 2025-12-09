import threading
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

# ======================================================================
# THREAD STATE ENUM
# ======================================================================
class ThreadState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"

# ======================================================================
# SHARED RESOURCE WITH LOCK + SEMAPHORE
# ======================================================================
class SharedResource:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(1)

    def work_with_monitor(self, name):
        print(f"{name} waiting for MONITOR | State: BLOCKED")
        with self.lock:
            print(f"{name} entered MONITOR | State: RUNNING")
            local = self.counter
            time.sleep(0.1)
            self.counter = local + 1
            print(f"{name} exiting MONITOR | counter = {self.counter}")

    def work_with_semaphore(self, name):
        print(f"{name} waiting for SEMAPHORE | State: BLOCKED")
        self.semaphore.acquire()
        try:
            print(f"{name} acquired SEMAPHORE | State: RUNNING")
            local = self.counter
            time.sleep(0.1)
            self.counter = local + 1
            print(f"{name} releasing SEMAPHORE | counter = {self.counter}")
        finally:
            self.semaphore.release()

# ======================================================================
# SIMULATED USER TASK
# ======================================================================
class SimulatedTask:
    def __init__(self, name, resource, use_semaphore):
        self.name = name
        self.resource = resource
        self.use_semaphore = use_semaphore
        self.state = ThreadState.NEW

    def run(self):
        self.state = ThreadState.READY
        print(f"{self.name} is READY")

        self.state = ThreadState.RUNNING
        print(f"{self.name} is RUNNING")

        if self.use_semaphore:
            self.resource.work_with_semaphore(self.name)
        else:
            self.resource.work_with_monitor(self.name)

        self.state = ThreadState.TERMINATED
        print(f"{self.name} is TERMINATED\n")

# ======================================================================
# MANY TO ONE
# ======================================================================
def demo_many_to_one():
    print("\n===== Many-to-One Model =====")
    resource = SharedResource()

    tasks = [
        SimulatedTask("UserThread-1", resource, False),
        SimulatedTask("UserThread-2", resource, False),
        SimulatedTask("UserThread-3", resource, False)
    ]

    def run_all():
        for task in tasks:
            task.run()

    kernel_thread = threading.Thread(target=run_all)
    kernel_thread.start()
    kernel_thread.join()

    print("Final Counter (Many-to-One):", resource.counter)

# ======================================================================
# ONE TO ONE
# ======================================================================
def demo_one_to_one():
    print("\n===== One-to-One Model =====")
    resource = SharedResource()

    threads = []
    for i in range(1, 4):
        task = SimulatedTask(f"UserThread-{i}", resource, True)
        t = threading.Thread(target=task.run)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Final Counter (One-to-One):", resource.counter)

# ======================================================================
# MANY TO MANY
# ======================================================================
def demo_many_to_many():
    print("\n===== Many-to-Many Model =====")
    resource = SharedResource()

    with ThreadPoolExecutor(max_workers=2) as executor:
        for i in range(1, 6):
            task = SimulatedTask(f"UserThread-{i}", resource, True)
            executor.submit(task.run)

    print("Final Counter (Many-to-Many):", resource.counter)

# ======================================================================
# MAIN
# ======================================================================
if __name__ == "__main__":
    print("Real-Time Multi-threaded Application Simulator\n")

    demo_many_to_one()
    demo_one_to_one()
    demo_many_to_many()

    print("\nSimulation Completed.")

