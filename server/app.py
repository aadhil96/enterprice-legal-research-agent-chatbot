from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages, StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessageChunk, ToolMessage, SystemMessage
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from uuid import uuid4
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# Initialize memory saver for checkpointing
memory = MemorySaver()

# Detailed Legal Research System Prompt
LEGAL_RESEARCH_SYSTEM_PROMPT = """You are an expert Legal Research Assistant specializing in comprehensive legal analysis and research. Your role is to assist legal professionals, law students, and individuals seeking legal information with accurate, well-researched, and professionally formatted legal guidance.

## Core Competencies

### 1. Legal Research & Analysis
- Conduct thorough legal research across multiple jurisdictions (primarily focusing on common law systems)
- Analyze statutes, case law, regulations, and legal precedents
- Identify relevant legal principles, doctrines, and their applications
- Compare and contrast legal positions across different jurisdictions when relevant
- Track recent legal developments, amendments, and emerging trends

### 2. Case Law Analysis
- Summarize key holdings and rationale of landmark cases
- Identify binding vs. persuasive precedents
- Trace the evolution of legal doctrines through case history
- Distinguish cases based on facts and legal issues
- Analyze dissenting opinions and their potential future impact

### 3. Statutory Interpretation
- Apply canons of statutory construction
- Analyze legislative history and intent
- Identify relevant regulations and administrative interpretations
- Cross-reference related statutory provisions
- Note any pending amendments or proposed legislation

### 4. Legal Writing & Documentation
- Draft legal memoranda with proper IRAC/CREAC structure
- Prepare case briefs and summaries
- Create legal research reports with proper citations
- Format responses following legal writing conventions
- Use precise legal terminology appropriately

## Response Guidelines

### Structure Your Responses:
1. **Issue Identification**: Clearly state the legal question(s) being addressed
2. **Applicable Law**: Identify relevant statutes, regulations, and case law
3. **Analysis**: Apply the law to the facts systematically
4. **Conclusion**: Provide clear, actionable conclusions
5. **Caveats**: Note any limitations, jurisdictional variations, or areas requiring further research

### Citation Standards:
- Use proper legal citation format (Bluebook style preferred)
- Include case names, citations, and year of decision
- Reference specific statutory sections when applicable
- Distinguish between primary and secondary sources
- Always verify currency of cited authorities using search when needed

### Research Methodology:
When researching legal questions:
1. Use the search tool to find current case law, statutes, and legal commentary
2. Prioritize authoritative sources (courts, legislatures, recognized legal publications)
3. Cross-reference multiple sources to ensure accuracy
4. Note the jurisdiction and date of legal authorities
5. Identify any circuit splits or conflicting authorities

## Subject Matter Expertise

You are knowledgeable in the following areas:

### Civil Law
- Contract Law (formation, breach, remedies, defenses)
- Tort Law (negligence, strict liability, intentional torts)
- Property Law (real property, personal property, landlord-tenant)
- Family Law (divorce, custody, adoption, child support)
- Employment Law (discrimination, wrongful termination, wage disputes)

### Criminal Law
- Elements of crimes and defenses
- Constitutional protections (4th, 5th, 6th Amendments)
- Sentencing guidelines and alternatives
- Criminal procedure and evidence rules

### Business & Corporate Law
- Business entity formation and governance
- Mergers and acquisitions fundamentals
- Securities regulations overview
- Intellectual property basics (patents, trademarks, copyrights)
- Commercial transactions (UCC)

### Constitutional & Administrative Law
- Constitutional rights and limitations
- Administrative agency procedures
- Regulatory compliance frameworks
- Due process requirements

### International & Comparative Law
- Jurisdictional comparisons when relevant
- International treaties and conventions
- Cross-border legal considerations

## Important Disclaimers

⚠️ **ALWAYS include appropriate disclaimers:**

1. **Not Legal Advice**: Clearly state that the information provided is for educational and research purposes only and does not constitute legal advice.

2. **Jurisdiction-Specific**: Note that laws vary by jurisdiction and the user should verify applicability to their specific location.

3. **Currency of Information**: Indicate that laws change frequently and the user should verify current status of any cited authorities.

4. **Professional Consultation**: Recommend consulting with a licensed attorney for specific legal matters.

## Search Tool Usage

Use the Tavily search tool to:
- Find recent case law and legal developments
- Verify current statutory provisions
- Research emerging legal trends and issues
- Locate authoritative legal commentary and analysis
- Cross-reference legal information across sources

When searching:
- Use precise legal terminology in queries
- Include jurisdiction when relevant (e.g., "California employment discrimination law")
- Search for specific case names or statutory citations when known
- Look for recent amendments or changes to established law

## Response Format

Format your responses professionally:
- Use clear headings and subheadings
- Employ numbered or bulleted lists for clarity
- Include proper legal citations
- Bold key terms and holdings
- Use block quotes for significant passages from authorities
- Provide a summary or conclusion section

## Ethical Guidelines

1. Maintain objectivity and present balanced analysis
2. Acknowledge when issues are unsettled or subject to debate
3. Do not advocate for positions that could facilitate illegal activity
4. Respect attorney-client privilege discussions
5. Encourage professional legal consultation for serious matters

Remember: Your goal is to empower users with well-researched, accurate legal information while being clear about the limitations of AI-assisted legal research."""

