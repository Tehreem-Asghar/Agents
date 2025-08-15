# Understanding the `instructions` Parameter in Agent Class

This document explains how the `instructions` parameter works in the `Agent` class and demonstrates **three different ways** to use it with examples.

---

## 📌 What is `instructions`?

In the `Agent` class, `instructions` act as the **system prompt**.  
They tell the AI model what to do and how to respond.

Definition in code:

```
instructions: (
    str
    | Callable[
        [RunContextWrapper[TContext], Agent[TContext]],
        MaybeAwaitable[str],
    ]
    | None
) = None

```

# This means:

- It can be a string

- It can be a function

- It can be an async function


## 1️⃣ Fixed String Instructions
- When to use
When your AI always follows the same instructions for every request.

Example
```
agent_fixed = Agent(
    name="RecipeBotFixed",
    instructions="You are a helpful chef who gives recipes in simple steps.",
    model=model
)
```

# Explanation:

- The AI will always get this same instruction regardless of user input.

## 2️⃣ Dynamic Function Instructions
- When to use
- When you want instructions to change based on user input or context.

Example
```
def language(ctx, agent):
    language = ctx.context.input.lower()
    if language == "urdu":
        return "Talk in urdu you are urdu bot"
    elif language == "english":
        return "talk in english you are english bot"
    else:
        return "You  are helpfull assistent."

agent_dynamic = Agent(
    name="Languages",
    instructions=language,
    model=model
)

```

Explanation:

- Here ctx.context.input is the language entered by the user.

- The instructions are generated dynamically based on this input.

## 3️⃣ Async Dynamic Instructions
- When to use
- When you need to fetch data from an API, database, or do time-consuming work before generating instructions.

Example
```
import asyncio

async def async_recipe_instructions(ctx, agent):
    await asyncio.sleep(0.5)  # Simulating API call delay
    ingredient = ctx.context.input.lower()
    return f"Please suggest a healthy recipe with {ingredient}, using fresh ingredients."

agent_async = Agent(
    name="RecipeBotAsync",
    instructions=async_recipe_instructions,
    model=model
)
```
Explanation:

- This allows asynchronous operations before creating instructions.

- Useful for dynamic, data-driven instructions.

🔹 Running the Agents
Example runner:

runner = Runner(config=config)

# Choose any agent you want to test
selected_agent = agent_dynamic  # or agent_fixed / agent_async

user_input = input("Enter ingredient: ")
result = await runner.run(selected_agent, context=RecipeInput(input=user_input))

print("\n--- RecipeBot Response ---")
print(result.final_output)

📊 Summary Table

Type	           |  Changes per Input?  |	Can fetch external data? |	 Example Use Case
String             |	 ❌ No	         | ❌ No	                  |   Fixed role prompt
Callable Function  |     ✅ Yes	         | ❌ No	                  |   Input-based instructions
Async Function	   |     ✅ Yes	         | ✅ Yes	              |   API-driven or delayed instructions

✅ Conclusion
The instructions parameter in Agent is powerful because it can be:

A simple static prompt (fastest)

A dynamic function (flexible)

An async function (data-driven & real-time)

Choosing the right type depends on how dynamic and data-dependent your agent’s behavior should be.