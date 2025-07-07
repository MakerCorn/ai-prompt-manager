# Adding AI Model Providers and Models

This guide explains how to add additional AI model providers and models to the AI Prompt Manager.

## 🎯 Quick Start

### Method 1: Web Interface (Recommended)

1. **Access AI Services**: Go to http://localhost:7860 → Settings → AI Services
2. **Click "Add Model"** button
3. **Fill in the configuration form**:
   - **Provider**: Select from dropdown (OpenAI, Azure, Anthropic, etc.)
   - **Model ID**: The actual model identifier from the provider
   - **Display Name**: Human-readable name for the UI
   - **API Key**: Your API key for the provider
   - **API Endpoint**: Custom endpoint URL (if needed)
   - **Context Length**: Maximum tokens the model can handle
   - **Costs**: Input/output token costs for billing estimation

### Method 2: Programmatic Configuration

```python
from src.core.config.ai_model_config import ModelConfig, AIProvider

# Example: Adding a new model
new_model = ModelConfig(
    name="my-custom-model",
    provider=AIProvider.OPENAI,
    model_id="gpt-4o-mini",
    display_name="My Custom GPT-4o Mini",
    description="Customized GPT-4o Mini for specific tasks",
    max_context_length=128000,
    cost_per_1k_input_tokens=0.00015,
    cost_per_1k_output_tokens=0.0006,
    api_key="your-api-key-here",
    supports_streaming=True,
    supports_function_calling=True,
    supports_vision=True,
    supports_json_mode=True,
    is_enabled=True
)
```

## 🏗️ Supported Providers

| Provider | Status | API Format | Features |
|----------|--------|------------|----------|
| **OpenAI** | ✅ Full | OpenAI API | Streaming, Functions, Vision, JSON |
| **Azure OpenAI** | ✅ Full | OpenAI API | Streaming, Functions, Vision |
| **Anthropic** | ✅ Full | Claude API | Streaming, Large Context |
| **Google** | ✅ Full | Gemini API | Streaming, Vision, Multimodal |
| **Ollama** | ✅ Full | Local API | Local Models, Free |
| **LM Studio** | ✅ Full | OpenAI Compatible | Local Models, Free |
| **Mistral** | ✅ New | Mistral API | Streaming, Functions |
| **Perplexity** | ✅ New | OpenAI Compatible | Web Search |
| **Hugging Face** | ✅ Basic | HF Inference API | Open Source Models |
| **Cohere** | ✅ Basic | Cohere API | Text Generation |
| **Together AI** | ✅ Basic | OpenAI Compatible | Open Source Models |
| **Replicate** | ✅ New | Replicate API | Community Models |

## 📝 Configuration Examples

### OpenAI Models

```python
# GPT-4 Turbo
ModelConfig(
    name="gpt-4-turbo",
    provider=AIProvider.OPENAI,
    model_id="gpt-4-turbo-preview",
    display_name="GPT-4 Turbo",
    max_context_length=128000,
    cost_per_1k_input_tokens=0.01,
    cost_per_1k_output_tokens=0.03,
    api_key=os.getenv("OPENAI_API_KEY"),
    supports_streaming=True,
    supports_function_calling=True,
    supports_vision=True,
    supports_json_mode=True
)

# GPT-4o Mini (Cost-effective)
ModelConfig(
    name="gpt-4o-mini",
    provider=AIProvider.OPENAI,
    model_id="gpt-4o-mini",
    display_name="GPT-4o Mini",
    max_context_length=128000,
    cost_per_1k_input_tokens=0.00015,
    cost_per_1k_output_tokens=0.0006,
    api_key=os.getenv("OPENAI_API_KEY"),
    supports_streaming=True,
    supports_function_calling=True,
    supports_vision=True
)
```

### Azure OpenAI Models

```python
ModelConfig(
    name="azure-gpt4",
    provider=AIProvider.AZURE_OPENAI,
    model_id="gpt-4",
    display_name="Azure GPT-4",
    api_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-15-preview",
    deployment_name="gpt-4-deployment",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    max_context_length=8192,
    cost_per_1k_input_tokens=0.03,
    cost_per_1k_output_tokens=0.06
)
```

### Anthropic Models

```python
# Claude 3 Opus (Most Capable)
ModelConfig(
    name="claude-3-opus",
    provider=AIProvider.ANTHROPIC,
    model_id="claude-3-opus-20240229",
    display_name="Claude 3 Opus",
    max_context_length=200000,
    cost_per_1k_input_tokens=0.015,
    cost_per_1k_output_tokens=0.075,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    supports_streaming=True,
    supports_vision=True
)

# Claude 3 Haiku (Fast & Cheap)
ModelConfig(
    name="claude-3-haiku",
    provider=AIProvider.ANTHROPIC,
    model_id="claude-3-haiku-20240307",
    display_name="Claude 3 Haiku",
    max_context_length=200000,
    cost_per_1k_input_tokens=0.00025,
    cost_per_1k_output_tokens=0.00125,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    supports_streaming=True,
    supports_vision=True
)
```

### Local Models (Ollama)

```python
# Llama 3 8B Local
ModelConfig(
    name="llama3-8b-local",
    provider=AIProvider.OLLAMA,
    model_id="llama3:8b",
    display_name="Llama 3 8B (Local)",
    api_endpoint="http://localhost:11434/api/generate",
    max_context_length=8192,
    cost_per_1k_input_tokens=0.0,  # Free local model
    cost_per_1k_output_tokens=0.0,
    supports_streaming=True
)

# Code Llama for Programming
ModelConfig(
    name="codellama-7b-local",
    provider=AIProvider.OLLAMA,
    model_id="codellama:7b",
    display_name="Code Llama 7B (Local)",
    api_endpoint="http://localhost:11434/api/generate",
    max_context_length=16384,
    cost_per_1k_input_tokens=0.0,
    cost_per_1k_output_tokens=0.0
)
```

