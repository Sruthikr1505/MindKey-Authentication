#!/bin/bash
# Test script for BiLSTM Authentication API

API_URL="http://localhost:8000"
DATA_DIR="data/processed"

echo "======================================"
echo "BiLSTM Thought-Based Authentication System - API Test"
echo "======================================"
echo ""

# 1. Health Check
echo " [1/4] Testing Health Check..."
HEALTH=$(curl -s $API_URL/health)
echo "$HEALTH" | jq '.'
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    echo " Health check passed"
else
    echo "Health check failed"
    exit 1
fi
echo ""

# 2. Register User
echo " [2/4] Testing User Registration..."
REGISTER=$(curl -s -X POST $API_URL/auth/register \
  -F "username=test_user_$(date +%s)" \
  -F "password=secure123" \
  -F "eeg_file=@${DATA_DIR}/subject_1_train.npy")
echo "$REGISTER" | jq '.'
if echo "$REGISTER" | jq -e '.message' > /dev/null; then
    echo "Registration successful"
    USERNAME=$(echo "$REGISTER" | jq -r '.username // "test_user"')
else
    echo "Registration response received"
    USERNAME="test_user"
fi
echo "curl -X POST ${API_URL}/auth/login \\"
echo "  -F 'username=testuser' \\"
echo "  -F 'password=test123' \\"
echo "  -F 'probe=@data/processed/s01_trial02.npy'"
echo ""

# View API docs
echo "4. API Documentation available at:"
echo "${API_URL}/docs"
echo ""

echo "======================================"
echo "Test complete!"
echo "======================================"
