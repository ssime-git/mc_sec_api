#!/bin/bash
# GDPR-Compliant API Testing Script
# This script tests all endpoints and functionality of the Security and Prediction APIs

# Text formatting
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GDPR-Compliant API Testing Script ===${NC}"
echo "Testing all endpoints and functionality..."
echo ""

# 1. Register a new test user
echo -e "${BLUE}1. Registering test user${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"apitest","password":"Test123!"}')

if [[ $REGISTER_RESPONSE == *"User created successfully"* ]]; then
  echo -e "${GREEN}✓ Registration successful${NC}"
  echo "Response: $REGISTER_RESPONSE"
else
  echo -e "${RED}✗ Registration failed${NC}"
  echo "Response: $REGISTER_RESPONSE"
  
  # Try alternative - maybe user exists
  echo -e "${BLUE}Attempting with different username...${NC}"
  REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/register" \
    -H "Content-Type: application/json" \
    -d '{"username":"apitest2","password":"Test123!"}')
  
  if [[ $REGISTER_RESPONSE == *"User created successfully"* ]]; then
    echo -e "${GREEN}✓ Registration successful with alternative username${NC}"
    echo "Response: $REGISTER_RESPONSE"
    USERNAME="apitest2"
  else
    echo -e "${RED}✗ Registration failed with alternative username${NC}"
    echo "Response: $REGISTER_RESPONSE"
    USERNAME="apitest" # Fallback to original for testing
  fi
fi

USERNAME=${USERNAME:-"apitest"}
echo "Using username: $USERNAME"
echo ""

# 2. Get authentication token
echo -e "${BLUE}2. Getting authentication token${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=Test123!")

if [[ $TOKEN_RESPONSE == *"access_token"* ]]; then
  echo -e "${GREEN}✓ Authentication successful${NC}"
  # Extract token
  TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//g')
  echo "Token received (truncated): ${TOKEN:0:20}..."
else
  echo -e "${RED}✗ Authentication failed${NC}"
  echo "Response: $TOKEN_RESPONSE"
  echo "Exiting tests as authentication is required for subsequent tests."
  exit 1
fi
echo ""

# 3. Pseudonymize data
echo -e "${BLUE}3. Testing data pseudonymization${NC}"
PSEUDO_RESPONSE=$(curl -s -X POST "http://localhost:8000/pseudonymize" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","phone":"+1234567890"}')

if [[ $PSEUDO_RESPONSE == *"name"* && $PSEUDO_RESPONSE == *"email"* ]]; then
  echo -e "${GREEN}✓ Pseudonymization successful${NC}"
  echo "Response: $PSEUDO_RESPONSE"
else
  echo -e "${RED}✗ Pseudonymization failed${NC}"
  echo "Response: $PSEUDO_RESPONSE"
fi
echo ""

# 3.5 Testing zodiac sign prediction via Security API
echo -e "${BLUE}3.5 Testing zodiac sign prediction via Security API${NC}"
ZODIAC_RESPONSE=$(curl -s -X POST "http://localhost:8000/forward-to-prediction" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"age":30,"sex":"Male","favorite_color":"Blue","favorite_food":"Pizza"}')

if [[ $ZODIAC_RESPONSE == *"prediction"* || $ZODIAC_RESPONSE == *"zodiac"* ]]; then
  echo -e "${GREEN}✓ Zodiac sign prediction successful${NC}"
  echo "Response: $ZODIAC_RESPONSE"
else
  echo -e "${RED}✗ Zodiac sign prediction failed${NC}"
  echo "Response: $ZODIAC_RESPONSE"
  
  # Try direct prediction API call as fallback test
  echo -e "${BLUE}Attempting direct zodiac sign prediction API call...${NC}"
  DIRECT_ZODIAC=$(curl -s -X POST "http://localhost:8001/predict" \
    -H "api-key: internal-secure-key" \
    -H "Content-Type: application/json" \
    -d '{"age":30,"sex":"Male","favorite_color":"Blue","favorite_food":"Pizza"}')
  
  if [[ $DIRECT_ZODIAC == *"prediction"* || $DIRECT_ZODIAC == *"zodiac"* ]]; then
    echo -e "${GREEN}✓ Direct zodiac sign prediction successful${NC}"
    echo "Response: $DIRECT_ZODIAC"
    echo -e "${RED}Note: Security API forwarding failed but direct prediction works${NC}"
  else
    echo -e "${RED}✗ Both zodiac sign prediction methods failed${NC}"
    echo "Direct response: $DIRECT_ZODIAC"
  fi
fi
echo ""

# 4. Access user data
echo -e "${BLUE}4. Testing user data access${NC}"
DATA_RESPONSE=$(curl -s -X GET "http://localhost:8000/user/data" \
  -H "Authorization: Bearer $TOKEN")

if [[ $DATA_RESPONSE == *"username"* ]]; then
  echo -e "${GREEN}✓ Data access successful${NC}"
  echo "Response: $DATA_RESPONSE"
else
  echo -e "${RED}✗ Data access failed${NC}"
  echo "Response: $DATA_RESPONSE"
fi
echo ""

# 5. Test invalid authentication
echo -e "${BLUE}5. Testing invalid authentication${NC}"
INVALID_AUTH=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=wronguser&password=wrongpass")

if [[ $INVALID_AUTH == *"Invalid credentials"* ]]; then
  echo -e "${GREEN}✓ Invalid authentication correctly rejected${NC}"
  echo "Response: $INVALID_AUTH"
else
  echo -e "${RED}✗ Invalid authentication test failed${NC}"
  echo "Response: $INVALID_AUTH"
fi
echo ""

# 6. Check GDPR logs
echo -e "${BLUE}6. Checking GDPR audit logs${NC}"
LOGS=$(docker exec securing_api-security_api-1 cat /app/logs/gdpr_audit.log 2>/dev/null)

if [[ -n "$LOGS" ]]; then
  echo -e "${GREEN}✓ GDPR logs available${NC}"
  echo "Last 3 log entries:"
  docker exec securing_api-security_api-1 tail -n 3 /app/logs/gdpr_audit.log 2>/dev/null
else
  echo -e "${RED}✗ GDPR logs not found or empty${NC}"
fi
echo ""

# 7. Check database persistence
echo -e "${BLUE}7. Checking database persistence${NC}"
DB_FILES=$(docker exec securing_api-security_api-1 ls -la /app/users/ 2>/dev/null)

if [[ -n "$DB_FILES" ]]; then
  echo -e "${GREEN}✓ Database files exist${NC}"
  echo "Database files:"
  docker exec securing_api-security_api-1 ls -la /app/users/ 2>/dev/null
else
  echo -e "${RED}✗ Database files not found${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}=== Test Summary ===${NC}"
echo "All tests completed. Check the results above for any failures."
echo "The system is now ready for use with the registered test user."
echo ""
