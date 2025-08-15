## 📖 Handoffs in Agents Framework
# What Are Handoffs?

- In the agents framework, handoffs allow an agent to delegate incoming tasks to another specialized agent or a predefined handoff target.

```
  handoffs: list[Agent[Any] | Handoff[TContext, Any]] = field(default_factory=list)
    """Handoffs are sub-agents that the agent can delegate to. You can provide a list of handoffs,
    and the agent can choose to delegate to them if relevant. Allows for separation of concerns and
    modularity.
    """
```

handoff() ka actual signature kuch is tarah ka hai (simplified):

```
handoff(
    agent,
    tool_name_override=None,
    tool_description_override=None,
    on_handoff=None,
    input_type=None,
    input_filter=None,
    is_enabled=True
)
```

Think of it as a switchboard operator who routes your request to the right department.


# Two Ways to Use Handoffs

- 1) Direct Agent Handoffs – Pass Agent objects directly.

- 2) Handoff Object Handoffs – Use the Handoff class for more control.

# 1️⃣ Direct Agent Handoff Example
```
from agents import Agent

# Specialized agents
joke_bot = Agent(
    name="JokeBot",
    instructions="You are a joke bot",
    model=model
)

speech_bot = Agent(
    name="SpeechBot",
    instructions="You are a speech bot that can generate speeches on various topics.",
    model=model
)

# Main agent with handoffs
delegate_bot = Agent(
    name="DelegateTaskBot",
    instructions="You are a task delegation bot that can delegate tasks to other agents.",
    model=model,
    handoffs=[joke_bot, speech_bot]  # Pass Agent objects directly
)
```

# 2️⃣ Handoff Object Example

- Using the Handoff class allows you to:

- 1) Give human-readable descriptions for routing.

- 2) Pass custom parameters during delegation.

```
from agents import Agent, handoff

# Specialized agents
recipe_bot = Agent(
    name="RecipeBot",
    instructions="You are a recipe bot that suggests healthy recipes.",
    model=model
)

news_bot = Agent(
    name="NewsBot",
    instructions="You are a news bot that provides the latest headlines.",
    model=model
)

# Using the `handoff()` helper to add descriptions
recipe_handoff = handoff(
    recipe_bot,
    tool_description_override="Handles recipe-related queries"
)

news_handoff = handoff(
    news_bot,
    tool_description_override="Handles news and headline-related queries"
)

# Main delegator agent
delegate_bot = Agent(
    name="DelegateTaskBot",
    instructions="You are a task delegator bot.",
    model=model,
    handoffs=[recipe_handoff, news_handoff]  # Pass Handoff objects
)

```

## How It Works

1) User sends request to the main agent.

2) The main agent evaluates which handoff is best.

3) The selected handoff’s agent processes the request.

4) The result is sent back to the user.

# Example Flow

User Input:
```
Tell me the latest news about space exploration.
```

Flow:
```
User → DelegateTaskBot → NewsBot → User
```

## Key Differences
Feature     	    |  Agent-based Handoff	|    Handoff Object
Simplicity  	    |    ✅ Simple	       |   ❌ Slightly more setup
Custom Description	|    ❌ No	           |   ✅ Yes
Extra Metadata	    |    ❌ No	           |   ✅ Yes