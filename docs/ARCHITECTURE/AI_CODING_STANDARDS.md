# AI Coding Standards & Prompt Engineering Guide
**Version**: 1.0.0
**Last Updated**: 2025-09-18
**Status**: Active

## Overview
This document defines coding standards, prompt engineering best practices, and AI persona configurations for the PayReady AI unified CLI system.

## 1. AI Coding Rules

### 1.1 Code Generation Standards

#### Python Code Rules
```yaml
language: python
version: "3.8+"
style:
  - Use type hints for all functions
  - Include docstrings (Google style)
  - Max line length: 120 characters
  - Use f-strings for formatting
  - Prefer pathlib over os.path
error_handling:
  - Never use bare except clauses
  - Always add timeout to external calls
  - Log errors with context
  - Graceful degradation preferred
security:
  - No hardcoded credentials
  - Use environment variables
  - Validate all inputs
  - Sanitize file paths
```

#### Bash Script Rules
```yaml
language: bash
shebang: "#!/usr/bin/env bash"
safety:
  - Always use: set -euo pipefail
  - Quote all variables: "${var}"
  - Check command existence before use
  - Add timeouts to network operations
style:
  - Use lowercase for variables
  - UPPERCASE for constants
  - Meaningful function names
  - Comment complex logic
```

### 1.2 Documentation Standards

All generated code must include:
- **Module/Script Header**: Purpose, author, date
- **Function Documentation**: Parameters, returns, examples
- **Inline Comments**: For complex logic only
- **TODO Format**: `# TODO(category): description`

### 1.3 Testing Requirements

Generated code should include:
- Unit test stubs
- Error case handling
- Example usage
- Performance considerations

## 2. Prompt Engineering Templates

### 2.1 Code Generation Prompts

#### Basic Template
```
Task: [SPECIFIC_TASK]
Language: [LANGUAGE]
Context: [PROJECT_CONTEXT]
Requirements:
- [REQ_1]
- [REQ_2]
Constraints:
- [CONSTRAINT_1]
- [CONSTRAINT_2]
Output: [EXPECTED_FORMAT]
```

#### Enhanced Template for Complex Tasks
```
Role: You are a senior [LANGUAGE] developer working on PayReady AI.
Context:
- Project: Payment processing automation system
- Current date: [DATE]
- Environment: [ENV_DETAILS]

Task: [DETAILED_TASK_DESCRIPTION]

Requirements:
1. Functional:
   - [FUNCTIONAL_REQ_1]
   - [FUNCTIONAL_REQ_2]
2. Non-functional:
   - Performance: [PERF_REQ]
   - Security: [SEC_REQ]
   - Scalability: [SCALE_REQ]

Constraints:
- Use existing libraries: [LIBRARIES]
- Follow project conventions in: [FILE_PATHS]
- Compatible with: [COMPATIBILITY]

Examples:
[PROVIDE_EXAMPLES]

Output Format:
- Complete, runnable code
- Include error handling
- Add comprehensive comments
- Provide usage examples
```

### 2.2 Code Review Prompts

```
Review this code for:
1. Security vulnerabilities
2. Performance bottlenecks
3. Error handling gaps
4. Code style violations
5. Missing documentation

Code:
[CODE_TO_REVIEW]

Provide:
- Severity rating (HIGH/MEDIUM/LOW)
- Specific line numbers
- Fix suggestions
- Improved code snippets
```

### 2.3 Refactoring Prompts

```
Refactor this code to:
- Improve readability
- Enhance performance
- Follow [PATTERN_NAME] pattern
- Add type hints
- Improve error handling

Original code:
[ORIGINAL_CODE]

Constraints:
- Maintain backward compatibility
- Keep same public API
- Add deprecation warnings if needed
```

## 3. AI Persona Configurations

### 3.1 Claude Persona (Code Analysis & Refactoring)

