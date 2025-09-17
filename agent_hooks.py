from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, ModelSettings, RunContextWrapper, FunctionTool, AgentHooks  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
import rich
from pydantic import BaseModel  # type: ignore
from typing import List, Any

# enable_verbose_stdout_logging()

load_dotenv()
openai = os.getenv("OPENAI_API_KEY")
Api_key = os.getenv("api_key")
if not Api_key:
    raise ValueError("API key is not set in the environment variables.")

External_client: AsyncOpenAI = AsyncOpenAI(
    api_key=Api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=External_client,
)

config = RunConfig(
    model=model,
    model_provider=External_client,
    tracing_disabled=False,
    workflow_name="agent_hook_workflow",
)


class AgentHooksflow(AgentHooks):
    async def on_start(
        self, context: RunContextWrapper, agent: Agent
    ):  # 2no argument required hai context and agent
        print("\nAgent on_start ---->\n")
        print(f"🕘 Agent {agent.name} is now in charge of handling the task")
        # rich.print(agent)
        print("\nAgent on_start ---->\n")

    async def on_end(
        self, context: RunContextWrapper, agent: Agent, output: Any
    ):  # 2no argument required hai context and agent
        """Called when the agent produces a final output."""
        print("\nAgent on_end ---->\n")
        print(f"Agent {agent.name} has completed the task and output  is {output} ")
        print("\nAgent on_end ---->\n")

    async def on_tool_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: FunctionTool,  # yha tool ka andar FunctionTool class return karta hai jisma name , description, params_json_schema, on_invoke_tool, strict_json_schema, is_enabled ya properties hoti hai
    ) -> None:
        """Called before a tool is invoked."""
        print("\nAgent on_tool_start ---->\n")
        print("Tool Name: ", tool.name)
        # rich.print(tool)

    async def on_tool_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: FunctionTool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print("\nAgent on_tool_end ---->  fire\n")
        print(f"agent {agent.name} tool{tool.name} result is --> {result}")

    async def on_handoff(
        self,
        context: RunContextWrapper,
        agent: Agent,
        source: Agent,
    ) -> None:

        print("handoff -----> fire")
        print(f" {agent.name} Agent is being handed off to {source.name}")


class FlightBook(BaseModel):
    name: List[str]
    from_location: str
    to_location: str
    date: str  # format "YYYY-MM-DD"
    seat_class: str  # "economy", "business", "first"
    num_passengers: int = 1  # default 1 passenger


@function_tool()
def book_flight(flight: FlightBook):
    """Book a flight"""
    passenger_names = ", ".join(flight.name)
    return f"Booked flight for {passenger_names} from {flight.from_location} to {flight.to_location} on {flight.date} in {flight.seat_class} class for {flight.num_passengers} passenger(s)."


class SeatChange(BaseModel):
    name: str
    current_class: str  # "economy", "business", "first"
    new_class: str  # "economy", "business", "first"


@function_tool
def change_seat_class(change: SeatChange):
    """Change seat class"""
    if change.current_class == change.new_class:
        return f"{change.name}, you are already in {change.current_class} class."
    return f"{change.name}'s seat has been changed from {change.current_class} to {change.new_class}."


flight_agent = Agent(
    name="flight agent",
    instructions="you are a flight agent that can provide information about flights. and you have also flight booking tool that can book flight if needed so you can use that tool to book flight.",
    model=model,
    tools=[book_flight, change_seat_class],
    hooks=AgentHooksflow(),
)

agent = Agent(
    name="traige agent",
    instructions="you  are orchestrator agent that can delegate tasks to other agents based on their expertise.",
    model=model,
    handoffs=[flight_agent],
    # hooks=AgentHooksflow(),
)


async def main():
    result = await Runner.run(
        agent,
        "Book a flight from karachi to dubai on 2023-06-15 in business class for 2 passengers. and passenger name is Tehreem and ayesha",
        run_config=config,
    )

    print(
        "\n--------------------------------------------------------\n",
        result.final_output,
        "\n===================================================\n",
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
