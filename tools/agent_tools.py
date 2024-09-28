from langchain.tools import tool
@tool
def add_event(admin_id: str, team_member_id: str, summary: str, start_time: str, end_time: str, description='', recurrence=[]):
    '''add an event to the calendar of the team member with id team_member_id working under admin with id admin_id'''
    print(f"added event for {admin_id} and {team_member_id} with {summary},{start_time},{end_time},{description},{recurrence}")
    return f"added event for {admin_id} and {team_member_id} with {summary},{start_time},{end_time},{description},{recurrence}"

@tool
def delete_event(admin_id: str, team_member_id: str, event_id: str):
    '''delete an event from the calendar of the team member with id team_member_id working under admin with id admin_id'''
    print(f"deleted event for {admin_id} and {team_member_id} with {event_id}")
    return f"deleted event for {admin_id} and {team_member_id} with {event_id}"

@tool
def modify_event(admin_id: str, team_member_id: str, event_id: str, summary: str=None, start_time: str=None, end_time: str=None, description: str = None, recurrence: list = None):
    '''modify an event in the calendar of the team member with id team_member_id working under admin with id admin_id'''
    print(f"modified event for {admin_id} and {team_member_id} with {event_id},{summary},{start_time},{end_time},{description},{recurrence}")
    return f"modified event for {admin_id} and {team_member_id} with {event_id},{summary},{start_time},{end_time},{description},{recurrence}"