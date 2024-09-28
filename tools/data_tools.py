from states.state import AgentGraphState
from langchain_core.messages import HumanMessage

def gather_team_data(state: AgentGraphState, admin):
    print("Gathered the team's information")
    data = None
    state["team_data"].append(HumanMessage(role="system", content=str({"team_data": data})))
    return {"team_data": state["team_data"]}

def find_available_times(state: AgentGraphState, team_member_assignment, team_information):
    for key in team_member_assignment:
        print(f"found available times for {key}")
    print(team_information)
    data = None
    state["available_timings"] = data
    return{"available_timings": state["available_timings"]}
    
    

