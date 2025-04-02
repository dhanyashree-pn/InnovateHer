# Climate Risk InsurTech Research Agent 🌍

An AI-powered research assistant for climate risk and insurance technology using Streamlit, LangChain, OpenAI, and Tavily Search.

## Features

- AI-driven research from trusted climate risk and insurtech sources
- Structured reports with executive summaries and key findings
- Customizable search parameters and trusted domains
- Focus areas: Physical Risks, Transition Risks, InsurTech Solutions, Regulatory Policies, Market Trends

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up API keys in a `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   ```

## Usage

1. Run the app:
   ```bash
   streamlit run app.py
   ```
2. Configure settings in the sidebar
3. Enter your research query
4. Review the generated report

## Requirements

- Python 3.7+
- OpenAI API key ([get here](https://platform.openai.com/))
- Tavily API key ([get here](https://tavily.com/))

## Dependencies

- streamlit
- langchain & langchain_openai
- langchain_community
- pydantic
- python-dotenv