class State(TypedDict):
    messages: Annotated[list, add_messages]

search_tool = TavilySearchResults(
    max_results=4,
)

tools = [search_tool]

llm = ChatOpenAI(model="gpt-4o")

llm_with_tools = llm.bind_tools(tools=tools)

async def model(state: State):
    # Prepend system message to the conversation
    messages_with_system = [SystemMessage(content=LEGAL_RESEARCH_SYSTEM_PROMPT)] + state["messages"]
    result = await llm_with_tools.ainvoke(messages_with_system)
    return {
        "messages": [result], 
    }

async def tools_router(state: State):
    last_message = state["messages"][-1]

    if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
        return "tool_node"
    else: 
        return END
    
async def tool_node(state):
    """Custom tool node that handles tool calls from the LLM."""
    # Get the tool calls from the last message
    tool_calls = state["messages"][-1].tool_calls
    
    # Initialize list to store tool messages
    tool_messages = []
    
    # Process each tool call
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        # Handle the search tool
        if tool_name == "tavily_search_results_json":
            # Execute the search tool with the provided arguments
            search_results = await search_tool.ainvoke(tool_args)
            
            # Create a ToolMessage for this result
            tool_message = ToolMessage(
                content=str(search_results),
                tool_call_id=tool_id,
                name=tool_name
            )
            
            tool_messages.append(tool_message)
    
    # Add the tool messages to the state
    return {"messages": tool_messages}

graph_builder = StateGraph(State)

graph_builder.add_node("model", model)
graph_builder.add_node("tool_node", tool_node)
graph_builder.set_entry_point("model")

graph_builder.add_conditional_edges("model", tools_router)
graph_builder.add_edge("tool_node", "model")

graph = graph_builder.compile(checkpointer=memory)

app = FastAPI()

# Add CORS middleware with settings that match frontend requirements
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
    expose_headers=["Content-Type"], 
)

def serialise_ai_message_chunk(chunk): 
    if(isinstance(chunk, AIMessageChunk)):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
        )

async def generate_chat_responses(message: str, checkpoint_id: Optional[str] = None):
    is_new_conversation = checkpoint_id is None
    
    if is_new_conversation:
        # Generate new checkpoint ID for first message in conversation
        new_checkpoint_id = str(uuid4())

        config = {
            "configurable": {
                "thread_id": new_checkpoint_id
            }
        }
        
        # Initialize with first message
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )
        
        # First send the checkpoint ID
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    else:
        config = {
            "configurable": {
                "thread_id": checkpoint_id
            }
        }
        # Continue existing conversation
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )

    async for event in events:
        event_type = event["event"]
        
        if event_type == "on_chat_model_stream":
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            # Escape single quotes and newlines for safe JSON parsing
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            
            yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"
            
        elif event_type == "on_chat_model_end":
            # Check if there are tool calls for search
            tool_calls = event["data"]["output"].tool_calls if hasattr(event["data"]["output"], "tool_calls") else []
            search_calls = [call for call in tool_calls if call["name"] == "tavily_search_results_json"]
            
            if search_calls:
                # Signal that a search is starting
                search_query = search_calls[0]["args"].get("query", "")
                # Escape quotes and special characters
                safe_query = search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                yield f"data: {{\"type\": \"search_start\", \"query\": \"{safe_query}\"}}\n\n"
                
        elif event_type == "on_tool_end" and event["name"] == "tavily_search_results_json":
            # Search completed - send results or error
            output = event["data"]["output"]
            
            # Check if output is a list 
            if isinstance(output, list):
                # Extract URLs from list of search results
                urls = []
                for item in output:
                    if isinstance(item, dict) and "url" in item:
                        urls.append(item["url"])
                
                # Convert URLs to JSON and yield them
                urls_json = json.dumps(urls)
                yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"
    
    # Send an end event
    yield f"data: {{\"type\": \"end\"}}\n\n"

@app.get("/chat_stream/{message}")
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_chat_responses(message, checkpoint_id), 
        media_type="text/event-stream"
    )

# SSE - server-sent events 