# 📊 Authentication Logging System

Complete tracking of all enrollment and authentication activities.

---

## 🗄️ **What Gets Logged**

### **Enrollment Logs**
- ✅ Username
- ✅ Password strength (Weak/Medium/Strong/Very Strong)
- ✅ EEG file(s) used for enrollment
- ✅ Timestamp
- ✅ Success/failure status
- ✅ User ID (if successful)

### **Authentication Logs**
- ✅ Username
- ✅ EEG file used for authentication
- ✅ Similarity score
- ✅ Calibrated probability
- ✅ Spoof detection score
- ✅ Spoof detected (yes/no)
- ✅ Authentication result (success/failure)
- ✅ Timestamp
- ✅ Result message

---

## 📁 **Database Location**

**File:** `d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth\auth_logs.db`

**Format:** SQLite database with 2 tables:
1. `enrollment_logs`
2. `authentication_logs`

---

## 🔍 **How to View Logs**

### **Method 1: Python Script (Recommended)**

```cmd
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"
venv\Scripts\activate
python view_auth_logs.py
```

**Output:**
```
==================================================================================================
ENROLLMENT HISTORY
==================================================================================================
+----+------------+-------------------+-------------------+---------------------+---------+---------+
| ID | Username   | Password Strength | Enrollment File   | Timestamp           | Success | User ID |
+====+============+===================+===================+=====================+=========+=========+
|  1 | Sruthi_15  | Strong            | s01_trial_00.npy  | 2025-10-18 08:42:15 | 1       | 11      |
+----+------------+-------------------+-------------------+---------------------+---------+---------+

==================================================================================================
AUTHENTICATION HISTORY
==================================================================================================
+----+------------+-------------------+--------+----------------+-------------+----------+---------------+---------------------+---------------------------+
| ID | Username   | Auth File         | Score  | Calibrated Prob| Spoof Score | Is Spoof | Authenticated | Timestamp           | Message                   |
+====+============+===================+========+================+=============+==========+===============+=====================+===========================+
|  1 | Sruthi_15  | s01_trial_01.npy  | 0.9768 | 0.9800         | 0.000020    | 0        | 1             | 2025-10-18 08:45:30 | Authentication successful |
+----+------------+-------------------+--------+----------------+-------------+----------+---------------+---------------------+---------------------------+

==================================================================================================
USER STATISTICS
==================================================================================================

👤 User: Sruthi_15
   Password Strength: Strong
   Enrollment File: s01_trial_00.npy
   Enrolled: 2025-10-18 08:42:15
   Total Auth Attempts: 3
   Successful: 2 (66.7%)
   Avg Score: 0.8542
   Score Range: 0.4521 - 0.9768
```

---

### **Method 2: Export to CSV**

```cmd
python view_auth_logs.py
# When prompted, type 'y' to export
```

**Output:** `auth_logs.csv` with all data in spreadsheet format

---

### **Method 3: Direct SQL Query**

```cmd
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"
sqlite3 auth_logs.db
```

```sql
-- View all enrollments
SELECT * FROM enrollment_logs ORDER BY timestamp DESC;

-- View all authentications
SELECT * FROM authentication_logs ORDER BY timestamp DESC;

-- View specific user
SELECT * FROM authentication_logs WHERE username = 'Sruthi_15';

-- Get success rate per user
SELECT 
    username,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN authenticated = 1 THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(score), 4) as avg_score
FROM authentication_logs
GROUP BY username;
```

---

## 📊 **Password Strength Criteria**

| Strength | Criteria |
|----------|----------|
| **Weak** | < 8 characters, no variety |
| **Medium** | 8+ characters, some variety |
| **Strong** | 12+ characters, uppercase, lowercase, numbers |
| **Very Strong** | 16+ characters, uppercase, lowercase, numbers, special chars |

**Examples:**
- `pass123` → Weak
- `Password123` → Medium
- `SecurePass123!` → Strong
- `MyV3ry$ecur3P@ssw0rd!` → Very Strong

---

## 🔄 **Automatic Logging**

Logging happens automatically when:

1. **User enrolls** (registers)
   - Logs username, password strength, enrollment file
   
2. **User authenticates** (logs in)
   - Logs username, auth file, scores, result

**No manual action required!**

---

## 📈 **Example Use Cases**

### **1. Check if user enrolled**
```python
from src.api.auth_logger import AuthLogger

logger = AuthLogger()
enrollments = logger.get_enrollment_history('Sruthi_15')
print(enrollments)
```

### **2. Get authentication history**
```python
auth_history = logger.get_authentication_history('Sruthi_15')
for record in auth_history:
    print(f"File: {record[2]}, Score: {record[3]}, Result: {record[7]}")
```

### **3. Get user statistics**
```python
stats = logger.get_user_stats('Sruthi_15')
print(f"Password Strength: {stats['enrollment'][0]}")
print(f"Success Rate: {stats['auth_stats'][1] / stats['auth_stats'][0] * 100}%")
```

---

## 🎯 **What You Requested**

✅ **Username** - Stored in both tables  
✅ **Password** - Not stored (only strength rating)  
✅ **Password Strength** - Weak/Medium/Strong/Very Strong  
✅ **Enrollment File** - File name(s) used to enroll  
✅ **Authentication File** - File name used to authenticate  
✅ **Scores** - Similarity score, calibrated probability, spoof score  
✅ **Results** - Success/failure with timestamp  

---

## 🚀 **Quick Start**

1. **Restart backend** (to load new logging):
   ```cmd
   cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"
   venv\Scripts\activate
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Enroll a user** (via frontend or API)

3. **Authenticate** (via frontend or API)

4. **View logs**:
   ```cmd
   python view_auth_logs.py
   ```

---

## 📁 **Files Created**

1. **`src/api/auth_logger.py`** - Logging system
2. **`view_auth_logs.py`** - View logs script
3. **`auth_logs.db`** - SQLite database (created automatically)
4. **`auth_logs.csv`** - CSV export (optional)

---

## ✅ **Summary**

All enrollment and authentication activities are now **automatically logged** with complete details including:
- Who (username)
- What (files used)
- When (timestamp)
- How (password strength)
- Result (success/failure with scores)

**Just restart the backend and start using the system - logging happens automatically!** 🎉
