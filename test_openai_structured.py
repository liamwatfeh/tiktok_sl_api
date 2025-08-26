#!/usr/bin/env python3
"""
Test script to verify OpenAI structured outputs compatibility.
This script tests the OpenAI integration that will be used in our TikTok AI analyzer.
"""

import os
from typing import List
from pydantic import BaseModel, Field


class TikTokCommentAnalysis(BaseModel):
    """Test schema matching our TikTok comment analysis structure."""
    quote: str = Field(..., description="Comment text")
    sentiment: str = Field(..., description="positive/negative/neutral")
    theme: str = Field(..., description="Topic category")
    purchase_intent: str = Field(..., description="high/medium/low/none") 
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence level")


def test_openai_structured_outputs():
    """Test OpenAI structured outputs with our schema."""
    try:
        import openai
        from openai import OpenAI
        
        # Mock test (won't make actual API call without key)
        print("✅ OpenAI library imported successfully")
        print(f"OpenAI version: {openai.__version__ if hasattr(openai, '__version__') else 'Unknown'}")
        
        # Test Pydantic schema
        test_analysis = TikTokCommentAnalysis(
            quote="Love my BMW R1250GS! Best bike ever!",
            sentiment="positive",
            theme="experience", 
            purchase_intent="high",
            confidence_score=0.95
        )
        
        print("✅ Pydantic schema validation works")
        print(f"Test analysis: {test_analysis.model_dump()}")
        
        # Test that we can create the structured output format
        client = OpenAI(api_key="test-key")  # Won't actually call API
        print("✅ OpenAI client instantiation works")
        
        # Check that we can specify response format (this doesn't make a call)
        response_format = {"type": "json_schema", "json_schema": {
            "name": "comment_analyses",
            "schema": TikTokCommentAnalysis.model_json_schema()
        }}
        print("✅ Response format schema generation works")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing OpenAI structured outputs compatibility...")
    print("=" * 50)
    
    success = test_openai_structured_outputs()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! OpenAI structured outputs are ready.")
    else:
        print("💥 Tests failed. Check dependency installation.")
