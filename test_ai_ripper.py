#!/usr/bin/env python3
"""
AI Ripper Tests
===============
Basic tests for AI Ripper functionality
"""

import unittest
import tempfile
import os
import json
from ai_ripper_core import AIRipper, EndpointConfig, ModelMetadata, RippingProgress


class TestAIRipperCore(unittest.TestCase):
    """Test core AI Ripper functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ripper = AIRipper()
        self.test_config = EndpointConfig(
            url="http://localhost:8000",
            timeout=30,
            scan_depth=3
        )
        
    def test_add_endpoint(self):
        """Test adding an endpoint"""
        self.ripper.add_endpoint("test", self.test_config)
        self.assertIn("test", self.ripper.endpoints)
        self.assertEqual(self.ripper.endpoints["test"].url, "http://localhost:8000")
        
    def test_remove_endpoint(self):
        """Test removing an endpoint"""
        self.ripper.add_endpoint("test", self.test_config)
        self.ripper.remove_endpoint("test")
        self.assertNotIn("test", self.ripper.endpoints)
        
    def test_progress_tracking(self):
        """Test progress tracking"""
        progress = RippingProgress(
            total_steps=10,
            current_step=5,
            current_task="Testing",
            status="running",
            start_time=0
        )
        
        self.assertEqual(progress.progress_percentage, 50.0)
        self.assertEqual(progress.current_task, "Testing")
        
    def test_metadata_creation(self):
        """Test model metadata creation"""
        metadata = ModelMetadata(
            name="test-model",
            endpoint_url="http://localhost:8000",
            model_type="llm",
            parameters={"test": "value"}
        )
        
        self.assertEqual(metadata.name, "test-model")
        self.assertEqual(metadata.model_type, "llm")
        self.assertIsNotNone(metadata.extraction_timestamp)
        
    def test_export_to_json(self):
        """Test JSON export"""
        # Create test metadata
        metadata = ModelMetadata(
            name="test-model",
            endpoint_url="http://localhost:8000",
            model_type="llm",
            parameters={"test": "value"}
        )
        
        self.ripper.extracted_models["test"] = metadata
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            success = self.ripper.export_to_json("test", temp_path)
            self.assertTrue(success)
            
            # Verify file contents
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['name'], "test-model")
                self.assertEqual(data['model_type'], "llm")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_export_to_python(self):
        """Test Python export"""
        # Create test metadata
        metadata = ModelMetadata(
            name="test-model",
            endpoint_url="http://localhost:8000",
            model_type="llm",
            parameters={"test": "value"}
        )
        
        self.ripper.extracted_models["test"] = metadata
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_path = f.name
        
        try:
            success = self.ripper.export_to_python("test", temp_path)
            self.assertTrue(success)
            
            # Verify file exists and has content
            with open(temp_path, 'r') as f:
                content = f.read()
                self.assertIn("MODEL_CONFIG", content)
                self.assertIn("test-model", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_compare_endpoints(self):
        """Test endpoint comparison"""
        # Create test metadata for multiple endpoints
        for i in range(3):
            metadata = ModelMetadata(
                name=f"model-{i}",
                endpoint_url=f"http://localhost:800{i}",
                model_type="llm",
                parameters={"test": i}
            )
            metadata.capabilities = ["chat", "completion"]
            self.ripper.extracted_models[f"endpoint-{i}"] = metadata
            self.ripper.response_times[f"endpoint-{i}"] = [0.1 * (i + 1)]
        
        # Compare endpoints
        comparison = self.ripper.compare_endpoints([f"endpoint-{i}" for i in range(3)])
        
        self.assertEqual(len(comparison['endpoints']), 3)
        self.assertIn('avg_response_time', comparison['metrics'])
        self.assertIn('capabilities', comparison['metrics'])
        
    def test_progress_callback(self):
        """Test progress callback"""
        callback_called = [False]
        received_progress = [None]
        
        def callback(progress):
            callback_called[0] = True
            received_progress[0] = progress
        
        self.ripper.set_progress_callback(callback)
        
        # Create progress and trigger update
        self.ripper.progress = RippingProgress(
            total_steps=10,
            current_step=0,
            current_task="Test",
            status="running",
            start_time=0
        )
        
        self.ripper._update_progress(5, "Testing progress")
        
        self.assertTrue(callback_called[0])
        self.assertIsNotNone(received_progress[0])
        self.assertEqual(received_progress[0].current_step, 5)


class TestEndpointConfig(unittest.TestCase):
    """Test EndpointConfig dataclass"""
    
    def test_config_creation(self):
        """Test creating endpoint config"""
        config = EndpointConfig(
            url="http://localhost:8000",
            api_key="test-key",
            timeout=60,
            max_retries=5,
            scan_depth=3
        )
        
        self.assertEqual(config.url, "http://localhost:8000")
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.scan_depth, 3)
        
    def test_config_defaults(self):
        """Test config default values"""
        config = EndpointConfig(url="http://localhost:8000")
        
        self.assertIsNone(config.api_key)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.scan_depth, 3)


class TestModelMetadata(unittest.TestCase):
    """Test ModelMetadata dataclass"""
    
    def test_metadata_creation(self):
        """Test creating model metadata"""
        metadata = ModelMetadata(
            name="test-model",
            endpoint_url="http://localhost:8000",
            model_type="llm",
            parameters={"param1": "value1"}
        )
        
        self.assertEqual(metadata.name, "test-model")
        self.assertIsNotNone(metadata.extraction_timestamp)
        self.assertEqual(metadata.capabilities, [])
        
    def test_metadata_with_capabilities(self):
        """Test metadata with capabilities"""
        metadata = ModelMetadata(
            name="test-model",
            endpoint_url="http://localhost:8000",
            model_type="llm",
            parameters={},
            capabilities=["chat", "completion"]
        )
        
        self.assertEqual(len(metadata.capabilities), 2)
        self.assertIn("chat", metadata.capabilities)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
