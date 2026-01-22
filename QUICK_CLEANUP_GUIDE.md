# Quick Cleanup Guide

## ✅ Already Fixed
- Removed unused imports from `cane_crush/views.py`:
  - `import io`
  - `import requests`
  - `from django.template.loader import render_to_string`
- Fixed duplicate imports in `cane_crush/views.py`

## 🗑️ Safe to Delete Now

### Templates (3 files)
```bash
rm cane_crush/templates/payment.html
rm cane_crush/templates/thankyou.html
rm cane_crush/templates/text.txt
```

### Static Files
```bash
rm -rf cane_crush/static/images/blogs/ChatGPT_files/
rm cane_crush/static/images/blogs/ChatGPT.html
```

## ⚠️ Review Before Deleting

### Deprecated View Function
**File**: `cane_crush/views.py` - `send_whatsapp_message()` function (line ~297)
**Status**: Still in URLs but not called from cart anymore
**Action**: 
1. Check if any external API or mobile app calls this endpoint
2. If not used, remove from `urls.py` and `views.py`

### Invoice Model
**File**: `cane_crush/models.py` - `Invoice` class
**Status**: Partially implemented, has incorrect foreign key
**Action**: Decide if invoice functionality is needed, then either fix or remove

## 🔍 Verification Commands

```bash
# Check for unused imports
python -m unimport --check cane_crush/views.py

# Check Django project health
python manage.py check

# Find unused templates (manual check)
grep -r "render.*payment.html" cane_crush/
grep -r "render.*thankyou.html" cane_crush/

# Check if send_whatsapp_message is called
grep -r "send_whatsapp_message" cane_crush/templates/
grep -r "/send_whatsapp_message" cane_crush/static/
```

## 📋 Cleanup Checklist

- [x] Remove unused imports
- [ ] Delete unused templates
- [ ] Delete ChatGPT_files directory
- [ ] Review and remove duplicate images
- [ ] Review send_whatsapp_message usage
- [ ] Test application after cleanup
- [ ] Run `python manage.py check`
- [ ] Run `python manage.py collectstatic` (if needed)

## 🚀 Automated Cleanup

Run the cleanup script:
```bash
python cleanup_script.py
```

Or use auto mode (use with caution):
```bash
python cleanup_script.py --auto
```

