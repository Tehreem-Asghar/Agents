## Handoff Code

```
from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable
from dataclasses import dataclass, replace as dataclasses_replace
from typing import TYPE_CHECKING, Any, Callable, Generic, cast, overload

from pydantic import TypeAdapter
from typing_extensions import TypeAlias, TypeVar

from .exceptions import ModelBehaviorError, UserError
from .items import RunItem, TResponseInputItem
from .run_context import RunContextWrapper, TContext
from .strict_schema import ensure_strict_json_schema
from .tracing.spans import SpanError
from .util import _error_tracing, _json, _transforms
from .util._types import MaybeAwaitable

if TYPE_CHECKING:
    from .agent import Agent, AgentBase


# The handoff input type is the type of data passed when the agent is called via a handoff.
THandoffInput = TypeVar("THandoffInput", default=Any)

# The agent type that the handoff returns
TAgent = TypeVar("TAgent", bound="AgentBase[Any]", default="Agent[Any]")

OnHandoffWithInput = Callable[[RunContextWrapper[Any], THandoffInput], Any]
OnHandoffWithoutInput = Callable[[RunContextWrapper[Any]], Any]


@dataclass(frozen=True)
class HandoffInputData:
    input_history: str | tuple[TResponseInputItem, ...]
    """
    The input history before `Runner.run()` was called.
    """

    pre_handoff_items: tuple[RunItem, ...]
    """
    The items generated before the agent turn where the handoff was invoked.
    """

    new_items: tuple[RunItem, ...]
    """
    The new items generated during the current agent turn, including the item that triggered the
    handoff and the tool output message representing the response from the handoff output.
    """

    run_context: RunContextWrapper[Any] | None = None
    """
    The run context at the time the handoff was invoked.
    Note that, since this property was added later on, it's optional for backwards compatibility.
    """

    def clone(self, **kwargs: Any) -> HandoffInputData:
        """
        Make a copy of the handoff input data, with the given arguments changed. For example, you
        could do:
        ```
        new_handoff_input_data = handoff_input_data.clone(new_items=())
        ```
        """
        return dataclasses_replace(self, **kwargs)


HandoffInputFilter: TypeAlias = Callable[[HandoffInputData], MaybeAwaitable[HandoffInputData]]
"""A function that filters the input data passed to the next agent."""


@dataclass
class Handoff(Generic[TContext, TAgent]):
    """A handoff is when an agent delegates a task to another agent.
    For example, in a customer support scenario you might have a "triage agent" that determines
    which agent should handle the user's request, and sub-agents that specialize in different
    areas like billing, account management, etc.
    """

    tool_name: str
    """The name of the tool that represents the handoff."""

    tool_description: str
    """The description of the tool that represents the handoff."""

    input_json_schema: dict[str, Any]
    """The JSON schema for the handoff input. Can be empty if the handoff does not take an input.
    """

    on_invoke_handoff: Callable[[RunContextWrapper[Any], str], Awaitable[TAgent]]
    """The function that invokes the handoff. The parameters passed are:
    1. The handoff run context
    2. The arguments from the LLM, as a JSON string. Empty string if input_json_schema is empty.

    Must return an agent.
    """

    agent_name: str
    """The name of the agent that is being handed off to."""

    input_filter: HandoffInputFilter | None = None
    """A function that filters the inputs that are passed to the next agent. By default, the new
    agent sees the entire conversation history. In some cases, you may want to filter inputs e.g.
    to remove older inputs, or remove tools from existing inputs.

    The function will receive the entire conversation history so far, including the input item
    that triggered the handoff and a tool call output item representing the handoff tool's output.

    You are free to modify the input history or new items as you see fit. The next agent that
    runs will receive `handoff_input_data.all_items`.

    IMPORTANT: in streaming mode, we will not stream anything as a result of this function. The
    items generated before will already have been streamed.
    """

    strict_json_schema: bool = True
    """Whether the input JSON schema is in strict mode. We **strongly** recommend setting this to
    True, as it increases the likelihood of correct JSON input.
    """

    is_enabled: bool | Callable[
        [RunContextWrapper[Any], AgentBase[Any]], MaybeAwaitable[bool]
    ] = True
    """Whether the handoff is enabled. Either a bool or a Callable that takes the run context and
    agent and returns whether the handoff is enabled. You can use this to dynamically enable/disable
    a handoff based on your context/state."""


    def get_transfer_message(self, agent: AgentBase[Any]) -> str:
        return json.dumps({"assistant": agent.name})

    @classmethod
    def default_tool_name(cls, agent: AgentBase[Any]) -> str:
        return _transforms.transform_string_function_style(f"transfer_to_{agent.name}")

    @classmethod
    def default_tool_description(cls, agent: AgentBase[Any]) -> str:
        return (
            f"Handoff to the {agent.name} agent to handle the request. "
            f"{agent.handoff_description or ''}"
        )


@overload
def handoff(
    agent: Agent[TContext],
    *,
    tool_name_override: str | None = None,
    tool_description_override: str | None = None,
    input_filter: Callable[[HandoffInputData], HandoffInputData] | None = None,
    is_enabled: bool | Callable[[RunContextWrapper[Any], Agent[Any]], MaybeAwaitable[bool]] = True,
) -> Handoff[TContext, Agent[TContext]]: ...


@overload
def handoff(
    agent: Agent[TContext],
    *,
    on_handoff: OnHandoffWithInput[THandoffInput],
    input_type: type[THandoffInput],
    tool_description_override: str | None = None,
    tool_name_override: str | None = None,
    input_filter: Callable[[HandoffInputData], HandoffInputData] | None = None,
    is_enabled: bool | Callable[[RunContextWrapper[Any], Agent[Any]], MaybeAwaitable[bool]] = True,
) -> Handoff[TContext, Agent[TContext]]: ...


@overload
def handoff(
    agent: Agent[TContext],
    *,
    on_handoff: OnHandoffWithoutInput,
    tool_description_override: str | None = None,
    tool_name_override: str | None = None,
    input_filter: Callable[[HandoffInputData], HandoffInputData] | None = None,
    is_enabled: bool | Callable[[RunContextWrapper[Any], Agent[Any]], MaybeAwaitable[bool]] = True,
) -> Handoff[TContext, Agent[TContext]]: ...


def handoff(
    agent: Agent[TContext],
    tool_name_override: str | None = None,
    tool_description_override: str | None = None,
    on_handoff: OnHandoffWithInput[THandoffInput] | OnHandoffWithoutInput | None = None,
    input_type: type[THandoffInput] | None = None,
    input_filter: Callable[[HandoffInputData], HandoffInputData] | None = None,
    is_enabled: bool
    | Callable[[RunContextWrapper[Any], Agent[TContext]], MaybeAwaitable[bool]] = True,
) -> Handoff[TContext, Agent[TContext]]:
    """Create a handoff from an agent.

    Args:
        agent: The agent to handoff to, or a function that returns an agent.
        tool_name_override: Optional override for the name of the tool that represents the handoff.
        tool_description_override: Optional override for the description of the tool that
            represents the handoff.
        on_handoff: A function that runs when the handoff is invoked.
        input_type: the type of the input to the handoff. If provided, the input will be validated
            against this type. Only relevant if you pass a function that takes an input.
        input_filter: a function that filters the inputs that are passed to the next agent.
        is_enabled: Whether the handoff is enabled. Can be a bool or a callable that takes the run
            context and agent and returns whether the handoff is enabled. Disabled handoffs are
            hidden from the LLM at runtime.
    """
    assert (on_handoff and input_type) or not (on_handoff and input_type), (
        "You must provide either both on_handoff and input_type, or neither"
    )
    type_adapter: TypeAdapter[Any] | None
    if input_type is not None:
        assert callable(on_handoff), "on_handoff must be callable"
        sig = inspect.signature(on_handoff)
        if len(sig.parameters) != 2:
            raise UserError("on_handoff must take two arguments: context and input")

        type_adapter = TypeAdapter(input_type)
        input_json_schema = type_adapter.json_schema()
    else:
        type_adapter = None
        input_json_schema = {}
        if on_handoff is not None:
            sig = inspect.signature(on_handoff)
            if len(sig.parameters) != 1:
                raise UserError("on_handoff must take one argument: context")

    async def _invoke_handoff(
        ctx: RunContextWrapper[Any], input_json: str | None = None
    ) -> Agent[TContext]:
        if input_type is not None and type_adapter is not None:
            if input_json is None:
                _error_tracing.attach_error_to_current_span(
                    SpanError(
                        message="Handoff function expected non-null input, but got None",
                        data={"details": "input_json is None"},
                    )
                )
                raise ModelBehaviorError("Handoff function expected non-null input, but got None")

            validated_input = _json.validate_json(
                json_str=input_json,
                type_adapter=type_adapter,
                partial=False,
            )
            input_func = cast(OnHandoffWithInput[THandoffInput], on_handoff)
            if inspect.iscoroutinefunction(input_func):
                await input_func(ctx, validated_input)
            else:
                input_func(ctx, validated_input)
        elif on_handoff is not None:
            no_input_func = cast(OnHandoffWithoutInput, on_handoff)
            if inspect.iscoroutinefunction(no_input_func):
                await no_input_func(ctx)
            else:
                no_input_func(ctx)

        return agent

    tool_name = tool_name_override or Handoff.default_tool_name(agent)
    tool_description = tool_description_override or Handoff.default_tool_description(agent)

    # Always ensure the input JSON schema is in strict mode
    # If there is a need, we can make this configurable in the future
    input_json_schema = ensure_strict_json_schema(input_json_schema)

    async def _is_enabled(ctx: RunContextWrapper[Any], agent_base: AgentBase[Any]) -> bool:
        from .agent import Agent

        assert callable(is_enabled), "is_enabled must be callable here"
        assert isinstance(agent_base, Agent), "Can't handoff to a non-Agent"
        result = is_enabled(ctx, agent_base)

        if inspect.isawaitable(result):
            return await result

        return result

    return Handoff(
        tool_name=tool_name,
        tool_description=tool_description,
        input_json_schema=input_json_schema,
        on_invoke_handoff=_invoke_handoff,
        input_filter=input_filter,
        agent_name=agent.name,
        is_enabled=_is_enabled if callable(is_enabled) else is_enabled,
    )


```







