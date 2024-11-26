import concurrent.futures
import time

class Thread:
    def __init__(self, max_workers=5):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def run_task(self, func, *args, **kwargs):
        """
        Runs a task in a thread

        Parameters:
        func -- Function to run
        *args -- Arguments to the function
        **kwargs -- Keyword arguments to the function

        Returns:
        Future object
        """
        future = self.executor.submit(func, *args, **kwargs)
        self.futures.append(future)
        return future

    def shutdown(self, wait=True):
        """
        Shuts down the thread pool
        """
        self.executor.shutdown(wait=wait)

    def check_status(self):
        """
        Checks the status of all submitted tasks
        """
        for future in self.futures:
            if future.done():
                print(f"Task {future} completed with result: {future.result()}")
            elif future.cancelled():
                print(f"Task {future} was cancelled.")
            else:
                print(f"Task {future} is still running.")

    def cancel_tasks(self):
        """
        Attempts to cancel all running tasks
        """
        for future in self.futures:
            future.cancel()

    def wait_for_all(self):
        """
        Waits for all tasks to complete
        """
        concurrent.futures.wait(self.futures)

    def get_results(self):
        """
        Retrieves results of all completed tasks
        """
        results = []
        for future in self.futures:
            if future.done() and not future.cancelled():
                results.append(future.result())
        return results

    def get_exceptions(self):
        """
        Retrieves exceptions from tasks that failed
        """
        exceptions = []
        for future in self.futures:
            if future.done() and future.exception() is not None:
                exceptions.append(future.exception())
        return exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()

def example_task(duration):
    print(f"Task starting, will take {duration} seconds.")
    time.sleep(duration)
    print("Task completed.")

def print_numbers(count):
    for i in range(count):
        print(i)
        time.sleep(1)
    print("Number printing completed.")

def calculate_sum(n):
    total = sum(range(n + 1))
    print(f"Sum of numbers from 0 to {n} is {total}.")
    return total

if __name__ == "__main__":
    # Example of using Thread without context manager
    thread_manager = Thread(max_workers=3)
    try:
        futures = []
        futures.append(thread_manager.run_task(example_task, 5))
        futures.append(thread_manager.run_task(print_numbers, 5))
        futures.append(thread_manager.run_task(calculate_sum, 100))

        total_sum = futures[2].result()
        print('The sum is: ', total_sum)

        # Wait for all tasks to complete
        thread_manager.wait_for_all()

        # Check status of all tasks
        thread_manager.check_status()

        # Get results of all completed tasks
        results = thread_manager.get_results()
        print('Results of all tasks:', results)

        # Get exceptions from tasks that failed
        exceptions = thread_manager.get_exceptions()
        if exceptions:
            print('Exceptions from tasks:', exceptions)
    finally:
        # Explicitly shut down the thread pool
        thread_manager.shutdown()


