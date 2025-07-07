# GitHub Format Support

The AI Prompt Manager now supports importing and exporting prompts in GitHub's standard YAML format, making it easy to share prompts across different platforms and integrate with GitHub workflows.

## GitHub Format Structure

The GitHub YAML format follows this structure:

```yaml
messages:
  - role: system
    content: 'You are a helpful assistant.'
  - role: user
    content: >-
      Your prompt content here.
      Can span multiple lines.
model: openai/gpt-4o
temperature: 0.7
max_tokens: 1000
top_p: 0.9
frequency_penalty: 0.1
presence_penalty: 0.2
```

### Required Fields

- `messages`: Array of message objects with `role` and `content`
- Each message must have:
  - `role`: One of `system`, `user`, or `assistant`
  - `content`: The message content (string)

### Optional Fields

- `model`: AI model identifier (defaults to `openai/gpt-4o`)
- `temperature`: Sampling temperature (0.0 to 2.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Nucleus sampling parameter
- `frequency_penalty`: Frequency penalty (-2.0 to 2.0)
- `presence_penalty`: Presence penalty (-2.0 to 2.0)

## Using the API

### Import GitHub Format

```bash
curl -X POST "http://localhost:7861/api/ai-models/github/import" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "messages:\n  - role: user\n    content: Hello world\nmodel: openai/gpt-4o",
    "name": "My GitHub Prompt",
    "category": "Imported"
  }'
```

### Export to GitHub Format

```bash
curl -X GET "http://localhost:7861/api/ai-models/github/export/123" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Get Format Information

```bash
curl -X GET "http://localhost:7861/api/ai-models/github/info" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

## Using the Python API

### Import from YAML String

```python
from src.prompts.models.prompt import Prompt

yaml_content = """
messages:
  - role: system
    content: 'You are helpful.'
  - role: user
    content: 'Hello!'
model: openai/gpt-4o
"""

prompt = Prompt.from_github_yaml(
    yaml_content,
    tenant_id="your_tenant",
    user_id="your_user",
    name="Imported Prompt"
)
```

### Export to YAML String

```python
# Assuming you have a prompt object
yaml_output = prompt.to_github_yaml()
print(yaml_output)
```

### File Operations

```python
from src.utils.github_format import GitHubFormatHandler

handler = GitHubFormatHandler()

# Import from file
prompt = handler.import_from_file(
    "prompt.yml",
    tenant_id="your_tenant",
    user_id="your_user"
)

# Export to file
handler.export_to_file(prompt, "exported_prompt.yml")

# Import from directory
prompts = handler.import_from_directory(
    "/path/to/prompts",
    tenant_id="your_tenant",
    user_id="your_user"
)

# Export to directory
created_files = handler.export_to_directory(
    prompts,
    "/path/to/output"
)
```

## Content Conversion

The system intelligently converts between GitHub format and internal prompt format:

### From GitHub to Internal

- Messages are converted to a single content string with role markers
- Model parameters are stored in metadata
- Auto-generates names from user message content if not provided

### From Internal to GitHub

- Parses content for role markers (`SYSTEM:`, `USER:`, `ASSISTANT:`)
- Extracts model parameters from metadata
- Creates proper message structure

### Example Conversion

**GitHub Format:**
```yaml
messages:
  - role: system
    content: 'You are helpful.'
  - role: user
    content: 'Create a Python script'
model: openai/gpt-4o
```

**Internal Format:**
```
SYSTEM: You are helpful.

USER: Create a Python script
```

## File Detection

The system automatically detects GitHub format files by:

1. Checking file extension (`.yml`, `.yaml`)
2. Parsing YAML content
3. Validating for required `messages` field structure

## Validation

All imported GitHub format data is validated for:

- Required fields presence
- Correct message structure
- Valid role values
- Proper data types for optional parameters

## Integration with Existing Features

GitHub format prompts integrate seamlessly with:

- ✅ Prompt categories and tags
- ✅ Search and filtering
- ✅ Template system
- ✅ Optimization services
- ✅ Multi-tenant isolation
- ✅ API authentication
- ✅ Export/import functionality

## Example Use Cases

### 1. GitHub Workflow Integration

Store prompts in your repository and import them:

```yaml
# .github/prompts/code-review.yml
messages:
  - role: system
    content: 'You are a senior code reviewer.'
  - role: user
    content: 'Review this pull request: {pr_content}'
model: openai/gpt-4o
temperature: 0.3
```

### 2. Team Collaboration

Share prompts in standard format across tools:

```bash
# Export your prompts
curl -X GET "http://localhost:7861/api/ai-models/github/export/123" > team-prompt.yml

# Team member imports
curl -X POST "http://localhost:7861/api/ai-models/github/import" \
  -d @team-prompt.yml
```

### 3. Bulk Migration

Convert existing prompt libraries:

```python
# Convert directory of GitHub format files
handler = GitHubFormatHandler()
prompts = handler.import_from_directory("./github-prompts", "tenant", "user")

# Export entire prompt library
all_prompts = data_manager.get_all_prompts()
handler.export_to_directory(all_prompts, "./exported-prompts")
```

## Limitations

- Metadata beyond standard GitHub format fields is not preserved in exports
- Complex nested structures in content are flattened
- File import/export requires file system access

## Error Handling

The system provides detailed error messages for:

- Invalid YAML syntax
- Missing required fields
- Invalid role values
- Malformed message structures
- File access issues

## Best Practices

1. **Use descriptive names**: Provide meaningful names for imported prompts
2. **Organize with categories**: Use consistent categorization
3. **Validate before import**: Check YAML syntax before importing
4. **Test exports**: Verify exported prompts work in target systems
5. **Version control**: Store GitHub format prompts in version control
6. **Document parameters**: Comment your model parameter choices