from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, handoff, enable_verbose_stdout_logging, function_tool, ModelSettings, trace, RunContextWrapper  # type: ignore
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
from pydantic import BaseModel  # type: ignore
import rich
from agents.extensions import handoff_filters

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
enable_verbose_stdout_logging()
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
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
    workflow_name="handoff demoo ",
)


class reason(BaseModel):
    reason: str


def OneHandoff(ctx: RunContextWrapper, input: reason):
    print("Handoff triger---->")
    print("Input : ", input)
    print("Context : ", ctx.context)


def Is_enabled(ctx: RunContextWrapper, agent: Agent):
    if ctx.context.is_student == True:
        return True

    return False


recipe_agent = Agent(
    name="RecipeAgent",
    instructions="You are a helpful cooking assistant. You can provide recipes and cooking tips to users. If a user asks for a recipe.",
    model=model,
    handoff_description="Use this agent to provide recipes and cooking tips to users.",
)


teacher_agent = Agent(
    name="TeacherAgent",
    instructions="You are a knowledgeable assistant who can answer technical questions. If a user asks a technical question, provide a clear and concise answer.",
    model=model,
    handoff_description="Use this agent to answer technical questions from users.",
)


racipe = recipe_agent.as_tool(
    tool_name="recipe_tool", tool_description=" A tool to tell racipe"
)
teacher = handoff(
    teacher_agent,
    tool_name_override="teacher_agent",
    # tool_description_override="A handofftool to answer technical questions ",
    on_handoff=OneHandoff,
    input_type=reason,
    input_filter=handoff_filters.remove_all_tools,
    is_enabled=Is_enabled,
)

agent = Agent(
    name="traige agent",
    instructions="you  are a triage agent that have handoff  agents and tools  to answer user questions. use them when needed. if the user asks for a recipe, use the recipe tool. if the user asks for a technical question, use the teacher agent. ",
    handoffs=[teacher],
    tools=[racipe],
)


class User(BaseModel):
    name: str
    age: int
    city: str
    is_student: bool


with trace(workflow_name="handoff_group_demo"):

    runner = Runner.run_sync(
        agent,
        "tel me racipe of tea " "tell me what is capital of pakistan  ?  ",
        run_config=config,
        context=User(name="Tehreem", age=20, city="New Karachi", is_student=True),
    )

    print(
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n",
        teacher.input_filter,
        "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
    )
    print(
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n",
        runner.final_output,
        "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
    )
    print(
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n",
        agent.handoffs,
        "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
    )

    # rich.print(runner.to_input_list())
    # print("Last Agent: ->>>>>>>>>", runner.last_agent)
