import streamlit as st
from dotenv import load_dotenv

load_dotenv()

import os
import litellm
from time import sleep
from crewai import Crew, Task, Agent, Process, LLM
from crewai_tools import TavilySearchTool


# === ROBUST MONKEY PATCH: Remove 'stop' parameter for Perplexity ===
# This must be done before any LLM initialization
def remove_stop_sequences(func):
    """Decorator to remove stop sequences from kwargs"""

    def wrapper(*args, **kwargs):
        # Remove stop-related parameters
        kwargs.pop("stop", None)
        kwargs.pop("stop_sequences", None)
        return func(*args, **kwargs)

    return wrapper


# Apply patch to litellm
litellm.completion = remove_stop_sequences(litellm.completion)
litellm.acompletion = remove_stop_sequences(litellm.acompletion)


# Setup LLM with corrected configuration
@st.cache_resource
def get_llm():
    return LLM(
        model="perplexity/sonar",  # Keep the prefix
        api_key=os.environ.get("PERPLEXITY_API_KEY"),
        temperature=0.7,  # Increase temperature slightly
        max_tokens=4000,  # Add max_tokens
    )


# Setup search tool
@st.cache_resource
def get_search_tool():
    return TavilySearchTool(
        max_results=5,  # Reduce to avoid timeout
        include_answer=True,
    )


