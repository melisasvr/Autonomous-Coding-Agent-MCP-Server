import json
import os

class TodoApp:
    def __init__(self, filename):
        self.filename = filename
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.tasks = json.load(file)
        else:
            self.tasks = []

    def save_tasks(self):
        with open(self.filename, 'w') as file:
            json.dump(self.tasks, file)

    def add_task(self, task):
        self.tasks.append(task)
        self.save_tasks()

    def remove_task(self, task_index):
        try:
            del self.tasks[task_index]
            self.save_tasks()
        except IndexError:
            print("Invalid task index")

    def list_tasks(self):
        for index, task in enumerate(self.tasks):
            print(f"{index + 1}. {task}")

def main():
    app = TodoApp('tasks.json')
    app.add_task("Task 1")
    app.add_task("Task 2")
    app.list_tasks()
    app.remove_task(0)
    app.list_tasks()

if __name__ == "__main__":
    main()