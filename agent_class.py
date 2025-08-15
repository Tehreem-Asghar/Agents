from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel ,handoff, RunContextWrapper  , TContext , function_tool  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import asyncio
from pydantic import BaseModel  # type: ignore
from dataclasses import dataclass
import rich
from agents import Prompt  # Add this import for Prompt
from agents.agent import StopAtTools  # <-- yahi import hona chahiye


load_dotenv()

# openai = os.getenv("OPENAI_API_KEY")
key = os.getenv("api_key")
if not key:
    raise ValueError("API key is not set in the environment variables.")


Externl_client: AsyncOpenAI = AsyncOpenAI(
    api_key=key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=Externl_client,


)

config: RunConfig = RunConfig(
    model=model,
    model_provider=Externl_client, 
    tracing_disabled=True
)

# @dataclass
# class RecipeInput:
#     input: str

class RecipeInput(BaseModel):
    input: str


async def dynamic_instructions(ctx, agent):
    # Suppose you fetch instructions from an API

    print("-----------------------------------------------------------------------------------------")
    print(agent)
    print("Dynamic Instructions Context:")
    print("context",ctx.context)
    print("input",ctx.context.input)
    return f"Give a healthy recipe based on ingredient: {ctx.context.input}"

agent1 = Agent(
    name="JokeBot",
    instructions="You are a joke bot",
    
    # instructions=dynamic_instructions,


    model=model
)
agent2 = Agent(
    name="speechBot",
    instructions="You are a speech bot that can generate speeches on various topics.",
    model=model
)


# Specialized agents
recipe_bot = Agent(
    name="RecipeBot",
    instructions="You are a recipe bot that suggests healthy recipes.",
    model=model
)

news_bot = Agent(
    name="NewsBot",
    instructions="You are a news bot that gives the latest headlines.",
    model=model
)

@function_tool
def wheather():
    """Get the current weather."""
    return "Sunny"
    
@function_tool
def Today():
    """ Get the current day"""
    return "Today is Monday"
        

agent3 = Agent(
    name="delegatetaskBot",
    instructions="You are a task delegation bot that can delegate tasks to other agents based on their expertise.",
    model=model,
    handoffs = [handoff(agent1 , tool_description_override="Handles joke-related queries") , handoff(agent2 , tool_description_override="Handles speech-related queries") , handoff(recipe_bot , tool_description_override="Handles recipe-related queries") , handoff(news_bot , tool_description_override="Handles news-related queries") ] ,
    tools=[wheather , Today],
    # tool_use_behavior="run_llm_again"  # User input → LLM decides tool → Tool output → LLM processes tool output → Final answer
    # tool_use_behavior="stop_on_first_tool" #  User input → LLM decides tool → Tool output → Final answer (LLM ko wapas nahi bhejte)
    tool_use_behavior=StopAtTools(stop_at_tool_name="Today"), # User Query → ToolCallItem → ToolCallOutputItem → MessageOutputItem → User
    reset_tool_choice = True # Reset tool choice after each run

)

copy = agent3.clone(name="teacher" , instructions="You are a teacher your job is to help users with queries strictly related to coding concepts and programming languages")

# Main function
async def main():

    # user_input = input("Enter ingredient (e.g., 'chocolate' or 'salad'): ")

    # result = await Runner.run(agent3, user_input , run_config=config , context=RecipeInput(input=user_input))
    result = await Runner.run(copy, "tell me a joke about python " , run_config=config )


    # print("\n--- RecipeBot Response ---")
    print(result.final_output)
    print("-----------------------------------------------------------------------------------------")
    rich.print(result)

# Run async main
if __name__ == "__main__":
    asyncio.run(main())
