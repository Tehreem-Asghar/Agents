from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, ToolCallOutputItem , enable_verbose_stdout_logging, function_tool, ModelSettings, RunContextWrapper, FunctionTool , RunResult  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
import rich
from pydantic import BaseModel  # type: ignore

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
    workflow_name="tools_Workflow ",
)

agent = Agent(
    name="Computer Teacher",
    instructions="You are a computer teacher. You can answer questions related to computer science and programming. ",
    model=model,
)

def error_handler(ctx : RunContextWrapper , error : Exception):
    """Ye ek custom function hai jo user-friendly error message deta hai."""
    print(f"A tool call failed with the following error: {error}")
    return "An internal server error occurred. Please try again later."

# Customizing tool_agents
@function_tool(
        # failure_error_function = None
)
async def math_tool(input: str):
    """This is math tool"""
    # raise ValueError("custom error give by tehreem")
    agent = Agent(
        name = "Math_Teacher",
        instructions = "You are a math teacher. You can answer questions related to math. ",
        model = model
    )

    result  = await Runner.run(
        agent,
        input,
        run_config=config,
        max_turns = 6
    )

    return str(result.final_output)


async def extract_json_payload(run_result: RunResult) -> str:
  
    # Scan the agent’s outputs in reverse order until we find a JSON-like message from a tool call.
    for item in reversed(run_result.new_items):
        if isinstance(item, ToolCallOutputItem) and item.output.strip().startswith("{"):
            return item.output.strip()
    # Fallback to an empty JSON object if nothing was found
    return "{}"




main_agent = Agent(
    name="main agent",
    instructions=" you are a main agent. if user query is related about programing and computer so use computer teacher tool and if user query is related about math so use math tooland you can also hanfoff to other agents if needed. ",
    model=model,
    tools=[
    agent.as_tool(
        tool_name="computer_teacher",
        tool_description="useful for answering questions related to computer science and programming.",
        # custom_output_extractor=  extract_json_payload # esma error arha hai abhi esko smjhna hai 
    ) ,
    math_tool
    ],
 
)

async def main():
    result = await Runner.run(
        starting_agent=main_agent,
        input="2 + 2 = ? ",
        run_config=config,
    )

    print("Final Result: " , result.final_output)

    # for i in result.new_items:
    #     print("\nNew Items ---> \n",i , "\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())