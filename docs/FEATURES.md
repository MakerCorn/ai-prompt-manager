# ✨ Features Guide

Comprehensive guide to the advanced features of AI Prompt Manager, including speech dictation, rules management, and GitHub integration.

## Table of Contents

1. [Speech Dictation](#speech-dictation)
2. [Rules Management](#rules-management)
3. [GitHub Integration](#github-integration)
4. [Advanced Search](#advanced-search)
5. [Multi-Language Support](#multi-language-support)

---

## Speech Dictation

### Overview

The AI Prompt Manager features a comprehensive speech dictation system supporting 12 languages with AI-powered enhancement and real-time translation capabilities.

### Supported Languages

| Language | Code | Voice Commands | Auto-Enhancement |
|----------|------|----------------|------------------|
| **English (US)** | en-US | ✅ | ✅ |
| **English (UK)** | en-GB | ✅ | ✅ |
| **Spanish** | es-ES | ✅ | ✅ |
| **French** | fr-FR | ✅ | ✅ |
| **German** | de-DE | ✅ | ✅ |
| **Italian** | it-IT | ✅ | ✅ |
| **Portuguese** | pt-PT | ✅ | ✅ |
| **Russian** | ru-RU | ✅ | ✅ |
| **Japanese** | ja-JP | ✅ | ✅ |
| **Korean** | ko-KR | ✅ | ✅ |
| **Chinese (Mandarin)** | zh-CN | ✅ | ✅ |
| **Arabic** | ar-SA | ✅ | ✅ |

### Getting Started

#### Basic Dictation

1. **Access Speech Features**: Navigate to Prompts → Create New Prompt
2. **Click Dictate Button**: Look for the microphone icon in the content area
3. **Grant Permissions**: Allow microphone access when prompted
4. **Start Speaking**: Click to begin dictation in your preferred language
5. **Control Recording**: Use pause/resume controls as needed

#### Voice Controls

```
Voice Command         Action
"new paragraph"    →  Adds line break
"period"          →  Adds . 
"comma"           →  Adds ,
"question mark"   →  Adds ?
"exclamation"     →  Adds !
"pause dictation" →  Pauses recording
"stop dictation"  →  Ends recording
```

### Language Configuration

#### Web Interface Setup

1. **Access Language Settings**:
   ```
   Navigate to: Prompts → Create/Edit → Dictation Controls → Language Selector
   ```

2. **Select Language**:
   - Choose from 12 supported languages
   - Language preference persists across sessions
   - Real-time language switching during dictation

3. **Configure Recognition**:
   ```javascript
   // Automatic language detection
   recognition.lang = 'auto';
   
   // Specific language
   recognition.lang = 'en-US';
   
   // Continuous recognition
   recognition.continuous = true;
   recognition.interimResults = true;
   ```

#### Advanced Configuration

```javascript
// Custom speech recognition configuration
const speechConfig = {
    language: 'en-US',              // Primary language
    continuous: true,               // Continuous recognition
    interimResults: true,           // Show interim results
    maxAlternatives: 3,             // Number of alternatives
    confidence: 0.8,                // Minimum confidence threshold
    timeout: 5000,                  // Silence timeout (ms)
    autoStop: false                 // Auto-stop after silence
};

// Apply configuration
updateSpeechRecognition(speechConfig);
```

### AI-Powered Enhancement

#### Automatic Text Enhancement

The speech dictation system includes AI-powered text enhancement that automatically:

- **Fixes Grammar**: Corrects grammatical errors from speech recognition
- **Improves Structure**: Enhances sentence flow and readability
- **Removes Filler Words**: Eliminates "um", "uh", "you know", etc.
- **Adds Punctuation**: Intelligent punctuation based on speech patterns
- **Formats Content**: Structures text for prompt usage

#### Enhancement Process

1. **Real-time Processing**: Text enhanced as you speak
2. **Manual Enhancement**: Click "Enhance" button for AI improvement
3. **Quality Control**: Review and edit enhanced text
4. **Multiple Passes**: Re-enhance text for better quality

```python
# Enhancement API endpoint
POST /enhance-text
{
    "text": "write email to customer about project um you know the status update",
    "type": "dictation"
}

# Enhanced response
{
    "success": true,
    "enhanced_text": "Write a professional email to the customer about the project status update.",
    "original_text": "write email to customer about project um you know the status update"
}
```

### Real-Time Translation

#### Automatic Translation

Dictate in your native language and automatically translate to English or other target languages:

1. **Enable Translation**: Click the translation button during dictation
2. **Select Target Language**: Choose from supported languages
3. **Real-time Processing**: Text translated as you speak
4. **Quality Review**: Edit translated text as needed

#### Translation API

```python
# Translation endpoint
POST /translate
{
    "text": "Hola mundo, esto es una prueba",
    "source_lang": "es",
    "target_lang": "en"
}

# Translation response
{
    "success": true,
    "translated_text": "Hello world, this is a test",
    "source_language": "es",
    "target_language": "en",
    "confidence": 0.95
}
```

### Browser Compatibility

#### Supported Browsers

| Browser | Version | Speech API | Features |
|---------|---------|------------|----------|
| **Chrome** | 25+ | ✅ WebKit | Full support |
| **Edge** | 79+ | ✅ WebKit | Full support |
| **Safari** | 14.1+ | ✅ WebKit | Full support |
| **Firefox** | 96+ | ✅ Web Speech | Limited support |
| **Opera** | 27+ | ✅ WebKit | Full support |

#### Feature Detection

```javascript
// Check for speech recognition support
function checkSpeechSupport() {
    if ('webkitSpeechRecognition' in window) {
        return 'webkit';
    } else if ('SpeechRecognition' in window) {
        return 'standard';
    } else {
        return null;
    }
}

// Initialize based on support
const speechSupport = checkSpeechSupport();
if (speechSupport) {
    initializeSpeechRecognition();
} else {
    showSpeechNotSupportedMessage();
}
```

### Accessibility Features

#### Keyboard Navigation

- **Space**: Start/pause dictation
- **Escape**: Stop dictation
- **Tab**: Navigate between controls
- **Enter**: Activate buttons

#### Screen Reader Support

```html
<!-- ARIA labels for speech controls -->
<button id="speech-btn" 
        aria-label="Start voice dictation"
        aria-describedby="speech-status"
        role="button">
    <i class="fas fa-microphone" aria-hidden="true"></i>
    <span>Dictate</span>
</button>

<div id="speech-status" 
     role="status" 
     aria-live="polite"
     aria-atomic="true">
    Ready for dictation
</div>
```

#### Visual Indicators

- **Microphone Icon**: Visual feedback for recording state
- **Status Messages**: Clear recording status updates
- **Progress Indicators**: Visual confidence and language display
- **Color Coding**: Different colors for recording, paused, error states

## Rules Management

### Overview

The Rules Management System provides structured Markdown-based guidelines for AI agents, enabling consistent behavior and quality standards across autonomous AI systems.

### Core Concepts

#### What are Rules?

Rules are structured Markdown documents that define:

- **Behavioral Guidelines**: How AI agents should operate
- **Quality Standards**: Expected output quality and format
- **Constraints**: What agents should and shouldn't do
- **Workflows**: Step-by-step process guidance
- **Context**: Domain-specific knowledge and requirements

#### Rules vs Prompts

| Aspect | Prompts | Rules |
|--------|---------|--------|
| **Purpose** | Request specific output | Define ongoing behavior |
| **Scope** | Single interaction | System-wide guidance |
| **Format** | Natural language | Structured Markdown |
| **Usage** | Direct execution | Background guidance |
| **Persistence** | One-time use | Continuous application |

### Creating Rules

#### Basic Rule Structure

```markdown
# Rule Title

## Purpose
Brief description of what this rule accomplishes.

## Guidelines
- Specific guideline 1
- Specific guideline 2
- Specific guideline 3

## Examples
### Good Example
```
Correct implementation
```

### Bad Example
```
Incorrect implementation
```

## Implementation Notes
Additional context and considerations.
```

#### Advanced Rule Template

```markdown
# Code Review Standards

## Purpose
Ensure consistent, high-quality code reviews that improve code quality and knowledge sharing.

## Guidelines

### Code Quality
- **Functionality**: Code works as intended and handles edge cases
- **Readability**: Clear, well-documented, follows style guides
- **Performance**: Efficient algorithms and resource usage
- **Security**: No vulnerabilities or security anti-patterns

### Review Process
- **Timely Response**: Review within 24 hours
- **Constructive Feedback**: Specific, actionable suggestions
- **Testing**: Verify tests cover new functionality
- **Documentation**: Update docs for user-facing changes

### Communication
- **Respectful Tone**: Professional, helpful feedback
- **Explain Reasoning**: Why changes are needed
- **Acknowledge Good Work**: Positive reinforcement
- **Ask Questions**: Clarify intent when uncertain

## Examples

### Good Review Comment
```
Consider using a more specific exception type here (e.g., ValueError) 
instead of the generic Exception. This makes error handling more 
precise and helps other developers understand what can go wrong.
```

### Bad Review Comment
```
This is wrong. Fix it.
```

## Implementation Notes
- Use code review checklists for consistency
- Pair programming for complex features
- Automated checks for style and basic issues
```

### Rules Categories

#### Development Rules

- **Code Standards**: Formatting, naming conventions, documentation
- **Testing Requirements**: Coverage, test types, automation
- **Security Guidelines**: Authentication, data protection, vulnerabilities
- **Performance Standards**: Optimization, monitoring, benchmarks

#### Content Rules

- **Writing Style**: Tone, voice, formatting standards
- **Documentation**: Structure, completeness, accuracy
- **Translation**: Consistency, cultural adaptation, quality
- **Review Process**: Approval workflows, quality gates

#### Operational Rules

- **Deployment**: Release procedures, rollback plans
- **Monitoring**: Alerting, logging, metrics collection
- **Support**: Response times, escalation procedures
- **Compliance**: Regulatory requirements, audit trails

### Rules Builder

#### Visual Rule Combination

The Rules Builder provides a drag-and-drop interface for combining multiple rules:

1. **Select Base Rules**: Choose foundational rules from your library
2. **Drag and Arrange**: Organize rules in priority order
3. **Preview Combination**: See how rules work together
4. **Export Format**: Generate combined rule sets for AI tools

#### Rule Templates

```markdown
# Project Template: {PROJECT_NAME}

## Development Rules
{INCLUDE: code-standards.md}
{INCLUDE: testing-requirements.md}
{INCLUDE: security-guidelines.md}

## Content Rules  
{INCLUDE: documentation-standards.md}
{INCLUDE: writing-style-guide.md}

## Operational Rules
{INCLUDE: deployment-procedures.md}
{INCLUDE: monitoring-requirements.md}

## Project-Specific Overrides
- Custom rule 1
- Custom rule 2
```

### Integration with AI Tools

#### Claude Code Integration

```markdown
# Claude Code Configuration

Export rules to CLAUDE.md format for seamless integration:

```bash
# Export to Claude Code format
curl -X POST http://localhost:7860/api/rules/export \
  -H "Content-Type: application/json" \
  -d '{"format": "claude", "rules": ["code-standards", "testing-requirements"]}' \
  > CLAUDE.md
```

#### GitHub Copilot Integration

```yaml
# .github/copilot-instructions.yml
rules:
  - name: "Code Standards"
    file: "docs/rules/code-standards.md"
  - name: "Testing Requirements"  
    file: "docs/rules/testing-requirements.md"
```

#### VS Code Integration

```json
// .vscode/settings.json
{
    "ai.rules": [
        "docs/rules/code-standards.md",
        "docs/rules/documentation-requirements.md"
    ]
}
```

### Rule Management API

#### List Rules

```bash
GET /api/rules
{
    "rules": [
        {
            "id": 1,
            "name": "code-standards",
            "title": "Code Standards",
            "category": "development",
            "tags": ["coding", "standards"],
            "created_at": "2025-01-01T12:00:00Z"
        }
    ]
}
```

#### Create Rule

```bash
POST /api/rules
{
    "name": "new-rule",
    "title": "New Rule Title",
    "content": "# New Rule\n\nRule content here...",
    "category": "development",
    "tags": ["new", "development"]
}
```

#### Export Rules

```bash
POST /api/rules/export
{
    "rules": ["code-standards", "testing-requirements"],
    "format": "claude"
}
```

## GitHub Integration

### GitHub Format Support

The AI Prompt Manager supports importing and exporting prompts in GitHub-compatible YAML format for seamless integration with GitHub workflows.

#### Supported Format

```yaml
# .github/prompts/code-review.yml
name: Code Review Prompt
description: Automated code review guidance
version: 1.0
category: Development
tags:
  - code-review
  - automation
  - quality

prompt: |
  Please review the following code changes:
  
  ## Guidelines
  - Check for functionality and correctness
  - Verify tests cover new features
  - Ensure documentation is updated
  - Look for security issues
  - Validate performance considerations
  
  ## Format
  Provide feedback in this structure:
  1. Summary of changes
  2. Issues found (if any)
  3. Suggestions for improvement
  4. Approval status

variables:
  - name: code_diff
    description: The git diff to review
    required: true
  - name: context
    description: Additional context about the changes
    required: false

examples:
  - input:
      code_diff: "Added user authentication"
      context: "Part of security enhancement project"
    output: "Code review feedback example..."
```

#### Import from GitHub

```bash
# Import prompts from GitHub repository
curl -X POST http://localhost:7860/api/prompts/import/github \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "username/repo",
    "path": ".github/prompts/",
    "branch": "main"
  }'
```

#### Export to GitHub Format

```bash
# Export prompts to GitHub YAML format
curl -X POST http://localhost:7860/api/prompts/export/github \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["code-review", "documentation"],
    "format": "github-yaml"
  }' > prompts.yml
```

### GitHub Actions Integration

#### Automated Prompt Testing

```yaml
# .github/workflows/prompt-testing.yml
name: Prompt Testing

on:
  pull_request:
    paths:
      - '.github/prompts/**'

jobs:
  test-prompts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate Prompt Format
        run: |
          pip install pyyaml
          python scripts/validate-prompts.py .github/prompts/
      
      - name: Test Prompt Execution
        uses: ai-prompt-manager/test-action@v1
        with:
          prompts-path: '.github/prompts/'
          api-key: ${{ secrets.OPENAI_API_KEY }}
```

#### Prompt Deployment

```yaml
# .github/workflows/deploy-prompts.yml
name: Deploy Prompts

on:
  push:
    branches: [main]
    paths:
      - '.github/prompts/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Prompt Manager
        run: |
          curl -X POST ${{ secrets.PROMPT_MANAGER_URL }}/api/prompts/bulk-import \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d @.github/prompts/prompts.json
```

## Advanced Search

### Search Capabilities

#### Multi-Entity Search

Search across prompts, templates, and rules simultaneously:

```bash
# Global search across all entities
GET /api/search?q=authentication&entities=prompts,templates,rules

{
    "results": {
        "prompts": [...],
        "templates": [...], 
        "rules": [...]
    },
    "total": 25,
    "query": "authentication"
}
```

#### Tag-Based Search

Advanced tag search with AND/OR logic:

```bash
# AND logic: items with ALL specified tags
GET /api/search?tags=security+authentication&logic=and

# OR logic: items with ANY specified tags  
GET /api/search?tags=security,authentication&logic=or

# Complex search with exclusions
GET /api/search?tags=security+authentication&exclude=deprecated
```

#### Advanced Filters

```bash
# Comprehensive filtering
GET /api/search?
  q=user+management&
  category=security&
  visibility=public&
  tags=authentication,authorization&
  created_after=2024-01-01&
  updated_since=2024-12-01&
  user_id=123&
  limit=20&
  offset=0
```

### Search Interface

#### Real-Time Search

- **Instant Results**: Search as you type with debounced queries
- **Suggestions**: Auto-complete based on existing content
- **Filters**: Visual filter interface for complex searches
- **Sorting**: Multiple sort options (relevance, date, popularity)

#### Search Syntax

```
Basic search:          authentication
Phrase search:         "user authentication"
Tag search:            #security #auth
Category filter:       category:development
Visibility filter:     visibility:public
User filter:           user:john.doe
Date range:            created:2024-01-01..2024-12-31
Boolean operators:     security AND authentication
Exclusion:             security NOT deprecated
Wildcard:              auth*
```

## Multi-Language Support

### Supported Languages

The AI Prompt Manager supports 10 languages with complete UI translation:

| Language | Code | Completion | Features |
|----------|------|------------|----------|
| **English** | en | 100% | All features |
| **Spanish** | es | 100% | All features |
| **German** | de | 100% | All features |
| **Portuguese** | pt | 100% | All features |
| **French** | fr | 100% | All features |
| **Italian** | it | 100% | All features |
| **Russian** | ru | 100% | All features |
| **Japanese** | ja | 100% | All features |
| **Chinese** | zh | 100% | All features |
| **Arabic** | ar | 100% | All features |

### Language Features

#### Dynamic Language Switching

- **Real-time**: Switch languages without page reload
- **Persistent**: Language preference saved in session
- **Automatic**: Detect browser language preference
- **Fallback**: Graceful fallback to English for missing translations

#### Translation Management

```bash
# Add new translation key
POST /api/language/keys
{
    "key": "feature.new_button",
    "translations": {
        "en": "New Feature",
        "es": "Nueva Función",
        "de": "Neue Funktion"
    }
}

# Auto-translate missing keys
POST /api/language/auto-translate
{
    "target_language": "fr",
    "service": "openai"
}
```

#### Content Translation

```bash
# Translate prompt content
POST /api/translate/content
{
    "content": "Write a professional email",
    "source_lang": "en",
    "target_lang": "es"
}

# Response
{
    "translated": "Escribe un correo electrónico profesional",
    "confidence": 0.95
}
```

---

*This features guide covers the advanced capabilities of the AI Prompt Manager. Each feature is designed to enhance productivity and streamline AI workflow management.*