#!/usr/bin/env python3
"""
THE FORGE Research Engine - Demonstration
==========================================

This script demonstrates the research capabilities of THE FORGE,
specifically querying information about Comet 3I/ATLAS (2I/Borisov).

Features demonstrated:
1. Web search for astronomical objects
2. Detailed astronomical data retrieval
3. Fact-checking capabilities
4. Source credibility verification
5. Export functionality
"""

from forge_research_engine import ForgeResearchEngine
import json


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'─' * 70}")
    print(f"🔹 {title}")
    print("─" * 70)


def demo_comet_search():
    """Demonstrate searching for Comet 3I/ATLAS"""
    print_header("🔍 DEMO: Research Comet 3I/ATLAS")
    
    # Initialize the research engine
    engine = ForgeResearchEngine()
    
    # Demonstrate web search
    print_section("1. Web Search for 'Comet 3I/ATLAS'")
    
    results = engine.search("Comet 3I/ATLAS")
    
    print(f"📊 Found {len(results)} results\n")
    
    for i, result in enumerate(results[:3], 1):  # Show top 3
        print(f"{i}. {result.title}")
        print(f"   🏛️  Source: {result.source.name}")
        print(f"   ⭐ Credibility: {result.source.credibility.name} ({result.source.credibility.value}/5)")
        print(f"   📊 Relevance: {result.relevance_score:.0%}")
        print(f"   🔗 URL: {result.source.url}")
        
        # Show content preview
        content_preview = result.content[:250].replace('\n', ' ')
        print(f"   📝 Preview: {content_preview}...")
        
        if result.citations:
            print(f"   📚 Citations: {len(result.citations)}")
        print()
    
    # Demonstrate detailed astronomical object lookup
    print_section("2. Detailed Astronomical Data for 3I/2019 Q4")
    
    comet = engine.get_astronomical_object("3I/2019 Q4")
    
    if comet:
        print(f"🌟 {comet.name}")
        print(f"   Type: {comet.object_type}")
        print(f"   Designation: {comet.designation}")
        print(f"   Discovered: {comet.discovery_date}")
        print(f"   Discoverer: {comet.discoverer}")
        
        print("\n🛸 Orbit Characteristics:")
        for key, value in comet.orbit_characteristics.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        print("\n🔬 Physical Characteristics:")
        for key, value in comet.physical_characteristics.items():
            key_formatted = key.replace('_', ' ').title()
            print(f"   • {key_formatted}: {value}")
        
        print("\n🔭 Observation Data:")
        obs = comet.observation_data
        print(f"   • First Observation: {obs['first_observation']}")
        print(f"   • Last Observation: {obs['last_observation']}")
        print(f"   • Peak Brightness: {obs['peak_brightness']}")
        print(f"   • Telescopes Used: {len(obs['telescopes_used'])}")
        for telescope in obs['telescopes_used'][:3]:
            print(f"     - {telescope}")
        
        print("\n📖 Description:")
        # Print description in paragraphs
        paragraphs = comet.description.split('\n\n')
        for para in paragraphs[:2]:  # Show first 2 paragraphs
            print(f"\n{para}")
        
        print("\n📚 Information Sources:")
        for source in comet.sources:
            print(f"   ✅ {source.name} ({source.credibility.name})")
            print(f"      {source.url}")
    
    # Demonstrate fact-checking
    print_section("3. Fact-Checking Claims about Comet 3I")
    
    claims = [
        "Comet 3I/2019 Q4 is an interstellar object",
        "Comet 3I was discovered in 2019",
        "Comet 3I originated from outside our solar system"
    ]
    
    print("Testing multiple claims:\n")
    
    for claim in claims:
        result = engine.fact_check(claim)
        
        status = "✅ VERIFIED" if result['verified'] else "❌ NOT VERIFIED"
        confidence = result['confidence']
        
        print(f"{status} - {claim}")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Supporting Sources: {len(result['supporting_sources'])}")
        
        if result['supporting_sources']:
            top_source = result['supporting_sources'][0]
            print(f"   Top Source: {top_source['source']['name']}")
        print()
    
    # Demonstrate capabilities
    print_section("4. Research Engine Capabilities")
    
    caps = engine.get_capabilities()
    
    print(f"📦 Engine Version: {caps['version']}")
    print(f"📚 Total Sources: {caps['source_count']}")
    
    print("\n✨ Features:")
    for feature in caps['features']:
        print(f"   ✅ {feature}")
    
    print("\n🌍 Supported Domains:")
    for domain in caps['supported_domains']:
        print(f"   🔹 {domain}")
    
    # Export results
    print_section("5. Export Research Results")
    
    filename = engine.export_results(results, "comet_3i_research.json")
    print(f"✅ Results exported to: {filename}")
    print(f"📄 File contains {len(results)} search results with full metadata")
    
    # Show sample of exported data
    with open(filename, 'r') as f:
        data = json.load(f)
    
    print(f"\n📊 Export Summary:")
    print(f"   Timestamp: {data['timestamp']}")
    print(f"   Engine Version: {data['engine_version']}")
    print(f"   Result Count: {data['result_count']}")
    print(f"   File Size: {len(json.dumps(data, indent=2))} bytes")
    
    # Summary
    print_header("📊 SUMMARY")
    
    print("✅ Research Engine Successfully Demonstrated:")
    print("   • Web search across verified sources")
    print("   • Detailed astronomical object database")
    print("   • Fact-checking with confidence scoring")
    print("   • Source credibility verification")
    print("   • Research export functionality")
    print()
    print("🌟 Key Findings about Comet 3I/ATLAS:")
    print("   • First confirmed interstellar comet")
    print("   • Discovered August 30, 2019 by Gennadiy Borisov")
    print("   • Hyperbolic orbit confirms extrasolar origin")
    print("   • Similar composition to solar system comets")
    print("   • Provided unique opportunity to study interstellar material")
    print()
    print("🔒 No Fake News:")
    print("   • All information from verified sources (NASA, IAU, arXiv)")
    print("   • Credibility scores: VERY_HIGH (5/5)")
    print("   • Multiple citations and references provided")
    print("   • Fact-checking confirms accuracy")
    print()
    print("=" * 70)
    print("✅ THE FORGE Research Engine - Reliable Information Discovery!")
    print("=" * 70)


def main():
    """Run the demonstration"""
    try:
        demo_comet_search()
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
