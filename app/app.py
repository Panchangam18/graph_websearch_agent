from agent_graph.graph import create_graph, compile_workflow

# server = 'ollama'
# model = 'llama3:instruct'
# model_endpoint = None

server = 'openai'
model = 'gpt-3.5-turbo'
model_endpoint = None

# server = 'vllm'
# model = 'meta-llama/Meta-Llama-3-70B-Instruct' # full HF path
# model_endpoint = 'https://kcpqoqtjz0ufjw-8000.proxy.runpod.net/' 
# #model_endpoint = runpod_endpoint + 'v1/chat/completions'
# stop = "<|end_of_text|>"

iterations = 40

print ("Creating graph and compiling workflow...")
graph = create_graph(server=server, model=model, model_endpoint=model_endpoint)
workflow = compile_workflow(graph)
print ("Graph and workflow created.")


if __name__ == "__main__":

    verbose = False


    query = input("Please enter your research question: ")
        


    company_projects = {
    "projects": [
        {
            "project_id": "P001",
            "project_name": "Website Redesign",
            "team_members": [
                {
                    "name": "Alice",
                    "role": "Designer",
                    "tasks": {
                        "Create wireframes": True,
                        "Design homepage": True,
                        "Design product pages": False,
                        "Create style guide": True
                    }
                },
                {
                    "name": "Bob",
                    "role": "Frontend Developer",
                    "tasks": {
                        "Implement homepage": True,
                        "Implement product pages": False,
                        "Setup React components": True,
                        "Integrate API": False
                    }
                }
            ]
        },
        {
            "project_id": "P002",
            "project_name": "Marketing Campaign",
            "team_members": [
                {
                    "name": "Charlie",
                    "role": "Marketing Specialist",
                    "tasks": {
                        "Create social media strategy": True,
                        "Design ad creatives": False,
                        "Schedule posts": True,
                        "Analyze campaign performance": False
                    }
                },
                {
                    "name": "Diana",
                    "role": "Content Writer",
                    "tasks": {
                        "Write blog posts": True,
                        "Create email newsletters": True,
                        "Develop ad copy": False,
                        "Prepare press releases": True
                    }
                }
            ]
        }
    ],
    "employees": [
        {
            "name": "Alice",
            "projects": {
                "Website Redesign": {
                    "Create wireframes": True,
                    "Design homepage": True,
                    "Design product pages": False,
                    "Create style guide": True
                }
            }
        },
        {
            "name": "Bob",
            "projects": {
                "Website Redesign": {
                    "Implement homepage": True,
                    "Implement product pages": False,
                    "Setup React components": True,
                    "Integrate API": False
                }
            }
        },
        {
            "name": "Charlie",
            "projects": {
                "Marketing Campaign": {
                    "Create social media strategy": True,
                    "Design ad creatives": False,
                    "Schedule posts": True,
                    "Analyze campaign performance": False
                }
            }
        },
        {
            "name": "Diana",
            "projects": {
                "Marketing Campaign": {
                    "Write blog posts": True,
                    "Create email newsletters": True,
                    "Develop ad copy": False,
                    "Prepare press releases": True
                }
            }
        }
    ]
}



    work_and_descrip = [
    {"name": "Alice", "role_description": "Project Manager responsible for overseeing the entire project, ensuring timely delivery and coordination among team members"},
    {"name": "Bob", "role_description": "Front-end Developer specializing in HTML, CSS, and JavaScript, responsible for the visual aspects of the website"},
    {"name": "Charlie", "role_description": "Back-end Developer experienced in server-side programming, databases, and APIs, responsible for the website's functionality"},
    {"name": "Diana", "role_description": "UI/UX Designer with expertise in creating user-friendly interfaces and improving user experience"},
    {"name": "Eve", "role_description": "Content Writer responsible for creating and managing the website's content, including text, images, and multimedia"},
    {"name": "Frank", "role_description": "SEO Specialist focused on optimizing the website for search engines to increase visibility and traffic"},
    {"name": "Grace", "role_description": "Quality Assurance Tester responsible for testing the website to identify bugs and ensure it meets quality standards"},
    {"name": "Hank", "role_description": "DevOps Engineer specializing in setting up and maintaining the hosting environment, CI/CD pipelines, and monitoring the deployment"}
]


    dict_inputs = {"research_question": query, "team_information": "The admin id is 1234, John's id is 5678, and Jane's key is 9012", "grand_calendar_info": company_projects, "workers_and_descriptions": work_and_descrip}
        # thread = {"configurable": {"thread_id": "4"}}
    limit = {"recursion_limit": iterations}

        # for event in workflow.stream(
        #     dict_inputs, thread, limit, stream_mode="values"
        #     ):
        #     if verbose:
        #         print("\nState Dictionary:", event)
        #     else:
        #         print("\n")

    for event in workflow.stream(
            dict_inputs, limit
            ):
            if verbose:
                print("\nState Dictionary:", event)
            else:
                print("\n")



    