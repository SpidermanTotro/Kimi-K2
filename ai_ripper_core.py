#!/usr/bin/env python3
"""
AI Ripper Core - Model Extraction and Analysis Engine
=====================================================
Core functionality for extracting, analyzing, and exporting AI models from endpoints.
"""

import json
import time
import requests
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import struct


@dataclass
class EndpointConfig:
    """Configuration for an AI endpoint"""
    url: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    scan_depth: int = 3


@dataclass
class ModelMetadata:
    """Metadata extracted from an AI model"""
    name: str
    endpoint_url: str
    model_type: str
    parameters: Dict[str, Any]
    architecture: Optional[str] = None
    vocabulary_size: Optional[int] = None
    context_length: Optional[int] = None
    capabilities: List[str] = None
    extraction_timestamp: str = None
    
    def __post_init__(self):
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now().isoformat()
        if self.capabilities is None:
            self.capabilities = []


@dataclass
class RippingProgress:
    """Progress tracking for ripping operation"""
    total_steps: int
    current_step: int
    current_task: str
    status: str  # 'running', 'completed', 'failed', 'paused'
    start_time: float
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage"""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds"""
        return time.time() - self.start_time


class AIRipper:
    """Core AI model ripper and analyzer"""
    
    def __init__(self):
        self.endpoints: Dict[str, EndpointConfig] = {}
        self.extracted_models: Dict[str, ModelMetadata] = {}
        self.progress: Optional[RippingProgress] = None
        self.progress_callback: Optional[Callable] = None
        self._stop_flag = threading.Event()
        self.response_times: Dict[str, List[float]] = {}
        
    def add_endpoint(self, name: str, config: EndpointConfig) -> None:
        """Add an endpoint to monitor"""
        self.endpoints[name] = config
        self.response_times[name] = []
        
    def remove_endpoint(self, name: str) -> None:
        """Remove an endpoint"""
        if name in self.endpoints:
            del self.endpoints[name]
        if name in self.response_times:
            del self.response_times[name]
            
    def set_progress_callback(self, callback: Callable) -> None:
        """Set callback for progress updates"""
        self.progress_callback = callback
        
    def _update_progress(self, step: int, task: str, status: str = 'running') -> None:
        """Update progress and notify callback"""
        if self.progress:
            self.progress.current_step = step
            self.progress.current_task = task
            self.progress.status = status
            
            if self.progress_callback:
                self.progress_callback(self.progress)
                
    def _add_error(self, error: str) -> None:
        """Add error to progress"""
        if self.progress:
            self.progress.errors.append(error)
            
    def _add_warning(self, warning: str) -> None:
        """Add warning to progress"""
        if self.progress:
            self.progress.warnings.append(warning)
    
    def probe_endpoint(self, config: EndpointConfig) -> Dict[str, Any]:
        """Probe an endpoint to gather basic information"""
        start_time = time.time()
        
        try:
            headers = {}
            if config.api_key:
                headers['Authorization'] = f'Bearer {config.api_key}'
            
            # Try common AI endpoint paths
            probe_paths = [
                '/v1/models',
                '/models',
                '/api/v1/models',
                '/',
            ]
            
            for path in probe_paths:
                try:
                    url = config.url.rstrip('/') + path
                    response = requests.get(
                        url,
                        headers=headers,
                        timeout=config.timeout
                    )
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'status_code': response.status_code,
                            'response_time': response_time,
                            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else {},
                            'path': path
                        }
                except requests.RequestException:
                    continue
            
            return {
                'success': False,
                'error': 'Could not connect to any known endpoint path',
                'response_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time': time.time() - start_time
            }
    
    def extract_model_info(self, endpoint_name: str, config: EndpointConfig) -> Optional[ModelMetadata]:
        """Extract model information from endpoint"""
        probe_result = self.probe_endpoint(config)
        
        if not probe_result['success']:
            self._add_error(f"Failed to probe {endpoint_name}: {probe_result.get('error')}")
            return None
        
        # Record response time
        self.response_times[endpoint_name].append(probe_result['response_time'])
        
        # Parse model information
        data = probe_result.get('data', {})
        
        # Extract model list if available
        models = data.get('data', []) if isinstance(data.get('data'), list) else []
        
        if models:
            # Use first model
            model_info = models[0]
            model_name = model_info.get('id', 'unknown')
        else:
            model_name = 'unknown'
        
        # Create metadata
        metadata = ModelMetadata(
            name=model_name,
            endpoint_url=config.url,
            model_type='llm',  # Default assumption
            parameters={
                'endpoint_type': probe_result.get('path', 'unknown'),
                'probe_data': data
            }
        )
        
        # Try to extract more details
        self._enrich_metadata(metadata, config)
        
        return metadata
    
    def _enrich_metadata(self, metadata: ModelMetadata, config: EndpointConfig) -> None:
        """Enrich metadata with additional probing"""
        try:
            headers = {}
            if config.api_key:
                headers['Authorization'] = f'Bearer {config.api_key}'
            
            # Try to get model capabilities via a test request
            test_url = config.url.rstrip('/') + '/v1/chat/completions'
            test_payload = {
                'model': metadata.name,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 5
            }
            
            try:
                response = requests.post(
                    test_url,
                    headers=headers,
                    json=test_payload,
                    timeout=config.timeout
                )
                
                if response.status_code == 200:
                    metadata.capabilities.append('chat_completion')
                    response_data = response.json()
                    
                    # Extract usage info if available
                    if 'usage' in response_data:
                        metadata.parameters['usage'] = response_data['usage']
                        
            except requests.RequestException:
                self._add_warning(f"Could not test chat completion for {metadata.name}")
                
        except Exception as e:
            self._add_warning(f"Error enriching metadata: {str(e)}")
    
    def rip_endpoint(self, endpoint_name: str, scan_depth: int = 3) -> bool:
        """Rip a single endpoint"""
        if endpoint_name not in self.endpoints:
            self._add_error(f"Endpoint {endpoint_name} not found")
            return False
        
        config = self.endpoints[endpoint_name]
        config.scan_depth = scan_depth
        
        self._update_progress(1, f"Probing endpoint: {endpoint_name}")
        
        metadata = self.extract_model_info(endpoint_name, config)
        
        if metadata:
            self.extracted_models[endpoint_name] = metadata
            self._update_progress(2, f"Extracted metadata for: {endpoint_name}")
            return True
        else:
            return False
    
    def rip_multiple_endpoints(self, endpoint_names: List[str], scan_depth: int = 3) -> Dict[str, bool]:
        """Rip multiple endpoints simultaneously"""
        total_steps = len(endpoint_names) * 3
        self.progress = RippingProgress(
            total_steps=total_steps,
            current_step=0,
            current_task="Starting multi-endpoint ripping",
            status='running',
            start_time=time.time()
        )
        
        results = {}
        
        for i, endpoint_name in enumerate(endpoint_names):
            if self._stop_flag.is_set():
                self._update_progress(self.progress.current_step, "Stopped by user", 'paused')
                break
            
            self._update_progress(i * 3 + 1, f"Processing endpoint {i+1}/{len(endpoint_names)}: {endpoint_name}")
            results[endpoint_name] = self.rip_endpoint(endpoint_name, scan_depth)
        
        self._update_progress(total_steps, "Completed", 'completed')
        
        return results
    
    def compare_endpoints(self, endpoint_names: List[str]) -> Dict[str, Any]:
        """Compare multiple endpoints"""
        comparison = {
            'endpoints': [],
            'metrics': {
                'avg_response_time': {},
                'capabilities': {},
                'model_types': {}
            }
        }
        
        for name in endpoint_names:
            if name in self.extracted_models:
                metadata = self.extracted_models[name]
                
                endpoint_data = {
                    'name': name,
                    'model_name': metadata.name,
                    'url': metadata.endpoint_url,
                    'capabilities': metadata.capabilities,
                    'architecture': metadata.architecture
                }
                
                comparison['endpoints'].append(endpoint_data)
                
                # Calculate metrics
                if name in self.response_times and self.response_times[name]:
                    comparison['metrics']['avg_response_time'][name] = sum(self.response_times[name]) / len(self.response_times[name])
                
                comparison['metrics']['capabilities'][name] = len(metadata.capabilities)
                comparison['metrics']['model_types'][name] = metadata.model_type
        
        return comparison
    
    def export_to_json(self, endpoint_name: str, filepath: str) -> bool:
        """Export model metadata to JSON"""
        if endpoint_name not in self.extracted_models:
            return False
        
        try:
            metadata = self.extracted_models[endpoint_name]
            data = asdict(metadata)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            self._add_error(f"Failed to export JSON: {str(e)}")
            return False
    
    def export_to_gguf(self, endpoint_name: str, filepath: str) -> bool:
        """Export model to GGUF format (placeholder for actual implementation)"""
        if endpoint_name not in self.extracted_models:
            return False
        
        try:
            metadata = self.extracted_models[endpoint_name]
            
            # This is a simplified GGUF format export
            # In a real implementation, this would involve actual model weights
            with open(filepath, 'wb') as f:
                # Write GGUF magic number
                f.write(b'GGUF')
                
                # Write version
                f.write(struct.pack('<I', 3))
                
                # Write metadata as key-value pairs
                metadata_json = json.dumps(asdict(metadata))
                f.write(struct.pack('<I', len(metadata_json)))
                f.write(metadata_json.encode('utf-8'))
            
            return True
        except Exception as e:
            self._add_error(f"Failed to export GGUF: {str(e)}")
            return False
    
    def export_to_onnx(self, endpoint_name: str, filepath: str) -> bool:
        """Export model to ONNX format (placeholder)"""
        if endpoint_name not in self.extracted_models:
            return False
        
        try:
            # This is a placeholder - real implementation would need actual model weights
            # and conversion to ONNX format
            self._add_warning("ONNX export is a placeholder - actual model weights not available from API endpoints")
            
            # Write a simple metadata file instead
            metadata = self.extracted_models[endpoint_name]
            with open(filepath + '.meta.json', 'w') as f:
                json.dump(asdict(metadata), f, indent=2)
            
            return True
        except Exception as e:
            self._add_error(f"Failed to export ONNX: {str(e)}")
            return False
    
    def export_to_python(self, endpoint_name: str, filepath: str) -> bool:
        """Export model configuration as Python code"""
        if endpoint_name not in self.extracted_models:
            return False
        
        try:
            metadata = self.extracted_models[endpoint_name]
            
            # Safely serialize all data using JSON to prevent code injection
            config_data = {
                "name": metadata.name,
                "endpoint_url": metadata.endpoint_url,
                "model_type": metadata.model_type,
                "architecture": metadata.architecture or 'unknown',
                "vocabulary_size": metadata.vocabulary_size,
                "context_length": metadata.context_length,
                "capabilities": metadata.capabilities,
                "parameters": metadata.parameters
            }
            
            # Use json.dumps for safe serialization
            config_json = json.dumps(config_data, indent=4)
            
            # Build Python code with safe JSON loading
            python_code = '''#!/usr/bin/env python3
"""
AI Model Configuration
Extracted from endpoint
Generated: {timestamp}
"""

import json

# Configuration data (safely serialized)
MODEL_CONFIG = {config_str}

def get_model_config():
    """Get the model configuration"""
    return MODEL_CONFIG

if __name__ == "__main__":
    config = get_model_config()
    print(f"Model: {{config['name']}}")
    print(f"Type: {{config['model_type']}}")
    print(f"Capabilities: {{', '.join(config['capabilities'])}}")
'''.format(timestamp=metadata.extraction_timestamp, config_str=config_json)
            
            with open(filepath, 'w') as f:
                f.write(python_code)
            
            return True
        except Exception as e:
            self._add_error(f"Failed to export Python: {str(e)}")
            return False
    
    def stop_ripping(self) -> None:
        """Stop the current ripping operation"""
        self._stop_flag.set()
    
    def reset(self) -> None:
        """Reset the ripper state"""
        self._stop_flag.clear()
        self.progress = None
        

