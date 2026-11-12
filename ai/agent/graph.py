"""Tool-calling LangGraph with offline mock and configurable OpenAI providers."""

import json
import os

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import input_schema, predict_income

TOOLS = [input_schema, predict_income]
SYSTEM_PROMPT = (
    'You are a census income assistant. Use input_schema to inspect required inputs. '
    'Use predict_income for every prediction; never invent model outputs. '
    'Never invent missing feature values. Ask the user for missing or invalid fields. '
    'income and high_income are targets and must not be passed as features. '
    'Explain the predicted class and its model probability without claiming certainty.'
)


class MockChatModel:
    """Deterministic LLM stand-in that emits real LangChain tool calls, offline."""

    def invoke(self, messages):
        last = messages[-1]
        if isinstance(last, ToolMessage):
            return AIMessage(content=f'Mock assistant — tool result:\n{last.content}')
        content = last.content.strip()
        if content.lower() in ('schema', '/schema'):
            return AIMessage(content='', tool_calls=[{'name': 'input_schema', 'args': {}, 'id': 'schema_call'}])
        try:
            record = json.loads(content)
        except (ValueError, TypeError):
            return AIMessage(content='Mock mode accepts a JSON feature record or /schema. Use /quit to exit.')
        if not isinstance(record, dict):
            return AIMessage(content='Please supply a JSON object containing the feature values.')
        return AIMessage(content='', tool_calls=[{'name': 'predict_income', 'args': {'record': record}, 'id': 'prediction_call'}])


def build_agent(provider='mock'):
    if provider == 'mock':
        model = MockChatModel()
    elif provider == 'openai':
        from langchain_openai import ChatOpenAI

        key = os.getenv('OPENAI_API_KEY', '')
        if not key or key == 'sk-fake-key-replace-me':
            raise ValueError('Set a real OPENAI_API_KEY to enable OpenAI, or use --provider mock.')
        model = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'), timeout=60, max_retries=2).bind_tools(TOOLS)
    else:
        raise ValueError(f'Unknown provider: {provider}')

    def call_model(state: MessagesState):
        return {'messages': [model.invoke([SystemMessage(content=SYSTEM_PROMPT), *state['messages']])]}

    graph = StateGraph(MessagesState)
    graph.add_node('assistant', call_model)
    graph.add_node('tools', ToolNode(TOOLS, handle_tool_errors=True))
    graph.add_edge(START, 'assistant')
    graph.add_conditional_edges('assistant', tools_condition)
    graph.add_edge('tools', 'assistant')
    return graph.compile()
