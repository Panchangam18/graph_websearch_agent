from states.state import AgentGraphState
from langchain_core.messages import HumanMessage

def add_event():
    pass

def delete_event():
    pass    

def modify_event():
    pass

def add_bulk_events(state: AgentGraphState, team_members_creds, events_for_members):
    print("Added all events")
    bulk_added_details = None
    state["bulk_events_added"].append(HumanMessage(role="system", content=str({"bulk_events_added": bulk_added_details})))
    pass

def delete_bulk_events():
    pass

def modify_bulk_events():
    pass