# 🌟 Overall Purpose

Ye code kaam karta hai:

- Ek Handoff object banata hai jo define karta hai:

    - Kaunsa agent agla kaam karega.

    - Kya input pass hoga.

    - Kaise input validate hoga.

    - Kaunse condition pe handoff enable/disable hoga.

# Soch lo aik Customer Support App hai:

- Triage Agent decide karta hai user ka issue billing ka hai ya technical ka.

- Agar billing ka hai → woh Billing Agent ko handoff karega.

- Agar technical hai → woh Tech Agent ko handoff karega.

# 🧩 Important Parts in Code
**1. HandoffInputData (dataclass)**

Yeh represent karta hai jab handoff hota hai to us waqt ka conversation snapshot.

- input_history: Pehle se jo inputs diye gaye.

- pre_handoff_items: Pehle se generated items (handoff se pehle).

- new_items: Abhi ke turn me generated items (handoff trigger waala bhi include).

- run_context: Optional, context jis waqt handoff hua.

👉 Iska kaam hai pura context safe rakhna jo agle agent ko milega.

**2. Handoff (dataclass)**

Yeh main object hai jo ek handoff definition hold karta hai.

Parameters:

- **tool_name →** Jo LLM ko dikhaya jayega ("transfer_to_billing").

- **tool_description →** LLM ko explain karega ke yeh tool kya karta hai.

