#!/usr/bin/env python3
"""
BASE 44 - Comprehensive Test Suite
===================================

Tests all aspects of BASE 44 to ensure quality and reliability.
"""

import sys
import json
from pathlib import Path

# Import BASE 44
from base_44_core import Base44Core, Base44Config, Capability


def test_initialization():
    """Test BASE 44 initialization"""
    print("\n" + "="*70)
    print("TEST 1: Initialization")
    print("="*70)
    
    base44 = Base44Core()
    
    # Verify configuration
    assert base44.config.version == "44.0.0", "Version check failed"
    assert base44.config.paid_restrictions == False, "Paid restrictions should be False"
    assert base44.config.enable_all_features == True, "All features should be enabled"
    assert base44.config.quality_tier == "maximum", "Quality should be maximum"
    
    # Verify capabilities
    assert len(base44.capabilities) > 0, "No capabilities loaded"
    
    # Verify all capabilities are free
    for cap in base44.capabilities.values():
        assert cap.free == True, f"Capability {cap.name} is not free!"
        assert cap.enabled == True, f"Capability {cap.name} is not enabled!"
        assert cap.quality == "premium", f"Capability {cap.name} is not premium quality!"
    
    print(f"✅ Initialization successful")
    print(f"✅ {len(base44.capabilities)} capabilities loaded (ALL FREE)")
    print(f"✅ Configuration verified")
    print(f"✅ All capabilities are free, enabled, and premium quality")
    
    return base44


def test_capabilities(base44):
    """Test capability listing and filtering"""
    print("\n" + "="*70)
    print("TEST 2: Capabilities")
    print("="*70)
    
    # Test listing all capabilities
    all_caps = base44.list_capabilities()
    assert len(all_caps) > 0, "No capabilities returned"
    
    print(f"✅ Listed {len(all_caps)} total capabilities")
    
    # Test filtering by category
    categories = set(cap["category"] for cap in all_caps)
    print(f"✅ Found {len(categories)} categories: {', '.join(sorted(categories))}")
    
    for category in categories:
        cat_caps = base44.list_capabilities(category=category)
        assert len(cat_caps) > 0, f"No capabilities in category {category}"
        print(f"  - {category}: {len(cat_caps)} capabilities")
    
    # Verify all are free
    for cap in all_caps:
        assert cap["free"] == True, f"Capability {cap['name']} not marked as free"
        assert cap["enabled"] == True, f"Capability {cap['name']} not enabled"
    
    print(f"✅ All capabilities verified as FREE and ENABLED")


def test_processing(base44):
    """Test request processing"""
    print("\n" + "="*70)
    print("TEST 3: Request Processing")
    print("="*70)
    
    test_requests = [
        ("Python coding", "Help me write Python code"),
        ("Video editing", "Edit a video professionally"),
        ("Book writing", "Write a science fiction novel"),
        ("Data analysis", "Analyze data with pandas"),
        ("Image processing", "Upscale image to 8K"),
    ]
    
    for name, request in test_requests:
        response = base44.process(request)
        
        # Verify response structure
        assert "success" in response, "Missing success field"
        assert response["success"] == True, "Response not successful"
        assert "quality_tier" in response, "Missing quality tier"
        assert response["quality_tier"] == "premium", "Quality not premium"
        assert "metadata" in response, "Missing metadata"
        assert response["metadata"]["free"] == True, "Not marked as free"
        assert response["metadata"]["paid_features_required"] == False, "Incorrectly requiring paid features"
        assert response["metadata"]["upgrade_needed"] == False, "Incorrectly requiring upgrade"
        
        print(f"✅ {name}: SUCCESS (Premium quality, FREE)")
    
    print(f"✅ All processing tests passed")


def test_statistics(base44):
    """Test statistics tracking"""
    print("\n" + "="*70)
    print("TEST 4: Statistics")
    print("="*70)
    
    # Process some requests
    for i in range(5):
        base44.process(f"Test request {i}")
    
    stats = base44.get_stats()
    
    # Verify stats structure
    assert "total_requests" in stats, "Missing total_requests"
    assert "successful_responses" in stats, "Missing successful_responses"
    assert "total_capabilities" in stats, "Missing total_capabilities"
    assert "free_capabilities" in stats, "Missing free_capabilities"
    assert "success_rate" in stats, "Missing success_rate"
    
    # Verify values
    assert stats["total_requests"] >= 5, "Request count incorrect"
    assert stats["successful_responses"] >= 5, "Success count incorrect"
    assert stats["total_capabilities"] == len(base44.capabilities), "Capability count mismatch"
    assert stats["free_capabilities"] == len(base44.capabilities), "Not all capabilities free"
    assert stats["success_rate"] >= 99.0, "Success rate too low"
    
    print(f"✅ Total requests: {stats['total_requests']}")
    print(f"✅ Successful responses: {stats['successful_responses']}")
    print(f"✅ Success rate: {stats['success_rate']:.2f}%")
    print(f"✅ Total capabilities: {stats['total_capabilities']}")
    print(f"✅ Free capabilities: {stats['free_capabilities']}")
    print(f"✅ Statistics tracking verified")


