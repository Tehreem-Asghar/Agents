from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , enable_verbose_stdout_logging , function_tool  # type: ignore
from agents.run import RunConfig  # type: ignore 
from dotenv import load_dotenv # type: ignore
from agents import TResponseInputItem  # Add this import if TResponseInputItem is defined in agents.types
import os
import rich
enable_verbose_stdout_logging()

load_dotenv()
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
)

def instructions_func(ctx, agent):
    rich.print(ctx)
    print("-----------------------------------------------------------------------------------------")
    rich.print(agent)

    return "You are a helpful assistant that helps users with their questions."

@function_tool
async def whether(city: str)-> str:
    return f"In {city} the whether is sunny"
    


recipe_bot = Agent(
    name="RecipeBot",
    instructions="You are a recipe bot that suggests healthy recipes.",
    model=model
)




agent = Agent(
    name = "Assistent",
    # instructions=instructions_func,
    instructions="You are a helpful assistant that helps users with their questions. if user ask about any recipy you can delegate task to recipe bot. if user ask about whether you can use whether tool",
    model=model,
    tools= [whether],
    handoffs = [recipe_bot]

)

# es trha list da saktta hai ham input ma 
input_list: list[TResponseInputItem] = [   
     {"role":"user", "content": "i am a teacher write a joke about teacher ?"},
     {"role": "system","content": "You are a teacher your job is to help users with queries strictly related to coding concepts and programming languages"},
     {"role": "user", "content": "tell me a joke about python?"},
     {"role":"user", "content": "i am a deveoper write a joke about bugs  in roman urdu?"},
     {"role":"user", "content": "mana  ap sa abhi tak kitna kon kon sa question kiya mujha btao?"},
      # jo end wala latest obj hoga wo as input use ho ga phala wala ovveride ho jayga
]

async def main():
    runner = await Runner.run(agent,"tell me tea recipe" , run_config=config)
    print("**********************************************************************************************************")

    print(runner.final_output)
    # rich.print(runner)


    print("**********************************************************************************************************")
   


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
