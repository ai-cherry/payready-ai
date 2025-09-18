#!/usr/bin/env python3
"""
Enhanced AI Router with weighted intent detection and fallback logic
Date: September 18, 2025
"""

import sys
import os
import subprocess
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Any
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ai-router.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

class EnhancedAIRouter:
    def __init__(self):
        self.load_date_context()
        self.project_root = Path('/Users/lynnmusil/payready-ai')

        # Enhanced capabilities with weighted keywords and patterns
        self.capabilities = {
            'claude': {
                'primary_triggers': {
                    'refactor': 10, 'analyze': 10, 'review': 10,
                    'understand': 8, 'explain': 8, 'debug': 9,
                    'architecture': 9, 'audit': 9, 'optimize': 7
                },
                'patterns': [
                    r'\b(code\s+review|analyze\s+this|explain\s+how|debug\s+why)\b',
                    r'\b(refactor|restructure|improve)\s+\w+\s+(module|class|function)\b'
                ],
                'command': 'claude-code',
                'fallback_command': './bin/codex',
                'strengths': 'deep codebase understanding, refactoring, analysis'
            },
            'codex': {
                'primary_triggers': {
                    'write': 10, 'create': 10, 'generate': 10,
                    'implement': 9, 'code': 8, 'build': 8,
                    'function': 9, 'endpoint': 9, 'api': 8
                },
                'patterns': [
                    r'\b(write|create|generate)\s+a?\s*\w*\s*(function|class|api|endpoint)\b',
                    r'\b(implement|build|develop)\s+\w+\s*(feature|service)\b'
                ],
                'command': f'{self.project_root}/bin/codex',
                'fallback_command': None,
                'strengths': 'code generation, implementation, syntax'
            },
            'web': {
                'primary_triggers': {
                    'search': 10, 'latest': 10, 'current': 9,
                    'find': 8, 'web': 9, 'news': 9,
                    'september': 8, '2025': 8, 'recent': 9
                },
                'patterns': [
                    r'\b(search|find|get)\s+(latest|current|recent)\b',
                    r'\b(what\'s|what is|show me)\s+new\b',
                    r'\b(september|august|july)\s+2025\b'
                ],
                'command': f'{self.project_root}/bin/codex-current',
                'fallback_command': f'{self.project_root}/bin/codex-web-2025',
                'strengths': 'web search, current information (2025 only)'
            },
            'agno': {
                'primary_triggers': {
                    'automate': 10, 'orchestrate': 10, 'deploy': 10,
                    'pipeline': 9, 'workflow': 9, 'agent': 8,
                    'schedule': 8, 'batch': 8, 'coordinate': 9
                },
                'patterns': [
                    r'\b(automate|orchestrate)\s+\w+\s+(workflow|pipeline)\b',
                    r'\b(deploy|release|ship)\s+to\s+(production|staging)\b'
                ],
                'command': 'agno',
                'fallback_command': f'{self.project_root}/bin/codex',
                'strengths': 'automation, multi-step workflows, deployment'
            }
        }

        # Ambiguous query handling
        self.ambiguous_keywords = {
            'optimize': ['claude', 'codex'],  # Could be refactoring or performance code
            'fix': ['claude', 'codex'],        # Could be debugging or writing fix
            'update': ['codex', 'web'],       # Could be code update or finding updates
            'test': ['codex', 'agno'],        # Could be writing tests or running them
        }

    def load_date_context(self):
        """Load live date context with cross-platform support."""
        now = datetime.now()
        self.context = {
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S %Z'),
            'timezone': 'PDT',
            'cutoff_days': 100,
            'cutoff_date': (now - timedelta(days=100)).strftime('%Y-%m-%d'),
            'timestamp': int(now.timestamp()),
            'day_of_week': now.strftime('%A'),
            'week_number': now.strftime('%V')
        }
        logging.info(f"Context loaded: {self.context['date']}")

    def calculate_intent_score(self, query: str, tool_config: Dict) -> float:
        """Calculate weighted score for tool matching."""
        query_lower = query.lower()
        score = 0.0

        # Check weighted triggers
        for keyword, weight in tool_config['primary_triggers'].items():
            if keyword in query_lower:
                score += weight
                logging.debug(f"Keyword '{keyword}' matched, score += {weight}")

        # Check regex patterns (bonus points for pattern matches)
        for pattern in tool_config['patterns']:
            if re.search(pattern, query_lower):
                score += 15  # Pattern matches are strong indicators
                logging.debug(f"Pattern '{pattern}' matched, score += 15")

        return score

    def route_request(self, query: str, debug: bool = False) -> Tuple[str, str, float]:
        """
        Enhanced routing with confidence scoring.
        Returns: (tool, processed_query, confidence)
        """
        query_lower = query.lower()

        # Check for explicit tool request
        explicit_tools = {
            'claude:': 'claude',
            'codex:': 'codex',
            'web:': 'web',
            'search:': 'web',
            'agno:': 'agno',
            'agent:': 'agno'
        }

        for prefix, tool in explicit_tools.items():
            if query_lower.startswith(prefix):
                logging.info(f"Explicit routing to {tool}")
                return tool, query[len(prefix):].strip(), 1.0

        # Calculate scores for each tool
        scores = {}
        for tool, config in self.capabilities.items():
            scores[tool] = self.calculate_intent_score(query, config)

        # Find best match
        best_tool = max(scores, key=scores.get)
        best_score = scores[best_tool]

        # Calculate confidence (normalized to 0-1)
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0

        # Check for ambiguous queries
        if confidence < 0.4:  # Low confidence threshold
            # Check ambiguous keywords
            for keyword, tools in self.ambiguous_keywords.items():
                if keyword in query_lower:
                    # Ask user for clarification
                    if not debug:
                        print(f"🤔 Ambiguous query detected. Did you mean:", file=sys.stderr)
                        for i, t in enumerate(tools, 1):
                            print(f"  {i}. {t}: {self.capabilities[t]['strengths']}", file=sys.stderr)
                        print(f"  Defaulting to {tools[0]}...", file=sys.stderr)
                    best_tool = tools[0]
                    confidence = 0.5
                    break

        if debug:
            print(f"Debug - Scores: {json.dumps(scores, indent=2)}", file=sys.stderr)
            print(f"Debug - Selected: {best_tool} (confidence: {confidence:.2%})", file=sys.stderr)

        logging.info(f"Routed to {best_tool} with confidence {confidence:.2%}")
        return best_tool, query, confidence

    def add_date_context(self, query: str, tool: str) -> str:
        """Add appropriate date context based on tool."""
        if tool == 'web':
            # For web searches, emphasize current date and cutoff
            return (f"{query} "
                   f"(current as of {self.context['date']}, "
                   f"only results from {self.context['cutoff_date']} onwards, "
                   f"exclude pre-2025 information)")
        else:
            # For other tools, add subtle context
            return f"{query} (context: today is {self.context['date']})"

    def execute_with_fallback(self, tool: str, query: str, confidence: float) -> str:
        """Execute tool with fallback handling."""
        contextualized_query = self.add_date_context(query, tool)
        config = self.capabilities[tool]

        # Try primary command
        cmd = None
        if config['command']:
            # Check if command exists
            if tool in ['claude', 'agno']:
                check_result = subprocess.run(['which', config['command']], capture_output=True)
                if check_result.returncode == 0:
                    if tool == 'claude':
                        cmd = [config['command'], 'chat', contextualized_query]
                    elif tool == 'agno':
                        cmd = [config['command'], 'execute', '--query', contextualized_query]
                else:
                    logging.warning(f"{config['command']} not found, using fallback")
            else:
                # For local scripts
                cmd_path = Path(config['command'])
                if cmd_path.exists():
                    if tool == 'codex':
                        cmd = [str(cmd_path), 'gpt-5-mini', contextualized_query]
                    elif tool == 'web':
                        cmd = [str(cmd_path), query]  # Already has date filtering

        # Use fallback if primary failed
        if not cmd and config['fallback_command']:
            logging.info(f"Using fallback command for {tool}")
            fallback_path = Path(config['fallback_command'])
            if fallback_path.exists():
                cmd = [str(fallback_path), 'gpt-5-mini', contextualized_query]
            else:
                return f"Error: No available command for {tool}"

        if not cmd:
            return f"Error: Tool {tool} not available and no fallback configured"

        # Execute with timeout and error handling
        try:
            env = os.environ.copy()
            env.update({
                'DATE_CONTEXT': self.context['date'],
                'TIME_CONTEXT': self.context['time'],
                'CUTOFF_DATE': self.context['cutoff_date'],
                'AI_CONFIDENCE': str(confidence)
            })

            logging.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                cwd=str(self.project_root),
                timeout=30  # 30 second timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                logging.error(f"Command failed: {error_msg}")

                # Try to provide helpful error message
                if "API" in error_msg:
                    return f"API Error: {error_msg}\n💡 Check your API keys in ~/.config/payready/env.llm"
                elif "not found" in error_msg:
                    return f"Command Error: {error_msg}\n💡 Try: {config['fallback_command']}"
                else:
                    return f"Error: {error_msg}"

            return result.stdout

        except subprocess.TimeoutExpired:
            logging.error("Command timed out after 30 seconds")
            return "Error: Command timed out. Try a simpler query or check your connection."
        except FileNotFoundError:
            logging.error(f"Command not found: {cmd[0]}")
            return f"Error: Command not found: {cmd[0]}"
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return f"Error executing {tool}: {e}"

