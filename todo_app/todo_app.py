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
    while True:
        print("\n1. Add task")
        print("2. Remove task")
        print("3. List tasks")
        print("4. Quit")
        choice = input("Choose an option: ")
        if choice == '1':
            task = input("Enter a task: ")
            app.add_task(task)
        elif choice == '2':
            app.list_tasks()
            task_index = int(input("Enter the task number to remove: ")) - 1
            app.remove_task(task_index)
        elif choice == '3':
            app.list_tasks()
        elif choice == '4':
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()