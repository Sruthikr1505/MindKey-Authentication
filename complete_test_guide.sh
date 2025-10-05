#!/bin/bash

# Complete Authentication Test Guide for MindKey System

API_URL="http://localhost:8000"
DATA_DIR="data/processed"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   MindKey - Complete Authentication Test Guide            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check services
echo "🔍 Checking services..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running on http://localhost:8000"
else
    echo "❌ Backend not running! Start with: python src/api/main.py"
    exit 1
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend running on http://localhost:5173"
else
    echo "⚠️  Frontend not running! Start with: npm run dev"
fi
echo ""

# Step 1: Register User
echo "═══════════════════════════════════════════════════════════"
echo "📝 STEP 1: REGISTER NEW USER (ENROLLMENT)"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Using Subject 1, Trial 0 for enrollment..."
echo ""

REGISTER_RESPONSE=$(curl -s -X POST ${API_URL}/register \
  -F "username=alice_test" \
  -F "password=SecurePass123" \
  -F "enrollment_trials=@${DATA_DIR}/s01_trial00.npy")

echo "Response:"
echo "$REGISTER_RESPONSE" | jq '.'
echo ""

if echo "$REGISTER_RESPONSE" | jq -e '.success == true' > /dev/null; then
    echo "✅ SUCCESS: User 'alice_test' enrolled successfully!"
else
    echo "❌ FAILED: Enrollment failed"
    echo "Error: $(echo "$REGISTER_RESPONSE" | jq -r '.detail // .message')"
    exit 1
fi
echo ""

# Wait a moment
sleep 2

# Step 2: Authenticate as Genuine User
echo "═══════════════════════════════════════════════════════════"
echo "🧠 STEP 2: AUTHENTICATE AS GENUINE USER"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Using Subject 1, Trial 1 (SAME SUBJECT, DIFFERENT TRIAL)..."
echo ""

AUTH_GENUINE=$(curl -s -X POST ${API_URL}/auth/login \
  -F "username=alice_test" \
  -F "password=SecurePass123" \
  -F "probe=@${DATA_DIR}/s01_trial01.npy")

echo "Response:"
echo "$AUTH_GENUINE" | jq '.'
echo ""

AUTHENTICATED=$(echo "$AUTH_GENUINE" | jq -r '.authenticated')
SCORE=$(echo "$AUTH_GENUINE" | jq -r '.score')
PROBABILITY=$(echo "$AUTH_GENUINE" | jq -r '.probability')

if [ "$AUTHENTICATED" = "true" ]; then
    echo "✅ SUCCESS: Genuine user authenticated!"
    echo "   Score: $SCORE"
    echo "   Probability: $PROBABILITY"
else
    echo "❌ FAILED: Genuine user was rejected"
    echo "   Score: $SCORE"
    echo "   This should not happen!"
fi
echo ""

# Wait a moment
sleep 2

# Step 3: Test Impostor
echo "═══════════════════════════════════════════════════════════"
echo "🚫 STEP 3: TEST IMPOSTOR DETECTION"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Using Subject 2, Trial 0 (DIFFERENT SUBJECT - Impostor)..."
echo ""

AUTH_IMPOSTOR=$(curl -s -X POST ${API_URL}/auth/login \
  -F "username=alice_test" \
  -F "password=SecurePass123" \
  -F "probe=@${DATA_DIR}/s02_trial00.npy")

echo "Response:"
echo "$AUTH_IMPOSTOR" | jq '.'
echo ""

AUTHENTICATED_IMP=$(echo "$AUTH_IMPOSTOR" | jq -r '.authenticated')
SCORE_IMP=$(echo "$AUTH_IMPOSTOR" | jq -r '.score')

if [ "$AUTHENTICATED_IMP" = "false" ]; then
    echo "✅ SUCCESS: Impostor correctly rejected!"
    echo "   Score: $SCORE_IMP (should be < 0.5)"
else
    echo "❌ FAILED: Impostor was accepted (security breach!)"
    echo "   Score: $SCORE_IMP"
fi
echo ""

# Step 4: Test Multiple Genuine Trials
echo "═══════════════════════════════════════════════════════════"
echo "🔄 STEP 4: TEST MULTIPLE GENUINE TRIALS"
echo "═══════════════════════════════════════════════════════════"
echo ""

for trial in 02 03 04 05; do
    echo "Testing Subject 1, Trial ${trial}..."
    
    AUTH_TEST=$(curl -s -X POST ${API_URL}/auth/login \
      -F "username=alice_test" \
      -F "password=SecurePass123" \
      -F "probe=@${DATA_DIR}/s01_trial${trial}.npy")
    
    SCORE=$(echo "$AUTH_TEST" | jq -r '.score')
    AUTH=$(echo "$AUTH_TEST" | jq -r '.authenticated')
    
    if [ "$AUTH" = "true" ]; then
        echo "  ✅ Trial ${trial}: Authenticated (Score: ${SCORE})"
    else
        echo "  ❌ Trial ${trial}: Rejected (Score: ${SCORE})"
    fi
done
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST COMPLETE! ✨                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Expected Results:"
echo "  • Genuine trials (s01_trial01-05): ✅ Authenticated (score > 0.7)"
echo "  • Impostor trial (s02_trial00):    ❌ Rejected (score < 0.5)"
echo ""
echo "🌐 Frontend Testing:"
echo "  1. Open: http://localhost:5173"
echo "  2. Click 'Enroll Now'"
echo "  3. Username: alice_test"
echo "  4. Password: SecurePass123"
echo "  5. Upload: data/processed/s01_trial01.npy"
echo "  6. Click 'Authenticate'"
echo "  7. Should redirect to Dashboard!"
echo ""
echo "🔍 View API Documentation:"
echo "  http://localhost:8000/docs"