```json
{
  "name": "Claude Analyst",
  "role": "Senior Code Architect",
  "expertise": [
    "Code refactoring",
    "Architecture review",
    "Security analysis",
    "Performance optimization"
  ],
  "personality": {
    "style": "Thorough and methodical",
    "communication": "Technical but clear",
    "approach": "Best practices focused"
  },
  "context_awareness": {
    "project_type": "Payment processing",
    "tech_stack": ["Python", "FastAPI", "Redis"],
    "standards": ["PEP 8", "SOLID principles"]
  }
}
```

### 3.2 Codex Persona (Code Generation)

```json
{
  "name": "Codex Builder",
  "role": "Full-Stack Developer",
  "expertise": [
    "Rapid prototyping",
    "API development",
    "Algorithm implementation",
    "Integration coding"
  ],
  "personality": {
    "style": "Pragmatic and efficient",
    "communication": "Code-first with examples",
    "approach": "Results-oriented"
  },
  "output_preferences": {
    "include_tests": true,
    "add_examples": true,
    "error_handling": "comprehensive"
  }
}
```

### 3.3 Web Search Persona (Research & Current Info)

```json
{
  "name": "Web Researcher",
  "role": "Technical Research Analyst",
  "expertise": [
    "Current tech trends",
    "Library research",
    "Security advisories",
    "Best practices"
  ],
  "personality": {
    "style": "Factual and current",
    "communication": "Concise with sources",
    "approach": "Evidence-based"
  },
  "search_parameters": {
    "date_filter": "last_100_days",
    "sources": ["official_docs", "github", "stackoverflow"],
    "verification": "cross_reference"
  }
}
```

### 3.4 Agno Persona (Automation & Orchestration)

```json
{
  "name": "Agno Orchestrator",
  "role": "DevOps Automation Engineer",
  "expertise": [
    "CI/CD pipelines",
    "Deployment automation",
    "Workflow orchestration",
    "Infrastructure as code"
  ],
  "personality": {
    "style": "Systematic and reliable",
    "communication": "Process-focused",
    "approach": "Automation-first"
  },
  "automation_rules": {
    "idempotency": "required",
    "rollback": "always_possible",
    "logging": "verbose"
  }
}
```

## 4. Prompt Enhancement Strategies

### 4.1 Context Injection

Always include:
- Current date and timezone
- Project root path
- Active git branch
- Recent file modifications
- Environment variables

```python
def enhance_prompt(base_prompt: str) -> str:
    context = get_context_manager().get_current_context()
    return f"""
    {base_prompt}

    Context:
    - Date: {context['date']}
    - Project: {context['project_root']}
    - Branch: {context['git_status']['branch']}
    - Recent files: {', '.join(f['path'] for f in context['active_files'][:5])}
    """
```

### 4.2 Few-Shot Learning

Include examples from project:
```python
def add_examples(prompt: str, task_type: str) -> str:
    examples = load_project_examples(task_type)
    return f"{prompt}\n\nExamples from this project:\n{examples}"
```

### 4.3 Chain-of-Thought

For complex tasks:
```
Let's approach this step-by-step:
1. First, understand the requirements
2. Identify existing code patterns
3. Plan the implementation
4. Write the code
5. Add tests
6. Document usage
```

### 4.4 Self-Consistency

For critical code:
```
Generate 3 different implementations and choose the best based on:
- Performance
- Readability
- Maintainability
```

## 5. Router Intelligence Rules

### 5.1 Intent Classification

```python
INTENT_PATTERNS = {
    'generate': {
        'keywords': ['create', 'write', 'implement', 'build'],
        'tool': 'codex',
        'confidence_boost': 0.2
    },
    'analyze': {
        'keywords': ['review', 'analyze', 'refactor', 'optimize'],
        'tool': 'claude',
        'confidence_boost': 0.3
    },
    'research': {
        'keywords': ['search', 'find', 'latest', 'current'],
        'tool': 'web',
        'confidence_boost': 0.25
    },
    'automate': {
        'keywords': ['deploy', 'pipeline', 'automate', 'orchestrate'],
        'tool': 'agno',
        'confidence_boost': 0.2
    }
}
```

### 5.2 Confidence Scoring

```python
def calculate_confidence(query: str, tool: str) -> float:
    base_score = keyword_match_score(query, tool)
    context_score = context_relevance_score(query)
    history_score = user_preference_score(tool)

    return (base_score * 0.5 +
            context_score * 0.3 +
            history_score * 0.2)
```

