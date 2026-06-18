import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AutoScaler:
    def __init__(self, min_instances=1, max_instances=10, target_cpu=70.0):
        self.current_instances = 2
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu = target_cpu

    def get_current_metric(self):
        # Simulate CPU load
        base_load = 50.0
        noise = random.uniform(-20, 40)
        return max(10.0, min(100.0, base_load + noise))

    def evaluate_scaling(self):
        cpu_load = self.get_current_metric()
        logging.info(f"Current CPU Load: {cpu_load:.1f}% across {self.current_instances} instances")

        if cpu_load > self.target_cpu + 10 and self.current_instances < self.max_instances:
            self.current_instances += 1
            logging.info(f"SCALING UP -> Now running {self.current_instances} instances")
        elif cpu_load < self.target_cpu - 20 and self.current_instances > self.min_instances:
            self.current_instances -= 1
            logging.info(f"SCALING DOWN -> Now running {self.current_instances} instances")
        else:
            logging.info("Load is optimal. No scaling required.")

if __name__ == "__main__":
    scaler = AutoScaler()
    logging.info("Starting Auto-Scaler daemon...")
    for _ in range(5):
        scaler.evaluate_scaling()
        time.sleep(1)
