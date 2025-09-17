from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, ModelSettings, RunContextWrapper, FunctionTool, RunHooks, TResponseInputItem  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
import rich
from pydantic import BaseModel  # type: ignore
from typing import List, Any, Optional

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
    workflow_name="Runner_hook_workflow",
)


class Run_Hooks_Flow(RunHooks):

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent):
        print(f"{agent.name} Agent Start ----> on_agent_start\n")

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any):
        print(f"{agent.name} Agent End ----> on_agent_end\n")
        print(f"Agent {agent.name} has completed the task and output  is {output} ")

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: Optional[
            str
        ],  # wo system-level prompt jo model ko diya ja raha hai (jaise instructions).
        input_items: list[
            TResponseInputItem
        ],  # model ke liye inputs (jaise user ke messages ya tool ke outputs).
    ) -> None:
        """Called just before invoking the LLM for this agent."""
        print(f"{agent.name} LLM Start ----> on_llm_start\n")
        print(f"System Prompt: {system_prompt}")
        print(f"Input Items: {input_items}")

    async def on_llm_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        response: Any,  # ModelResponse type hota hai
    ) -> None:
        print(f"{agent.name} LLM End ----> on_llm_end\n")
        print(f"Response: {response}")

    async def on_tool_start(
        self, context: RunContextWrapper, agent: Agent, tool: FunctionTool
    ):
        print(f"{tool.name} Tool Start ----> on_tool_start\n")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: FunctionTool, result: str
    ):
        print(f"{tool.name} Tool End ----> on_tool_end ---> Result is {result}\n")

    async def on_handoff(
        self,
        context: RunContextWrapper,
        # agent: Agent,
        from_agent: Agent,
        to_agent: Agent,
    ):
        print(
            f"{from_agent.name} Agent is delegate task to {to_agent.name} Agent    ---> on_handoff fire\n"
        )


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
)

agent = Agent(
    name="traige agent",
    instructions="you  are orchestrator agent that can delegate tasks to other agents based on their expertise.",
    model=model,
    handoffs=[flight_agent],
)


async def main():
    result = await Runner.run(
        agent,
        # "Hello, how are you?",
        "Book a flight from karachi to dubai on 2023-06-15 in business class for 2 passengers. and passenger name is Tehreem and ayesha",
        run_config=config,
        hooks=Run_Hooks_Flow(),
    )

    print(
        "\n--------------------------------------------------------\n",
        result.final_output,
        "\n===================================================\n",
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
