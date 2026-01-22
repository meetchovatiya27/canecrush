# Django Project Cleanup Report
## CaneCrush E-commerce Project

Generated: 2026-01-22

---

## 🔴 HIGH PRIORITY - Safe to Delete

### 1. Unused Python Imports (`cane_crush/views.py`)

**Issue**: Unused imports that can be safely removed

**Files to fix**: `cane_crush/views.py`

**Unused imports**:
- `import io` (line 16) - Not used anywhere in the file
- `import requests` (line 19) - Not used anywhere in the file  
- `from django.template.loader import render_to_string` (line 13) - Not used anywhere in the file

**Action**: Remove these imports to clean up the code.

---

### 2. Unused Template Files

#### `cane_crush/templates/payment.html`
- **Status**: ❌ UNUSED
- **Reason**: This is an old Razorpay payment template. The project now uses `online_payment.html` instead.
- **Safe to delete**: ✅ YES
- **Replaced by**: `online_payment.html`

#### `cane_crush/templates/thankyou.html`
- **Status**: ❌ UNUSED
- **Reason**: No view renders this template. The project uses `payment_success.html` instead.
- **Safe to delete**: ✅ YES
- **Replaced by**: `payment_success.html`

#### `cane_crush/templates/text.txt`
- **Status**: ❌ UNUSED
- **Reason**: This is just a text file with content about jaggery sugar, not a template.
- **Safe to delete**: ✅ YES (unless you want to keep it as documentation)

#### `accounts/templates/base.html`
- **Status**: ⚠️ POTENTIALLY UNUSED
- **Reason**: `payment.html` extends `base.html`, but since `payment.html` is unused, this might also be unused.
- **Check**: Verify if any other template extends this file.
- **Safe to delete**: ⚠️ CHECK FIRST

---

### 3. Unused Static Files

#### `cane_crush/static/images/blogs/ChatGPT_files/` (Entire Directory)
- **Status**: ❌ UNUSED
- **Reason**: This appears to be a downloaded ChatGPT HTML page with all its assets. Contains 43 files including:
  - Multiple `.js.download` files
  - CSS files
  - HTML files
  - Images
- **Size**: Likely several MB
- **Safe to delete**: ✅ YES - This is clearly scraped/downloaded content not used in the project

#### `cane_crush/static/images/blogs/ChatGPT.html`
- **Status**: ❌ UNUSED
- **Reason**: Part of the ChatGPT download, not used in the project
- **Safe to delete**: ✅ YES

---

### 4. Unused/Deprecated View Function

#### `send_whatsapp_message()` in `cane_crush/views.py`
- **Status**: ⚠️ DEPRECATED BUT STILL IN URLS
- **Reason**: This function is still in `urls.py` but the cart checkout flow now redirects to `create_order` instead. However, it might still be called from somewhere.
- **Action**: 
  1. Check if any JavaScript or templates still call this endpoint
  2. If not used, remove the view and URL pattern
  3. If still used, keep it but document it

---

## 🟡 MEDIUM PRIORITY - Review Before Deleting

### 5. Duplicate Images in Media Folder

**Location**: `media/product_images/`

**Duplicates found**:
- `Default_Honey_0.jpg` and `Default_Honey_0_46bxe4d.jpg` (same image, different names)
- `Default_Jaggery_Liquid0.jpg` and `Default_Jaggery_Liquid0_Q4VlSvV.jpg`
- `Default_This_1.jpg` and `Default_This_1_mnx9BfK.jpg`
- `Default_This_2.jpg` and `Default_This_2_68UUDrL.jpg`
- `organic_sugar1.jpg` and `organic_sugar1_To8yp1E.jpg`

