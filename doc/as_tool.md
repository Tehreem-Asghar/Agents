**as_tool()** ka kaam ye hota hai ki tum apne Agent ko ek tool me badal do taake koi dusra Agent use call kar sake — jaise ek helper function.


# **1. Problem ye solve karta hai**

Kabhi tumhare paas ek Agent hota hai jo ek specific kaam me expert hai (e.g., "Weather Agent"),
aur tum chahte ho ki koi dusra Agent usko call kare jaise ek function call karta hai.
as_tool() isi kaam ke liye hota hai.

# **2. Basic Kaam**

- Ye Agent ko ek Tool object me convert karta hai.

- Wo Tool phir kisi aur Agent ke tools list me add ho sakta hai.

- Jab dusra Agent ko lagta hai ki is kaam ke liye ye tool best hai, to wo direct is tool ko call karega,
aur tumhara original Agent run hoga.

# **3. Difference from Handoff**

**Handoff**                                                            
- Conversation ka control dusre agent ko de deta hai  
- Sub-agent ko poora conversation history milta hai    
- Sub-agent poora conversation le leta hai	         

**as_tool**
- Sirf ek helper call hota hai, control wapas original agent ke paas jata hai
- Sirf specific input milta hai
- Ye sirf ek call hota hai

# **4. Parameters**
```
as_tool(
    tool_name=None,                # Tool ka naam (default: agent ka naam)
    tool_description=None,         # Ye batata hai ki tool kya karta hai
    custom_output_extractor=None   # Agar tum custom output nikalna chahte ho
)
```

- tool_name: Dusre agent ki tool list me jo naam show hoga.

- tool_description: LLM ko batane ke liye ki ye kab use kare.

- custom_output_extractor: Agar tumhe default se alag format me output chahiye, to ye function define kar sakte ho.

# **5. Workflow Example**

```
# Step 1: Expert Agent banao
weather_agent = Agent(instructions="You are a weather expert.")

# Step 2: Usko tool me convert karo
weather_tool = weather_agent.as_tool(
    tool_name="get_weather",
    tool_description="Fetches weather for a given location"
)

# Step 3: Dusre agent me use add karo
main_agent = Agent(
    instructions="You are a travel assistant.",
    tools=[weather_tool]
)

# Step 4: Jab main_agent ko weather chahiye, wo weather_tool call karega
```

# **6. Kaise Kaam Karta Hai Under the Hood**

- as_tool() ek inner async function run_agent() banata hai.

- Ye function jab call hota hai:

1) Runner.run() ko call karta hai, jo tumhara Agent execute karta hai.

2) Agar custom_output_extractor diya hai, to usse output process hota hai.

3) Warna default se agent ka last message return hota hai.

- Phir ye function @function_tool decorator se wrap hota hai aur ek Tool object ban jata hai.

# **7. Kyun Use Karein**

**Modularity:** Har Agent apne kaam me expert hota hai.

**Reusability:** Ek agent ko multiple agents call kar sakte hain bina code repeat kiye.

**Control:** Main conversation ka flow control original agent ke paas rehta hai.

**Scalability:** Badi systems me alag-alag kaam ke liye specialized agents use karna easy ho jata hai.