def request_ethical_consent() -> bool:
    """Request ethical consent before ripping"""
    consent_text = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                    ETHICAL USAGE AGREEMENT                     ║
    ╠════════════════════════════════════════════════════════════════╣
    ║                                                                ║
    ║  This tool is designed for legitimate research and analysis   ║
    ║  purposes only. By proceeding, you agree to:                  ║
    ║                                                                ║
    ║  1. Only scan endpoints you own or have permission to access  ║
    ║  2. Respect API rate limits and terms of service              ║
    ║  3. Not use extracted data for malicious purposes             ║
    ║  4. Comply with all applicable laws and regulations           ║
    ║                                                                ║
    ║  Unauthorized access to computer systems may be illegal.      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(consent_text)
    return True  # In GUI, this will be an interactive dialog


if __name__ == "__main__":
    # Example usage
    ripper = AIRipper()
    
    # Add an example endpoint
    config = EndpointConfig(
        url="http://localhost:8000",
        timeout=30,
        scan_depth=3
    )
    
    ripper.add_endpoint("local_model", config)
    
    # Request consent
    if request_ethical_consent():
        print("\n✅ Starting AI model ripping...")
        
        # Rip the endpoint
        success = ripper.rip_endpoint("local_model")
        
        if success:
            print("✅ Successfully extracted model information")
            
            # Export to different formats
            ripper.export_to_json("local_model", "model_metadata.json")
            ripper.export_to_python("local_model", "model_config.py")
            
            print("📦 Exported model data to files")
        else:
            print("❌ Failed to extract model information")
