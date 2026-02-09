# AI Investment Researcher

This is a simple web app that uses AI agents to create professional investment reports for any company you enter, like Tata Motors or Reliance. Just type the company name, click generate, and get a full analysis with a BUY/SELL/HOLD recommendation.

## What this app does

The app runs three AI agents that work together:

- **Financial Analyst**: Looks at revenue growth, profit margins, debt-to-equity and other key financial metrics.
- **Strategy Analyst**: Examines industry trends, competition, management guidance, risks and opportunities.
- **Investment Advisor**: Combines the above analysis into a clear, human-readable investment report.

The final report includes sections like:
- Executive summary  
- Financial performance  
- Strategic outlook  
- Competitive moat  
- Investment recommendation (BUY/SELL/HOLD)

## Tech stack

- **Streamlit** – builds the web UI
- **CrewAI** – manages multiple AI agents and tasks
- **Perplexity Sonar** – main LLM used for analysis
- **Tavily Search** – fetches fresh web data for research
- **LiteLLM** – routes LLM calls
- **python-dotenv** – loads API keys from environment variables

All dependencies are listed in `requirements.txt`.

## How to run locally

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/mas-ai-investment-report.git
   cd mas-ai-investment-report

2. **Create and activate a virtual environment (optional but recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt

6. **Create a .env file in the project root:**
   ```bash
   PERPLEXITY_API_KEY=your_perplexity_key_here
   TAVILY_API_KEY=your_tavily_key_here

7. **Run the app**
   ```bash
   streamlit run app.py

9. **Open the URL shown in the terminal (usually http://localhost:8501) in your browser.**

[Watch the video](data/AI based investment report generator.mp4)
