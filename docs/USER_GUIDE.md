# 📖 AI Prompt Manager User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Managing Prompts](#managing-prompts)
3. [Prompt Visibility](#prompt-visibility)
4. [Using the Prompt Builder](#using-the-prompt-builder)
5. [Search and Organization](#search-and-organization)
6. [AI Services](#ai-services)
7. [API Access](#api-access)
8. [Multi-Language Support](#multi-language-support)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Enhanced Dashboard Experience

The AI Prompt Manager features a redesigned dashboard with improved organization and user experience:

#### **Quick Actions Panel**
- **📝 Create New Prompt**: Start building your perfect prompt with guided creation
- **📄 Browse Prompts**: Access your personal prompt library with advanced filtering
- **📚 Rules Library**: Manage AI behavior guidelines and constraints
- **📋 Templates**: Use pre-built templates to save time
- **🔧 Prompt Builder**: Combine multiple prompts visually with drag-and-drop
- **⚙️ Settings**: Configure preferences and integrations

#### **Recent Prompts Section**
- View your most recently created and modified prompts
- Quick access to edit and execute actions
- Visual indicators for prompt visibility (🔒 Private, 🌐 Public)
- Tag display and category organization

#### **Smart Interface Features**
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Theme Compatibility**: Full light/dark mode support with system preference detection
- **Dynamic Content**: Panels automatically hide when empty for cleaner interface
- **Multi-language Support**: All dashboard elements available in 10 languages

### Installation

The AI Prompt Manager can be installed via PyPI or run directly from the source code:

```bash
# Install from PyPI
pip install promptman
python -m promptman

# Or install from source
git clone https://github.com/makercorn/ai-prompt-manager.git
cd ai-prompt-manager
poetry install
poetry run python run.py
```

### First Time Setup

When you first start the application, you'll be prompted to:

1. **Choose your deployment mode**:
   - **Single-User Mode**: No authentication required, ideal for personal use
   - **Multi-Tenant Mode**: Full authentication with user management

2. **Set up your account** (Multi-Tenant Mode only):
   - Create admin account with email and password
   - Configure tenant settings

3. **Access the web interface**:
   - Open your browser to `http://localhost:7860`
   - Login with your credentials (if multi-tenant mode)

---

## Managing Prompts

### Creating a New Prompt

1. **Navigate to the Prompts section** in the main navigation
2. **Click "Create New Prompt"**
3. **Fill in the prompt details**:
   - **Name**: Unique identifier for your prompt
   - **Title**: Display name for the prompt
   - **Content**: The actual prompt text
   - **Category**: Organize prompts into categories
   - **Tags**: Add comma-separated tags for easy searching
   - **Visibility**: Choose who can see this prompt (Multi-Tenant Mode only)

4. **Save the prompt** by clicking "Create Prompt"

### Editing Prompts

1. **Find the prompt** you want to edit in the prompt library
2. **Click the "Edit" button** or the prompt name
3. **Make your changes** in the edit form
4. **Save changes** by clicking "Update Prompt"

### Deleting Prompts

1. **Navigate to the prompt** you want to delete
2. **Click the "Delete" button** (usually a trash icon)
3. **Confirm the deletion** when prompted

> ⚠️ **Warning**: Deleting a prompt is permanent and cannot be undone.

---

## Prompt Visibility

> 👥 **Note**: Visibility features are only available in Multi-Tenant Mode. In Single-User Mode, all prompts are accessible to the user.

### Understanding Visibility Levels

The AI Prompt Manager supports two visibility levels for prompts:

#### 🔒 Private Prompts
- **Visible only to you**: Only the creator can see and use the prompt
- **Default setting**: New prompts are private by default
- **Use case**: Personal prompts, work-in-progress content, sensitive information

#### 🌐 Public Prompts
- **Visible to all users in your tenant**: All users in your organization can see and use the prompt
- **Shared knowledge**: Enables team collaboration and knowledge sharing
- **Use case**: Team templates, shared workflows, approved content

### Setting Prompt Visibility

#### When Creating a Prompt
1. In the **Create Prompt** form, look for the **Visibility** section
2. Select either:
   - 🔒 **Private**: Only you can see this prompt
   - 🌐 **Public**: All users in your tenant can see this prompt
3. The default is **Private** for security

#### When Editing a Prompt
1. Open the prompt for editing
2. Find the **Visibility** dropdown in the edit form
3. Change the visibility setting as needed
4. Save your changes

### Viewing Prompts by Visibility

#### Your Dashboard View
By default, you'll see:
- ✅ **All your own prompts** (both private and public)
- ✅ **Public prompts from other users** in your tenant
- ❌ **Private prompts from other users** (never visible)

#### Filtering by Visibility
Use the filter options to narrow down your view:

1. **All Prompts** (default): Your prompts + public prompts from others
2. **My Prompts Only**: Only your own prompts (private + public)
3. **Public Prompts**: Only public prompts from your tenant
4. **Private Prompts**: Only your private prompts

### Best Practices for Visibility

#### When to Use Private Prompts
- **Work in progress**: Prompts you're still developing
- **Personal notes**: Prompts with personal information or preferences
- **Experimental content**: Untested or draft prompts
- **Sensitive information**: Prompts containing confidential data

#### When to Use Public Prompts
- **Team templates**: Standardized prompts for team use
- **Best practices**: Proven prompts that work well
- **Shared workflows**: Prompts that support team processes
- **Knowledge sharing**: Educational or reference prompts

#### Security Considerations
- **Review before making public**: Ensure no sensitive information is included
- **Use descriptive titles**: Help teammates understand the prompt's purpose
- **Keep it updated**: Maintain public prompts as team standards change
- **Regular audits**: Periodically review public prompts for relevance

### Visibility Statistics

Track your prompt visibility distribution:

1. **Navigate to Settings** or **Dashboard**
2. **View Visibility Statistics** to see:
   - Total prompts in your tenant
   - Number of private vs. public prompts
   - Percentage breakdown
   - Usage patterns

---

## Using the Prompt Builder

### Overview

The Prompt Builder is a drag-and-drop interface that allows you to combine multiple prompts and templates to create sophisticated AI workflows.

### Creating a Combined Prompt

1. **Navigate to the Prompt Builder**
2. **Select a template type**:
   - **Sequential**: Combine prompts in order
   - **Sections**: Organize prompts into sections
   - **Layered**: Apply prompts in layers
   - **Custom**: Create your own structure

3. **Add prompts to your combination**:
   - Drag prompts from the library
   - Drop them into the builder area
   - Arrange them in your desired order

4. **Preview the result** in real-time
5. **Save the combined prompt** with a new name

### Template Types Explained

#### Sequential Template
```
Prompt 1 → Prompt 2 → Prompt 3
```
- Prompts are combined in order
- Each prompt builds on the previous one
- Great for multi-step processes

#### Sections Template
```
[Section 1: Prompt A]
[Section 2: Prompt B]
[Section 3: Prompt C]
```
- Prompts are organized into sections
- Each section has a clear purpose
- Ideal for structured documents

#### Layered Template
```
Base Layer: Prompt 1
Enhancement Layer: Prompt 2
Final Layer: Prompt 3
```
- Prompts are applied as layers
- Each layer refines the previous one
- Perfect for iterative improvements

---

## Search and Organization

### Searching Prompts

The search functionality helps you find prompts quickly:

#### Basic Search
1. **Use the search bar** at the top of the prompt library
2. **Type your search term**
3. **Press Enter** or click the search button

#### Advanced Search Options
- **Search in specific fields**: Name, title, content, or tags
- **Filter by category**: Narrow results to specific categories
- **Filter by visibility**: Show only private or public prompts
- **Combine filters**: Use multiple filters for precise results

#### Search Tips
- **Use quotes**: Search for exact phrases with "quotation marks"
- **Use tags**: Search by tags to find related prompts
- **Use categories**: Filter by category for organized browsing
- **Use partial matches**: Search will find partial word matches

### Organizing with Categories

#### Creating Categories
Categories are created automatically when you assign them to prompts. Common categories include:
- **Business**: Business-related prompts
- **Creative**: Creative writing prompts
- **Technical**: Technical documentation prompts
- **Personal**: Personal use prompts
- **Templates**: Reusable template prompts

#### Best Practices
- **Use consistent naming**: Stick to a naming convention
- **Keep categories broad**: Avoid too many narrow categories
- **Use subcategories**: Use tags for more specific classification

### Using Tags

Tags provide fine-grained organization:

#### Adding Tags
1. **When creating or editing a prompt**
2. **Add comma-separated tags** in the tags field
3. **Use descriptive keywords** that you'll remember

#### Tag Suggestions
- **Purpose**: `template`, `example`, `workflow`
- **Audience**: `team`, `client`, `personal`
- **Status**: `draft`, `approved`, `archived`
- **Topic**: `marketing`, `support`, `development`

---

## AI Services

### Overview

The AI Prompt Manager integrates with various AI services to provide optimization, translation, and enhancement capabilities.

### Supported AI Providers

#### OpenAI
- **Models**: GPT-4, GPT-3.5 Turbo
- **Features**: Text generation, optimization
- **Setup**: Add your OpenAI API key in settings

#### Anthropic Claude
- **Models**: Claude 3 (Opus, Sonnet, Haiku)
- **Features**: Advanced reasoning, code generation
- **Setup**: Add your Anthropic API key in settings

#### Google Gemini
- **Models**: Gemini Pro, Gemini Ultra
- **Features**: Multimodal capabilities
- **Setup**: Add your Google API key in settings

#### Local Models
- **Ollama**: Run models locally
- **LM Studio**: Local model deployment
- **llama.cpp**: Direct model execution

### AI-Powered Features

#### Prompt Optimization
1. **Select a prompt** to optimize
2. **Click "Optimize"** in the prompt actions
3. **Choose optimization type**:
   - General improvement
   - Cost reduction
   - Performance enhancement
4. **Review the optimized version**
5. **Save or apply the changes**

#### Language Translation
1. **Select a prompt** to translate
2. **Click "Translate"** in the prompt actions
3. **Choose target language**
4. **Review the translation**
5. **Save as new prompt** or replace existing

#### Content Enhancement
- **Grammar checking**: Automatic grammar correction
- **Style improvement**: Enhance writing style
- **Clarity enhancement**: Make prompts clearer and more effective

---

## API Access

### Getting Started with the API

#### Enabling API Access
1. **Start the application with API enabled**:
   ```bash
   poetry run python run.py --with-api
   ```
2. **API will be available at**: `http://localhost:7861`
3. **Documentation available at**: `http://localhost:7861/docs`

#### Creating API Tokens
1. **Navigate to Settings → API Tokens**
2. **Click "Create New Token"**
3. **Give your token a name**
4. **Set expiration date** (optional)
5. **Copy the token** (shown only once)
6. **Use the token** in your API requests

#### Using API Tokens
Include the token in your request headers:
```bash
curl -H "Authorization: Bearer apm_your_token_here" \
     http://localhost:7861/api/prompts
```

### API Endpoints with Visibility

#### List Prompts with Visibility Filtering
```bash
# Get all prompts (default behavior)
curl -H "Authorization: Bearer apm_your_token" \
     "http://localhost:7861/api/prompts"

# Get only public prompts
curl -H "Authorization: Bearer apm_your_token" \
     "http://localhost:7861/api/prompts?visibility=public"

# Get only your own prompts
curl -H "Authorization: Bearer apm_your_token" \
     "http://localhost:7861/api/prompts?include_public=false"
```

#### Search with Visibility
```bash
# Search with visibility filtering
curl -H "Authorization: Bearer apm_your_token" \
     "http://localhost:7861/api/search?q=template&visibility=public"
```

#### Get Visibility Statistics
```bash
curl -H "Authorization: Bearer apm_your_token" \
     "http://localhost:7861/api/prompts/visibility-stats"
```

For complete API documentation, see [API.md](API.md).

---

## Multi-Language Support

### Supported Languages

The AI Prompt Manager supports 10 languages:
- **English** (en) - Default
- **Spanish** (es)
- **French** (fr)
- **German** (de)
- **Italian** (it)
- **Portuguese** (pt)
- **Dutch** (nl)
- **Russian** (ru)
- **Chinese** (zh)
- **Japanese** (ja)

### Changing Language

#### In the Web Interface
1. **Look for the language selector** in the top navigation
2. **Click on the current language** (e.g., "English")
3. **Select your preferred language** from the dropdown
4. **The interface will update immediately**

#### Language Persistence
- **Your language choice is remembered** across sessions
- **Each user can have their own language preference**
- **Language setting is stored in your browser**

### Contributing Translations

#### Adding New Languages
1. **Check the `languages/` directory** for existing language files
2. **Copy `languages/en.json`** as a template
3. **Translate all strings** to your target language
4. **Test the translation** in the application
5. **Submit a pull request** with your translation

#### Improving Existing Translations
1. **Find the language file** in `languages/[language_code].json`
2. **Edit the translations** as needed
3. **Test your changes** in the application
4. **Submit a pull request** with improvements

---

## Advanced Features

### Theme System

#### Light and Dark Modes
- **Light Mode**: Default bright theme
- **Dark Mode**: Dark theme for low-light environments
- **System Mode**: Automatically matches your system preference

#### Changing Themes
1. **Click the theme toggle** in the top navigation
2. **Cycle through options**: Light → Dark → System
3. **Your preference is saved** automatically

### Keyboard Shortcuts

#### Navigation
- **Ctrl+/** (or **Cmd+/**): Open search
- **Ctrl+N** (or **Cmd+N**): Create new prompt
- **Ctrl+S** (or **Cmd+S**): Save current prompt
- **Esc**: Close modal dialogs

#### Prompt Management
- **Tab**: Navigate between form fields
- **Ctrl+Enter** (or **Cmd+Enter**): Save and continue editing
- **Ctrl+D** (or **Cmd+D**): Duplicate current prompt

### Backup and Export

#### Exporting Prompts
1. **Navigate to Settings → Export**
2. **Choose export format**:
   - JSON (for backup)
   - CSV (for spreadsheets)
   - YAML (for configuration)
3. **Select prompts to export**:
   - All prompts
   - By category
   - By visibility
   - Selected prompts
4. **Download the export file**

#### Importing Prompts
1. **Navigate to Settings → Import**
2. **Choose import format**
3. **Upload your file**
4. **Review the import preview**
5. **Confirm the import**

### Integration Features

#### GitHub Integration
- **Export to GitHub format**: YAML files compatible with GitHub Actions
- **Import from GitHub**: Import prompts from GitHub repositories
- **Version control**: Track changes to your prompts

#### Webhook Support
- **Prompt created**: Trigger when new prompts are created
- **Prompt updated**: Trigger when prompts are modified
- **Visibility changed**: Trigger when prompt visibility changes

---

## Troubleshooting

### Common Issues

#### Can't See Public Prompts
**Problem**: Public prompts from other users are not showing up.

**Solution**:
1. **Check you're in Multi-Tenant Mode**: Visibility only works in multi-tenant deployments
2. **Verify filter settings**: Make sure "include_public" is enabled
3. **Check tenant isolation**: You can only see public prompts from your own tenant
4. **Refresh the page**: Sometimes a page refresh helps

#### Visibility Option Not Available
**Problem**: Can't find visibility settings when creating prompts.

**Solution**:
1. **Confirm Multi-Tenant Mode**: Visibility is disabled in single-user mode
2. **Check user permissions**: Some roles may have restricted visibility options
3. **Update your installation**: Ensure you have the latest version with visibility features

#### Search Not Finding Public Prompts
**Problem**: Search results don't include public prompts from other users.

**Solution**:
1. **Check search filters**: Ensure visibility filter is set to "all" or "public"
2. **Verify search parameters**: API calls need `include_public=true`
3. **Review prompt content**: Search only works on visible content

#### API Token Issues
**Problem**: API requests failing with authentication errors.

**Solution**:
1. **Check token format**: Tokens should start with `apm_`
2. **Verify token expiration**: Check if your token has expired
3. **Correct header format**: Use `Authorization: Bearer apm_your_token`
4. **Check token permissions**: Ensure token has required permissions

### Performance Issues

#### Slow Prompt Loading
**Solution**:
1. **Check filters**: Too many prompts can slow loading
2. **Use pagination**: Limit results per page
3. **Optimize search**: Use more specific search terms
4. **Clear browser cache**: Sometimes cached data causes issues

#### API Response Slow
**Solution**:
1. **Reduce page size**: Use smaller `page_size` parameters
2. **Limit search scope**: Use specific filters to reduce data
3. **Check database**: Large datasets may need optimization
4. **Monitor resources**: Ensure adequate system resources

### Getting Help

#### Documentation
- **User Guide**: This document
- **API Documentation**: [API.md](API.md)
- **Architecture Guide**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

#### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Community Discussions**: Join community conversations
- **Documentation**: Check existing documentation first

#### Reporting Issues
When reporting issues, please include:
1. **Version information**: Application version and deployment mode
2. **Environment details**: Operating system, browser, Python version
3. **Steps to reproduce**: Clear instructions to reproduce the issue
4. **Expected vs. actual behavior**: What should happen vs. what happens
5. **Screenshots**: Visual aids when relevant
6. **Log files**: Error messages and relevant logs

---

## Conclusion

The AI Prompt Manager with visibility features provides a comprehensive solution for managing AI prompts in both personal and team environments. The visibility system enables secure collaboration while maintaining privacy and control over sensitive content.

### Key Takeaways

1. **Visibility Control**: Use private prompts for personal content, public for team sharing
2. **Security First**: Review content before making prompts public
3. **Organization**: Use categories and tags for effective prompt management
4. **Collaboration**: Leverage public prompts for team knowledge sharing
5. **API Integration**: Programmatic access with full visibility support

### Next Steps

1. **Explore the interface**: Try creating prompts with different visibility levels
2. **Set up API access**: Generate tokens for programmatic access
3. **Organize your prompts**: Use categories and tags for better organization
4. **Share with your team**: Create public prompts for team collaboration
5. **Integrate with workflows**: Use the API to integrate with existing tools

For additional help and advanced configuration options, refer to the other documentation files in the `docs/` directory.

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**