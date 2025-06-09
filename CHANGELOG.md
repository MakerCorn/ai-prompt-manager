# Changelog

## [v2.0.0] - 2025-01-09 - Unified Application

### 🚀 Major Changes

#### **Combined Single User & Multi-Tenant Architecture**
- **Unified Codebase**: Merged single-user and multi-tenant versions into one application
- **Mode Detection**: Automatic mode selection based on environment variables
- **Backward Compatibility**: Existing single-user functionality preserved
- **Universal Launcher**: New `run.py` launcher supports all modes

#### **File Structure Changes**
- `prompt_manager_mt.py` → `prompt_manager.py` (main unified version)
- `prompt_manager.py` → `legacy/prompt_manager_single_user_legacy.py` (moved to legacy)
- `prompt_data_manager_old.py` → `legacy/` (moved to legacy)
- Added `run.py` - Universal launcher with mode detection

#### **Licensing Updates**
- **Standardized Licensing**: All code files now have consistent Non-Commercial License headers
- **Copyright Notice**: Updated all files with "Copyright (c) 2025 MakerCorn"
- **License Compliance**: Ensured all modules include proper license references

### ✨ New Features

#### **Environment-Based Configuration**
```bash
# Control application mode
MULTITENANT_MODE=true|false    # Enable/disable multi-tenant features
ENABLE_API=true|false          # Enable/disable REST API endpoints

# Database selection
DB_TYPE=sqlite|postgres        # Choose database backend
```

#### **Universal Launcher**
- **Smart Detection**: Automatically detects desired mode from environment
- **Flexible Deployment**: Single command supports all configurations
- **Clear Feedback**: Startup messages show active features and access URLs

### 🔧 Technical Improvements

#### **Code Organization**
- **Reduced Redundancy**: Eliminated duplicate functionality between versions
- **Maintainability**: Single codebase easier to maintain and update
- **Feature Parity**: All features available in unified version

#### **Deployment Options**
1. **Single-User Mode**: `MULTITENANT_MODE=false run.py`
2. **Multi-Tenant Mode**: `MULTITENANT_MODE=true run.py` 
3. **Full-Featured Mode**: `MULTITENANT_MODE=true ENABLE_API=true run.py`

### 📚 Documentation Updates

#### **Updated README**
- **Configuration Guide**: Comprehensive environment variable documentation
- **Mode Examples**: Clear examples for different deployment scenarios
- **Launch Options**: Updated launch commands for new structure

#### **Migration Guide**
- **Legacy Support**: Existing installations continue to work
- **Upgrade Path**: Clear instructions for migrating to unified version
- **Environment Setup**: New configuration options explained

### 🧹 Cleanup

#### **File Management**
- **Legacy Folder**: Moved old versions to `legacy/` folder
- **Reduced Clutter**: Eliminated redundant files
- **Clear Structure**: More intuitive file organization

#### **Import Updates**
- **Unified Imports**: All launcher scripts import from `prompt_manager`
- **Consistent Naming**: Standardized module references
- **Clean Dependencies**: Removed circular dependencies

### 🔄 Migration Notes

#### **For Existing Users**
- **Zero Downtime**: Existing `prompt_manager.py` calls work unchanged
- **Database Compatibility**: All existing databases work with new version
- **Feature Access**: All previous features remain available

#### **For New Deployments**
- **Recommended**: Use `run.py` for new installations
- **Configuration**: Set environment variables for desired features
- **Flexibility**: Easy switching between modes without code changes

### 🎯 Benefits

1. **Simplified Deployment**: One application, multiple modes
2. **Reduced Maintenance**: Single codebase to maintain
3. **Better Testing**: Unified test suite covers all scenarios
4. **Clear Licensing**: Consistent licensing across all files
5. **Future-Proof**: Easier to add new features to unified architecture

---

### Files Changed
- ✅ Combined `prompt_manager.py` (unified version)
- ✅ Updated `run_mt.py` and `run_mt_with_api.py` imports
- ✅ Added licensing headers to all `.py` files
- ✅ Created `run.py` universal launcher
- ✅ Updated `README.md` with configuration guide
- ✅ Moved legacy files to `legacy/` folder
- ✅ Created this changelog

### Compatibility
- ✅ **Database**: Existing SQLite/PostgreSQL databases work unchanged
- ✅ **API**: All REST API endpoints remain the same
- ✅ **Authentication**: Multi-tenant auth system unchanged
- ✅ **Features**: All existing features preserved
- ✅ **Environment**: Existing environment variables still work