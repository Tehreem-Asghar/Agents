@dataclass
class ModelSettings:
    """Settings to use when calling an LLM.

    This class holds optional model configuration parameters (e.g. temperature,
    top_p, penalties, truncation, etc.).

    Not all models/providers support all of these parameters, so please check the API documentation
    for the specific model and provider you are using.
    """

    temperature: float | None = None
    """The temperature to use when calling the model."""

    top_p: float | None = None
    """The top_p to use when calling the model.""" 

    frequency_penalty: float | None = None
    """The frequency penalty to use when calling the model."""

    presence_penalty: float | None = None
    """The presence penalty to use when calling the model."""

    tool_choice: ToolChoice | None = None
    """The tool choice to use when calling the model."""

    parallel_tool_calls: bool | None = None
    """Controls whether the model can make multiple parallel tool calls in a single turn.
    If not provided (i.e., set to None), this behavior defers to the underlying
    model provider's default. For most current providers (e.g., OpenAI), this typically
    means parallel tool calls are enabled (True).
    Set to True to explicitly enable parallel tool calls, or False to restrict the
    model to at most one tool call per turn.
    """

    truncation: Literal["auto", "disabled"] | None = None
    """The truncation strategy to use when calling the model."""

    max_tokens: int | None = None
    """The maximum number of output tokens to generate."""

    reasoning: Reasoning | None = None
    """Configuration options for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning).
    """

    metadata: dict[str, str] | None = None
    """Metadata to include with the model response call."""

    store: bool | None = None
    """Whether to store the generated model response for later retrieval.
    Defaults to True if not provided."""

    include_usage: bool | None = None
    """Whether to include usage chunk.
    Defaults to True if not provided."""

    response_include: list[ResponseIncludable] | None = None
    """Additional output data to include in the model response.
    [include parameter](https://platform.openai.com/docs/api-reference/responses/create#responses-create-include)"""

    extra_query: Query | None = None
    """Additional query fields to provide with the request.
    Defaults to None if not provided."""

    extra_body: Body | None = None
    """Additional body fields to provide with the request.
    Defaults to None if not provided."""

    extra_headers: Headers | None = None
    """Additional headers to provide with the request.
    Defaults to None if not provided."""

    extra_args: dict[str, Any] | None = None
    """Arbitrary keyword arguments to pass to the model API call.
    These will be passed directly to the underlying model provider's API.
    Use with caution as not all models support all parameters."""


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
