
## tool_use_behavior 

- tool_use_behavior : ka kaam simple shabdon me yeh decide karna hai ki jab Agent apne tools ka use kare, to uske baad ka flow kaise chale.
- Ye basically tool call ke baad ka control flow manage karta hai.

# Kyun use hota hai?

- Har baar jab LLM  kisi Tool ko call karta hai, ek decision lena padta hai:

- 1) Tool ka result LLM ko wapas dena hai taaki wo final answer banaye?

- 2) Ya tool ka output hi final answer hai, bina LLM ke re-process kiye?

- 3) Ya tool ka result dekh kar decide karna hai ki stop karein ya aur tools call karein?

tool_use_behavior isi decision ko automate karta hai.

```
tool_use_behavior: (
    Literal["run_llm_again", "stop_on_first_tool"] | StopAtTools | ToolsToFinalOutputFunction
    ) = "run_llm_again"
    """
    This lets you configure how tool use is handled.
    - "run_llm_again": The default behavior. Tools are run, and then the LLM receives the results
        and gets to respond.
    - "stop_on_first_tool": The output of the first tool call is used as the final output. This
        means that the LLM does not process the result of the tool call.
    - A StopAtTools object: The agent will stop running if any of the tools listed in
        `stop_at_tool_names` is called.
        The final output will be the output of the first matching tool call.
        The LLM does not process the result of the tool call.
    - A function: If you pass a function, it will be called with the run context and the list of
      tool results. It must return a `ToolsToFinalOutputResult`, which determines whether the tool
      calls result in a final output.

      NOTE: This configuration is specific to FunctionTools. Hosted tools, such as file search,
      web search, etc. are always processed by the LLM.
    """
```    

## Options Explained

# 1️⃣ "run_llm_again" (Default)

- Flow:

```
User input → LLM decides tool → Tool output → LLM processes tool output → Final answer
```

LLM ko tool ka result milta hai, wo usko use karke final response generate karta hai.

Kab use kare: Jab tum chahte ho ki model tool ka data interpret kare, summarize kare, ya apne style me answer de.

Example:

```
agent = Agent(
    name="WeatherBot",
    instructions="Get weather and explain nicely.",
    tools=[weather_tool],
    tool_use_behavior="run_llm_again"
)
```

## 2️⃣ "stop_on_first_tool"

- Flow:
```
User input → LLM decides tool → Tool output → Final answer (LLM ko wapas nahi bhejte)
```

Tool ka result direct user ko return hota hai.

Kab use kare: Jab tool ka output already final form me hai (jaise DB query ka result, calculation, API ka JSON).

Example:
```
agent = Agent(
    name="CalcBot",
    instructions="Do math.",
    tools=[calculator_tool],
    tool_use_behavior="stop_on_first_tool"
)
```

## 3️⃣ StopAtTools Object

Tum specify karte ho ki kis-kis tool pe stop karna hai.

Agar specified tool call hota hai, uska result final answer ban jata hai.

Baaki tools ke liye normal "run_llm_again" behavior hota hai.

- Example:
```
from agents import StopAtTools

agent = Agent(
    name="MixedBot",
    tools=[weather_tool, translate_tool],
    tool_use_behavior=StopAtTools(stop_at_tool_names=["weather_tool"])
)
```

- Agar weather_tool call hua → direct output.

- Agar translate_tool call hua → LLM se process karke output.

# 4️⃣ Custom Function

Tum apni logic likh sakte ho jo decide karegi ki tool ka output final answer banega ya nahi.

Function ka signature:
```
def my_tool_decision(run_context, tool_results):
    return ToolsToFinalOutputResult(final_output="...", stop=True)
```

Example:
```
def decide_output(ctx, tool_results):
    if "error" in tool_results[0].output:
        return ToolsToFinalOutputResult(final_output="Something went wrong", stop=True)
    return ToolsToFinalOutputResult(stop=False)

agent = Agent(
    name="SmartBot",
    tools=[custom_tool],
    tool_use_behavior=decide_output
)
```

## Summary Table
Behavior	           | LLM Reprocess Tool Result?   |    Use Case
run_llm_again          |      ✅ Yes	                 |   Need interpretation / formatting
stop_on_first_tool	   |      ❌ No	                 |   Tool output is final answer
StopAtTools            |      ✅/❌Mixed	           |    Some tools stop, some don’t
Custom Function	       |      ✅/❌Your Choice	   |   Complex logic or conditions