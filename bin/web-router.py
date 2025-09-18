#!/usr/bin/env python3
"""
Unified Web Router - CURRENT 2025 ONLY
Today: September 18, 2025
Only searches for information from June 2025 onwards (last 100 days)
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

# CRITICAL: Today's date
TODAY = datetime(2025, 9, 18)
CUTOFF_DATE = TODAY - timedelta(days=100)  # June 10, 2025

class WebRouter2025:
    """Routes queries to appropriate APIs with STRICT 2025 filtering."""

    def __init__(self):
        self.apis = {
            'perplexity': os.getenv('PERPLEXITY_API_KEY'),
            'brave': os.getenv('BRAVE_API_KEY'),
            'exa': os.getenv('EXA_API_KEY'),
            'venice': os.getenv('VENICE_AI_API_KEY'),
            'zenrows': os.getenv('ZENROWS_API_KEY'),
            'apify': os.getenv('APIFY_API_TOKEN'),
        }

        # Date context for ALL queries
        self.date_context = (
            f"Current date: {TODAY.strftime('%B %d, %Y')}. "
            f"ONLY use information from {CUTOFF_DATE.strftime('%B %Y')} onwards. "
            "Exclude ALL content from 2024 or earlier."
        )

    def search_perplexity(self, query: str) -> Dict[str, Any]:
        """Search with Perplexity - enforcing 2025 only."""
        if not self.apis['perplexity']:
            return {'error': 'Perplexity API key not set'}

        dated_query = f"{query} {self.date_context}"

        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={'Authorization': f"Bearer {self.apis['perplexity']}"},
            json={
                'model': 'sonar',
                'messages': [
                    {
                        'role': 'system',
                        'content': f"Today is {TODAY.strftime('%B %d, %Y')}. "
                                   "You MUST only provide information from 2025. "
                                   "If information is from 2024 or earlier, say 'OUTDATED' and stop."
                    },
                    {'role': 'user', 'content': dated_query}
                ]
            }
        )

        if response.ok:
            result = response.json()
            content = result['choices'][0]['message']['content']

            # Check if response mentions old data
            if any(year in content.lower() for year in ['2024', '2023', '2022']):
                print("⚠️ WARNING: Response contains outdated information!", file=sys.stderr)

            return {'source': 'perplexity', 'content': content}

        return {'error': f"Perplexity error: {response.text}"}

    def search_brave(self, query: str) -> Dict[str, Any]:
        """Search with Brave - filtering for 2025 results only."""
        if not self.apis['brave']:
            return {'error': 'Brave API key not set'}

        # Add date qualifiers to query
        dated_query = f"{query} 2025 -2024 -2023"

        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers={'X-Subscription-Token': self.apis['brave']},
            params={
                'q': dated_query,
                'freshness': 'month',  # Only recent results
                'count': 10
            }
        )

        if response.ok:
            results = response.json()

            # Filter results to 2025 only
            filtered_results = []
            for result in results.get('web', {}).get('results', []):
                # Check if result is from 2025
                age = result.get('age', '')
                if '2025' in age or 'days ago' in age or 'hours ago' in age:
                    filtered_results.append({
                        'title': result.get('title'),
                        'url': result.get('url'),
                        'snippet': result.get('description'),
                        'date': age
                    })

            if not filtered_results:
                return {'error': 'No 2025 results found'}

            return {'source': 'brave', 'results': filtered_results[:5]}

        return {'error': f"Brave error: {response.text}"}

    def search_exa(self, query: str) -> Dict[str, Any]:
        """Search with Exa AI - semantic search with date filtering."""
        if not self.apis['exa']:
            return {'error': 'Exa API key not set'}

        response = requests.post(
            'https://api.exa.ai/search',
            headers={'x-api-key': self.apis['exa']},
            json={
                'query': query,
                'num_results': 10,
                'start_published_date': CUTOFF_DATE.strftime('%Y-%m-%d'),
                'end_published_date': TODAY.strftime('%Y-%m-%d'),
                'use_autoprompt': True,
                'type': 'neural'
            }
        )

        if response.ok:
            results = response.json()
            return {
                'source': 'exa',
                'results': results.get('results', [])[:5]
            }

        return {'error': f"Exa error: {response.text}"}

    def route_query(self, query: str, preferred_api: str = None) -> Dict[str, Any]:
        """Route query to appropriate API with 2025 filtering."""

        print(f"📅 Searching with 2025-only filter (since {CUTOFF_DATE.strftime('%B %Y')})...", file=sys.stderr)

        # Determine best API based on query type
        if preferred_api:
            api_order = [preferred_api]
        elif 'latest' in query.lower() or 'current' in query.lower() or '2025' in query.lower():
            api_order = ['perplexity', 'brave', 'exa']
        elif 'similar' in query.lower() or 'like' in query.lower():
            api_order = ['exa', 'perplexity']
        elif 'uncensored' in query.lower() or 'unfiltered' in query.lower():
            api_order = ['venice']
        else:
            api_order = ['perplexity', 'brave', 'exa']

        # Try APIs in order
        for api in api_order:
            if api == 'perplexity' and self.apis['perplexity']:
                result = self.search_perplexity(query)
                if 'error' not in result:
                    return result
            elif api == 'brave' and self.apis['brave']:
                result = self.search_brave(query)
                if 'error' not in result:
                    return result
            elif api == 'exa' and self.apis['exa']:
                result = self.search_exa(query)
                if 'error' not in result:
                    return result

        return {'error': 'No APIs available or all failed'}

    def verify_date(self, content: str) -> bool:
        """Verify content is from 2025."""
        # Check for old year mentions
        old_years = ['2024', '2023', '2022', '2021', '2020']
        for year in old_years:
            if year in content:
                return False

        # Check for 2025 mention
        return '2025' in content or 'this year' in content.lower()


def main():
    if len(sys.argv) < 2:
        print("Usage: web-router.py <query> [--api=<api>]")
        print("APIs: perplexity, brave, exa, venice")
        print(f"Note: Only searches from {CUTOFF_DATE.strftime('%B %Y')} onwards")
        sys.exit(1)

    query = sys.argv[1]
    preferred_api = None

    # Check for API preference
    for arg in sys.argv[2:]:
        if arg.startswith('--api='):
            preferred_api = arg.split('=')[1]

    router = WebRouter2025()
    result = router.route_query(query, preferred_api)

    if 'error' in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if result['source'] == 'perplexity':
        print(result['content'])
    else:
        print(f"Source: {result['source']}")
        print(json.dumps(result.get('results', []), indent=2))

    # Verify date
    content_str = json.dumps(result)
    if not router.verify_date(content_str):
        print("\n⚠️ WARNING: Response may contain outdated pre-2025 information!", file=sys.stderr)


if __name__ == "__main__":
    main()