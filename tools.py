from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , enable_verbose_stdout_logging , function_tool , ModelSettings  # type: ignore
from agents.run import RunConfig  # type: ignore 
from dotenv import load_dotenv # type: ignore
import os
import rich

# enable_verbose_stdout_logging()

load_dotenv()
openai = os.getenv("OPENAI_API_KEY")
Api_key = os.getenv("api_key")
if not Api_key:
    raise ValueError("API key is not set in the environment variables.")


External_client:AsyncOpenAI = AsyncOpenAI(
    api_key=Api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model :OpenAIChatCompletionsModel= OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=External_client,
)

config = RunConfig(
    model=model,
    model_provider=External_client,
    tracing_disabled=False,
    workflow_name="tools_Workflow "
)


@function_tool
def weather_news(city: str)-> str:
    """ Returns the weather news for a given city. """
    return f"The weather in {city} is sunny with a high of 25°C and a low of 15°C."


@function_tool
async def whether(city: str)-> str:
    return f"In {city} the whether is sunny"
    
recipe_bot = Agent(
    name="RecipeBot",
    instructions="You are a recipe bot that suggests healthy recipes.",
    model=model
)


agent = Agent(
    name = "AssistantBot",
    instructions="You are a helpful assistant that helps users with their questions. if user ask about any recipy you can delegate task to recipe bot. if user ask about whether you can use whether tool",
    model=model,
    tools= [whether , weather_news],
    handoffs = [recipe_bot],
    model_settings = ModelSettings(
        # parallel_tool_calls = True,
        # tool_choice = "required"  # default value is "None"
    ),
    # reset_tool_choice = True #default true hota hai agar ham esa false set kar da ga to ya infinite loop ma chala ja ga (agar tool use karna cha ha to) 
    # tool_use_behavior = "stop_on_first_tool"
)




async def main():
    # runner = await Runner.run(agent,"how many  tools you have" , run_config=config)
    runner = await Runner.run(agent,"what is wheather in karachi and what is news about weather " , run_config=config )
    print("**********************************************************************************************************")
    print(runner.final_output)
    # rich.print(runner)
    print("**********************************************************************************************************")
   


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
