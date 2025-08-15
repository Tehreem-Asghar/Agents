
## 1. **clone() ka code**

```
def clone(self, **kwargs: Any) -> Agent[TContext]:
    return dataclasses.replace(self, **kwargs)
```
```
  def clone(self, **kwargs: Any) -> Agent[TContext]:
        """Make a copy of the agent, with the given arguments changed.
        Notes:
            - Uses `dataclasses.replace`, which performs a **shallow copy**.
            - Mutable attributes like `tools` and `handoffs` are shallow-copied:
              new list objects are created only if overridden, but their contents
              (tool functions and handoff objects) are shared with the original.
            - To modify these independently, pass new lists when calling `clone()`.
        Example:
            ```python
            new_agent = agent.clone(instructions="New instructions")
            ```
        """
        return dataclasses.replace(self, **kwargs)
        
```

- Ye dataclasses.replace() ka use karta hai.

- dataclasses.replace() ek nayi object instance banata hai jo original ke saare fields copy karta hai, except un fields ke jo tum kwargs me specify karte ho — unko update kar deta hai.

## 2. **Shallow Copy ka Matlab**

**Shallow copy ka matlab:**

- Immutable cheezein (string, int, bool) safe hoti hain, kyunki unka reference change nahi hota.

- Mutable cheezein (lists, dicts, custom objects) sirf reference copy hota hai, naya object nahi banta.

**Iska effect ye hota hai:**

- Agar tum cloned agent ke andar tools list me append karoge, to original agent ki list bhi change ho jayegi (kyunki dono same list reference share kar rahe hain).

**Example:**
```
agent1 = Agent(tools=["ToolA"])
agent2 = agent1.clone()

agent2.tools.append("ToolB")

print(agent1.tools)  # ["ToolA", "ToolB"]  ← dono me change aa gaya!
```

- 📌 Agar tum chahte ho ki list independent ho, to clone call karte waqt nayi list pass karni padegi:
```
agent2 = agent1.clone(tools=list(agent1.tools))  # Nayi copy ban gayi
```
## 3. **clone()** ka kaam step-by-step

- 1) Base agent bana lo.

- 2) clone() call karo aur jo cheezein change karni hain unko kwargs me pass karo.

- 3) Ye ek naya Agent object banata hai — baaki fields original se copy hoti hain.

- 4) Tum naye agent ko independently use kar sakte ho (except shared mutable fields ka dhyan rakho).

## **4. Real Example**

```
# Base agent

news_agent = Agent(
    instructions="You are a news summarizer",
    model="gpt-4o"
)


# Clone with minor change

sports_agent = news_agent.clone(
    instructions="You are a sports news summarizer"
)
```

# **Output check**
```
print(news_agent.instructions)   # You are a news summarizer
print(sports_agent.instructions) # You are a sports news summarizer
```


⚡ **Benefit**: Tum ek hi config se multiple variations bana sakte ho bina bar-bar saari fields likhe.

5. Clone kyun use karein?

- 1) Reuse: Same base config ko multiple purposes ke liye use karna.
- 2) Versioning: Ek agent ka original safe rakhna, aur variations create karna without risk.
- 3) Performance: Har variation ke liye pura naya object manually banane ki zarurat nahi.