# Initialize crew
@st.cache_resource
def initialize_crew():
    llm = get_llm()
    search_tool = get_search_tool()

    # --- Agents with shorter, more focused descriptions ---
    financial_analyst_agent = Agent(
        role="Financial Analyst",
        goal="Analyze {company_name} financial metrics including revenue, profit margins, and debt.",
        backstory="You analyze company financials and extract key performance indicators.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    strategy_analyst_agent = Agent(
        role="Strategy Analyst",
        goal="Research {company_name} competitive position, management guidance, and industry trends.",
        backstory="You evaluate business strategy and competitive advantages.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    investment_advisor_agent = Agent(
        role="Investment Advisor",
        goal="Create investment report for {company_name} with BUY/SELL/HOLD recommendation.",
        backstory="You synthesize financial and strategic analysis into actionable investment advice.",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Tasks with more concise descriptions ---
    financial_analysis_task = Task(
        description=(
            "Research and analyze {company_name}'s latest financial performance: "
            "1. Revenue growth (YoY) "
            "2. Profit margins (EBITDA, Net) "
            "3. Debt-to-equity ratio "
            "4. Key financial highlights from latest quarterly/annual report"
        ),
        expected_output="Financial summary with key metrics and trends for {company_name}.",
        agent=financial_analyst_agent,
        async_execution=True,
    )

    strategy_analysis_task = Task(
        description=(
            "Analyze {company_name}'s strategic position: "
            "1. Recent management guidance from earnings calls "
            "2. Industry outlook and trends "
            "3. Competitive advantages (moat) "
            "4. Major risks and opportunities"
        ),
        expected_output="Strategic assessment covering guidance, industry trends, and competitive position.",
        agent=strategy_analyst_agent,
        async_execution=True,
    )

    report_generation_task = Task(
        description=(
            "Create a comprehensive investment report for {company_name} with these sections: "
            "1. Executive Summary (2-3 sentences) "
            "2. Financial Performance (key metrics) "
            "3. Strategic Outlook (management guidance, industry trends) "
            "4. Competitive Moat (strengths vs competitors) "
            "5. Investment Recommendation (BUY/SELL/HOLD with clear justification)"
        ),
        expected_output="Professional investment report with clear recommendation.",
        agent=investment_advisor_agent,
        context=[financial_analysis_task, strategy_analysis_task],
        async_execution=False,
    )

    # --- Crew ---
    crew = Crew(
        agents=[
            financial_analyst_agent,
            strategy_analyst_agent,
            investment_advisor_agent,
        ],
        tasks=[
            financial_analysis_task,
            strategy_analysis_task,
            report_generation_task,
        ],
        process=Process.sequential,
        verbose=True,
        max_rpm=10,  # Add rate limiting
    )

    return crew


def run_analysis(company_name, progress_bar, status_text):
    """Run the crew analysis with retry logic"""
    max_retries = 3
    result = None

    for attempt in range(max_retries):
        try:
            status_text.text(
                f"🔄 Attempt {attempt + 1}/{max_retries} - Analyzing {company_name}..."
            )
            progress_bar.progress(10)

            # Re-initialize crew on each attempt to avoid state issues
            crew = initialize_crew()

            status_text.text(f"🔍 Gathering financial data...")
            progress_bar.progress(30)

            result = crew.kickoff(inputs={"company_name": company_name})

            status_text.text("✅ Analysis completed successfully!")
            progress_bar.progress(100)
            return str(result)

        except Exception as e:
            error_msg = str(e)
            status_text.error(f"⚠️ Attempt {attempt + 1} failed: {error_msg}")

            # Clear cache and retry if it's an API error
            if "BadRequestError" in error_msg or "empty" in error_msg.lower():
                st.cache_resource.clear()

            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3  # Progressive wait
                status_text.warning(f"⏳ Retrying in {wait_time} seconds...")
                sleep(wait_time)
            else:
                status_text.error(
                    f"❌ All {max_retries} attempts failed. Error: {error_msg}"
                )
                return None

    return None


# === STREAMLIT UI ===
def main():
    # Page config
    st.set_page_config(
        page_title="AI Investment Researcher", page_icon="📊", layout="wide"
    )

    # Header
    st.title("📊 AI Investment Researcher")
    st.markdown("### Generate comprehensive investment reports powered by AI")
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses AI agents to:
        - 📈 Analyze financial performance
        - 🎯 Evaluate strategic outlook
        - 💼 Generate investment recommendations
        
        **Powered by:**
        - Perplexity Sonar LLM
        - Tavily Search
        - CrewAI Framework
        """)

        st.divider()

        # API Key check
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        tavily_key = os.environ.get("TAVILY_API_KEY")

        if api_key:
            st.success("✅ Perplexity API Key Loaded")
        else:
            st.error("❌ PERPLEXITY_API_KEY not found")

        if tavily_key:
            st.success("✅ Tavily API Key Loaded")
        else:
            st.error("❌ TAVILY_API_KEY not found")

        st.divider()

        # Clear cache button
        if st.button("🔄 Reset Application", use_container_width=True):
            st.cache_resource.clear()
            st.session_state.clear()
            st.rerun()

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        company_name = st.text_input(
            "🏢 Enter Company Name",
            placeholder="e.g., Tata Motors, Reliance Industries, Infosys",
            help="Enter the full or commonly known name of the company",
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        analyze_button = st.button(
            "🚀 Generate Report", type="primary", use_container_width=True
        )

    # Initialize session state for storing report
    if "report" not in st.session_state:
        st.session_state.report = None
    if "analyzed_company" not in st.session_state:
        st.session_state.analyzed_company = None

    # Analysis execution
    if analyze_button:
        if not company_name or company_name.strip() == "":
            st.error("⚠️ Please enter a company name")
        elif not os.environ.get("PERPLEXITY_API_KEY"):
            st.error("⚠️ PERPLEXITY_API_KEY not found in environment variables")
        else:
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Run analysis
            report = run_analysis(company_name, progress_bar, status_text)

            if report:
                st.session_state.report = report
                st.session_state.analyzed_company = company_name
                st.success(f"✅ Report generated for **{company_name}**!")
            else:
                st.error(
                    "❌ Failed to generate report. Try the 'Reset Application' button in sidebar."
                )

    # Display report
    if st.session_state.report:
        st.divider()
        st.header(f"📄 Investment Report: {st.session_state.analyzed_company}")

        # Create tabs for different views
        tab1, tab2 = st.tabs(["📖 Report", "💾 Download"])

        with tab1:
            # Display report with nice formatting
            st.markdown(st.session_state.report)

        with tab2:
            # Download options
            st.subheader("Download Options")

            filename = f"{st.session_state.analyzed_company.replace(' ', '_')}_Investment_Report"

            col1, col2 = st.columns(2)

            with col1:
                # Text file download
                st.download_button(
                    label="📄 Download as TXT",
                    data=st.session_state.report,
                    file_name=f"{filename}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            with col2:
                # Markdown file download
                st.download_button(
                    label="📝 Download as MD",
                    data=st.session_state.report,
                    file_name=f"{filename}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            st.info("💡 Tip: You can copy the report directly from the Report tab")

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>Built with CrewAI, Perplexity Sonar & Streamlit | AI-powered investment research</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
