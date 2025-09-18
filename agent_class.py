from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel ,handoff,RunContextWrapper  , TContext , function_tool , TResponseInputItem  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import asyncio
from pydantic import BaseModel  # type: ignore
from dataclasses import dataclass
import rich 
from agents import Prompt  # type: ignore Add this import for Prompt
from agents.agent import StopAtTools  # type: ignore <-- yahi import hona chahiye
from agents.run import TraceCtxManager # type: ignore


load_dotenv()

openai = os.getenv("OPENAI_API_KEY")
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


def filter_func(input_text: str) -> str:
    return f"""🧐 {input_text.lower() }"""


config: RunConfig = RunConfig(
    model=model,
    model_provider=Externl_client, 
    tracing_disabled=False,
    handoff_input_filter=filter_func,
    workflow_name="Quiz_Preparation_Workflow",
    trace_id="trace_abc123",
    group_id="group-1",
    trace_metadata={"author": "Tehreem"}
)

# @dataclass
# class RecipeInput:
#     input: str

class RecipeInput(BaseModel):
    input: str


async def dynamic_instructions(ctx, agent):
    # Suppose you fetch instructions from an API
    print(ctx)
    print("-----------------------------------------------------------------------------------------")
    rich.print(agent)
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
        
xy = agent1.as_tool(tool_name = "joke_tool", tool_description="A tool to tell jokes about Python")        

agent3 = Agent(
    name="delegatetaskBot",
    instructions= dynamic_instructions,
    # instructions="You are a task delegation bot that can delegate tasks to other agents based on their expertise.",
    model=model,
    handoffs = [
                #  handoff(agent1 , tool_description_override="Handles joke-related queries") ,
                 handoff(agent2 , tool_description_override="Handles speech-related queries") , handoff(recipe_bot , tool_description_override="Handles recipe-related queries") , handoff(news_bot , tool_description_override="Handles news-related queries") ] ,
    tools=[wheather , Today , xy],
    # tool_use_behavior="run_llm_again"  # User input → LLM decides tool → Tool output → LLM processes tool output → Final answer
    # tool_use_behavior="stop_on_first_tool" #  User input → LLM decides tool → Tool output → Final answer (LLM ko wapas nahi bhejte)
    tool_use_behavior=StopAtTools(stop_at_tool_name="Today"), # User Query → ToolCallItem → ToolCallOutputItem → MessageOutputItem → User
    reset_tool_choice = True # Reset tool choice after each run

)
# Suppose ek conversation input hai
input_items: list[TResponseInputItem] = [
    {"role": "system","content": "You are a teacher your job is to help users with queries strictly related to coding concepts and programming languages"},
    {"role": "user", "content": "tell me a joke about python?"},
]

copy = agent3.clone(name="teacher" , instructions="You are a teacher your job is to help users with queries strictly related to coding concepts and programming languages")

# Main function
async def main():
     with TraceCtxManager(
        workflow_name=config.workflow_name,
        trace_id=config.trace_id,
        group_id=config.group_id,
        metadata=config.trace_metadata,
        disabled=config.tracing_disabled,
    ):

    #    user_input = input("Enter ingredient (e.g., 'chocolate' or 'salad'): ")

    #    result = await Runner.run(agent3, user_input , run_config=config , context=RecipeInput(input=user_input) )
        result = await Runner.run(copy, "kiya apko yad hai mara phala message kiya tha ??" , run_config=config )

    # result =  Runner.run_streamed(agent3, "wrie a speach about mobile use cases transfer this query to speech bot" , run_config=config )

# Example input as a list of items
# from src.agents.items import TResponseInputItem
#  input ma es trha ki list send ki ja sakti hai 
# input_list = [
#     TResponseInputItem(role="user", content="Hello!"),
#     TResponseInputItem(role="system", content="System message here"),
#     TResponseInputItem(role="tool", content="Tool output here"),
# ]

    # print("\n--- RecipeBot Response ---")
     print(result.final_output)
    # async for event in result.stream_events():
        # print(event)

        # if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
        #         token = event.data.delta
        #         print(token, end='', flush=True)    
     print("-----------------------------------------------------------------------------------------")
    #  rich.print(result)
        
# Run async main
if __name__ == "__main__":
    asyncio.run(main())
