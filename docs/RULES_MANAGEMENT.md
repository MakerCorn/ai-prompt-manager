# Rules Management Guide

## Overview

The Rules Management system in AI Prompt Manager provides a comprehensive solution for creating, organizing, and combining structured guidelines that direct AI behavior and responses. Rules are written in Markdown format and can be used individually or combined to create comprehensive guideline sets for agentic coding applications like Claude and Amazon Q.

## Table of Contents

- [Key Features](#key-features)
- [Getting Started](#getting-started)
- [Creating Rules](#creating-rules)
- [Rule Builder](#rule-builder)
- [Managing Rules](#managing-rules)
- [Markdown Formatting](#markdown-formatting)
- [Best Practices](#best-practices)
- [Integration with AI Tools](#integration-with-ai-tools)
- [API Reference](#api-reference)
- [Testing](#testing)

## Key Features

### ✨ Core Functionality
- **Markdown-Based**: Full Markdown support for rich formatting
- **Categories & Tags**: Organize rules by category and tag for easy discovery
- **Search & Filter**: Powerful search and filtering capabilities
- **Visual Builder**: Drag-and-drop interface for combining rules
- **Multi-Tenant**: Complete tenant isolation and user management
- **Export Options**: Download individual rules or combinations as Markdown files
- **Built-in Templates**: Pre-configured rule templates for common scenarios

### 🎯 Rule Types
- **Coding Guidelines**: Standards for programming and development
- **Analysis Rules**: Guidelines for data analysis and research
- **Writing Standards**: Rules for content creation and documentation
- **Constraints**: Limitations and requirements for AI responses
- **General Guidelines**: Universal rules applicable across contexts

### 🔧 Advanced Features
- **Rule Combinations**: Merge multiple rules into comprehensive sets
- **Live Preview**: Real-time markdown rendering and preview
- **Validation**: Content validation and formatting assistance
- **Template Insertion**: Quick insertion of common rule patterns
- **Unicode Support**: Full support for international characters and emojis

## Getting Started

### Accessing Rules Management

1. **Navigation**: Click "Rules" in the main navigation menu
2. **Rules Library**: View all existing rules with search and filter options
3. **Create New Rule**: Click "New Rule" to start creating guidelines
4. **Rules Builder**: Access the visual combination tool via "Rules Builder"

### Initial Setup

```bash
# Ensure Rules functionality is available
poetry run python run.py --single-user  # Single-user mode
# OR
poetry run python run.py                # Multi-tenant mode
```

### Basic Workflow

1. **Create Categories**: Organize rules by purpose (Coding, Writing, Analysis)
2. **Write Rules**: Use Markdown to create structured guidelines
3. **Tag for Discovery**: Apply relevant tags for easy searching
4. **Test & Iterate**: Preview and refine rule content
5. **Combine as Needed**: Use the builder to create comprehensive sets

## Creating Rules

### Rule Structure

A well-structured rule follows this pattern:

```markdown
# Rule Title

## Purpose
Brief description of what this rule aims to achieve.

## Guidelines
- Specific directive or instruction
- Another actionable guideline
- Clear, measurable requirements

## Examples
```
Example code, output, or usage scenarios
```

## Constraints
- Limitations or restrictions
- Format requirements
- Boundary conditions

## References
- [Related Documentation](https://example.com)
- See also: Other Rule Name
```

### Form Fields

- **Name**: Unique identifier (required)
- **Title**: Human-readable title (required)
- **Category**: Organizational grouping (required)
- **Tags**: Comma-separated keywords for discovery
- **Description**: Brief summary of the rule's purpose
- **Content**: Full Markdown content (required)

### Content Guidelines

1. **Be Specific**: Provide clear, actionable directives
2. **Use Examples**: Include concrete examples when helpful
3. **Structure Well**: Use headers, lists, and formatting consistently
4. **Keep Focused**: Each rule should address a specific aspect
5. **Update Regularly**: Review and refine rules based on usage

## Rule Builder

### Overview

The Rules Builder provides a visual interface for combining multiple rules into comprehensive guideline sets. This is particularly useful for creating complete instruction sets for AI agents.

### Builder Interface

#### Left Panel: Available Rules
- **Search**: Filter rules by name, content, or tags
- **Category Filter**: Show rules from specific categories
- **Rule Cards**: Click to add rules to your combination

#### Right Panel: Configuration & Preview
- **Combination Settings**: Name, category, and separator style
- **Selected Rules**: Reorder, preview, or remove rules
- **Live Preview**: Real-time markdown preview of the combination

### Using the Builder

1. **Configure Combination**:
   ```
   Combination Name: "Full Stack Development Rules"
   Category: "Development"
   Separator Style: "Headers" (recommended)
   ```

2. **Add Rules**: Click rules from the library to add them
3. **Reorder**: Use up/down arrows to arrange rules logically
4. **Preview**: Review the combined output in real-time
5. **Save**: Save the combination as a new rule

### Separator Styles

- **Headers**: Each rule gets its own header section
- **Lines**: Rules separated by horizontal lines
- **Spaces**: Simple spacing between rules
- **Numbered**: Rules numbered sequentially

## Managing Rules

### Library Operations

#### Viewing Rules
- **List View**: Comprehensive view with details and actions
- **Search**: Real-time search across names, titles, and content
- **Filter**: Category-based filtering
- **Sort**: By creation date, name, or category

#### Rule Actions
- **Preview**: Quick modal preview of rule content
- **Edit**: Modify existing rules (not available for built-in rules)
- **Copy**: Copy rule content to clipboard for external use
- **Delete**: Remove rules (with confirmation)

### Categories

Default categories include:
- **General**: Universal guidelines
- **Coding**: Programming and development standards
- **Analysis**: Data analysis and research guidelines
- **Writing**: Content creation and documentation rules
- **Constraints**: Limitations and boundary conditions

Custom categories can be created as needed.

### Tags

Tags enable cross-cutting organization:
- **Functional**: `validation`, `error-handling`, `optimization`
- **Technology**: `python`, `javascript`, `api`, `database`
- **Domain**: `security`, `performance`, `accessibility`, `testing`
- **Scope**: `frontend`, `backend`, `fullstack`, `mobile`

## Markdown Formatting

### Supported Syntax

Rules support full Markdown syntax:

```markdown
# Headers (H1-H6)
## Second Level
### Third Level

**Bold text** and *italic text*
`Inline code` and code blocks:

```python
def example():
    return "Hello, World!"
```

- Unordered lists
- With multiple items

1. Ordered lists
2. With sequential numbering

> Blockquotes for important notes

[Links](https://example.com) and references

| Tables | Are | Supported |
|--------|-----|-----------|
| Data   | Can | Be Shown  |

---

Horizontal rules for separation
```

### Special Elements

#### Code Blocks with Language
```python
def validate_input(data):
    """Validate user input according to rules."""
    if not data or not data.strip():
        raise ValueError("Input cannot be empty")
    return data.strip()
```

#### Blockquotes for Important Notes
> **Warning**: Always validate user input before processing.

#### Task Lists
- [x] Completed task
- [ ] Pending task
- [ ] Future enhancement

## Best Practices

### Rule Design

1. **Single Responsibility**: Each rule should focus on one specific aspect
2. **Clear Language**: Use precise, unambiguous terminology
3. **Actionable Content**: Provide concrete steps and examples
4. **Consistent Structure**: Follow established patterns for similar rules
5. **Regular Updates**: Review and refine rules based on feedback

### Organization

1. **Logical Categories**: Group related rules together
2. **Descriptive Tags**: Use consistent, meaningful tags
3. **Hierarchical Naming**: Use clear, descriptive names
4. **Version Control**: Document major changes in descriptions
5. **Deprecation Path**: Mark outdated rules before removal

### Content Guidelines

1. **Start with Purpose**: Clearly state what the rule achieves
2. **Provide Context**: Explain when and why to apply the rule
3. **Include Examples**: Show correct and incorrect usage
4. **Define Boundaries**: Specify limitations and exceptions
5. **Reference Related Rules**: Link to complementary guidelines

### Combination Strategy

1. **Logical Flow**: Arrange rules in a logical progression
2. **Avoid Redundancy**: Don't repeat information across rules
3. **Resolve Conflicts**: Address contradictions between rules
4. **Test Combinations**: Verify combined rules work together
5. **Document Intent**: Explain why rules are combined

## Integration with AI Tools

### Claude (Anthropic)

Rules can be directly used with Claude by copying the markdown content:

1. **Copy Rule**: Use the copy button to get markdown content
2. **Paste in Claude**: Add to your conversation or project
3. **Reference**: Include rule names in prompts for consistency

Example:
```
Please follow the "Python Coding Standards" rule when writing code.

[Paste rule content here]

Now implement a function that validates email addresses.
```

### Amazon Q

For Amazon Q integration:

1. **Download Rules**: Export individual rules or combinations
2. **Upload to Q**: Add rules to your Q workspace
3. **Reference in Queries**: Mention rule names in your requests

### VS Code Extensions

Rules work well with coding assistants:

1. **Copy to Comments**: Paste rules as code comments
2. **Reference in Prompts**: Include rule names in AI prompts
3. **Template Creation**: Use rules to create code templates

### GitHub Copilot

Enhance Copilot suggestions:

1. **Inline Comments**: Add rule excerpts as comments above code
2. **Commit Messages**: Reference rules in commit descriptions
3. **PR Templates**: Include relevant rules in pull request templates

## API Reference

### Endpoints

#### Rules Management
```http
GET    /rules                    # List all rules
POST   /rules/new                # Create new rule
GET    /rules/{id}/edit          # Get rule for editing
POST   /rules/{id}/edit          # Update rule
DELETE /rules/{id}               # Delete rule
```

#### Search and Filter
```http
GET    /rules/search?q={query}           # Search rules
GET    /rules/filter?category={cat}      # Filter by category
```

#### Builder
```http
GET    /rules/builder            # Rules builder interface
```

### Data Format

#### Rule Object
```json
{
    "id": 1,
    "tenant_id": "uuid",
    "user_id": "uuid",
    "name": "python-standards",
    "title": "Python Coding Standards",
    "content": "# Python Standards\n\n...",
    "category": "Coding",
    "tags": "python,standards,pep8",
    "description": "PEP 8 compliance guidelines",
    "is_builtin": false,
    "created_at": "2025-01-06T12:00:00Z",
    "updated_at": "2025-01-06T12:00:00Z"
}
```

### Response Codes

- **200**: Success
- **302**: Redirect after successful operation
- **400**: Bad request (validation errors)
- **404**: Rule not found
- **500**: Server error

## Testing

### Unit Tests

Run rule-specific unit tests:

```bash
# Test rules management functionality
poetry run python tests/unit/test_rules_management.py

# Test database operations
poetry run python tests/unit/test_prompt_data_manager.py
```

### Integration Tests

Test API endpoints:

```bash
# Test rules API integration
poetry run python tests/integration/test_rules_api_integration.py
```

### E2E Tests

Test complete user workflows:

```bash
# Install E2E dependencies
poetry install --with e2e
poetry run playwright install chromium

# Run rules E2E tests
poetry run python tests/e2e/test_rules_system_e2e.py
```

### Test Coverage

The Rules system includes comprehensive testing:

- **Unit Tests**: Database operations, CRUD functionality, validation
- **Integration Tests**: API endpoints, search, filtering, builder
- **E2E Tests**: Complete user workflows, UI interactions, responsive design

## Troubleshooting

### Common Issues

#### Rules Not Appearing
1. Check tenant isolation - rules are tenant-specific
2. Verify user authentication
3. Check database connection

#### Search Not Working
1. Ensure search terms match content
2. Check category filters
3. Verify HTMX is loading correctly

#### Builder Issues
1. Refresh the page if rules don't load
2. Check JavaScript console for errors
3. Verify rules exist and are accessible

#### Export Problems
1. Check browser's download permissions
2. Verify file format support
3. Ensure adequate disk space

### Performance Optimization

#### Large Rule Sets
- Use pagination for large collections
- Implement server-side search
- Cache frequently accessed rules

#### Builder Performance
- Limit rules displayed simultaneously
- Use virtual scrolling for large lists
- Optimize preview rendering

### Support

For additional help:
1. Check the [main documentation](../README.md)
2. Review [API documentation](API.md)
3. Examine [test cases](../tests/) for examples
4. Report issues via GitHub Issues

---

## Conclusion

The Rules Management system provides a powerful framework for creating, organizing, and combining structured guidelines for AI interactions. By following the patterns and best practices outlined in this guide, you can create effective rule sets that improve AI agent performance and consistency.

Whether you're building coding standards, analysis guidelines, or comprehensive instruction sets, the Rules system offers the flexibility and tools needed to manage complex requirements effectively.