import asyncio
import logging

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from audiointel import Broker

logging.basicConfig(format="[%(asctime)s][%(module)s]: %(message)s")
logging.getLogger("audiointel").setLevel(logging.DEBUG)
logging.getLogger("phonemizer").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Graph:
    def __init__(self):
        tools = [WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())]
        tool_node = ToolNode(tools)
        self.model = ChatOllama(model="mistral", temperature=0).bind_tools(tools)

        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", tool_node)
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", self.should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")
        self.graph = workflow.compile()

    def should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def call_model(self, state):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    async def request(self, msg):
        logger.info("Processing request: %s", msg)
        result = await self.graph.ainvoke({"messages": [("human", msg)]})
        logger.info("Final response: %s", result["messages"][-1].text())
        return result


async def main():
    broker = Broker("robot")
    await broker.say("You can wake me up with the word 'robot'.")
    graph = Graph()

    async for request in broker.wake_listen_loop():
        result = await graph.request(request)

        # if no message in the history has any tool_calls then say an error
        # before we end
        if not any(getattr(msg, "tool_calls", []) for msg in result["messages"]):
            await broker.say_error("No matching tool found.")
        else:
            await broker.say(result["messages"][-1].text())


asyncio.run(main())
