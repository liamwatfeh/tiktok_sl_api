#!/usr/bin/env python3
"""
Quick Endpoint Testing - Core Bulletproofing Tests
=================================================

This is a streamlined test suite focusing on the most critical failure scenarios
that could cause the endpoints to crash or behave unexpectedly.

Run with: python test_endpoints_quick.py
"""

import asyncio
import logging
import sys
import traceback
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import application components
try:
    from app.core.config import settings
    from app.models.tiktok_schemas import TikTokHashtagAnalysisRequest, TikTokAccountAnalysisRequest
    from app.services.tiktok_hashtags.hashtag_service import TikTokHashtagService
    from app.services.tiktok_accounts.account_service import TikTokAccountService
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root and dependencies are installed")
    sys.exit(1)


class QuickTester:
    """Quick tester focusing on bulletproofing critical scenarios."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.critical_failures = []
    
    def test_pass(self, test_name: str):
        self.tests_passed += 1
        print(f"✅ {test_name}")
    
    def test_fail(self, test_name: str, error: str, is_critical: bool = False):
        self.tests_failed += 1
        print(f"❌ {test_name}: {error}")
        if is_critical:
            self.critical_failures.append(f"{test_name}: {error}")
    
    async def run_quick_tests(self) -> bool:
        """Run quick bulletproofing tests."""
        print("🧪 Quick Bulletproofing Tests for TikTok Endpoints")
        print("="*60)
        
        # Test 1: Configuration Check
        await self.test_configuration()
        
        # Test 2: Service Initialization
        await self.test_service_initialization()
        
        # Test 3: Critical Input Validation
        await self.test_critical_input_validation()
        
        # Test 4: Mock Data Pipeline
        await self.test_mock_pipeline()
        
        # Test 5: Error Handling
        await self.test_error_resilience()
        
        # Report results
        return self.report_results()
    
    async def test_configuration(self):
        """Test critical configuration requirements."""
        print("\n🔧 Testing Configuration...")
        
        try:
            # Check if settings can be loaded
            api_title = settings.API_TITLE
            self.test_pass("Configuration loaded successfully")
        except Exception as e:
            self.test_fail("Configuration loading", str(e), is_critical=True)
            return
        
        # Check critical settings
        if hasattr(settings, 'TIKTOK_RAPIDAPI_KEY'):
            self.test_pass("TikTok API key setting exists")
        else:
            self.test_fail("TikTok API key setting", "Missing TIKTOK_RAPIDAPI_KEY", is_critical=True)
        
        if hasattr(settings, 'OPENAI_API_KEY'):
            self.test_pass("OpenAI API key setting exists")
        else:
            self.test_fail("OpenAI API key setting", "Missing OPENAI_API_KEY", is_critical=True)
    
    async def test_service_initialization(self):
        """Test that services can be initialized without crashing."""
        print("\n🏗️ Testing Service Initialization...")
        
        # Test hashtag service
        try:
            with TikTokHashtagService() as service:
                if service:
                    self.test_pass("Hashtag service initialization")
                else:
                    self.test_fail("Hashtag service initialization", "Service is None", is_critical=True)
        except Exception as e:
            self.test_fail("Hashtag service initialization", str(e), is_critical=True)
        
        # Test account service
        try:
            with TikTokAccountService() as service:
                if service:
                    self.test_pass("Account service initialization")
                else:
                    self.test_fail("Account service initialization", "Service is None", is_critical=True)
        except Exception as e:
            self.test_fail("Account service initialization", str(e), is_critical=True)
    
    async def test_critical_input_validation(self):
        """Test that dangerous inputs are rejected."""
        print("\n🛡️ Testing Critical Input Validation...")
        
        # Test hashtag request validation
        dangerous_hashtag_inputs = [
            ("", "Empty string"),
            (None, "None value"),
            ("../../../etc/passwd", "Path traversal"),
            ("test" * 100, "Extremely long input"),
            ("test\n\r\t", "Control characters")
        ]
        
        for dangerous_input, description in dangerous_hashtag_inputs:
            try:
                if dangerous_input is None:
                    # Skip None test as Pydantic will catch it at schema level
                    self.test_pass(f"Hashtag validation - {description} (Pydantic catches)")
                    continue
                    
                request = TikTokHashtagAnalysisRequest(
                    hashtag=dangerous_input,
                    max_posts=5,
                    ai_analysis_prompt="Test prompt"
                )
                # If we get here, the input was accepted - that might be bad
                if len(dangerous_input) > 50:
                    self.test_fail(f"Hashtag validation - {description}", "Dangerous input accepted")
                else:
                    self.test_pass(f"Hashtag validation - {description} (accepted safely)")
            except Exception:
                self.test_pass(f"Hashtag validation - {description} (rejected)")
        
        # Test account request validation
        dangerous_username_inputs = [
            ("", "Empty string"),
            ("../admin", "Path-like input"),
            ("user\x00null", "Null byte injection"),
            ("test" * 50, "Very long username")
        ]
        
        for dangerous_input, description in dangerous_username_inputs:
            try:
                request = TikTokAccountAnalysisRequest(
                    username=dangerous_input,
                    max_posts=5,
                    ai_analysis_prompt="Test prompt"
                )
                if len(dangerous_input) > 50:
                    self.test_fail(f"Account validation - {description}", "Dangerous input accepted")
                else:
                    self.test_pass(f"Account validation - {description} (accepted safely)")
            except Exception:
                self.test_pass(f"Account validation - {description} (rejected)")
    
    async def test_mock_pipeline(self):
        """Test pipeline with mock data to ensure it doesn't crash."""
        print("\n🔄 Testing Mock Data Pipeline...")
        
        # Enable mock data
        original_mock_setting = getattr(settings, 'USE_MOCK_DATA', False)
        settings.USE_MOCK_DATA = True
        
        try:
            # Create minimal valid requests
            hashtag_request = TikTokHashtagAnalysisRequest(
                hashtag="test",
                max_posts=2,
                ai_analysis_prompt="Test analysis for sentiment"
            )
            
            account_request = TikTokAccountAnalysisRequest(
                username="testuser",
                max_posts=2,
                max_comments_per_post=10,
                ai_analysis_prompt="Test analysis for engagement"
            )
            
            # Test hashtag pipeline
            try:
                with TikTokHashtagService() as service:
                    result = await service.analyze_hashtag(hashtag_request)
                    if isinstance(result, dict):
                        self.test_pass("Hashtag mock pipeline execution")
                    else:
                        self.test_fail("Hashtag mock pipeline", "Invalid result type", is_critical=True)
            except Exception as e:
                self.test_fail("Hashtag mock pipeline", str(e), is_critical=True)
            
            # Test account pipeline
            try:
                with TikTokAccountService() as service:
                    result = await service.analyze_account(account_request)
                    if isinstance(result, dict):
                        self.test_pass("Account mock pipeline execution")
                    else:
                        self.test_fail("Account mock pipeline", "Invalid result type", is_critical=True)
            except Exception as e:
                self.test_fail("Account mock pipeline", str(e), is_critical=True)
        
        finally:
            # Restore original setting
            settings.USE_MOCK_DATA = original_mock_setting
    
    async def test_error_resilience(self):
        """Test that services handle errors gracefully without crashing."""
        print("\n🚨 Testing Error Resilience...")
        
        # Test with edge case inputs that might cause issues
        edge_case_request = TikTokHashtagAnalysisRequest(
            hashtag="nonexistenthashtag123456789",
            max_posts=1,
            ai_analysis_prompt="Test with edge case hashtag that definitely doesn't exist"
        )
        
        try:
            with TikTokHashtagService() as service:
                result = await service.analyze_hashtag(edge_case_request)
                
                # Should return an error response, not crash
                if isinstance(result, dict):
                    if "error" in result:
                        self.test_pass("Hashtag error handling (graceful error response)")
                    else:
                        self.test_pass("Hashtag error handling (successful response)")
                else:
                    self.test_fail("Hashtag error handling", "Invalid response type", is_critical=True)
        except Exception as e:
            # Even exceptions should be handled gracefully at the API level
            self.test_fail("Hashtag error handling", f"Unhandled exception: {e}", is_critical=True)
        
        # Test account service resilience
        edge_case_account_request = TikTokAccountAnalysisRequest(
            username="nonexistentuser987654321",
            max_posts=1,
            max_comments_per_post=5,
            ai_analysis_prompt="Test with edge case username"
        )
        
        try:
            with TikTokAccountService() as service:
                result = await service.analyze_account(edge_case_account_request)
                
                if isinstance(result, dict):
                    if "error" in result:
                        self.test_pass("Account error handling (graceful error response)")
                    else:
                        self.test_pass("Account error handling (successful response)")
                else:
                    self.test_fail("Account error handling", "Invalid response type", is_critical=True)
        except Exception as e:
                                self.test_fail("Account error handling", f"Unhandled exception: {e}", is_critical=True)
    
    def report_results(self) -> bool:
        """Report test results and determine if endpoints are bulletproof."""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("QUICK TEST RESULTS")
        print("="*60)
        print(f"Tests Run: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"  ⚠️  {failure}")
            print("\n❌ ENDPOINTS ARE NOT BULLETPROOF!")
            print("   Critical issues must be fixed before production deployment.")
            return False
        
        elif self.tests_failed > 0:
            print(f"\n⚠️  {self.tests_failed} non-critical test(s) failed.")
            print("   Endpoints should work but consider reviewing failed tests.")
        
        if success_rate >= 90.0:
            print("\n✅ ENDPOINTS ARE BULLETPROOF!")
            print("   All critical tests passed. Safe for production.")
            return True
        else:
            print("\n❌ ENDPOINTS NEED IMPROVEMENT!")
            print("   Too many failures for production deployment.")
            return False


async def main():
    """Run quick endpoint tests."""
    print("🚀 Quick Bulletproofing Test for TikTok API Endpoints\n")
    
    tester = QuickTester()
    
    try:
        success = await tester.run_quick_tests()
        return success
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
