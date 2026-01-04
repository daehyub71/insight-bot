import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import InsightBotGraph

def main():
    load_dotenv()
    
    print("🚀 Starting InsightBot...")
    graph = InsightBotGraph().build_graph()
    
    # Initialize with empty state
    initial_state = {"articles": []}
    
    result = graph.invoke(initial_state)
    
    print("\n🎉 Workflow Completed!")
    final_articles = result.get("articles", [])
    print(f"Final Count: {len(final_articles)}")
    
    # Temporary output for verification
    for idx, article in enumerate(final_articles, 1):
        print(f"\n[{idx}] {article.title} (Score: {article.relevance_score})")
        print(f"   Summary: {article.summary[:100]}...")
        print(f"   Insight: {article.insight}")

if __name__ == "__main__":
    main()