def main():
    # Parse arguments
    debug = '--debug' in sys.argv
    if debug:
        sys.argv.remove('--debug')
        logging.getLogger().setLevel(logging.DEBUG)

    if len(sys.argv) < 2 or '--help' in sys.argv:
        print("🤖 Enhanced AI Router (v2.0)")
        print("=" * 50)
        print("\nUsage: ai-router <query> [--debug]")
        print("\nCapabilities:")
        print("  • Code analysis (refactor, review, debug, explain)")
        print("  • Code generation (write, create, implement, build)")
        print("  • Web search (search, latest, current, news)")
        print("  • Automation (orchestrate, deploy, pipeline)")
        print("\nExamples:")
        print('  ai-router "refactor the auth module"')
        print('  ai-router "search latest FastAPI features"')
        print('  ai-router "create REST endpoint for users"')
        print('  ai-router --debug "optimize this workflow"')
        print("\nExplicit routing:")
        print('  ai-router "claude: analyze architecture"')
        print('  ai-router "web: Python 3.13 news"')
        print("\nDate Context:")
        router = EnhancedAIRouter()
        print(f"  Today: {router.context['date']} ({router.context['day_of_week']})")
        print(f"  Cutoff: {router.context['cutoff_date']} (100 days ago)")
        print(f"  Week: {router.context['week_number']}")
        sys.exit(0)

    query = ' '.join(arg for arg in sys.argv[1:] if not arg.startswith('--'))

    # Initialize router and process query
    router = EnhancedAIRouter()
    tool, processed_query, confidence = router.route_request(query, debug)

    # Display routing info
    print(f"🤖 Using {tool} ({router.capabilities[tool]['strengths']})", file=sys.stderr)
    print(f"📊 Confidence: {confidence:.0%}", file=sys.stderr)
    print(f"📅 Context: {router.context['date']} | Cutoff: {router.context['cutoff_date']}", file=sys.stderr)

    # Execute with fallback
    result = router.execute_with_fallback(tool, processed_query, confidence)
    print(result)

if __name__ == "__main__":
    main()