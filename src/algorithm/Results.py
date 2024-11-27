from utils import IO
from algorithm import Context, Instance, Solution

class Results:
    def __init__(self, context: Context, instance: Instance, solution: Solution):
        self.context = context
        self.instance = instance
        self.solution = solution

        self.save_results()
        self.solution_validation()

    def save_results(self):
        """
        Save the results
        """
        pass

    def solution_validation(self):
        """
        Validate the solution
        """
        pass

    def __str__(self) -> str:
        pass