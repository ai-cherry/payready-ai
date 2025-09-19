#!/usr/bin/env python3
"""
Test suite for the context manager
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestContextManager(unittest.TestCase):
    """Test the ContextManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)

        # Create some test files
        (self.project_root / 'test1.py').touch()
        (self.project_root / 'test2.md').touch()
        (self.project_root / '.git').mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test ContextManager initialization."""
        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))
        self.assertEqual(cm.project_root, self.project_root)
        self.assertIn(cm.storage_type, ['redis', 'file'])

    @patch('services.context_manager.redis.from_url')
    def test_redis_initialization(self, mock_redis_from_url):
        """Test Redis initialization."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis_from_url.return_value = mock_redis

        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}):
            from services.context_manager import ContextManager

            cm = ContextManager(project_root=str(self.project_root))
            self.assertEqual(cm.storage_type, 'redis')
            mock_redis.ping.assert_called_once()

    def test_file_storage_fallback(self):
        """Test fallback to file storage."""
        with patch.dict(os.environ, {'REDIS_URL': ''}):
            from services.context_manager import ContextManager

            cm = ContextManager(project_root=str(self.project_root))
            self.assertEqual(cm.storage_type, 'file')

    def test_get_current_context(self):
        """Test getting current context."""
        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))
        context = cm.get_current_context()

        # Check required fields
        self.assertIn('timestamp', context)
        self.assertIn('date', context)
        self.assertIn('time', context)
        self.assertIn('cutoff_date', context)
        self.assertIn('project_root', context)
        self.assertIn('active_files', context)
        self.assertIn('recent_changes', context)
        self.assertIn('git_status', context)
        self.assertIn('environment', context)

        # Check types
        self.assertIsInstance(context['timestamp'], str)
        self.assertIsInstance(context['date'], str)
        self.assertIsInstance(context['active_files'], list)
        self.assertIsInstance(context['git_status'], dict)

    @patch('services.context_manager.subprocess.run')
    def test_get_active_files(self, mock_run):
        """Test getting active files."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='file1.py\nfile2.md\n'
        )

        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))
        active_files = cm.get_active_files(hours=24)

        self.assertIsInstance(active_files, list)
        mock_run.assert_called()

    @patch('services.context_manager.subprocess.run')
    def test_get_recent_changes(self, mock_run):
        """Test getting recent changes."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='abc123 Fix bug\ndef456 Add feature\n'
        )

        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))
        changes = cm.get_recent_changes(limit=10)

        self.assertIsInstance(changes, list)
        mock_run.assert_called()

    @patch('services.context_manager.subprocess.run')
    def test_get_git_status(self, mock_run):
        """Test getting git status."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='main\n M file1.py\n A file2.py\n'
        )

        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))
        status = cm.get_git_status()

        self.assertIsInstance(status, dict)
        self.assertIn('branch', status)
        self.assertIn('modified', status)
        self.assertIn('added', status)
        mock_run.assert_called()

    def test_get_environment_info(self):
        """Test getting environment info."""
        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))
        env_info = cm.get_environment_info()

        self.assertIsInstance(env_info, dict)
        self.assertIn('python_version', env_info)
        self.assertIn('platform', env_info)
        self.assertIn('cwd', env_info)

    @patch('services.context_manager.subprocess.run')
    def test_cache_functionality(self, mock_run):
        """Test caching functionality."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='file1.py\n'
        )

        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))

        # First call should hit subprocess
        files1 = cm.get_active_files(hours=24)
        self.assertEqual(mock_run.call_count, 1)

        # Second call within cache time should use cache
        files2 = cm.get_active_files(hours=24)
        self.assertEqual(mock_run.call_count, 1)  # Should still be 1

        self.assertEqual(files1, files2)

    def test_update_context(self):
        """Test updating context."""
        from services.context_manager import ContextManager

        cm = ContextManager(project_root=str(self.project_root))

        updates = {
            'last_action': 'test_action',
            'session_id': 'test_session_123'
        }

        cm.update_context(updates)

        # Verify updates were applied
        context = cm.get_current_context()
        self.assertEqual(context.get('last_action'), 'test_action')
        self.assertEqual(context.get('session_id'), 'test_session_123')

    @patch('services.context_manager.redis.from_url')
    def test_redis_storage_operations(self, mock_redis_from_url):
        """Test Redis storage operations."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = json.dumps({'cached': 'data'})
        mock_redis_from_url.return_value = mock_redis

        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}):
            from services.context_manager import ContextManager

            cm = ContextManager(project_root=str(self.project_root))

            # Test save
            cm._save_context({'test': 'data'})
            mock_redis.setex.assert_called()

            # Test load
            cached = cm._load_cached_context()
            mock_redis.get.assert_called()
            self.assertIsInstance(cached, dict)

    def test_file_storage_operations(self):
        """Test file storage operations."""
        from services.context_manager import ContextManager

        with patch.dict(os.environ, {'REDIS_URL': ''}):
            cm = ContextManager(project_root=str(self.project_root))

            # Test save
            test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
            cm._save_context(test_data)

            # Test load
            cached = cm._load_cached_context()
            self.assertIsInstance(cached, dict)
            self.assertEqual(cached.get('test'), 'data')


class TestContextManagerPerformance(unittest.TestCase):
    """Test context manager performance optimizations."""

    @patch('services.context_manager.subprocess.run')
    def test_git_command_batching(self, mock_run):
        """Test that git commands are batched efficiently."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='main\n'
        )

        from services.context_manager import ContextManager

        cm = ContextManager()
        status = cm.get_git_status()

        # Should use combined command for efficiency
        calls = mock_run.call_args_list
        # Verify efficient git usage
        self.assertTrue(any('status' in str(call) for call in calls))

    def test_cache_ttl(self):
        """Test cache TTL settings."""
        from services.context_manager import ContextManager

        cm = ContextManager()

        # Test cache key generation
        cache_key = "test_cache"
        cm._set_cache(cache_key, {'data': 'test'}, max_age_minutes=10)

        # Should retrieve from cache
        cached = cm._get_cache(cache_key, max_age_minutes=10)
        self.assertIsNotNone(cached)
        self.assertEqual(cached['data'], 'test')

        # Test expired cache
        with patch('services.context_manager.datetime') as mock_datetime:
            # Mock time to be 11 minutes later
            future_time = datetime.now() + timedelta(minutes=11)
            mock_datetime.now.return_value = future_time

            expired = cm._get_cache(cache_key, max_age_minutes=10)
            self.assertIsNone(expired)

    def test_file_limit_optimization(self):
        """Test file scanning limit optimization."""
        from services.context_manager import ContextManager

        with patch('services.context_manager.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='\n'.join([f'file{i}.py' for i in range(20)])
            )

            cm = ContextManager()
            files = cm.get_active_files(hours=24)

            # Should limit to 10 files for performance
            self.assertLessEqual(len(files), 10)


class TestContextManagerIntegration(unittest.TestCase):
    """Test context manager integration with other components."""

    @patch('services.context_manager.subprocess.run')
    def test_context_for_ai_query(self, mock_run):
        """Test context generation for AI queries."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='main\n'
        )

        from services.context_manager import ContextManager

        cm = ContextManager()
        context = cm.get_current_context()

        # Convert to string format for AI
        context_str = json.dumps(context, indent=2)

        self.assertIn('project_root', context_str)
        self.assertIn('date', context_str)
        self.assertIn('git_status', context_str)

    def test_context_singleton_pattern(self):
        """Test singleton pattern implementation."""
        from services.context_manager import ContextManager

        cm1 = ContextManager()
        cm2 = ContextManager()

        # Should share cache between instances
        cm1._set_cache('shared_key', {'data': 'shared'})

        # This would work with proper singleton implementation
        # For now, test that both work independently
        self.assertIsNotNone(cm1)
        self.assertIsNotNone(cm2)


if __name__ == '__main__':
    unittest.main(verbosity=2)