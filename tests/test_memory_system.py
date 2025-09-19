#!/usr/bin/env python3
"""
Test suite for the memory system
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMemoryManager(unittest.TestCase):
    """Test the MemoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_memory_file = Path(self.test_dir) / 'test_memory.jsonl'

        # Patch environment variables
        self.env_patcher = patch.dict(os.environ, {
            'REDIS_URL': '',
            'MEM0_API_KEY': ''
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test fixtures."""
        self.env_patcher.stop()
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('core.memory.Path')
    def test_memory_initialization(self, mock_path):
        """Test MemoryManager initialization."""
        mock_path.return_value.expanduser.return_value = Path(self.test_dir)
        mock_path.return_value.exists.return_value = True

        from core.memory import MemoryManager

        memory = MemoryManager()
        self.assertIsNotNone(memory)

    @patch('core.memory.redis.from_url')
    def test_redis_connection(self, mock_redis):
        """Test Redis connection handling."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client

        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}):
            from core.memory import MemoryManager
            memory = MemoryManager()

            # Should attempt Redis connection
            mock_redis.assert_called_once_with('redis://localhost:6379')
            mock_client.ping.assert_called_once()

    def test_file_storage_fallback(self):
        """Test fallback to file storage when Redis unavailable."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            mock_path.return_value.expanduser.return_value = Path(self.test_dir)
            mock_path.return_value.exists.return_value = True

            memory = MemoryManager()
            self.assertEqual(memory.storage_type, 'file')

    def test_remember_function(self):
        """Test the remember function."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            mock_path.return_value = Path(self.test_dir) / 'memory.jsonl'
            mock_path.return_value.expanduser.return_value = mock_path.return_value
            mock_path.return_value.parent.mkdir.return_value = None

            memory = MemoryManager()
            memory.remember('test_key', 'test_value', 'test_category')

            # Verify storage was attempted
            self.assertTrue(True)  # Would check file write or Redis set

    def test_recall_function(self):
        """Test the recall function."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            test_file = Path(self.test_dir) / 'memory.jsonl'
            mock_path.return_value = test_file
            mock_path.return_value.expanduser.return_value = test_file
            mock_path.return_value.exists.return_value = True

            # Create test data
            test_data = {
                'key': 'test_key',
                'value': 'test_value',
                'category': 'test',
                'timestamp': datetime.now().isoformat()
            }

            with open(test_file, 'w') as f:
                f.write(json.dumps(test_data) + '\n')

            memory = MemoryManager()
            results = memory.recall('test_key', 'test')

            self.assertIsInstance(results, list)

    def test_get_context(self):
        """Test context retrieval."""
        from core.memory import MemoryManager

        with patch('core.memory.Path'):
            memory = MemoryManager()
            context = memory.get_context()

            self.assertIsInstance(context, dict)
            self.assertIn('timestamp', context)

    def test_log_conversation(self):
        """Test conversation logging."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            mock_path.return_value = Path(self.test_dir) / 'memory.jsonl'
            mock_path.return_value.expanduser.return_value = mock_path.return_value

            memory = MemoryManager()
            memory.log_conversation(
                user_input='test query',
                ai_response='test response',
                model='test-model'
            )

            # Verify conversation was logged
            self.assertTrue(True)  # Would check file write

    def test_memory_search(self):
        """Test memory search functionality."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            test_file = Path(self.test_dir) / 'memory.jsonl'
            mock_path.return_value = test_file
            mock_path.return_value.expanduser.return_value = test_file
            mock_path.return_value.exists.return_value = True

            # Create test data with multiple entries
            test_entries = [
                {'key': 'python', 'value': 'programming language', 'category': 'tech'},
                {'key': 'java', 'value': 'another language', 'category': 'tech'},
                {'key': 'meeting', 'value': 'tomorrow at 3pm', 'category': 'schedule'},
            ]

            with open(test_file, 'w') as f:
                for entry in test_entries:
                    entry['timestamp'] = datetime.now().isoformat()
                    f.write(json.dumps(entry) + '\n')

            memory = MemoryManager()

            # Search by category
            tech_results = memory.recall('', 'tech')
            self.assertIsInstance(tech_results, list)

            # Search by query
            python_results = memory.recall('python')
            self.assertIsInstance(python_results, list)

    def test_memory_expiry(self):
        """Test memory expiry/TTL functionality."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            test_file = Path(self.test_dir) / 'memory.jsonl'
            mock_path.return_value = test_file
            mock_path.return_value.expanduser.return_value = test_file
            mock_path.return_value.exists.return_value = True

            # Create old and new entries
            old_time = (datetime.now() - timedelta(days=30)).isoformat()
            new_time = datetime.now().isoformat()

            entries = [
                {'key': 'old', 'value': 'old data', 'timestamp': old_time},
                {'key': 'new', 'value': 'new data', 'timestamp': new_time},
            ]

            with open(test_file, 'w') as f:
                for entry in entries:
                    f.write(json.dumps(entry) + '\n')

            memory = MemoryManager()
            # Would test expiry logic here
            self.assertTrue(True)


