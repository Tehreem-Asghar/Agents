from agents import (  # type: ignore
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    input_guardrail,
    GuardrailFunctionOutput,
    input_guardrail,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    ModelSettings,
    function_tool,
    enable_verbose_stdout_logging
)
from agents.run import RunConfig  # type: ignore
from dotenv import load_dotenv
import os
from pydantic import BaseModel  # type: ignore
import asyncio
import  rich

load_dotenv()

# openai = os.getenv("OPENAI_API_KEY")
key = os.getenv("api_key")
if not key:
    raise ValueError("API key is not set in the environment variables.")

print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
enable_verbose_stdout_logging()
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")


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


class IsTeacherQuery(BaseModel):
    is_teacher_query: bool
    reason: str
    output: str


TeacherQueryGuardrail = Agent(
    name="TeacherQueryGuardrail",
    instructions="""
You are an input guardrail agent. Your job is to verify if the user's query is related to a teacher's responsibility.

✅ Allow only questions that are directly related to a teacher’s duties, such as:
- Subject-related queries (  coding, programming , projects , assignment ,  etc.)
- Course content
- Lectures
- Assignments
- Quizzes
- Class participation
- Understanding concepts

❌ Reject queries that fall under the administrative team's responsibility, including:
- Class timing or slot changes
- Early leave or schedule changes
- Exam schedules or timing issues
- Mark sheet corrections or grade appeals
- Enrollment or registration issues

Only approve the query if it clearly relates to a teacher's academic role.
""",
    output_type=IsTeacherQuery,
    model=model,
  
)


@input_guardrail
async def is_teacher_query_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: TResponseInputItem
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        starting_agent=TeacherQueryGuardrail,
        input=input,
        context=ctx.context,
        run_config=config,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_teacher_query,
    )

@function_tool
def is_additional_query(num1 , num2):
    """ this fuction add two numbers"""
    return f"Your output is {num1 + num2}"




TeacherAgent = Agent(
    name="Teacher",
    instructions="""
You are a programming teacher.

✅ Your job is to help users with queries strictly related to:
- Coding concepts and logic
- Programming languages (e.g., JavaScript, Python, TypeScript, Next.js , AI  etc.)
- Debugging code
- Understanding syntax or errors
- Explaining algorithms or data structures
- Helping with assignments, quizzes, or concept clarity in programming

if query is math addition related then use is_additional_query function to add two numbers
""",
    model=model,
    tools=[is_additional_query],
    input_guardrails=[is_teacher_query_guardrail],
      model_settings=ModelSettings(
        temperature=0.4, # control randomness and creativity
        top_p=0.3, # use only top 30% of vocabulary 
        # max_tokens=100, # limit the response length
        # frequency_penalty=0.0, # avoid repeating words
        presence_penalty=0.9, # introduce new ideas and concepts encourage new topics
        tool_choice = "auto",  # let the model choose the best tool
        # parallel_tool_calls=True,  # allow parallel tool calls
        truncation = "auto" , # automatically truncate the input if it exceeds the model's context length Agar prompt lamba ho jaye to purana text cut karna hai ya nahi.
        
    )
)


async def main():
    try:
        result = await Runner.run(
            TeacherAgent,
            "What is the difference between JavaScript and TypeScript?",
            run_config=config,
        )
        print("✅ Result:", result.final_output)
        print("-" * 50)
        rich.print(result.new_items)

    except InputGuardrailTripwireTriggered as e:
        print("Your Query is not related to a teacher's responsibility.")
        print("❌ Guardrail triggered!", e)


if __name__ == "__main__":
    asyncio.run(main())
