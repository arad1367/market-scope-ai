from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.openbb_tools import OpenBBTools
import openai
import os
from dotenv import load_dotenv
from typing import Optional, List
import phi

from phi.playground import Playground, serve_playground_app # just for playground


# Load environment variables
load_dotenv()

# Set up API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
phi.api=os.getenv("PHI_API_KEY")

# Verify API keys are present
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

class MarketIntelligenceSystem:
    def __init__(self):
        try:
            # Initialize agents
            self.web_search_agent = self._create_web_search_agent()
            self.finance_agent = self._create_finance_agent()
            self.market_analysis_team = self._create_market_analysis_team()
        except Exception as e:
            print(f"Error initializing agents: {str(e)}")
            raise

    def _create_web_search_agent(self):
        return Agent(
            name="Web Search Agent",
            role="Search the web for market information and news",
            model=Groq(
                api_key=groq_api_key,
                id="mixtral-8x7b-32768",  # Using Mixtral model which better supports function calling
                temperature=0.3,
                max_tokens=4096
            ),
            tools=[DuckDuckGo()],
            instructions=[
                "Always include sources",
                "Prioritize recent and reliable financial news sources",
                "Include relevant market context",
                "Adapt search terms based on asset type (crypto, stock, etc.)"
            ],
            show_tools_calls=True,
            markdown=True,
        )

    def _create_finance_agent(self):
        return Agent(
            name="Finance AI Agent",
            model=Groq(
                api_key=groq_api_key,
                id="mixtral-8x7b-32768",  # Using Mixtral model which better supports function calling
                temperature=0.3,
                max_tokens=4096
            ),
            tools=[OpenBBTools()],
            instructions=[
                "Use tables to display financial data",
                "Include both technical and fundamental analysis when relevant",
                "Provide context for financial metrics",
                "Highlight significant changes or unusual patterns",
                "Include source and timestamp for all financial data",
                "Adapt analysis based on asset type (crypto, stock, etc.)",
                "Use OpenBB functions: get_stock_price, get_company_news, get_company_profile, get_price_targets"
            ],
            show_tools_calls=True,
            markdown=True,
        )

    def _create_market_analysis_team(self):
        return Agent(
            team=[self.web_search_agent, self.finance_agent],
            instructions=[
                "Always include sources",
                "Use tables to display financial data",
                "Combine market news with financial analysis",
                "Prioritize actionable insights",
                "Highlight any discrepancies between different data sources",
                "Include both short-term and long-term perspectives",
                "Adapt analysis based on asset type"
            ],
            show_tools_calls=True,
            markdown=True,
        )

    def analyze_asset(self, symbol: str, asset_type: Optional[str] = None):
        """
        Comprehensive asset analysis function that works for both stocks and cryptocurrencies
        """
        try:
            if asset_type is None:
                asset_type = 'crypto' if any(crypto_indicator in symbol.upper() 
                                           for crypto_indicator in ['BTC', 'ETH', 'USDT', 'BNB']) else 'stock'

            prompt = f"""
            Analyze {symbol} ({asset_type}):
            1. Get current price using get_stock_price
            2. Search latest news using get_company_news
            3. Get company/asset profile using get_company_profile
            4. Check price targets using get_price_targets
            5. Analyze broader market impact and trends
            
            Adapt the analysis for {asset_type} specifically.
            """
            return self.market_analysis_team.print_response(prompt, stream=True)
        except Exception as e:
            print(f"Error analyzing asset: {str(e)}")
            return None

    def market_overview(self, focus_areas: Optional[List[str]] = None):
        """
        General market overview function with customizable focus areas
        """
        try:
            focus_str = ", ".join(focus_areas) if focus_areas else "all major markets"
            prompt = f"""
            Provide a market overview focusing on {focus_str}, including:
            1. Use get_stock_price for key market indicators
            2. Get latest news using get_company_news for major market movers
            3. Check market trends and patterns
            4. Analyze sector/asset performance
            """
            return self.market_analysis_team.print_response(prompt, stream=True)
        except Exception as e:
            print(f"Error getting market overview: {str(e)}")
            return None

    def custom_analysis(self, query: str):
        """
        Handle custom user queries about any market-related topic
        """
        try:
            return self.market_analysis_team.print_response(query, stream=True)
        except Exception as e:
            print(f"Error processing custom query: {str(e)}")
            return None

# With Terminal (Solution 1)
def main():
    try:
        # Initialize the system
        market_system = MarketIntelligenceSystem()
        
        while True:
            print("\nMarket Intelligence System")
            print("1. Analyze specific asset (stock/crypto)")
            print("2. Market overview")
            print("3. Custom query")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                symbol = input("Enter asset symbol (e.g., AAPL, BTC-USD): ")
                asset_type = input("Enter asset type (stock/crypto) or press Enter to auto-detect: ").lower() or None
                market_system.analyze_asset(symbol, asset_type)
            
            elif choice == '2':
                areas = input("Enter focus areas (comma-separated) or press Enter for all markets: ")
                focus_areas = [area.strip() for area in areas.split(",")] if areas else None
                market_system.market_overview(focus_areas)
            
            elif choice == '3':
                query = input("Enter your custom query: ")
                market_system.custom_analysis(query)
            
            elif choice == '4':
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please try again.")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Exiting due to error...")

if __name__ == "__main__":
    main()


# If you need phi playground (Solution 2)
# market_system = MarketIntelligenceSystem()
# app = Playground(agents=[
#     market_system._create_web_search_agent(),
#     market_system._create_finance_agent(), 
#     market_system._create_market_analysis_team()
# ]).get_app()

# if __name__ == "__main__":
#     serve_playground_app("agents:app",reload=True)