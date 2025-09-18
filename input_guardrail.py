from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, ModelSettings, RunContextWrapper, FunctionTool, AgentHooks, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered  # type: ignore
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


class input_guard(BaseModel):
    is_flight_related: bool
    reason: str


user_input_guard = Agent(
    name="Input Guardrail",
    instructions=(
        "You are an input guardrail. Your job is to carefully check the user's input before "
        "it is passed to any other agent. You must block or flag input if it is irrelevant, "
        "malicious, unsafe, or not related to flights. Allow only inputs that are clearly about "
        "booking flights, changing seats, or asking flight-related questions."
    ),
    model=model,
    output_type=input_guard,
)


@input_guardrail
async def inputguardrail(
    ctx: RunContextWrapper, agent: Agent, input: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        starting_agent=user_input_guard,
        input=input,
        context=ctx.context,
        run_config=config,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_flight_related,
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
    input_guardrails=[inputguardrail],
)


async def main():
    try:
        result = await Runner.run(
            agent,
            "what is answer 2 + 2 = ?",
            # "Book a flight from karachi to dubai on 2023-06-15 in business class for 2 passengers. and passenger name is Tehreem and ayesha",
            run_config=config,
        )

        print(
            "\n--------------------------------------------------------\n",
            result.final_output,
            "\n===================================================\n",
        )

    except InputGuardrailTripwireTriggered as e:
        print("Your Query is not related to flights.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
