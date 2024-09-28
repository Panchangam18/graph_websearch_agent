import json
import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from models.openai_models import get_open_ai_json
from langgraph.checkpoint.sqlite import SqliteSaver
from agents.agents import (
    PlannerAgent,
    SelectorAgent,
    ReporterAgent,
    ReviewerAgent,
    RouterAgent,
    FinalReportAgent,
    DeciderAgent,
    InterpreterAgent,
    InterpretationReviewerAgent,
    BasicAgent,
    # AddEventAgent,
    # ModifyEventAgent,
    # DeleteEventAgent,
    SubtaskAgent,
    DelegationReviewerAgent,
    RestructureAgent,
    RestructureReviewerAgent,
    EndNodeAgent
)
from prompts.prompts import (
    reviewer_prompt_template, 
    planner_prompt_template, 
    selector_prompt_template, 
    reporter_prompt_template,
    router_prompt_template,
    decider_prompt_template,
    interpreter_prompt_template,
    # interpretation_reviewer_prompt_template,
    basic_prompt_template,
    # add_event_prompt_template,
    # modify_event_prompt_template,
    # delete_event_prompt_template,
    subtask_prompt_template,
    delegation_reviewer_prompt_template,
    restructure_prompt_template,
    restructure_reviewer_prompt_template,
    reviewer_guided_json,
    selector_guided_json,
    planner_guided_json,
    router_guided_json,
    decider_guided_json,
    interpreter_guided_json,
    interpretation_reviewer_guided_json,
    basic_guided_json,
    # add_event_guided_json,
    # modify_event_guided_json,
    # delete_event_guided_json,
    subtask_guided_json,
    delegation_reviewer_guided_json,
    restructure_guided_json,
    restructure_reviewer_guided_json
)
from tools.google_serper import get_google_serper
from tools.basic_scraper import scrape_website
from tools.bipartite import assign_tasks
from tools.data_tools import gather_team_data, find_available_times
from tools.event_tools import add_bulk_events, modify_bulk_events, delete_bulk_events

