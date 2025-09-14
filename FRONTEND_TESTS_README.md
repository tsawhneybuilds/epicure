# Frontend Conversational Search Tests

This directory contains comprehensive tests to verify that the conversational search functionality works properly in the frontend.

## Test Files

### 1. `test_frontend_conversational_search.py`
**Comprehensive Integration Tests**
- Tests the conversational AI endpoint directly
- Verifies API responses and data structure
- Tests multiple conversation turns
- Validates chat history persistence
- Checks menu item data quality

### 2. `test_frontend_user_journey.py`
**User Experience Simulation**
- Simulates a real user interacting with the app
- Tests the complete user journey from app load to multiple refinements
- Verifies frontend state updates
- Tests menu item switching/swiping
- Includes error handling scenarios

### 3. `test_backend_endpoints.py`
**Backend Endpoint Verification**
- Quick tests to verify backend endpoints are working
- Tests health, conversational search, and AI recommendation endpoints
- Useful for debugging backend issues

### 4. `run_frontend_tests.py`
**Test Runner**
- Runs all test suites
- Provides comprehensive reporting
- Saves results to JSON files

## How to Run the Tests

### Prerequisites
1. **Backend must be running** on `http://localhost:8000`
   ```bash
   cd backend
   python main.py
   ```

2. **Install required Python packages**
   ```bash
   pip install requests
   ```

### Running Individual Tests

```bash
# Test backend endpoints first
python test_backend_endpoints.py

# Run comprehensive integration tests
python test_frontend_conversational_search.py

# Run user journey simulation
python test_frontend_user_journey.py
```

### Running All Tests

```bash
# Run all tests with comprehensive reporting
python run_frontend_tests.py
```

## What the Tests Verify

### ✅ Conversational Search Flow
- User types in "Continue the conversation" input
- Frontend calls `/conversational/search` endpoint
- AI processes the message and conversation context
- New search results are returned and displayed
- Chat history is updated with user message and AI response

### ✅ Multiple Conversation Turns
- User can refine their search multiple times
- Each refinement builds on the previous conversation
- AI maintains context across multiple turns
- Search results update appropriately

### ✅ Data Quality
- Menu items have all required fields (name, description, price, restaurant)
- AI responses are meaningful and contextual
- Chat history is properly structured and maintained

### ✅ Error Handling
- Empty messages are handled gracefully
- API errors don't crash the frontend
- Invalid requests return appropriate error codes

## Expected Test Results

When all tests pass, you should see:
```
🎉 ALL TESTS PASSED! The conversational search is working perfectly!

✨ What this means:
   • Users can type in the 'Continue the conversation' input
   • The AI properly processes their requests
   • Search results update based on the conversation
   • Chat history is maintained correctly
   • The frontend displays everything properly
```

## Troubleshooting

### Backend Not Running
```
❌ Backend is not running: Connection refused
```
**Solution**: Start the backend server
```bash
cd backend
python main.py
```

### No Menu Items Returned
```
❌ No menu items returned from first search
```
**Solution**: Check that the database has menu items and the search is working

### API Endpoint Errors
```
❌ Conversational search failed: 500
```
**Solution**: Check backend logs for errors, verify the conversational AI service is working

### Chat History Issues
```
❌ Chat history length incorrect: expected 6, got 4
```
**Solution**: Verify that the frontend is properly updating chat history after each API call

## Test Output Files

The tests generate several output files:
- `frontend_integration_test_results.json` - Detailed results from integration tests
- `frontend_user_journey_results.json` - Results from user journey simulation
- `frontend_test_summary.json` - Overall test summary

## Understanding the Test Output

### Success Indicators
- ✅ All API calls return 200 status codes
- ✅ Menu items are returned with proper structure
- ✅ AI responses are contextual and meaningful
- ✅ Chat history grows with each conversation turn
- ✅ Search results change based on user input

### Failure Indicators
- ❌ API calls return error status codes
- ❌ No menu items returned
- ❌ AI responses are generic or don't match context
- ❌ Chat history is not updated
- ❌ Search results don't change with user input

## Customizing Tests

You can modify the test scenarios by editing the test files:

### Adding New Test Scenarios
Edit `test_frontend_user_journey.py` and add new test methods:
```python
def test_your_custom_scenario(self) -> bool:
    # Your test logic here
    pass
```

### Modifying Test Data
Update the test messages and contexts in the test files:
```python
user_message = "Your custom test message"
search_request = {
    "message": user_message,
    "context": {
        "location": {"lat": 40.7580, "lng": -73.9855},
        "meal_context": "lunch"
    },
    # ... rest of request
}
```

## Integration with CI/CD

These tests can be integrated into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Frontend Tests
  run: |
    python test_backend_endpoints.py
    python run_frontend_tests.py
```

The tests will return exit code 0 for success and 1 for failure, making them suitable for automated testing.