- **input_json_schema →** Input ka schema (agar koi input required hai to).

- **on_invoke_handoff →**  jo call hoga jab handoff trigger hota hai.

- **agent_name →** Jis agent ko handoff karna hai uska naam.

- **input_filter →** Agar tum filter karna chaho inputs ko (jaise purani baaton ko remove karna).

- **strict_json_schema →** Default True, matlab JSON strict validation ke sath check hoga.

- **is_enabled →** Decide karega ke handoff enable hai ya disable (yeh bool ya function dono ho sakta hai).

**3. handoff Function**

Yeh helper function hai jo Handoff object banata hai.

Parameters:

**agent** → Jis agent ko handoff karna hai. (Required ✅)

**tool_name_override →** Agar custom naam dena ho tool ka. (Optional ❌)

**tool_description_override →** Custom description. (Optional ❌)

**on_handoff →** Callback function jo chale jab handoff hota hai. (Optional ❌)

    - Agar input required hai → function signature (ctx, input)

    - Agar input nahi hai → function signature (ctx)

**input_type →** Agar tum input expect kar rahe ho (e.g. ek dataclass), to woh type. (Optional ❌ but required agar input lena hai).

**input_filter →** Input filter karne ke liye function. (Optional ❌)

**is_enabled →** True/False ya function, jo decide karega ke handoff available hai ya nahi. (Default True ✅)

**Return:**

Ek Handoff object jo ready hota hai use karne ke liye.

## **🔑 Important Logic in Function**

# 1. Validation of **on_handoff** function
- Agar input_type diya hai to function ko 2 arguments lene chahiye (ctx, input).
- Agar input_type nahi diya to sirf ek argument (ctx) hona chahiye.

# 2. _invoke_handoff function

- Yeh async function hai jo actual handoff execute karta hai.

- Agar input hai → usay validate karta hai pydantic se.

- Phir on_handoff callback run karta hai.

- End me agent return karta hai jisko handoff kiya gaya tha.

# 3. is_enabled handling

- Agar callable diya hai → woh run hota hai aur decide karta hai enable/disable.

- Agar sirf bool diya hai → directly use hota hai.

## **✅ Required vs Optional Parameters**
**Required**

- **agent →** bina iske handoff possible hi nahi.

**Optional**

- tool_name_override (default = "transfer_to_{agent.name}")

- tool_description_override (default = "Handoff to {agent.name}")

- on_handoff (agar input handling chahiye)

- input_type (agar input chahiye to ye required ho jata hai)

- input_filter (by default pura history forward hota hai)

- is_enabled (default = True)

# **🧠 Simple Example**
```
# Example: Triage agent se Billing agent ko handoff
handoff_to_billing = handoff(
    agent=billing_agent,
    on_handoff=lambda ctx, input: print(f"Handoff with {input}"),
    input_type=dict,  # expect dict input
)
```

- Agar LLM decide kare ke billing agent ko call karna hai, to yeh handoff trigger hoga.

- Input dict validate hoga.

- on_handoff run hoga.

- Conversation continue karega billing agent ke sath.

# **📌 Key Points**

- Handoff ek bridge hai ek agent se dusre agent tak.

- input_type aur on_handoff dono sath honay chahiye agar input lena ho.

- Default JSON schema strict hai → input validation strong hoti hai.

- is_enabled dynamically decide kar sakta hai ke agent available hai ya nahi.

- Agar input filtering nahi karte to pura history agle agent ko milta hai.