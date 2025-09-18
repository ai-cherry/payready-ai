#!/bin/bash
# Test all web search APIs with CURRENT 2025 data
# Today: September 18, 2025

set -euo pipefail

echo "🌐 Testing Web Search APIs (2025 ONLY)"
echo "======================================="
echo "Date: September 18, 2025"
echo "Cutoff: June 2025 (last 100 days)"
echo ""

# Export all API keys
export PERPLEXITY_API_KEY="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"
export BRAVE_API_KEY="BSApz0194z7SG6DplmVozl7ttFOi0Eo"
export EXA_API_KEY="fdf07f38-34ad-44a9-ab6f-74ca2ca90fd4"
export VENICE_AI_API_KEY="7hcepmOBBqSqi_kZICeC3QJdqPqtGhsKUxrTIyLx02"
export ZENROWS_API_KEY="dba8152e8ded37bbd3aa5e464c8269b93225b648"
export APIFY_API_TOKEN="apify_api_GlLw4ETpvZgjmOVLYx5XDL4d91IhFJ0gr9pi"

echo "1. Testing Perplexity (Real-time web search)"
echo "--------------------------------------------"
./bin/codex-current "Latest AI news September 2025" | head -3
echo ""

echo "2. Testing Brave Search (Privacy-focused search)"
echo "------------------------------------------------"
curl -s -X GET \
  "https://api.search.brave.com/res/v1/web/search?q=GPT-5%20features%202025&freshness=month&count=2" \
  -H "X-Subscription-Token: $BRAVE_API_KEY" | jq '.web.results[:2] | .[].title' 2>/dev/null || echo "Brave API error"
echo ""

echo "3. Testing Exa AI (Semantic neural search)"
echo "------------------------------------------"
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest machine learning breakthroughs 2025",
    "num_results": 2,
    "start_published_date": "2025-06-01",
    "type": "neural"
  }' | jq '.results[:2] | .[].title' 2>/dev/null || echo "Exa API error"
echo ""

echo "4. Testing Venice AI (Uncensored models)"
echo "----------------------------------------"
curl -s -X POST https://api.venice.ai/v1/chat/completions \
  -H "Authorization: Bearer $VENICE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dolphin-mistral",
    "messages": [{"role": "user", "content": "What happened in AI in September 2025? Be brief."}],
    "max_tokens": 100
  }' | jq -r '.choices[0].message.content' 2>/dev/null | head -2 || echo "Venice API error"
echo ""

echo "5. Testing ZenRows (Web scraping)"
echo "---------------------------------"
curl -s "https://api.zenrows.com/v1/?url=https%3A%2F%2Fnews.ycombinator.com&apikey=$ZENROWS_API_KEY" \
  | grep -o '<title>[^<]*</title>' | head -1 || echo "ZenRows API error"
echo ""

echo "6. Testing Unified Router"
echo "-------------------------"
.venv/bin/python ./bin/web-router.py "Current state of AI in September 2025" 2>&1 | head -5
echo ""

echo "✅ Web API Tests Complete"
echo ""
echo "Summary:"
echo "- Perplexity: Real-time search with citations"
echo "- Brave: Privacy-focused, date-filtered results"
echo "- Exa: Semantic search with date ranges"
echo "- Venice: Uncensored AI responses"
echo "- ZenRows: Web scraping capabilities"
echo "- Router: Intelligent API selection"