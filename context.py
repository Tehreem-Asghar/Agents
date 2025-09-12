from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , enable_verbose_stdout_logging    # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
from pydantic import BaseModel
# enable_verbose_stdout_logging()

load_dotenv()

Api_key = os.getenv("api_key")
if not Api_key:
    raise ValueError("API key is not set in the environment variables.")

# External client
External_client: AsyncOpenAI = AsyncOpenAI(
    api_key=Api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Model
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=External_client,
)

# Run config
config = RunConfig(
    model=model,
    model_provider=External_client,
    tracing_disabled=False,
)


# Admin data model
class IsAdmin(BaseModel):
    username: str
    password: str


# Tool to check admin
@function_tool
async def check_admin(username: str, password: str) -> bool:
    """Check if the user is an admin."""
    admin_user = IsAdmin(username="admin", password="admin123")
    return username == admin_user.username and password == admin_user.password


# Greeting agent
admin_agent = Agent(
    name="AdminGreetingBot",
    instructions="You are a greeting bot that greets the admin with his/her name. Take username from context.",
    model=model
)

# Main agent
agent = Agent(
    name="greetingBot",
    instructions=(
        "greet the user based on the context provided. "
        # "You are an admin check bot. Verify if the user is an admin using the check_admin tool. "
        # "Take username and password from context. "
        # "If user is admin, handoff task to admin_agent to greet them. "
        # "Otherwise reply with 'You are not authorized to access this service.'"
    ),
    model=model,
    # tools=[check_admin],
    # handoffs=[admin_agent]
)

# Main runner
async def main():
    result = await Runner.run(
        agent,
        input="greet the user with his/her name",
        run_config=config,
        context=IsAdmin(username="Tehreem", password="tehreem123")
    )
    
    print(result.final_output)
    # print(result.new_items)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())