import numpy as np
from scipy.optimize import linear_sum_assignment
import spacy
from termcolor import colored
nlp = spacy.load("en_core_web_lg")
from states.state import AgentGraphState
from langchain_core.messages import HumanMessage
import json

# Provided data
# team_members_json = [
#     {"name": "Alice", "role_description": "Janitor and sweeper, responsible for maintaining cleanliness in the office"},
#     {"name": "Bob", "role_description": "Software engineer and developer"},
#     {"name": "Carol", "role_description": "Marketing manager and strategist"},
#     {"name": "Dave", "role_description": "Graphic designer and illustrator"},
#     {"name": "Eve", "role_description": "Project manager and coordinator"}
# ]

# tasks_json = [
#     {"description": "Clean the office and empty trash bins"},
#     {"description": "Develop a new feature for the company website"},
#     {"description": "Create and manage social media campaigns"},
#     {"description": "Design a new logo for the product launch"},
#     {"description": "Coordinate the upcoming team meeting"},
#     {"description": "Sweep and mop the floors in the lobby"},
#     {"description": "Fix bugs in the mobile application"},
#     {"description": "Analyze market trends and customer feedback"},
#     {"description": "Design promotional materials for the new product"},
#     {"description": "Organize the project timeline and assign tasks"},
#     {"description": "Clean the windows and dust the office furniture"},
#     {"description": "Implement a new API for the backend system"},
#     {"description": "Create a marketing plan for the holiday season"},
#     {"description": "Develop visual concepts for the ad campaign"},
#     {"description": "Oversee the progress of the project milestones"},
#     {"description": "Clean the restrooms and refill supplies"},
#     {"description": "Optimize the database performance"},
#     {"description": "Conduct market research and competitor analysis"},
#     {"description": "Design the layout for the company's annual report"},
#     {"description": "Manage the project budget and resources"},
#     {"description": "Create a marketing strategy for the upcoming year"},
#     {"description": "Implement a new backend python feature"},
#     {"description": "Make a new design for the product's logo"},
#     {"description": "Do all of the dishes"},
#     {"description": "Supervise all of the team members in their tasks"}
# ]
# def get_cost_matrix(team_members_json, tasks_json):
#     # Extract role and task descriptions
#     role_descriptions = [member["role_description"] for member in team_members_json]
#     task_descriptions = [task["description"] for task in tasks_json]

#     # Convert descriptions to spaCy vectors
#     role_vectors = np.array([nlp(role).vector for role in role_descriptions])
#     task_vectors = np.array([nlp(task).vector for task in task_descriptions])

#     # Calculate similarity matrix using cosine similarity
#     similarity_matrix = np.dot(role_vectors, task_vectors.T) / (
#         np.linalg.norm(role_vectors, axis=1)[:, None] * np.linalg.norm(task_vectors, axis=1)
#     )

#     # Convert similarity to cost (1 - similarity)
#     cost_matrix = 1 - similarity_matrix

#     return cost_matrix

# Function to perform matching and ensure each worker gets at least one task
def assign_tasks(state: AgentGraphState, tasks_json, workers):

    tasks_dict = json.loads(tasks_json)

    role_descriptions = [member["role_description"] for member in workers]
    
    # Extract task descriptions and their categories including project name
    task_descriptions = []
    task_categories = []
    for project_name, categories in tasks_dict.items():
        for category, tasks in categories.items():
            for task in tasks:
                task_descriptions.append(task)
                task_categories.append(f"{project_name}: {category}")
    
    # Convert descriptions to spaCy vectors
    role_vectors = np.array([nlp(role).vector for role in role_descriptions])
    task_vectors = np.array([nlp(task).vector for task in task_descriptions])

    # Calculate similarity matrix using cosine similarity
    similarity_matrix = np.dot(role_vectors, task_vectors.T) / (
        np.linalg.norm(role_vectors, axis=1)[:, None] * np.linalg.norm(task_vectors, axis=1)
    )

    # Convert similarity to cost (1 - similarity)
    cost_matrix = 1 - similarity_matrix

    assigned_tasks = set()
    worker_task_assignment = {worker["name"]: {} for worker in workers}

    tasks = task_descriptions

    # First round to ensure each worker gets at least one task
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    for i, j in zip(row_ind, col_ind):
        if j not in assigned_tasks:
            worker_name = workers[i]["name"]
            task_category = task_categories[j]
            if task_category not in worker_task_assignment[worker_name]:
                worker_task_assignment[worker_name][task_category] = []
            worker_task_assignment[worker_name][task_category].append(tasks[j])
            assigned_tasks.add(j)

    # Assign remaining tasks
    remaining_tasks = [j for j in range(len(tasks)) if j not in assigned_tasks]
    while remaining_tasks:
        row_ind, col_ind = linear_sum_assignment(cost_matrix[:, remaining_tasks])
        for i, j in zip(row_ind, col_ind):
            task_index = remaining_tasks[j]
            worker_name = workers[i]["name"]
            task_category = task_categories[task_index]
            if task_category not in worker_task_assignment[worker_name]:
                worker_task_assignment[worker_name][task_category] = []
            worker_task_assignment[worker_name][task_category].append(tasks[task_index])
            assigned_tasks.add(task_index)
        remaining_tasks = [j for j in range(len(tasks)) if j not in assigned_tasks]

    new_state = state.copy()
    new_state["team_member_assignment"] = worker_task_assignment

    state = new_state

    print(colored(f"Assignment: {worker_task_assignment}", 'red'))

    return {"team_member_assignment": state["team_member_assignment"]}

# # Perform task assignment
# task_assignment = assign_tasks(get_cost_matrix(team_members_json, tasks_json), team_members_json, [task["description"] for task in tasks_json])

# # Display the results
# for worker, tasks in task_assignment.items():
#     print(f"Worker {worker} is assigned to tasks:")
#     for task in tasks:
#         print(f"  - {task}")
