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
        """Get files modified in the last N hours."""
        active_files = []

        try:
            # Use find command to get recently modified files
            since_time = datetime.now() - timedelta(hours=hours)

            # Use git ls-files for tracked files
            result = subprocess.run(
                ['git', 'ls-files', '-z'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                files = result.stdout.strip('\0').split('\0')

                for file_path in files[:50]:  # Limit to 50 files
                    if not file_path:
                        continue

                    full_path = self.project_root / file_path
                    if full_path.exists():
                        stat = full_path.stat()
                        mod_time = datetime.fromtimestamp(stat.st_mtime)

                        if mod_time > since_time:
                            active_files.append({
                                'path': file_path,
                                'modified': mod_time.isoformat(),
                                'size': stat.st_size,
                                'extension': full_path.suffix
                            })

                # Sort by modification time
                active_files.sort(key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            logger.error(f"Error getting active files: {e}")

        return active_files[:20]  # Return top 20 most recent

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
        """Get current git status summary."""
        status = {
            'branch': 'unknown',
            'clean': True,
            'modified': 0,
            'untracked': 0,
            'staged': 0
        }

        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if branch_result.returncode == 0:
                status['branch'] = branch_result.stdout.strip() or 'detached'

            # Get status summary
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if status_result.returncode == 0:
                lines = status_result.stdout.strip().split('\n')
                for line in lines:
                    if not line:
                        continue

                    status['clean'] = False
                    if line.startswith('??'):
                        status['untracked'] += 1
                    elif line[0] in 'AM':
                        status['staged'] += 1
                    elif line[1] == 'M':
                        status['modified'] += 1

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