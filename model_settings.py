model_settings = ModelSettings(
    temperature=None,            
    # Range: 0.0 se ~2.0 tak
    # Kaam: Jawab kitna creative/random ho
    # Suggestion: 
    #   0.0 - exact / safe answers
    #   0.7 - balance creative + accurate
    #   1.0+ - zyada creative (story writing, jokes)

    top_p=None,                   
    # Range: 0.0 se 1.0 tak
    # Kaam: Top percentage possible words ka selection
    # Suggestion: 
    #   1.0 - full variety (default)
    #   0.9 - thoda filter (quality + variety)
    #   0.5 - sirf best options (kam variety)

    frequency_penalty=None,       
    # Range: -2.0 se 2.0 tak
    # Kaam: Same word repeat hone se rokta hai
    # Suggestion: 
    #   0.0 - normal repetition
    #   1.0+ - kam repetition (writing tasks me useful)

    presence_penalty=None,        
    # Range: -2.0 se 2.0 tak
    # Kaam: Naye topics introduce karne ka chance
    # Suggestion: 
    #   0.0 - normal
    #   1.0+ - zyada new ideas (creative writing)
    #   Negative - topics limited rakhe

    tool_choice=None,             
    # Values: specific tool ka naam ya "auto"
    # Kaam: Kaunsa tool use hoga decide kare
    # Suggestion: "auto" - model khud decide kare

    parallel_tool_calls=None,     
    # Values: True/False
    # Kaam: Multiple tools ek sath chalane ka option
    # Suggestion: True agar speed chahiye, False agar order important hai

    truncation=None,              
    # Values: True/False
    # Kaam: Text limit cross hone par cut karna
    # Suggestion: True agar fixed size chahiye

    max_tokens=None,              
    # Range: Model ke limit tak (jaise GPT-4 me ~4096+)
    # Kaam: Output ka maximum length
    # Suggestion: Short answers = 100-200, long answers = 1000+

    reasoning=None,               
    # Values: Level/Mode
    # Kaam: Logical soch depth set karna
    # Suggestion: Zyada complex problems ke liye high value

    metadata=None,                
    # Values: Dict (key:value)
    # Kaam: Extra info save karna
    # Suggestion: Optional

    store=None,                   
    # Values: True/False
    # Kaam: Data save karna ya nahi
    # Suggestion: True agar logs chahiye

    include_usage=None,           
    # Values: True/False
    # Kaam: Tokens/usage ka detail response me dena
    # Suggestion: True agar cost ya usage track karna hai

    response_include=None,        
    # Values: List of fields
    # Kaam: Response me kya kya cheezen show karni
    # Suggestion: ["text", "usage"]

    extra_query=None,             
    # Values: Dict
    # Kaam: API me extra query params bhejna
    # Suggestion: Rarely use hota hai

    extra_body=None,              
    # Values: Dict
    # Kaam: API body me extra data
    # Suggestion: Advanced use

    extra_headers=None,           
    # Values: Dict
    # Kaam: API ke headers me extra fields
    # Suggestion: Authentication ya custom info ke liye

    extra_args=None               
    # Values: Dict
    # Kaam: Jo parameter aur kahin fit na ho
    # Suggestion: Rarely use hota hai
)
