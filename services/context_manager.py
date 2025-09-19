"""
Complete Context Manager with active file tracking and git integration
Date: September 18, 2025
"""

import os
import json
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Try Redis, fall back to file-based storage
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextManager:
    def __init__(self, project_root: str = '/Users/lynnmusil/payready-ai'):
        self.project_root = Path(project_root)
        self.context_key = "ai:shared:context"
        self.fallback_file = Path('/tmp/ai_context.json')

        # Initialize storage
        if HAS_REDIS and os.getenv('REDIS_URL'):
            try:
                self.redis = redis.from_url(os.getenv('REDIS_URL'))
                self.redis.ping()  # Test connection
                self.storage_type = 'redis'
                logger.info("Using Redis for context storage")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to file storage")
                self.redis = None
                self.storage_type = 'file'
        else:
            self.redis = None
            self.storage_type = 'file'
            logger.info("Using file-based context storage")

    def get_current_context(self) -> Dict[str, Any]:
        """Get current shared context with live date and project state."""
        now = datetime.now()

        base_context = {
            'timestamp': now.isoformat(),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'cutoff_date': (now - timedelta(days=100)).strftime('%Y-%m-%d'),
            'project_root': str(self.project_root),
            'active_files': self.get_active_files(hours=24),
            'recent_changes': self.get_recent_changes(limit=10),
            'git_status': self.get_git_status(),
            'environment': self.get_environment_info()
        }

        # Merge with cached context
        cached = self._load_cached_context()
        if cached:
            # Preserve certain cached values
            for key in ['last_action', 'session_id', 'user_preferences']:
                if key in cached:
                    base_context[key] = cached[key]

        return base_context

    def get_active_files(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get files modified in the last N hours - OPTIMIZED."""
        # Check cache first
        cache_key = f"active_files_{hours}h"
        cached = self._get_cache(cache_key, max_age_minutes=10)
        if cached:
            return cached

        active_files = []
        try:
            since_time = datetime.now() - timedelta(hours=hours)

            # Use git diff to get only changed files (much faster)
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                changed_files = result.stdout.strip().split('\n')

                for file_path in changed_files[:10]:  # Limit to 10 files
                    if not file_path or not file_path.strip():
                        continue

                    full_path = self.project_root / file_path
                    if full_path.exists():
                        stat = full_path.stat()
                        mod_time = datetime.fromtimestamp(stat.st_mtime)

                        active_files.append({
                            'path': file_path,
                            'modified': mod_time.isoformat(),
                            'size': stat.st_size,
                            'extension': full_path.suffix
                        })

            # Cache the result
            self._set_cache(cache_key, active_files)

        except Exception as e:
            logger.error(f"Error getting active files: {e}")

        return active_files[:10]  # Return top 10 most recent

    def get_recent_changes(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent git commits and changes."""
        changes = []

        try:
            # Get recent commits
            result = subprocess.run(
                ['git', 'log', '--oneline', f'-{limit}', '--format=%H|%s|%an|%ar'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            changes.append({
                                'commit': parts[0][:8],
                                'message': parts[1][:50],
                                'author': parts[2],
                                'time': parts[3]
                            })

            # Add uncommitted changes summary
            diff_result = subprocess.run(
                ['git', 'diff', '--stat'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if diff_result.returncode == 0 and diff_result.stdout.strip():
                lines = diff_result.stdout.strip().split('\n')
                if lines:
                    changes.insert(0, {
                        'commit': 'uncommitted',
                        'message': f"Uncommitted changes in {len(lines)-1} files",
                        'author': 'current',
                        'time': 'now'
                    })

        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")

        return changes

    def get_git_status(self) -> Dict[str, Any]:
        """Get current git status summary - CACHED."""
        # Cache git status for 30 seconds
        cached = self._get_cache("git_status", max_age_minutes=0.5)
        if cached:
            return cached

        status = {
            'branch': 'unknown',
            'clean': True,
            'modified': 0,
            'untracked': 0,
            'staged': 0
        }

        try:
            # Get current branch and status in one call
            result = subprocess.run(
                ['git', 'status', '--porcelain', '-b'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')

                # First line is branch info
                if lines and lines[0].startswith('##'):
                    branch_line = lines[0][3:]  # Remove '## '
                    status['branch'] = branch_line.split()[0] if branch_line else 'main'

                # Process file status lines
                for line in lines[1:]:
                    if not line.strip():
                        continue

                    status['clean'] = False
                    if line.startswith('??'):
                        status['untracked'] += 1
                    elif line[0] in 'AM':
                        status['staged'] += 1
                    elif line[1] == 'M':
                        status['modified'] += 1

            # Cache the result
            self._set_cache("git_status", status)

        except Exception as e:
            logger.error(f"Error getting git status: {e}")

        return status

    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            'python_version': subprocess.run(
                ['python3', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            ).stdout.strip(),
            'platform': os.uname().sysname if hasattr(os, 'uname') else 'unknown',
            'user': os.environ.get('USER', 'unknown'),
            'shell': os.environ.get('SHELL', 'unknown'),
            'venv': bool(os.environ.get('VIRTUAL_ENV')),
            'storage_type': self.storage_type
        }

    def update_context(self, updates: Dict[str, Any]) -> bool:
        """Update shared context with new information."""
        try:
            current = self.get_current_context()
            current.update(updates)
            current['last_updated'] = datetime.now().isoformat()

            return self._save_context(current)
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            return False

    def _save_context(self, context: Dict[str, Any]) -> bool:
        """Save context to storage."""
        try:
            context_json = json.dumps(context, default=str)

            if self.redis:
                self.redis.setex(
                    self.context_key,
                    3600,  # 1 hour TTL
                    context_json
                )
            else:
                # File-based fallback
                self.fallback_file.write_text(context_json)

            return True
        except Exception as e:
            logger.error(f"Error saving context: {e}")
            return False

    def _load_cached_context(self) -> Optional[Dict[str, Any]]:
        """Load cached context from storage."""
        try:
            if self.redis:
                cached = self.redis.get(self.context_key)
                if cached:
                    return json.loads(cached)
            elif self.fallback_file.exists():
                cached_text = self.fallback_file.read_text()
                return json.loads(cached_text)
        except Exception as e:
            logger.error(f"Error loading cached context: {e}")

        return None

    def _get_cache(self, key: str, max_age_minutes: float = 10) -> Optional[Any]:
        """Get cached value if it's fresh enough."""
        try:
            cache_key = f"{self.context_key}:cache:{key}"

            if self.redis:
                cached_data = self.redis.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    return data.get('value')
            else:
                cache_file = Path(f"/tmp/ai_cache_{key}.json")
                if cache_file.exists():
                    cached_data = json.loads(cache_file.read_text())
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    age_minutes = (datetime.now() - cache_time).total_seconds() / 60

                    if age_minutes < max_age_minutes:
                        return cached_data.get('value')
        except Exception as e:
            logger.error(f"Error getting cache for {key}: {e}")

        return None

    def _set_cache(self, key: str, value: Any, ttl_minutes: float = 10) -> bool:
        """Set cached value with TTL."""
        try:
            cache_key = f"{self.context_key}:cache:{key}"
            cache_data = {
                'value': value,
                'timestamp': datetime.now().isoformat()
            }

            if self.redis:
                self.redis.setex(
                    cache_key,
                    int(ttl_minutes * 60),
                    json.dumps(cache_data, default=str)
                )
            else:
                cache_file = Path(f"/tmp/ai_cache_{key}.json")
                cache_file.write_text(json.dumps(cache_data, default=str))

            return True
        except Exception as e:
            logger.error(f"Error setting cache for {key}: {e}")
            return False

    def clear_context(self) -> bool:
        """Clear all cached context."""
        try:
            if self.redis:
                self.redis.delete(self.context_key)
            if self.fallback_file.exists():
                self.fallback_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error clearing context: {e}")
            return False

    def get_summary(self) -> str:
        """Get a human-readable summary of the current context."""
        ctx = self.get_current_context()
        git = ctx.get('git_status', {})

        summary = [
            f"📅 Date: {ctx['date']} {ctx['time']}",
            f"🌍 Cutoff: {ctx['cutoff_date']} (100 days ago)",
            f"🔧 Project: {self.project_root.name}",
            f"🌲 Branch: {git.get('branch', 'unknown')}",
            f"📝 Status: {'Clean' if git.get('clean') else f'{git.get("modified", 0)} modified, {git.get("untracked", 0)} untracked'}",
            f"📂 Active files: {len(ctx.get('active_files', []))} recently modified",
            f"📊 Recent commits: {len(ctx.get('recent_changes', []))}",
            f"💾 Storage: {self.storage_type}"
        ]

        return '\n'.join(summary)


# Singleton instance
_context_manager = None

def get_context_manager(project_root: str = None) -> ContextManager:
    """Get or create the singleton ContextManager."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager(project_root or '/Users/lynnmusil/payready-ai')
    return _context_manager


if __name__ == "__main__":
    # Test the context manager
    cm = get_context_manager()
    print("Context Manager Test")
    print("=" * 50)
    print(cm.get_summary())
    print("\nFull Context:")
    print(json.dumps(cm.get_current_context(), indent=2, default=str))