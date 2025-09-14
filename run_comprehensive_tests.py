#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs both API and Supabase integration tests with detailed reporting
"""

import subprocess
import sys
import time
import os
from datetime import datetime
from typing import Dict, List, Tuple

class TestRunner:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        self.server_process = None
    
    def check_requirements(self) -> bool:
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check if backend directory exists
        if not os.path.exists("backend"):
            print("❌ Backend directory not found")
            return False
        
        # Check if frontend directory exists
        if not os.path.exists("frontend_new"):
            print("❌ Frontend directory not found")
            return False
        
        # Check if test files exist
        test_files = [
            "comprehensive_user_tests.py",
            "supabase_integration_test.py"
        ]
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                print(f"❌ Test file not found: {test_file}")
                return False
        
        print("✅ All requirements met")
        return True
    
    def start_backend_server(self) -> bool:
        """Start the backend server or check if it's already running"""
        print("\n🚀 Checking backend server...")
        
        # First check if server is already running
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is already running")
                return True
        except:
            pass
        
        print("Starting new backend server...")
        try:
            # Change to backend directory and start server
            self.server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd="backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if server is running
            if self.server_process.poll() is None:
                print("✅ Backend server started successfully")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                if "Address already in use" in stderr:
                    print("✅ Backend server is already running (address in use)")
                    return True
                else:
                    print(f"❌ Backend server failed to start")
                    print(f"STDOUT: {stdout}")
                    print(f"STDERR: {stderr}")
                    return False
                
        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False
    
    def stop_backend_server(self):
        """Stop the backend server"""
        if self.server_process:
            print("\n🛑 Stopping backend server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Backend server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing backend server...")
                self.server_process.kill()
                self.server_process.wait()
    
    def run_test_script(self, script_name: str, description: str) -> Tuple[bool, str]:
        """Run a test script and return success status and output"""
        print(f"\n🧪 Running {description}...")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            success = result.returncode == 0
            output = result.stdout + "\n" + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            print(f"❌ {description} timed out after 5 minutes")
            return False, "Test timed out"
        except Exception as e:
            print(f"❌ Failed to run {description}: {e}")
            return False, str(e)
    
    def run_supabase_tests(self) -> bool:
        """Run Supabase integration tests"""
        success, output = self.run_test_script(
            "supabase_integration_test.py",
            "Supabase Integration Tests"
        )
        
        self.results["supabase"] = {
            "success": success,
            "output": output,
            "description": "Supabase Integration Tests"
        }
        
        return success
    
    def run_api_tests(self) -> bool:
        """Run API integration tests"""
        success, output = self.run_test_script(
            "comprehensive_user_tests.py",
            "API Integration Tests"
        )
        
        self.results["api"] = {
            "success": success,
            "output": output,
            "description": "API Integration Tests"
        }
        
        return success
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Run: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration: {duration:.2f} seconds")
        report.append("")
        
        # Summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        report.append("SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Test Suites: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 20)
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            report.append(f"{result['description']}: {status}")
            
            if not result["success"]:
                report.append("  Error Details:")
                # Extract error summary from output
                lines = result["output"].split('\n')
                error_lines = [line for line in lines if '❌' in line or 'Error:' in line or 'FAILED' in line]
                for error_line in error_lines[:5]:  # Show first 5 errors
                    report.append(f"    {error_line.strip()}")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 20)
        
        if failed_tests == 0:
            report.append("🎉 All tests passed! Your user system is working correctly.")
            report.append("")
            report.append("Next steps:")
            report.append("1. Deploy your backend to production")
            report.append("2. Set up your frontend with the production backend URL")
            report.append("3. Configure your Supabase project for production")
        else:
            report.append("⚠️  Some tests failed. Please address the following issues:")
            report.append("")
            
            for test_name, result in self.results.items():
                if not result["success"]:
                    report.append(f"• {result['description']}: Check the error details above")
            
            report.append("")
            report.append("Common fixes:")
            report.append("• Ensure Supabase is properly configured with correct credentials")
            report.append("• Verify that all required tables exist in your Supabase database")
            report.append("• Check that the backend server is running and accessible")
            report.append("• Ensure all required environment variables are set")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, report: str):
        """Save the test report to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"\n📄 Test report saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all tests and generate report"""
        print("🧪 Comprehensive User System Test Suite")
        print("=" * 60)
        
        # Check requirements
        if not self.check_requirements():
            return False
        
        # Start backend server
        if not self.start_backend_server():
            print("\n❌ Cannot run tests without backend server")
            return False
        
        try:
            # Run Supabase tests first (don't need server)
            supabase_success = self.run_supabase_tests()
            
            # Run API tests (need server)
            api_success = self.run_api_tests()
            
            # Generate and display report
            report = self.generate_report()
            print("\n" + report)
            
            # Save report
            self.save_report(report)
            
            return supabase_success and api_success
            
        finally:
            # Always stop the server
            self.stop_backend_server()

def main():
    """Main test runner"""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the report above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
