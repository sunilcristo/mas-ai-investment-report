This is a simple web app that uses AI agents to create professional investment reports for any company you enter, like Tata Motors or Reliance. Just type the company name, click generate, and get a full analysis with BUY/SELL/HOLD advice.
​

What It Does
The app runs three smart AI agents working together:

Financial Analyst: Checks revenue growth, profits, debt, and key numbers from recent reports.

Strategy Analyst: Looks at competition, industry trends, management plans, and risks.

Investment Advisor: Combines everything into a clear report with a recommendation.

It pulls real-time data using search tools and generates reports in seconds.

Tech Stack
Frontend: Streamlit (easy web interface)

AI Framework: CrewAI (manages the agent team)

AI Model: Perplexity Sonar (smart analysis)

Search: Tavily (fresh web data)

Other: LiteLLM (API handling), python-dotenv (secrets)

Your requirements.txt has all packages needed.
​

Quick Start (Local Run)
Clone the repo: git clone https://github.com/yourusername/mas-ai-investment-report.git

Open folder in VSCode or terminal.

Create .env file:

text
PERPLEXITY_API_KEY=your_perplexity_key_here
TAVILY_API_KEY=your_tavily_key_here
Install packages: pip install -r requirements.txt

Run: streamlit run app.py

Enter a company like "Infosys" and click "Generate Report". Download as TXT or MD.

Deploy to Streamlit Cloud (Free)
Perfect for personal use in Bengaluru—no server costs.

Push to public GitHub (use VSCode Source Control).
​

Go to share.streamlit.io, "New app".

Select repo, branch main, file app.py → Deploy.

Add secrets (API keys) in app settings → .streamlit/secrets.toml format:

text
PERPLEXITY_API_KEY = "your_key"
TAVILY_API_KEY = "your_key"
App live at https://yourapp.streamlit.app. Updates auto on git push.

Tip: Free for solo use; sleeps after inactivity but wakes fast.
​

Key Features
Progress bar and retry (up to 3 tries if API hiccups).

Clean reports without messy citations.

Sidebar shows API status.

Reset button clears cache.

Example companies: Indian stocks like HDFC Bank, TCS.

Get API Keys
Perplexity: Sign up at perplexity.ai, get key from dashboard (free tier ok for testing).

Tavily: tavily.com, free search API for tools.

Customize
Change agents/tasks in initialize_crew() for new analysis types.

Add more tools or models via CrewAI docs.

For parallel agents: Set Process.hierarchical or async tweaks.
​

Troubleshooting
API errors: Check keys in .env or secrets. Retry clears cache.

Monkey patch: Fixes Perplexity "stop" issue—don't remove.

Slow? Reduce max_results in Tavily tool.