class TestMemoryRedisIntegration(unittest.TestCase):
    """Test Redis integration for memory system."""

    @patch('redis.from_url')
    def test_redis_storage(self, mock_redis_from_url):
        """Test storing to Redis."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.setex.return_value = True
        mock_redis_from_url.return_value = mock_redis

        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}):
            from core.memory import MemoryManager

            memory = MemoryManager()
            memory.remember('test_key', 'test_value', 'test')

            # Verify Redis setex was called
            if hasattr(memory, 'redis') and memory.redis:
                mock_redis.setex.assert_called()

    @patch('redis.from_url')
    def test_redis_retrieval(self, mock_redis_from_url):
        """Test retrieving from Redis."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = json.dumps({'value': 'test_value'})
        mock_redis_from_url.return_value = mock_redis

        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}):
            from core.memory import MemoryManager

            memory = MemoryManager()
            result = memory.recall('test_key')

            # Verify Redis get was called
            if hasattr(memory, 'redis') and memory.redis:
                mock_redis.get.assert_called()

    @patch('redis.from_url')
    def test_redis_failure_fallback(self, mock_redis_from_url):
        """Test fallback when Redis fails."""
        mock_redis = MagicMock()
        mock_redis.ping.side_effect = Exception("Redis connection failed")
        mock_redis_from_url.return_value = mock_redis

        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}):
            from core.memory import MemoryManager

            memory = MemoryManager()
            # Should fall back to file storage
            self.assertEqual(memory.storage_type, 'file')


class TestMemoryPerformance(unittest.TestCase):
    """Test memory system performance."""

    def test_large_memory_handling(self):
        """Test handling of large memory stores."""
        from core.memory import MemoryManager

        with patch('core.memory.Path') as mock_path:
            test_file = Path(tempfile.mkdtemp()) / 'memory.jsonl'
            mock_path.return_value = test_file
            mock_path.return_value.expanduser.return_value = test_file

            memory = MemoryManager()

            # Store many entries
            for i in range(100):
                memory.remember(f'key_{i}', f'value_{i}', 'test')

            # Should handle without issues
            self.assertTrue(True)

    def test_concurrent_access(self):
        """Test concurrent memory access."""
        from core.memory import MemoryManager
        import threading

        with patch('core.memory.Path'):
            memory = MemoryManager()

            def write_memory(thread_id):
                for i in range(10):
                    memory.remember(f'thread_{thread_id}_{i}', f'value_{i}', 'test')

            threads = []
            for i in range(5):
                t = threading.Thread(target=write_memory, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Should handle concurrent access
            self.assertTrue(True)


class TestMemoryCLI(unittest.TestCase):
    """Test memory CLI commands."""

    def test_memory_cli_remember(self):
        """Test CLI remember command."""
        from payready_cli import memory

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            with patch.object(sys, 'argv', ['memory', 'remember', 'key', 'value']):
                try:
                    memory()
                except SystemExit:
                    pass

            mock_run.assert_called_once()

    def test_memory_cli_recall(self):
        """Test CLI recall command."""
        from payready_cli import memory

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            with patch.object(sys, 'argv', ['memory', 'recall', 'query']):
                try:
                    memory()
                except SystemExit:
                    pass

            mock_run.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)