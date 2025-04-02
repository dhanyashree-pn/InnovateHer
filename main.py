import streamlit as st
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
import os
import datetime
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = ""
TAVILY_API_KEY = ""

# Trusted sources for climate risk and insurtech news
TRUSTED_SOURCES = [
    "insurancejournal.com",
    "artemis.bm",
    "reuters.com",
    "tnfd.global",
    "swissre.com",
    "munichre.com",
    "lloyds.com",
    "genevaassociation.org",
    "naic.gov",
    "abi.org.uk"
]


# STREAMLIT UI SETUP
st.set_page_config(
    page_title="Climate Risk InsurTech AI Agent",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Climate Risk & InsurTech Research Agent")
st.caption("AI-powered research assistant for climate risk and insurance technology")


# SIDEBAR CONFIGURATION
with st.sidebar:
    st.header("Configuration")
    
    # API Keys
    tavily_api_key = st.text_input(
        "Tavily API Key",
        type="password",
        value=os.getenv("TAVILY_API_KEY", TAVILY_API_KEY)
    )
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
    )
    
    # Search Parameters
    search_depth = st.selectbox(
        "Search Depth",
        ["basic", "advanced"],
        index=1,
        help="Advanced search provides more comprehensive results"
    )
    max_results = st.slider(
        "Max Results",
        1, 20, 5,
        help="Number of sources to retrieve"
    )
    
    # Domain Focus
    selected_domains = st.multiselect(
        "Focus Domains",
        TRUSTED_SOURCES,
        default=TRUSTED_SOURCES[:3],
        help="Select trusted sources for research"
    )
    
    # Report Type
    report_focus = st.selectbox(
        "Report Focus Area",
        [
            "Climate Physical Risks",
            "Transition Risks",
            "InsurTech Solutions",
            "Regulatory Policies",
            "Market Trends"
        ]
    )
    
    if st.button("🔄 Clear Session"):
        st.session_state.clear()
        st.rerun()


# AGENT INITIALIZATION
def initialize_agent(openai_key, tavily_key):
    """Initialize the AI research agent with configured tools"""
    
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-1106-preview",
        api_key=openai_key
    )
    
    tavily_tool = TavilySearchResults(
        max_results=max_results,
        search_depth=search_depth,
        include_answer=True,
        include_raw_content=True,
        include_domains=selected_domains,
        tavily_api_key=tavily_api_key
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""
        You are an expert AI research assistant specializing in climate risk and insurance technology. 
        Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}.
        
        Your task is to analyze and report on:
        - Physical climate risks affecting insurance portfolios
        - Transition risks and regulatory changes
        - Innovative InsurTech solutions
        - Market trends in climate risk transfer
        
        Follow these guidelines:
        1. Provide concise, structured reports with clear insights
        2. Always cite sources with direct links
        3. Highlight insurance-specific implications
        4. Use professional tone suitable for industry executives
        5. Include risk assessment when possible
        """),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    agent = create_openai_tools_agent(llm=llm, tools=[tavily_tool], prompt=prompt_template)
    return AgentExecutor(agent=agent, tools=[tavily_tool], verbose=True)


# REPORT GENERATION
def generate_structured_report(response):
    """Transform agent response into structured report format"""
    
    report = {
        "summary": "",
        "key_findings": [],
        "sources": [],
        "insurance_implications": ""
    }
    
    # Extract main content
    report["summary"] = response.get("output", "")
    
    # Extract sources if available
    if hasattr(response, 'intermediate_steps'):
        for step in response.intermediate_steps:
            if step[0].tool == "tavily_search":
                for result in step[1].get("results", []):
                    source = {
                        "title": result.get("title", "Untitled"),
                        "url": result.get("url", "#"),
                        "content": result.get("content", "")[:500] + "..."
                    }
                    report["sources"].append(source)
    
    return report


# MAIN APPLICATION
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
# User input
if prompt := st.chat_input("Enter your climate risk or insurtech query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Validate API keys
    if not tavily_api_key or not openai_api_key:
        st.error("Please provide both API keys in the sidebar")
        st.stop()
    
    try:
        # Initialize agent
        agent_executor = initialize_agent(openai_api_key, tavily_api_key)
        
        # Enhanced prompt with report focus
        research_prompt = f"""
        Analyze recent developments in {report_focus} with focus on insurance implications.
        Provide a structured report with:
        1. Key findings
        2. Source verification
        3. Risk assessment
        4. Industry impact
        
        Query: {prompt}
        """
        
        with st.spinner("🔍 Researching latest developments..."):
            response = agent_executor.invoke({
                "messages": [HumanMessage(content=research_prompt)]
            })
            
            # Generate structured report
            report = generate_structured_report(response)
            
            # Display results
            with st.chat_message("assistant"):
                st.subheader("Research Report")
                
                # Summary
                st.markdown("### Executive Summary")
                st.write(report["summary"])
                
                # Key Findings
                st.markdown("### Key Findings")
                if report.get("key_findings"):
                    for finding in report["key_findings"]:
                        st.markdown(f"- {finding}")
                else:
                    st.write("No specific findings extracted")
                
                # Insurance Implications
                st.markdown("### Insurance Implications")
                st.write(report.get("insurance_implications", "Analyzing implications..."))
                
                # Sources
                with st.expander("View Research Sources"):
                    for source in report["sources"]:
                        st.markdown(f"#### [{source['title']}]({source['url']})")
                        st.caption(source["content"])
                        st.write("---")
                
                # Add to session
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": report["summary"]
                })
    
    except Exception as e:
        st.error(f"Research failed: {str(e)}")
        st.stop()


# INSTRUCTIONS FOR USE
st.sidebar.markdown("""
### Setup Instructions
1. Obtain API keys for [Tavily](https://tavily.com/) and [OpenAI](https://platform.openai.com/)
2. Add keys in the sidebar
3. Select search parameters
4. Enter your research query

""")