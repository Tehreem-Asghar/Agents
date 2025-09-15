from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, ModelSettings, RunContextWrapper, FunctionTool  # type: ignore
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


class address(BaseModel):
    city: str


@function_tool
def weather_news(city: str) -> str:
    """Returns the weather news for a given city."""
    # raise ValueError("fail to fetch whether news")
    return f"The weather in {city} is sunny with a high of 25°C and a low of 15°C."


class AddParams(BaseModel):
    num1: int
    num2: int


async def on_invoke(ctx: RunContextWrapper, arg: AddParams) -> str:
    arg = AddParams.model_validate_json(arg)
    print("Pluse tool fire --->>")
    return f"The sum of {arg.num1} and {arg.num2} is {arg.num1 + arg.num2}"


plus_tool = FunctionTool(
    name="add_numbers",
    description="Adds two numbers together.",
    params_json_schema=AddParams.model_json_schema(),
    on_invoke_tool=on_invoke,
)


def error_handler(ctx: RunContextWrapper, Exception) -> str:
    return "Sorry, I couldn't fetch the weather information right now."


def enable(ctx: RunContextWrapper, Agent: Agent) -> bool:
    # print("Context in enable function : ", ctx.context.city)
    # print("AgentBase in enable function : ", Agent)
    if ctx.context.city == "Larkana":
        return True
    return False


@function_tool(
    name_override="check_weather",
    strict_mode=True,
    description_override="get the whether of a city",
    failure_error_function=error_handler,
    is_enabled=enable,
    docstring_style="google",
    use_docstring_info=True,
    # is_enabled=True,
)
async def whether(ctx: RunContextWrapper, city: str) -> str:
    """Returns the weather for a given city."""
    # raise ValueError("fail to fetch whether")
    print("Context in tool : ", ctx.context.city)
    return f"In {city} the whether is sunny"


recipe_bot = Agent(
    name="RecipeBot",
    instructions="You are a recipe bot that suggests healthy recipes.",
    model=model,
)


agent = Agent(
    name="AssistantBot",
    instructions="You are a helpful assistant that helps users with their questions. if user ask about any recipy you can delegate task to recipe bot. if user ask about whether you can use whether tool",
    model=model,
    tools=[whether, weather_news, plus_tool],
    handoffs=[recipe_bot],
    model_settings=ModelSettings(
        # tool_choice="none"
    ),
)


async def main():
    runner = await Runner.run(
        agent,
        "what is wheather in New_Karachi",
        run_config=config,
        context=address(city="Karachi"),
    )
    print(
        "**********************************************************************************************************"
    )
    print(runner.final_output)
    # rich.print(runner)
    print(
        "**********************************************************************************************************"
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())