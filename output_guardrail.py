from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, ModelSettings, RunContextWrapper, FunctionTool, AgentHooks, output_guardrail, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered  # type: ignore
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
    workflow_name="input_guardrail_workflow",
)


class output_guard(BaseModel):
    is_flight_related: bool
    reason: str


agent_output_guard = Agent(
    name="Output Guardrail",
    instructions=(
        "You are an output guardrail agent. "
        "Your task is to analyze the agent's response and determine if it is related "
        "to flights, flight booking, or flight seat changes. "
        "If the response is related to flights, set `is_flight_related=True` with a clear reason. "
        "If the response is not related to flights, set `is_flight_related=False` and explain why."
    ),
    model=model,
    output_type=output_guard,
)


class MessageOutput(BaseModel):  # (1)!
    response: str


@output_guardrail
async def outputguardrail(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        agent_output_guard, output.response, context=ctx.context, run_config=config
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_flight_related,
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
    output_guardrails=[outputguardrail],
    output_type=MessageOutput,
)

agent = Agent(
    name="traige agent",
    instructions="you  are orchestrator agent that can delegate tasks to other agents based on their expertise.",
    model=model,
    handoffs=[flight_agent],
    # output_guardrails=[outputguardrail],
)


async def main():
    try:
        result = await Runner.run(
            agent,
            "what is answer 2 + 2 = ?",
            # "Book a flight from karachi to dubai on 2023-06-15 in business class for 2 passengers. and passenger name is Tehreem and ayesha",
            run_config=config,
        )

        print(result.final_output)

    except OutputGuardrailTripwireTriggered as e:
        print("agent output is not related to flights.", e)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