### 5.3 Fallback Chain

```yaml
fallback_priority:
  claude:
    - codex  # If Claude unavailable
    - web    # For research tasks
  codex:
    - claude # For complex generation
    - agno   # For automation scripts
  web:
    - codex  # Generate from docs
  agno:
    - codex  # Generate automation code
```

## 6. Quality Assurance Rules

### 6.1 Pre-Generation Checks

Before generating code:
1. Verify API keys are configured
2. Check rate limits
3. Validate input length
4. Sanitize user input

### 6.2 Post-Generation Validation

After generating code:
1. Syntax validation
2. Security scan (no exposed secrets)
3. Style check (PEP 8 for Python)
4. Dependency verification

### 6.3 Continuous Improvement

```python
def track_quality_metrics():
    metrics = {
        'syntax_errors': 0,
        'security_issues': 0,
        'user_edits': 0,
        'regeneration_rate': 0
    }
    # Log metrics for analysis
    log_to_analytics(metrics)
```

## 7. Integration Guidelines

### 7.1 Tool Chaining

```python
# Example: Research → Generate → Review
async def complex_task_chain(requirement: str):
    # Step 1: Research current best practices
    research = await web_search(f"best practices {requirement} 2025")

    # Step 2: Generate implementation
    code = await codex_generate(f"{requirement}\nBased on: {research}")

    # Step 3: Review and optimize
    reviewed = await claude_review(code)

    return reviewed
```

### 7.2 Parallel Processing

```python
# Run multiple tools concurrently
async def parallel_analysis(code: str):
    tasks = [
        claude_security_check(code),
        codex_suggest_tests(code),
        web_check_dependencies(code)
    ]
    results = await asyncio.gather(*tasks)
    return combine_results(results)
```

## 8. Monitoring & Metrics

### 8.1 Track Success Rate

```python
METRICS = {
    'tool_usage': Counter(),
    'success_rate': defaultdict(float),
    'response_time': defaultdict(list),
    'user_satisfaction': defaultdict(int)
}
```

### 8.2 Adaptive Learning

```python
def adapt_routing_weights():
    """Adjust routing based on success metrics"""
    for tool in TOOLS:
        if METRICS['success_rate'][tool] < 0.7:
            adjust_confidence_threshold(tool, increase=0.1)
        if average(METRICS['response_time'][tool]) > 5000:
            add_cache_layer(tool)
```

## 9. Error Handling Standards

### 9.1 Graceful Degradation

```python
try:
    result = await primary_tool.execute(query)
except ToolUnavailable:
    result = await fallback_tool.execute(query)
except RateLimit:
    result = await cache.get_similar(query)
finally:
    log_execution(query, result)
```

### 9.2 User Communication

```python
ERROR_MESSAGES = {
    'rate_limit': "⏱️ Rate limit reached. Try again in {time}",
    'api_error': "🔧 Service temporarily unavailable. Using cache.",
    'timeout': "⏰ Request timed out. Trying alternative approach.",
    'invalid_input': "❌ Invalid input: {reason}"
}
```

## 10. Best Practices Checklist

### For Every AI Interaction:
- [ ] Include context (date, project, environment)
- [ ] Set appropriate timeout
- [ ] Handle errors gracefully
- [ ] Log for analytics
- [ ] Cache when possible
- [ ] Validate output
- [ ] Track metrics
- [ ] Update documentation

### For Code Generation:
- [ ] Include type hints
- [ ] Add error handling
- [ ] Write docstrings
- [ ] Generate tests
- [ ] Check security
- [ ] Validate syntax
- [ ] Format code
- [ ] Add examples

### For System Integration:
- [ ] Use environment variables
- [ ] Implement fallbacks
- [ ] Add monitoring
- [ ] Document API
- [ ] Version endpoints
- [ ] Rate limit protection
- [ ] Cache responses
- [ ] Audit logging

---

*This document defines the standards for AI-powered development in PayReady AI. Update as patterns emerge and tools evolve.*