**Action**: 
1. Check which files are actually referenced in the database
2. Keep only the ones in use
3. Delete duplicates (usually the ones with hash suffixes are Django's duplicate handling)

---

### 6. Incomplete Model Usage

#### `Invoice` Model
- **Status**: ⚠️ PARTIALLY USED
- **Current usage**: 
  - Model exists in `models.py`
  - `view_invoice()` function exists but might not be fully functional
  - Referenced in `payment_success.html` template
- **Issue**: The Invoice model has a foreign key to `OrderItem` instead of `Order`, which seems incorrect
- **Action**: 
  1. Review if Invoice functionality is needed
  2. If not needed, remove model, view, and URL
  3. If needed, fix the model relationship

---

## 🟢 LOW PRIORITY - Keep But Document

### 7. Empty/Placeholder Views

#### `blog()` and `services()` views
- **Status**: ✅ USED BUT MINIMAL
- **Reason**: These views exist and render templates, but the templates might be empty/placeholder pages
- **Action**: Review templates to see if they contain actual content or are placeholders

---

## 📋 Migration Files

### Current Migrations:
- `cane_crush/migrations/0001_initial.py` ✅ KEEP
- `cane_crush/migrations/0002_alter_order_options_alter_payment_options_and_more.py` ✅ KEEP
- `cane_crush/migrations/0003_alter_orderitem_price.py` ✅ KEEP
- `cane_crush/migrations/0004_payment_notification_sent.py` ✅ KEEP
- `accounts/migrations/0001_initial.py` ✅ KEEP
- `accounts/migrations/0002_alter_adminuser_address_alter_adminuser_is_active_and_more.py` ✅ KEEP

**Recommendation**: ✅ KEEP ALL - Migration files should never be deleted as they represent the database schema history.

---

## 🛠️ Recommended Cleanup Actions

### Step 1: Remove Unused Imports
```python
# In cane_crush/views.py, remove:
- import io
- import requests  
- from django.template.loader import render_to_string
```

### Step 2: Delete Unused Templates
```bash
# Delete these files:
- cane_crush/templates/payment.html
- cane_crush/templates/thankyou.html
- cane_crush/templates/text.txt
```

### Step 3: Delete Unused Static Files
```bash
# Delete entire directory:
- cane_crush/static/images/blogs/ChatGPT_files/
- cane_crush/static/images/blogs/ChatGPT.html
```

### Step 4: Review and Clean Duplicate Images
```bash
# Review and delete duplicates in:
- media/product_images/
```

### Step 5: Review Deprecated Views
- Check if `send_whatsapp_message` is still needed
- If not, remove from `urls.py` and `views.py`

---

## 🔍 Tools for Detecting Unused Code

### 1. **vulture** - Dead Code Detector
```bash
pip install vulture
vulture cane_crush/ accounts/
```

### 2. **pylint** - Code Quality Checker
```bash
pip install pylint
pylint cane_crush/ accounts/
```

### 3. **unimport** - Find Unused Imports
```bash
pip install unimport
unimport --check cane_crush/views.py
```

### 4. **Django Check Command**
```bash
python manage.py check --deploy
```

### 5. **Custom Script to Find Unused Templates**
```python
# Check which templates are referenced
grep -r "render.*\.html" cane_crush/views.py accounts/views.py
```

---

## ✅ Best Practices for Django Project Cleanup

1. **Never Delete Migration Files**: Keep all migration files for database history
2. **Use Version Control**: Always commit before deleting files
3. **Test After Cleanup**: Run tests after removing files
4. **Document Removals**: Keep a changelog of what was removed
5. **Incremental Cleanup**: Remove files in small batches and test
6. **Backup First**: Create a backup before major cleanup
7. **Check Dependencies**: Verify files aren't imported dynamically
8. **Review Static Files**: Check if static files are referenced in templates
9. **Check URLs**: Ensure no URLs point to deleted views
10. **Database References**: Check if models/images are referenced in database

---

## 📊 Estimated Space Savings

- ChatGPT_files directory: ~5-10 MB
- Duplicate images: ~2-5 MB
- Unused templates: ~50 KB
- **Total estimated**: ~7-15 MB

---

## ⚠️ Warnings

1. **Before deleting `send_whatsapp_message`**: Check if any JavaScript/AJAX calls still use this endpoint
2. **Before deleting templates**: Verify they're not extended by other templates
3. **Before deleting images**: Check database for references
4. **Before deleting Invoice model**: Review if invoice functionality is planned

---

## 📝 Summary

**Safe to Delete Immediately**:
- 3 unused template files
- ChatGPT_files directory (43 files)
- 3 unused imports

**Review Before Deleting**:
- `send_whatsapp_message` view
- Duplicate images
- Invoice model (if not needed)

**Keep**:
- All migration files
- All models (unless confirmed unused)
- All active templates

---

## 🚀 Next Steps

1. Create a backup: `git commit -am "Backup before cleanup"`
2. Remove unused imports
3. Delete unused templates
4. Delete ChatGPT_files directory
5. Test the application
6. Review duplicate images
7. Document changes

