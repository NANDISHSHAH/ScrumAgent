import os
from crewai import Agent, Task, Crew,Process
from langchain_openai import ChatOpenAI
from crewai_tools import BaseTool 
from pydantic import BaseModel
# Set your API key directly or ensure the environment variable is set correctly
os.environ["OPENAI_API_KEY"] = "NA"  # Replace with your actual API key
from crewai_tools import BaseTool

# class MyCustomTool(BaseTool):
#     name: str = "Scrum tool"
#     description: str = "Clear description for what this tool is useful for, your agent will need this information to use it."
#     model_set:None
#     def __init__(self, model_name, base_url, api_key):
#         self.model_set = ChatOpenAI(model=model_name, base_url=base_url, openai_api_key=api_key)
    

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         response = self.model_set(argument)
#         return response
    
class ChatOpenAITool(BaseTool):
    model_name: str
    base_url: str
    api_key: str = "NA"
    name:str
    description:str
    llm: ChatOpenAI = None

    def __init__(self, **data):
        super().__init__(**data)
        # llm initialization moved to post_init to avoid attribute errors
        self._post_init()

    def _post_init(self):
        # Initialize the llm attribute after the Pydantic model is constructed
        self.llm = ChatOpenAI(model=self.model_name, base_url=self.base_url, openai_api_key=self.api_key)

    def _run(self, prompt: str) -> str:
        # Pass the prompt to the LLM and return the response
        response = self.llm(prompt)
        return response['choices'][0]['message']['content']  # Adjust this to match the LLM's response format

    def _arun(self, prompt: str) -> str:
        # Optional: Implement this if you need asynchronous functionality
        raise NotImplementedError("Async run is not implemented for this tool.")


# Initialize the LLM with the correct API key
llm = ChatOpenAI(
    model="llama3.1:latest",
    base_url="http://localhost:11434/v1",
    openai_api_key=os.getenv("NA")  # This should now correctly fetch the API key
)

ollama_tool = ChatOpenAITool(
    model_name="llama3.1:latest",
    base_url="http://localhost:11434/v1",
    name="Ollama LLM Tool",  # Provide a descriptive name
    description="Tool to interact with the Ollama LLM for Scrum tasks."  # Provide a meaningful description
)
# Ask the user for the topic of the Scrum meeting
topic = input("Enter the topic for the Scrum planner: ")

# Define the agents with the topic integrated into their goals
scrum_master = Agent(
    role='Scrum Master',
    goal=f'Facilitate the Scrum meeting on "{topic}", ensuring that it stays on track, and the Scrum process is followed.',
    backstory='As the Scrum Master, you are the guardian of the process and help the team to stay focused and efficient.',
    llm = llm
    # tools=[llm]  # Attach the Ollama tool
)

product_owner = Agent(
    role='Product Owner',
    goal=f'Prioritize the backlog related to "{topic}" and ensure that the team understands the goals for the sprint.',
    backstory='You are responsible for maximizing the value of the product by managing and prioritizing the product backlog.',
    llm =llm
    # tools=[llm]  # Attach the Ollama tool
)

development_team = Agent(
    role='Development Team',
    goal=f'Provide estimates, discuss technical aspects of "{topic}", and commit to the sprint goals.',
    backstory='You are the team responsible for delivering potentially shippable increments of the product at the end of each sprint.',
    llm = llm
    # tools=[llm]  # Attach the Ollama tool
)

# Define the tasks with the topic integrated into their descriptions
backlog_review_task = Task(
    description=f'Review the product backlog for "{topic}", prioritize items based on their value, and clarify any requirements.',
    expected_output='A prioritized list of backlog items ready for sprint planning.',
    agent=product_owner
)

sprint_planning_task = Task(
    description=f'Lead the planning session on "{topic}", facilitate discussions, and ensure the team commits to the sprint goals.',
    expected_output='A finalized sprint plan with committed tasks and goals.',
    agent=scrum_master
)

task_estimation_task = Task(
    description=f'Discuss the technical aspects of "{topic}", provide estimates, and identify any potential risks.',
    expected_output='Time and effort estimates for all tasks in the sprint.',
    agent=development_team
)

finalization_task = Task(
    description=f'Finalize the sprint plan for "{topic}", ensure everyone is aligned, and confirm that the sprint goals are achievable.',
    expected_output='A confirmed sprint plan ready for execution.',
    agent=scrum_master
)

# process = Process(
#     sequential=True,
#     iteration_limit=100,  # Increase the iteration limit
#     time_limit=600  # Increase the time limit in seconds
# )

# Create the crew
crew = Crew(
    agents=[scrum_master, product_owner, development_team],
    tasks=[backlog_review_task, sprint_planning_task, task_estimation_task, finalization_task],
    # verbose=True
)
# Create the crew
# crew = Crew(
#     agents=[scrum_master, product_owner, development_team],
#     tasks=[backlog_review_task, sprint_planning_task, task_estimation_task, finalization_task]
# )

# Run the crew with the topic as input
result = crew.kickoff(inputs={'topic': topic})
print(result)
