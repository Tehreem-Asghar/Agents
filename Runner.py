from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel ,handoff, ModelSettings , RunContextWrapper  , TContext , function_tool , TResponseInputItem  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import asyncio
from pydantic import BaseModel  # type: ignore
from dataclasses import dataclass
import rich 
from agents import Prompt  # Add this import for Prompt
from agents.agent import StopAtTools  # <-- yahi import hona chahiye
from agents.run import HandoffInputFilter



load_dotenv()



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



# Example handoff filter
def my_handoff_filter(input_data: dict) -> dict:
    # input_data hota hai ek dictionary jisme handoff context hota hai
    rich.print("----------------------------------------------------------------------------Original Input Data:", input_data)
    user_input = input_data.get("input", "")
    
    # Simple filter: sirf 'recipe' ke baad ka text nikaal lo
    if "recipe" in user_input.lower():
        user_input = user_input.lower().split("recipe")[-1].strip()
    
    # Return modified input
    return {"input": user_input}

config: RunConfig = RunConfig(
    model=model,
    model_provider=Externl_client,
    tracing_disabled=False,
      model_settings=ModelSettings(
        temperature=0.4, # control randomness and creativity
        top_p=0.3, # use only top 30% of vocabulary 
        # max_tokens=100, # limit the response length
        # frequency_penalty=0.0, # avoid repeating words
        presence_penalty=0.9, # introduce new ideas and concepts encourage new topics
        tool_choice = "auto",  # let the model choose the best tool
        # parallel_tool_calls=True,  # allow parallel tool calls
        truncation = "auto" , # automatically truncate the input if it exceeds the model's context length Agar prompt lamba ho jaye to purana text cut karna hai ya nahi.
        
    ),

   handoff_input_filter = my_handoff_filter
)

# @dataclass
# class RecipeInput:
#     input: str

class RecipeInput(BaseModel):
    input: str





# async def dynamic_instructions(ctx, agent):
#     # Suppose you fetch instructions from an API
#     print(ctx)
#     print("-----------------------------------------------------------------------------------------")
#     rich.print(agent)
#     print("Dynamic Instructions Context:")
#     print("context",ctx.context)
#     print("input",ctx.context.input)
#     return f"Give a healthy recipe based on ingredient: {ctx.context.input}"

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
    
    instructions="You are a task delegation bot that can delegate tasks to other agents based on their expertise.",
    model=model,
    handoffs = [
                 handoff(agent2 , tool_description_override="Handles speech-related queries") , handoff(recipe_bot , tool_description_override="Handles recipe-related queries") , handoff(news_bot , tool_description_override="Handles news-related queries") ] ,
    tools=[wheather , Today , xy],
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
    result = await Runner.run( agent3, "Give me a recipe for spicy chicken curry ??" , run_config=config )

    print(result.final_output)
  
    print("-----------------------------------------------------------------------------------------")
  
if __name__ == "__main__":
    asyncio.run(main())
