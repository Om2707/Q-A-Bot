import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from config import Config

class WebSearch:
    def __init__(self):
        self.serpapi_key = Config.SERPAPI_KEY
    
    def search_google(self, query: str, num_results: int = 3) -> List[Dict]:
        """Search Google using SerpAPI (optional)"""
        if not self.serpapi_key:
            return []
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results
            }
            
            response = requests.get(url, params=params)
            results = response.json()
            
            search_results = []
            for result in results.get("organic_results", []):
                search_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", "")
                })
            
            return search_results
        except Exception as e:
            print(f"Error in web search: {e}")
            return []
    
    def get_web_context(self, query: str) -> str:
        """Get web context for the query"""
        results = self.search_google(query)
        
        if not results:
            return ""
        
        context = "Here are some relevant web results:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['snippet']}\n"
            context += f"   Source: {result['link']}\n\n"
        
        return context