from states.state import AgentGraphState, get_agent_graph_state, state

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    graph.add_node("decider",
        lambda state: DeciderAgent(
            state=state,
            model=model,
            server=server,
            guided_json=decider_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            prompt=decider_prompt_template,
            user_prompt=state["research_question"]
        )
    )

    graph.add_node("interpreter",
        lambda state: InterpreterAgent(
            state=state,
            model=model,
            server=server,
            guided_json=interpreter_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            prompt=interpreter_prompt_template,
            project_data=state["grand_calendar_info"],
            thing_to_do=state["research_question"]
        )
    )

    # graph.add_node("interpretation_reviewer",
    #     lambda state: InterpretationReviewerAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=interpretation_reviewer_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         prompt=interpretation_reviewer_prompt_template,
    #         team_data=state["team_data"]
    #     )
    # )

    graph.add_node("basic",
        lambda state: BasicAgent(
            state=state,
            model=model,
            server=server,
            guided_json=basic_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            prompt=basic_prompt_template,
            query=state["research_question"],
            team_information=state["team_information"]
        )
    )

    # # graph.add_node("add_event",
    # #     lambda state: AddEventAgent(
    # #         state=state,
    # #         model=model,
    # #         server=server,
    # #         guided_json=add_event_guided_json,
    # #         stop=stop,
    # #         model_endpoint=model_endpoint,
    # #         temperature=temperature
    # #     ).invoke(
    # #         prompt=add_event_prompt_template
    # #     )
    # # )

    # # graph.add_node("modify_event",
    # #     lambda state: ModifyEventAgent(
    # #         state=state,
    # #         model=model,
    # #         server=server,
    # #         guided_json=modify_event_guided_json,
    # #         stop=stop,
    # #         model_endpoint=model_endpoint,
    # #         temperature=temperature
    # #     ).invoke(
    # #         prompt=modify_event_prompt_template
    # #     )
    # # )

    # # graph.add_node("delete_event",
    # #     lambda state: DeleteEventAgent(
    # #         state=state,
    # #         model=model,
    # #         server=server,
    # #         guided_json=delete_event_guided_json,
    # #         stop=stop,
    # #         model_endpoint=model_endpoint,
    # #         temperature=temperature
    # #     ).invoke(
    # #         prompt=delete_event_prompt_template
    # #     )
    # # )

    graph.add_node("subtask",
        lambda state: SubtaskAgent(
            state=state,
            model=model,
            server=server,
            guided_json=subtask_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            subtask_prompt=subtask_prompt_template,
            thing_to_do=state["research_question"]
        )
    )

    # graph.add_node("delegation_reviewer",
    #     lambda state: DelegationReviewerAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=delegation_reviewer_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         prompt=delegation_reviewer_prompt_template
    #     )
    # )

    # graph.add_node("restructure",
    #     lambda state: RestructureAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=restructure_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         prompt=restructure_prompt_template
    #     )
    # )

    # graph.add_node("restructure_reviewer",
    #     lambda state: RestructureReviewerAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=restructure_reviewer_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         prompt=restructure_reviewer_prompt_template
    #     )
    # )

    # graph.add_node(
    #     "gather_team_data",
    #     lambda state: gather_team_data(
    #         state=state,
    #         admin=lambda: get_agent_graph_state(state=state, state_key="decider_admin_latest"),
    #     )
    # )

    graph.add_node(
        "assign_tasks",
        lambda state: assign_tasks(
            state=state,
            tasks_json=state["subtask_response"],
            workers=state["workers_and_descriptions"],
        )
    )

    graph.add_node(
        "find_available_times",
        lambda state: find_available_times(
            state=state,
            team_member_assignment=state["team_member_assignment"],
            team_information=state["team_information"],
        )
    )

    # graph.add_node(
    #     "bulk_add",
    #     lambda state: add_bulk_events(
    #         state=state,
    #         team_members_creds=lambda: get_agent_graph_state(state=state, state_key="team_members_creds"),
    #         events_for_members=lambda: get_agent_graph_state(state=state, state_key="events_for_members"),
    #     )
    # )

    # graph.add_node(
    #     "bulk_modify",
    #     lambda state: modify_bulk_events(
    #         state=state,
    #         team_member_creds=lambda: get_agent_graph_state(state=state, state_key="team_member_creds"),
    #         events_to_modify=lambda: get_agent_graph_state(state=state, state_key="events_to_modify"),
    #     )
    # )

    # graph.add_node(
    #     "planner", 
    #     lambda state: PlannerAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=planner_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         research_question=state["research_question"],
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
    #         # previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all"),
    #         prompt=planner_prompt_template
    #     )
    # )

    # graph.add_node(
    #     "selector",
    #     lambda state: SelectorAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=selector_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         research_question=state["research_question"],
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
    #         previous_selections=lambda: get_agent_graph_state(state=state, state_key="selector_all"),
    #         serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
    #         prompt=selector_prompt_template,
    #     )
    # )

    # graph.add_node(
    #     "reporter", 
    #     lambda state: ReporterAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         research_question=state["research_question"],
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
    #         previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"),
    #         research=lambda: get_agent_graph_state(state=state, state_key="scraper_latest"),
    #         prompt=reporter_prompt_template
    #     )
    # )

    # graph.add_node(
    #     "reviewer", 
    #     lambda state: ReviewerAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=reviewer_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         research_question=state["research_question"],
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
    #         # planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"),
    #         # selector=lambda: get_agent_graph_state(state=state, state_key="selector_latest"),
    #         reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
    #         # planner_agent=planner_prompt_template,
    #         # selector_agent=selector_prompt_template,
    #         # reporter_agent=reporter_prompt_template,
    #         # serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
    #         prompt=reviewer_prompt_template
    #     )
    # )

    # graph.add_node(
    #     "router", 
    #     lambda state: RouterAgent(
    #         state=state,
    #         model=model,
    #         server=server,
    #         guided_json=router_guided_json,
    #         stop=stop,
    #         model_endpoint=model_endpoint,
    #         temperature=temperature
    #     ).invoke(
    #         research_question=state["research_question"],
    #         feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
    #         # planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"),
    #         # selector=lambda: get_agent_graph_state(state=state, state_key="selector_latest"),
    #         # reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
    #         # planner_agent=planner_prompt_template,
    #         # selector_agent=selector_prompt_template,
    #         # reporter_agent=reporter_prompt_template,
    #         # serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
    #         prompt=router_prompt_template
    #     )
    # )


    # graph.add_node(
    #     "serper_tool",
    #     lambda state: get_google_serper(
    #         state=state,
    #         plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
    #     )
    # )

    # graph.add_node(
    #     "scraper_tool",
    #     lambda state: scrape_website(
    #         state=state,
    #         research=lambda: get_agent_graph_state(state=state, state_key="selector_latest")
    #     )
    # )

    # graph.add_node(
    #     "final_report", 
    #     lambda state: FinalReportAgent(
    #         state=state
    #     ).invoke(
    #         final_response=lambda: get_agent_graph_state(state=state, state_key="reporter_latest")
    #     )
    # )

    graph.add_node("end", lambda state: EndNodeAgent(state).invoke())

    # Define the edges in the agent graph
    def pass_review(state: AgentGraphState):
        review_list = state["router_response"]
        if review_list:
            review = review_list[-1]
        else:
            review = "No review"

        if review != "No review":
            if isinstance(review, HumanMessage):
                review_content = review.content
            else:
                review_content = review
            
            review_data = json.loads(review_content)
            next_agent = review_data["next_agent"]
        else:
            next_agent = "end"

        return next_agent

    def decider_next(state: AgentGraphState):
        review_list = state["decider_response"]
        review = review_list[-1]

        if isinstance(review, HumanMessage):
            review_content = review.content
        else:
            review_content = review
        
        review_data = json.loads(review_content)
        next_agent = review_data["next_agent"]

        return next_agent

    # # Add edges to the graph
    # graph.set_entry_point("planner")
    # graph.set_finish_point("end")
    # graph.add_edge("planner", "serper_tool")
    # graph.add_edge("serper_tool", "selector")
    # graph.add_edge("selector", "scraper_tool")
    # graph.add_edge("scraper_tool", "reporter")
    # graph.add_edge("reporter", "reviewer")
    # graph.add_edge("reviewer", "router")

    # graph.add_conditional_edges(
    #     "router",
    #     lambda state: pass_review(state=state),
    # )

    # graph.add_edge("final_report", "end")

    # INITIAL DECLARATIONS

    graph.set_entry_point("decider")
    
    graph.set_finish_point("end")
    
    graph.add_conditional_edges("decider",
        lambda state: decider_next(state=state),) # adjust pass review function to fit
    
    # PATH 1 (Interpreting Calendar And Events)

    graph.add_edge("interpreter", "end")
    
    # graph.add_conditional_edges("interpreter",
    #     lambda state: pass_review(state=state),) # may need to add an agent to provide more data if necessary

    # graph.add_conditional_edges("interpetation_reviewer",
    #     lambda state: pass_review(state=state),) 

    # PATH 2 (Basic Requests on Calendar)

    graph.add_edge("basic", "end")
    
                    # graph.add_edge("add_event", "basic_reviewer")

                    # graph.add_edge("modify_event", "basic_reviewer")

                    # graph.add_edge("delete_event", "basic_reviewer")

    # PATH 3 (Project Creator and Delegator)

    graph.add_edge("subtask", "assign_tasks")

    graph.add_edge("assign_tasks", "find_available_times")

    graph.add_edge("find_available_times", "end")

    # graph.add_edge("delegation_reviewer", "find_available_times")

    # graph.add_edge("find_available_times", "bulk_add")

    # graph.add_edge("bulk_add", "end")

    # PATH 4 (Restructure/Optimize Calendar)

    # graph.add_edge("restructure", "restructure_reviewer")

    # graph.add_conditional_edges("restructure_reviewer",
    #     lambda state: pass_review(state=state),)

    # graph.add_edge("bulk_modify", "end")

    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow
