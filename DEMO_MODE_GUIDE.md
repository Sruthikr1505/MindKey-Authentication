# MindKey Demo Mode - User Guide

## 🎮 How to Use Without Hardware

Your MindKey system now supports **Demo Mode** - users can authenticate without EEG hardware by using pre-loaded brain pattern samples!

---

## 📋 **For Users: How to Authenticate**

### Step 1: Enroll (Register)

1. Go to: `http://localhost:5173`
2. Click "**Enroll Now**"
3. Fill in:
   - Username: `demo_user`
   - Password: `SecurePass123`
4. **Download Sample EEG:**
   - Visit: `http://localhost:8000/samples/s01_trial00`
   - This downloads `s01_trial00.npy`
5. **Upload the file** in the enrollment form
6. Click "**Enroll Now**"
7. ✅ Success! You're registered

### Step 2: Authenticate (Login)

1. Switch to "**Sign In**" mode
2. Fill in:
   - Username: `demo_user`
   - Password: `SecurePass123`
3. **Download Different Sample** (same person):
   - Visit: `http://localhost:8000/samples/s01_trial01`
   - This downloads `s01_trial01.npy`
4. **Upload the file**
5. Click "**Authenticate**"
6. ✅ Success! Authenticated as genuine user

### Step 3: Test Impostor Detection

1. Try to login as `demo_user`
2. **Download Different Person's EEG:**
   - Visit: `http://localhost:8000/samples/s02_trial00`
   - This is Subject 2 (different person)
3. **Upload the file**
4. Click "**Authenticate**"
5. ❌ Access Denied! Impostor detected

---

## 🎯 **Available Sample EEG Files**

| Sample ID | Description | Use For |
|-----------|-------------|---------|
| `s01_trial00` | Subject 1 - Relaxed | ✅ Enrollment |
| `s01_trial01` | Subject 1 - Focused | ✅ Genuine Auth |
| `s01_trial02` | Subject 1 - Active | ✅ Genuine Auth |
| `s02_trial00` | Subject 2 - Relaxed | ❌ Impostor Test |
| `s02_trial01` | Subject 2 - Focused | ❌ Impostor Test |
| `s03_trial00` | Subject 3 - Relaxed | ❌ Impostor Test |

---

## 🔗 **Quick Download Links**

### For Enrollment:
```
http://localhost:8000/samples/s01_trial00
```

### For Genuine Authentication:
```
http://localhost:8000/samples/s01_trial01
http://localhost:8000/samples/s01_trial02
```

### For Impostor Testing:
```
http://localhost:8000/samples/s02_trial00
http://localhost:8000/samples/s03_trial00
```

---

## 📊 **API Endpoints**

### List All Samples:
```bash
curl http://localhost:8000/samples/list | jq
```

**Response:**
```json
{
  "samples": [
    {
      "id": "s01_trial00",
      "name": "Subject 1 - Trial 0 (Relaxed)",
      "subject": 1,
      "description": "Use for enrollment"
    },
    ...
  ]
}
```

### Download Sample:
```bash
curl -O http://localhost:8000/samples/s01_trial00
```

---

## 🎓 **For Presentations/Demos**

### Scenario 1: Successful Authentication
1. **Enroll**: Use `s01_trial00`
2. **Login**: Use `s01_trial01`
3. **Result**: ✅ Authenticated (Score: ~90%)

### Scenario 2: Impostor Detection
1. **Enroll**: Use `s01_trial00`
2. **Login**: Use `s02_trial00` (different person)
3. **Result**: ❌ Rejected (Score: ~25%)

### Scenario 3: Multiple Genuine Attempts
1. **Enroll**: Use `s01_trial00`
2. **Login 1**: Use `s01_trial01` → ✅ Success
3. **Login 2**: Use `s01_trial02` → ✅ Success
4. Shows consistency of genuine user

---

## 💡 **Tips for Users**

1. **Same Subject = Genuine**
   - Enroll with `s01_trial00`
   - Auth with `s01_trial01` or `s01_trial02`
   - Result: Authenticated ✅

2. **Different Subject = Impostor**
   - Enroll with `s01_trial00`
   - Auth with `s02_trial00` or `s03_trial00`
   - Result: Rejected ❌

3. **View Your Results**
   - After authentication, check the Dashboard
   - See similarity scores
   - View decision explanation graphs

---

## 🚀 **For Deployment**

When deploying to production:

1. **Add Download Buttons** in frontend
2. **Sample Library Page** showing all available patterns
3. **Instructions** for users
4. **Demo Video** showing the process

---

## 📱 **Future: Real Hardware**

This demo mode is perfect for:
- ✅ Testing
- ✅ Presentations
- ✅ Academic demonstrations
- ✅ Proof of concept

For production, integrate with:
- Muse 2 headset ($250)
- Emotiv EPOC X ($850)
- OpenBCI ($500)

---

## ✨ **Summary**

**Users don't need hardware!** They can:
1. Download sample EEG files from your API
2. Upload them like regular files
3. Test the full authentication flow
4. See genuine vs impostor detection

**Perfect for demos, testing, and showcasing your project!** 🎉
