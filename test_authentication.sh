#!/bin/bash

# Test Authentication Flow for MindKey System

API_URL="http://localhost:8000"
DATA_DIR="data/processed"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   MindKey Authentication System - Test Flow               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Register User (Subject 1)
echo "📝 [1/4] Registering new user (Subject 1)..."
REGISTER_RESPONSE=$(curl -s -X POST ${API_URL}/auth/register \
  -F "username=test_subject1" \
  -F "password=SecurePass123" \
  -F "eeg_file=@${DATA_DIR}/s01_trial00.npy")

echo "$REGISTER_RESPONSE" | jq '.'
echo ""

# Test 2: Authenticate as Genuine User (Same subject, different trial)
echo "✅ [2/4] Testing GENUINE authentication (Subject 1, different trial)..."
AUTH_GENUINE=$(curl -s -X POST ${API_URL}/auth/authenticate \
  -F "username=test_subject1" \
  -F "password=SecurePass123" \
  -F "eeg_file=@${DATA_DIR}/s01_trial01.npy")

echo "$AUTH_GENUINE" | jq '.'

if echo "$AUTH_GENUINE" | jq -e '.authenticated == true' > /dev/null; then
    echo "✅ SUCCESS: Genuine user authenticated!"
else
    echo "❌ FAILED: Genuine user rejected"
fi
echo ""

# Test 3: Test Impostor (Different subject)
echo "🚫 [3/4] Testing IMPOSTOR detection (Subject 2 pretending to be Subject 1)..."
AUTH_IMPOSTOR=$(curl -s -X POST ${API_URL}/auth/authenticate \
  -F "username=test_subject1" \
  -F "password=SecurePass123" \
  -F "eeg_file=@${DATA_DIR}/s02_trial00.npy")

echo "$AUTH_IMPOSTOR" | jq '.'

if echo "$AUTH_IMPOSTOR" | jq -e '.authenticated == false' > /dev/null; then
    echo "✅ SUCCESS: Impostor correctly detected!"
else
    echo "❌ FAILED: Impostor was accepted"
fi
echo ""

# Test 4: Multiple Genuine Trials
echo "🔄 [4/4] Testing multiple genuine trials..."
for trial in 02 03 04; do
    echo "  Testing trial ${trial}..."
    AUTH_TEST=$(curl -s -X POST ${API_URL}/auth/authenticate \
      -F "username=test_subject1" \
      -F "password=SecurePass123" \
      -F "eeg_file=@${DATA_DIR}/s01_trial${trial}.npy")
    
    SCORE=$(echo "$AUTH_TEST" | jq -r '.score')
    AUTH=$(echo "$AUTH_TEST" | jq -r '.authenticated')
    echo "    Score: ${SCORE}, Authenticated: ${AUTH}"
done
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Test Complete! ✨                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "  • Genuine users should have score > 0.7"
echo "  • Impostors should have score < 0.5"
echo "  • EER threshold: ~0.838 (from evaluation)"
echo ""
echo "🌐 Test in Frontend:"
echo "  1. Open: http://localhost:5173"
echo "  2. Click 'Enroll Now'"
echo "  3. Username: test_subject1"
echo "  4. Password: SecurePass123"
echo "  5. Upload: data/processed/s01_trial01.npy"
echo "  6. Should authenticate successfully!"