### Mistral Models

```python
# Mistral Large (Most Capable)
ModelConfig(
    name="mistral-large",
    provider=AIProvider.MISTRAL,
    model_id="mistral-large-latest",
    display_name="Mistral Large",
    api_endpoint="https://api.mistral.ai/v1/chat/completions",
    api_key=os.getenv("MISTRAL_API_KEY"),
    max_context_length=32768,
    cost_per_1k_input_tokens=0.008,
    cost_per_1k_output_tokens=0.024,
    supports_streaming=True,
    supports_function_calling=True
)

# Mistral 7B (Cost-effective)
ModelConfig(
    name="mistral-7b",
    provider=AIProvider.MISTRAL,
    model_id="mistral-7b-instruct",
    display_name="Mistral 7B Instruct",
    api_key=os.getenv("MISTRAL_API_KEY"),
    max_context_length=32768,
    cost_per_1k_input_tokens=0.00025,
    cost_per_1k_output_tokens=0.00025
)
```

### Perplexity Models (with Web Search)

```python
ModelConfig(
    name="perplexity-sonar",
    provider=AIProvider.PERPLEXITY,
    model_id="llama-3.1-sonar-large-128k-online",
    display_name="Perplexity Sonar Large",
    description="Online model with web search capabilities",
    api_endpoint="https://api.perplexity.ai/chat/completions",
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    max_context_length=131072,
    cost_per_1k_input_tokens=0.001,
    cost_per_1k_output_tokens=0.001,
    supports_streaming=True
)
```

## 🎯 Operation-Specific Model Assignment

Assign different models to different operations for optimal performance and cost:

```python
operation_configs = {
    # Fast, cheap models for testing
    OperationType.PROMPT_TESTING: [
        "ollama-llama3", "mistral-7b", "gpt-4o-mini"
    ],
    
    # High-quality models for enhancement
    OperationType.PROMPT_ENHANCEMENT: [
        "gpt-4-turbo", "claude-3-opus", "mistral-large"
    ],
    
    # Balanced models for optimization
    OperationType.PROMPT_OPTIMIZATION: [
        "gpt-4", "claude-3-sonnet", "mistral-medium"
    ],
    
    # Specialized models for code generation
    OperationType.GENERATION: [
        "codellama-7b-local", "gpt-4-turbo", "claude-3-opus"
    ],
    
    # Cost-effective models for translation
    OperationType.TRANSLATION: [
        "gpt-4o-mini", "mistral-medium", "claude-3-haiku"
    ],
    
    # Models with web access for analysis
    OperationType.ANALYSIS: [
        "perplexity-sonar", "claude-3-haiku", "gemini-pro"
    ]
}
```

## 🔧 Environment Variables

Set up your API keys:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Azure OpenAI
export AZURE_OPENAI_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# Mistral
export MISTRAL_API_KEY="..."

# Perplexity
export PERPLEXITY_API_KEY="pplx-..."

# Hugging Face
export HUGGINGFACE_API_KEY="hf_..."

# Cohere
export COHERE_API_KEY="..."
```

## 🏥 Health Checks and Monitoring

The system automatically performs health checks on configured models:

- **Green**: Model is responding correctly
- **Yellow**: Model has issues but is available
- **Red**: Model is unavailable or misconfigured

Access health monitoring at: **Settings → AI Services → Status & Usage**

## 💡 Best Practices

### 1. **Cost Management**
- Use cheaper models for testing and development
- Use expensive models only for production/critical tasks
- Set up proper operation-specific assignments

### 2. **Performance Optimization**
- Use local models (Ollama) for development
- Use streaming models for better user experience
- Configure proper context lengths

### 3. **Reliability**
- Set up multiple models per operation type for failover
- Use health checks to monitor model availability
- Configure reasonable timeout values

### 4. **Security**
- Store API keys in environment variables
- Use different keys for different environments
- Monitor API usage and costs

## 🔄 Model Updates

### Adding New Models via Web Interface

1. Go to **Settings → AI Services**
2. Click **"Add Model"**
3. Fill in the configuration form
4. Test the model connection
5. Assign to operations as needed

### Updating Existing Models

1. Go to **Settings → AI Services → Models**
2. Click on the model you want to edit
3. Update the configuration
4. Save and test

### Importing/Exporting Configurations

- **Export**: Settings → AI Services → Export (downloads JSON)
- **Import**: Settings → AI Services → Import (uploads JSON)

## 🐛 Troubleshooting

### Common Issues

1. **"Model not responding"**
   - Check API key validity
   - Verify endpoint URL
   - Check network connectivity

2. **"Invalid model ID"**
   - Verify model ID with provider documentation
   - Check for typos in model identifier

3. **"Rate limit exceeded"**
   - Check API quota limits
   - Implement request throttling
   - Consider upgrading API plan

4. **"Local model not found"**
   - Ensure Ollama is running
   - Pull the model: `ollama pull llama3:8b`
   - Check endpoint connectivity

### Getting Help

- Check the application logs for detailed error messages
- Use the health check feature to diagnose issues
- Refer to provider-specific documentation for API details

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Google AI Studio](https://ai.google.dev/)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Perplexity API Docs](https://docs.perplexity.ai/)