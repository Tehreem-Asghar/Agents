from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, SQLiteSession    # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
import asyncio

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
Gemini_API_KEY = os.getenv("api_key")
if not API_KEY and not Gemini_API_KEY:
    raise ValueError("API key is not set in the environment variables.")

external_client = AsyncOpenAI(
    api_key=Gemini_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=False,
    workflow_name="session_workflow",
)


session = SQLiteSession("conversations_123"  , "conversations_practice.db")
# session = SQLiteSession("conversations_123"  )



Agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant that helps people with their queries.",
    model=model,
)

new_items = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]

async def main():

    # get all items
    # all_items = await session.get_items(1)
    # print(all_items) # output : [........all items return]

    # Add new items to a session
    # newitems = await session.add_items(new_items)
    # print(newitems) # output : None

    # # Remove and return the most recent item
    # removed_last_items = await session.pop_item()
    # print(removed_last_items) # output  : {'role': 'assistant', 'content': 'Hi there!'}

    # # Clear all items from a session
    # clear_all = await session.clear_session()
    # print(clear_all) # output : None

    
    while True:
        user_input = input("Enter your message (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        response = await Runner.run(
            Agent,
            user_input,
            run_config=config,
            session=session,
        )

        print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main())
