# 🚨 QUICK FIX - Updated Render Settings

## ❌ Problem:
```
python: can't open file '/opt/render/project/src/uvicorn': [Errno 2] No such file or directory
```

## ✅ Solution:

### **Updated Render Configuration:**

```
Name: data-cleaner-api
Environment: Python 3
Branch: main
Root Directory: (leave empty)

Build Command: pip install --no-cache-dir fastapi uvicorn python-multipart pandas numpy

Start Command: uvicorn main_robust:app --host 0.0.0.0 --port $PORT
```

## 🔧 Key Fix:
- **OLD (Broken):** `python uvicorn main_robust:app --host 0.0.0.0 --port $PORT`
- **NEW (Fixed):** `uvicorn main_robust:app --host 0.0.0.0 --port $PORT`

## 🚀 Steps to Fix:

1. **Go to Render Dashboard**
2. **Select your service**
3. **Go to Settings tab**
4. **Update Start Command to:**
   ```
   uvicorn main_robust:app --host 0.0.0.0 --port $PORT
   ```
5. **Click "Save Changes"**
6. **Redeploy manually or push new code**

## 📋 Alternative Commands (if needed):

### Option 1 (Recommended):
```
Start Command: uvicorn main_robust:app --host 0.0.0.0 --port $PORT
```

### Option 2 (With Python module):
```
Start Command: python -m uvicorn main_robust:app --host 0.0.0.0 --port $PORT
```

### Option 3 (Gunicorn + Uvicorn):
```
Build Command: pip install --no-cache-dir fastapi uvicorn gunicorn pandas numpy
Start Command: gunicorn -w 1 -k uvicorn.workers.UvicornWorker main_robust:app --bind 0.0.0.0:$PORT
```

## 🎯 Expected Result:
- ✅ Build succeeds
- ✅ Enhanced classifier loads
- ✅ API starts on correct port
- ✅ 90%+ classification accuracy

## 🔍 To Verify Fix:
1. **Check build logs** - should show "Installing dependencies..."
2. **Check app logs** - should show "Using Enhanced Column Classifier" or fallback message
3. **Test endpoint:** `https://your-service.onrender.com/health`

---

**The fix is simply removing `python` from the start command! Uvicorn should be called directly.**