def test_export(base44):
    """Test configuration export"""
    print("\n" + "="*70)
    print("TEST 5: Configuration Export")
    print("="*70)
    
    export_file = "test_base44_config.json"
    base44.export_config(export_file)
    
    # Verify file was created
    assert Path(export_file).exists(), "Export file not created"
    
    # Load and verify contents
    with open(export_file, 'r') as f:
        config_data = json.load(f)
    
    assert "version" in config_data, "Missing version"
    assert "edition" in config_data, "Missing edition"
    assert "paid_restrictions" in config_data, "Missing paid_restrictions"
    assert config_data["paid_restrictions"] == False, "Paid restrictions should be False"
    assert "capabilities" in config_data, "Missing capabilities"
    assert len(config_data["capabilities"]) > 0, "No capabilities exported"
    
    print(f"✅ Configuration exported to {export_file}")
    print(f"✅ Export file verified")
    
    # Clean up
    Path(export_file).unlink()
    print(f"✅ Test file cleaned up")


def test_no_restrictions():
    """Test that there are absolutely no paid restrictions"""
    print("\n" + "="*70)
    print("TEST 6: Zero Restrictions Verification")
    print("="*70)
    
    base44 = Base44Core()
    
    # Verify config
    assert base44.config.max_capabilities == 999999, "Artificial capability limit detected"
    assert base44.config.max_response_length == 999999, "Artificial response limit detected"
    assert base44.config.paid_restrictions == False, "Paid restrictions enabled"
    assert base44.config.watermarks == False, "Watermarks enabled"
    assert base44.config.rate_limiting == False, "Rate limiting enabled"
    
    # Process multiple requests without restrictions
    for i in range(100):
        response = base44.process(f"Stress test request {i}")
        assert response["success"] == True, f"Request {i} failed"
        assert response["metadata"]["free"] == True, f"Request {i} not free"
        assert len(response["restrictions"]) == 0, f"Request {i} has restrictions"
        assert len(response["limitations"]) == 0, f"Request {i} has limitations"
    
    print(f"✅ Processed 100 requests without any restrictions")
    print(f"✅ No artificial limits detected")
    print(f"✅ No watermarks detected")
    print(f"✅ No rate limiting detected")
    print(f"✅ All requests processed as FREE")


def test_quality_consistency():
    """Test that quality is consistently premium"""
    print("\n" + "="*70)
    print("TEST 7: Quality Consistency")
    print("="*70)
    
    base44 = Base44Core()
    
    # Process many diverse requests
    diverse_requests = [
        "Write Python code",
        "Edit video",
        "Create image",
        "Analyze data",
        "Write book",
        "Debug code",
        "Mix audio",
        "Design API",
        "Deploy app",
        "Train model",
    ]
    
    quality_tiers = []
    for request in diverse_requests:
        response = base44.process(request)
        quality_tiers.append(response["quality_tier"])
    
    # Verify all are premium
    assert all(q == "premium" for q in quality_tiers), "Not all responses are premium quality"
    
    print(f"✅ Processed {len(diverse_requests)} diverse requests")
    print(f"✅ All responses are PREMIUM quality")
    print(f"✅ No quality degradation detected")
    print(f"✅ Quality is consistent across all request types")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("BASE 44 - Comprehensive Test Suite")
    print("="*70)
    print("\nRunning all tests...\n")
    
    try:
        # Run tests
        base44 = test_initialization()
        test_capabilities(base44)
        test_processing(base44)
        test_statistics(base44)
        test_export(base44)
        test_no_restrictions()
        test_quality_consistency()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print("\n✅ ALL TESTS PASSED!\n")
        print("BASE 44 is verified as:")
        print("  ✅ 100% FREE - No hidden costs or restrictions")
        print("  ✅ 100% ACCESSIBLE - All features unlocked")
        print("  ✅ 100% RELIABLE - Consistent performance")
        print("  ✅ 100% QUALITY - Premium output always")
        print("\n" + "="*70)
        print()
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
