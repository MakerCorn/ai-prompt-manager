# Changelog

## [v0.2.0] - 2025-06-11 - Enhanced Testing & Model Configuration

### 🧪 New Testing Features

#### **Prompt Testing in Editor**
- **Test Prompt Section**: Added interactive testing capability directly in the prompt editor
- **Test Input Field**: Optional context input to test prompts with specific scenarios
- **Real-time Testing**: Test prompts using configured LLM models without leaving the editor
- **Status Feedback**: Clear success/error indicators and detailed output display
- **Compact UI**: Responsive design that integrates seamlessly with existing editor

#### **Separate Model Configurations**
- **Test Service Configuration**: Dedicated model configuration specifically for prompt testing
- **Independent Settings**: Test service can use different API endpoints, keys, and models
- **Fallback Logic**: Gracefully falls back to primary configuration if test config not set
- **Configuration Management**: Full CRUD operations for test service settings

### ⚙️ Configuration Enhancements

#### **Three-Tier Model System**
1. **Primary AI Service**: For general prompt execution and production use
2. **Enhancement Service**: For prompt optimization and improvement (existing)
3. **Test Service**: For prompt testing and development (new)

#### **Flexible Model Selection**
- **Service Types**: Support for OpenAI, LM Studio, Ollama, Llama.cpp across all configurations
- **Model Optimization**: Use fast models for testing, powerful models for enhancement
- **Cost Control**: Configure cheaper models for testing, premium models for production
- **Environment Flexibility**: Different endpoints for different purposes

### 🛠️ Technical Improvements

#### **Backend Architecture**
- **Configuration Storage**: Persistent storage for test service configurations
- **User Isolation**: Test configurations are user-specific in multi-tenant mode
- **Error Handling**: Comprehensive error handling for configuration and testing
- **Validation**: Proper authentication and configuration validation

#### **UI/UX Enhancements**
- **Internationalization**: Added translation keys for testing functionality
- **Consistent Design**: Testing UI follows existing design patterns
- **Responsive Layout**: Works across desktop and mobile interfaces
- **Status Indicators**: Clear visual feedback for all testing operations

### 🔧 Code Quality

#### **Function Organization**
- **Modular Functions**: Clean separation of test and configuration logic
- **Event Handling**: Proper Gradio event handler implementation
- **Code Reuse**: Leveraged existing AI service integration
- **Documentation**: Clear function documentation and comments

### 📋 Configuration Structure

```python
# Test Configuration Example
{
    'service_type': 'openai',
    'api_endpoint': 'http://localhost:1234/v1',
    'api_key': '',
    'model_name': 'gpt-3.5-turbo'  # Fast model for testing
}

# Enhancement Configuration Example  
{
    'service_type': 'openai',
    'api_endpoint': 'https://api.openai.com/v1',
    'api_key': 'sk-...',
    'model_name': 'gpt-4'  # Powerful model for enhancement
}
```

### ✨ User Benefits

1. **Rapid Iteration**: Test prompts immediately during development
2. **Cost Efficiency**: Use appropriate models for different tasks
3. **Better Workflow**: Seamless testing without configuration switching
4. **Quality Assurance**: Validate prompts before saving or deployment
5. **Flexibility**: Configure optimal models for each use case

---

## [v0.1.0] - 2025-06-09 - Unified Application

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