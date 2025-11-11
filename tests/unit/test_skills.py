"""
Unit tests for Skills module
"""

import pytest
from unittest.mock import Mock, patch
from kimi_k2.skills import (
    AdvancedReasoning,
    TextToImageGenerator,
    ContextualChat,
    SpecializedPipeline
)


class TestAdvancedReasoning:
    """Test suite for AdvancedReasoning."""
    
    @patch('kimi_k2.skills.reasoning.KimiClient')
    def test_chain_of_thought(self, mock_client_class):
        """Test chain-of-thought reasoning."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Step 1: ...\nStep 2: ...\nAnswer: 42"
        mock_client_class.return_value = mock_client
        
        reasoning = AdvancedReasoning()
        result = reasoning.chain_of_thought("Test problem", domain="math")
        
        assert result["problem"] == "Test problem"
        assert result["domain"] == "math"
        assert result["type"] == "chain_of_thought"
        assert "reasoning" in result
    
    @patch('kimi_k2.skills.reasoning.KimiClient')
    def test_decompose_problem(self, mock_client_class):
        """Test problem decomposition."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Sub-problem 1: ...\nSub-problem 2: ..."
        mock_client_class.return_value = mock_client
        
        reasoning = AdvancedReasoning()
        result = reasoning.decompose_problem("Complex problem")
        
        assert result["original_problem"] == "Complex problem"
        assert result["type"] == "problem_decomposition"
        assert "decomposition" in result
    
    @patch('kimi_k2.skills.reasoning.KimiClient')
    def test_multi_hop_reasoning(self, mock_client_class):
        """Test multi-hop reasoning."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Using contexts 1 and 2: ..."
        mock_client_class.return_value = mock_client
        
        reasoning = AdvancedReasoning()
        result = reasoning.multi_hop_reasoning(
            "Question?",
            ["Context 1", "Context 2", "Context 3"]
        )
        
        assert result["question"] == "Question?"
        assert result["num_contexts"] == 3
        assert result["type"] == "multi_hop_reasoning"


class TestTextToImageGenerator:
    """Test suite for TextToImageGenerator."""
    
    def test_initialization(self):
        """Test generator initialization."""
        gen = TextToImageGenerator(backend="dalle", api_key="test_key")
        
        assert gen.backend == "dalle"
        assert gen.api_key == "test_key"
    
    def test_unsupported_backend(self):
        """Test unsupported backend."""
        gen = TextToImageGenerator(backend="unsupported")
        result = gen.generate("test prompt")
        
        assert result["status"] == "error"
        assert "Unsupported backend" in result["message"]
    
    def test_stable_diffusion_placeholder(self):
        """Test stable diffusion placeholder."""
        gen = TextToImageGenerator(backend="stable-diffusion")
        result = gen.generate("test prompt")
        
        assert result["backend"] == "stable-diffusion"
        assert "placeholder" in result["status"]
    
    @patch('kimi_k2.client.KimiClient')
    def test_enhance_prompt(self, mock_client_class):
        """Test prompt enhancement."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Enhanced: detailed prompt with style"
        
        gen = TextToImageGenerator()
        enhanced = gen.enhance_prompt("simple prompt", mock_client)
        
        assert "Enhanced" in enhanced


class TestContextualChat:
    """Test suite for ContextualChat."""
    
    @patch('kimi_k2.skills.contextual_chat.KimiClient')
    def test_chat_with_context(self, mock_client_class):
        """Test contextual chat."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Response"
        mock_client_class.return_value = mock_client
        
        chat = ContextualChat()
        result = chat.chat_with_context(
            "Hello",
            context={"user_info": "Test user"}
        )
        
        assert result["response"] == "Response"
        assert result["context_used"] is True
        assert result["history_length"] == 2  # User + assistant
    
    @patch('kimi_k2.skills.contextual_chat.KimiClient')
    def test_clear_context(self, mock_client_class):
        """Test clearing context."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Response"
        mock_client_class.return_value = mock_client
        
        chat = ContextualChat()
        chat.chat_with_context("Message 1")
        chat.chat_with_context("Message 2")
        
        assert len(chat.context_window) == 4  # 2 exchanges
        
        chat.clear_context()
        
        assert len(chat.context_window) == 0
        assert chat.current_topic is None
    
    @patch('kimi_k2.skills.contextual_chat.KimiClient')
    def test_get_context_stats(self, mock_client_class):
        """Test context statistics."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Response"
        mock_client_class.return_value = mock_client
        
        chat = ContextualChat()
        chat.chat_with_context("Message 1")
        chat.chat_with_context("Message 2")
        
        stats = chat.get_context_stats()
        
        assert stats["message_count"] == 4
        assert stats["user_messages"] == 2
        assert stats["assistant_messages"] == 2


class TestSpecializedPipeline:
    """Test suite for SpecializedPipeline."""
    
    @patch('kimi_k2.skills.specialized_pipelines.KimiClient')
    def test_healthcare_pipeline(self, mock_client_class):
        """Test healthcare pipeline."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Medical analysis"
        mock_client_class.return_value = mock_client
        
        pipeline = SpecializedPipeline("healthcare")
        result = pipeline.healthcare_analysis(["symptom1", "symptom2"])
        
        assert result["domain"] == "healthcare"
        assert "response" in result
    
    @patch('kimi_k2.skills.specialized_pipelines.KimiClient')
    def test_education_pipeline(self, mock_client_class):
        """Test education pipeline."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Tutorial response"
        mock_client_class.return_value = mock_client
        
        pipeline = SpecializedPipeline("education")
        result = pipeline.education_tutor(
            "math",
            "algebra",
            "high",
            "How to solve equations?"
        )
        
        assert result["domain"] == "education"
        assert "response" in result
    
    @patch('kimi_k2.skills.specialized_pipelines.KimiClient')
    def test_wrong_domain_method(self, mock_client_class):
        """Test using wrong domain method."""
        mock_client_class.return_value = Mock()
        
        pipeline = SpecializedPipeline("legal")
        result = pipeline.healthcare_analysis(["symptom"])
        
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
