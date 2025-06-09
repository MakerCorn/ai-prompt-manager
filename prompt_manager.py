"""
MIT License

Copyright (c) 2025 MakerCorn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import gradio as gr
import json
import requests
import sqlite3
from typing import Dict, Optional, List
from prompt_data_manager import PromptDataManager

class AIPromptManager:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.data = PromptDataManager(db_path)
        self.init_database = self.data.init_database
        self.add_prompt = self.data.add_prompt
        self.update_prompt = self.data.update_prompt
        self.delete_prompt = self.data.delete_prompt
        self.get_all_prompts = self.data.get_all_prompts
        self.get_enhancement_prompts = self.data.get_enhancement_prompts
        self.get_categories = self.data.get_categories
        self.search_prompts = self.data.search_prompts
        self.get_prompts_by_category = self.data.get_prompts_by_category
        self.get_prompt_by_name = self.data.get_prompt_by_name
        
        self.config = self.load_config()
        self.enhancement_config = self.load_enhancement_config()
    
    def save_config(self, service_type: str, api_endpoint: str, api_key: str, model_name: str) -> str:
        """Save AI service configuration"""
        config = {
            'service_type': service_type,
            'api_endpoint': api_endpoint,
            'api_key': api_key,
            'model_name': model_name
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                      ('ai_service', json.dumps(config)))
        conn.commit()
        conn.close()
        
        self.config = config
        return "Configuration saved successfully!"
    
    def save_enhancement_config(self, service_type: str, api_endpoint: str, api_key: str, model_name: str, enhancement_prompt_name: Optional[str] = None, set_as_default: bool = False) -> str:
        """Save enhancement service configuration"""
        config = {
            'service_type': service_type,
            'api_endpoint': api_endpoint,
            'api_key': api_key,
            'model_name': model_name,
            'enhancement_prompt_name': enhancement_prompt_name
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                      ('enhancement_service', json.dumps(config)))
        
        if set_as_default:
            # Also update the main config as default
            cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                          ('default_enhancement_service', json.dumps(config)))
        
        conn.commit()
        conn.close()
        
        self.enhancement_config = config
        return "Enhancement configuration saved successfully!"
    
    def load_config(self) -> Dict:
        """Load AI service configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', ('ai_service',))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        else:
            return {
                'service_type': 'openai',
                'api_endpoint': 'http://localhost:1234/v1',
                'api_key': '',
                'model_name': 'gpt-3.5-turbo'
            }
    
    def load_enhancement_config(self) -> Dict:
        """Load enhancement service configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', ('enhancement_service',))
        result = cursor.fetchone()
        
        if not result:
            # Try loading default enhancement service
            cursor.execute('SELECT value FROM config WHERE key = ?', ('default_enhancement_service',))
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result[0])
        else:
            return {
                'service_type': 'openai',
                'api_endpoint': 'http://localhost:1234/v1',
                'api_key': '',
                'model_name': 'gpt-4',
                'enhancement_prompt_name': None
            }
    
    def format_prompts_for_display(self, prompts: List[Dict]) -> str:
        """Format prompts for tree view display"""
        if not prompts:
            return "No prompts found."
        
        # Separate enhancement prompts from regular prompts
        regular_prompts = [p for p in prompts if not p.get('is_enhancement_prompt', False)]
        enhancement_prompts = [p for p in prompts if p.get('is_enhancement_prompt', False)]
        
        output = []
        
        # Display enhancement prompts first if any
        if enhancement_prompts:
            output.append("🔧 **Enhancement Prompts**")
            for prompt in sorted(enhancement_prompts, key=lambda x: x['name']):
                preview = prompt['content'][:100] + "..." if len(prompt['content']) > 100 else prompt['content']
                tags_str = f" 🏷️ {prompt['tags']}" if prompt['tags'] else ""
                output.append(f"  └── ⚡ **{prompt['name']}** - {prompt['title']}{tags_str}")
                output.append(f"      {preview}")
                output.append("")
        
        # Group regular prompts by category
        categories = {}
        for prompt in regular_prompts:
            category = prompt['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(prompt)
        
        # Format regular prompts as tree view
        for category, category_prompts in sorted(categories.items()):
            output.append(f"📁 **{category}** ({len(category_prompts)} prompts)")
            for prompt in sorted(category_prompts, key=lambda x: x['name']):
                preview = prompt['content'][:100] + "..." if len(prompt['content']) > 100 else prompt['content']
                tags_str = f" 🏷️ {prompt['tags']}" if prompt['tags'] else ""
                output.append(f"  └── 📄 **{prompt['name']}** - {prompt['title']}{tags_str}")
                output.append(f"      {preview}")
                output.append("")
        
        return "\n".join(output)
    
    def call_ai_service(self, prompt_text: str, config: Dict) -> str:
        """Call AI service with given configuration"""
        try:
            service_type = config['service_type']
            api_endpoint = config['api_endpoint']
            api_key = config['api_key']
            model_name = config['model_name']
            
            headers = {'Content-Type': 'application/json'}
            
            if service_type == 'ollama':
                # Ollama API format
                endpoint = f"{api_endpoint.rstrip('/')}/generate"
                payload = {
                    "model": model_name,
                    "prompt": prompt_text,
                    "stream": False
                }
            elif service_type == 'llamacpp':
                # Llama.cpp server format
                endpoint = f"{api_endpoint.rstrip('/')}/completion"
                payload = {
                    "prompt": prompt_text,
                    "n_predict": 1024,
                    "temperature": 0.7,
                    "stop": ["</s>", "Human:", "Assistant:"]
                }
            else:
                # OpenAI compatible format (including LMStudio)
                endpoint = f"{api_endpoint.rstrip('/')}/chat/completions"
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt_text}],
                    "temperature": 0.7,
                    "max_tokens": 1500
                }
                if api_key:
                    headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response based on service type
            if service_type == 'ollama':
                return result.get('response', 'No response received')
            elif service_type == 'llamacpp':
                return result.get('content', 'No response received')
            else:
                # OpenAI compatible
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return 'No response received'
                    
        except requests.exceptions.RequestException as e:
            return f"Error connecting to AI service: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Error decoding response from AI service: {str(e)}"
        except KeyError as e:
            return f"Error parsing AI service response: missing key {str(e)}"
    
    def execute_prompt(self, prompt_text: str) -> str:
        """Execute a prompt against the configured AI service"""
        if not prompt_text.strip():
            return "Error: No prompt provided!"
        
        if not self.config.get('api_endpoint') or not self.config.get('model_name'):
            return "Error: AI service not configured! Please configure the service first."
        
        return self.call_ai_service(prompt_text, self.config)
    
    def enhance_prompt(self, original_prompt: str, enhancement_prompt_name: Optional[str] = None) -> str:
        """Enhance a prompt using the enhancement service and prompt"""
        if not original_prompt.strip():
            return "Error: No original prompt provided!"
        
        if not self.enhancement_config.get('api_endpoint') or not self.enhancement_config.get('model_name'):
            return "Error: Enhancement service not configured! Please configure the enhancement service first."
        
        # Get enhancement prompt
        if enhancement_prompt_name:
            enhancement_prompt_data = self.get_prompt_by_name(enhancement_prompt_name)
            if not enhancement_prompt_data:
                return f"Error: Enhancement prompt '{enhancement_prompt_name}' not found!"
            enhancement_template = enhancement_prompt_data['content']
        else:
            # Default enhancement prompt
            enhancement_template = """You are an expert prompt engineer. Your task is to enhance and improve the given prompt to make it more effective, clear, and likely to produce better results from AI models.

Please improve the following prompt by:
1. Making it more specific and clear
2. Adding context where helpful
3. Improving the structure and flow
4. Adding relevant constraints or guidelines
5. Making it more engaging and effective

Original prompt:
{original_prompt}

Please provide only the enhanced prompt as your response, without any explanations or additional text.
"""
        
        # Replace placeholder with original prompt
        full_enhancement_prompt = enhancement_template.replace("{original_prompt}", original_prompt)
        
        return self.call_ai_service(full_enhancement_prompt, self.enhancement_config)

# Initialize the prompt manager
prompt_manager = AIPromptManager()

# Gradio interface functions
def save_configuration(service_type, api_endpoint, api_key, model_name):
    """Save the AI service configuration to the database"""
    result = prompt_manager.save_config(service_type, api_endpoint, api_key, model_name)
    return (result,)

def save_enhancement_configuration(service_type, api_endpoint, api_key, model_name, enhancement_prompt_name, set_as_default):
    result = prompt_manager.save_enhancement_config(service_type, api_endpoint, api_key, model_name, enhancement_prompt_name, set_as_default)
    return (result,)

def add_new_prompt(name, title, content, category, tags, is_enhancement_prompt):
    result = prompt_manager.add_prompt(name, title, content, category, tags, is_enhancement_prompt)
    # Refresh the prompts display
    prompts = prompt_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + prompt_manager.get_categories()
    
    # Update enhancement prompts dropdown
    enhancement_prompts = prompt_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    return result, tree_view, gr.update(choices=categories), gr.update(choices=enhancement_choices), "", "", "", "", "", False

def refresh_prompts_display(search_term="", category_filter="All"):
    if search_term:
        prompts = prompt_manager.search_prompts(search_term)
    else:
        prompts = prompt_manager.get_prompts_by_category(category_filter if category_filter != "All" else None)
    
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    return tree_view

def load_prompt_for_editing(prompt_name):
    if not prompt_name.strip():
        return "", "", "", "", "", False, "Please enter a prompt name!"
    
    prompt = prompt_manager.get_prompt_by_name(prompt_name.strip())
    if prompt:
        return (prompt['name'], prompt['title'], prompt['content'], prompt['category'], 
               prompt['tags'] or "", prompt.get('is_enhancement_prompt', False),
               f"Loaded prompt '{prompt['name']}' for editing")
    else:
        return "", "", "", "", "", False, f"Prompt '{prompt_name}' not found!"

def update_existing_prompt(original_name, new_name, title, content, category, tags, is_enhancement_prompt):
    if not original_name.strip():
        return "Please enter the original prompt name!", "", gr.update(), gr.update(), "", "", "", "", "", False, ""
    
    result = prompt_manager.update_prompt(original_name, new_name, title, content, category, tags, is_enhancement_prompt)
    # Refresh the prompts display
    prompts = prompt_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + prompt_manager.get_categories()
    
    # Update enhancement prompts dropdown
    enhancement_prompts = prompt_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    return result, tree_view, gr.update(choices=categories), gr.update(choices=enhancement_choices), "", "", "", "", "", False, ""

def delete_existing_prompt(prompt_name):
    if not prompt_name.strip():
        return "Please enter a prompt name!", "", gr.update(), gr.update()
    
    result = prompt_manager.delete_prompt(prompt_name.strip())
    # Refresh the prompts display
    prompts = prompt_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + prompt_manager.get_categories()
    
    # Update enhancement prompts dropdown
    enhancement_prompts = prompt_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    return result, tree_view, gr.update(choices=categories), gr.update(choices=enhancement_choices)

def select_prompt_for_execution(prompt_name):
    if not prompt_name.strip():
        return "Please enter a prompt name!"
    
    prompt = prompt_manager.get_prompt_by_name(prompt_name.strip())
    if prompt:
        return prompt['content']
    else:
        return f"Prompt '{prompt_name}' not found!"

def execute_ai_prompt(prompt_text):
    if not prompt_text.strip():
        return "Please enter a prompt to execute!"
    
    return prompt_manager.execute_prompt(prompt_text)

def enhance_ai_prompt(original_prompt, enhancement_prompt_name):
    if not original_prompt.strip():
        return "Please enter a prompt to enhance!"
    
    return prompt_manager.enhance_prompt(original_prompt, enhancement_prompt_name)

# Create Gradio interface
def create_interface():
    # Load initial data
    config = prompt_manager.load_config()
    enhancement_config = prompt_manager.load_enhancement_config()
    prompts = prompt_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + prompt_manager.get_categories()
    
    # Get enhancement prompts for dropdown
    enhancement_prompts = prompt_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    with gr.Blocks(title="AI Prompt Manager", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🤖 AI Prompt Manager
        
        Manage and execute AI prompts with multiple service providers including OpenAI, LM Studio, Ollama, and Llama.cpp.
        **New**: Enhance your prompts using different AI models and enhancement templates!
        """)
        
        with gr.Tabs():
            # Prompt Management Tab
            with gr.TabItem("📝 Prompt Management"):
                gr.Markdown("### Add/Edit Prompts")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        prompt_name = gr.Textbox(label="Prompt Name (Required)", placeholder="Enter unique prompt name")
                        prompt_title = gr.Textbox(label="Prompt Title", placeholder="Enter prompt title")
                        prompt_category = gr.Textbox(label="Category", placeholder="e.g., Writing, Analysis, Creative")
                        prompt_content = gr.Textbox(
                            label="Prompt Content",
                            lines=6,
                            placeholder="Enter your AI prompt here..."
                        )
                        prompt_tags = gr.Textbox(label="Tags (comma-separated)", placeholder="creative, writing, analysis")
                        is_enhancement_prompt = gr.Checkbox(
                            label="Enhancement Prompt", 
                            value=False,
                            info="Check this if this prompt is designed to enhance other prompts"
                        )
                        
                        with gr.Row():
                            add_btn = gr.Button("➕ Add Prompt", variant="primary")
                            update_btn = gr.Button("✏️ Update Prompt", variant="secondary")
                            clear_btn = gr.Button("🗑️ Clear Form")
                        
                        prompt_status = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Quick Actions")
                        edit_prompt_name = gr.Textbox(label="Prompt Name to Edit", placeholder="Enter prompt name")
                        load_edit_btn = gr.Button("📝 Load for Editing")
                        
                        delete_prompt_name = gr.Textbox(label="Prompt Name to Delete", placeholder="Enter prompt name")
                        delete_btn = gr.Button("🗑️ Delete Prompt", variant="stop")
                        
                        edit_status = gr.Textbox(label="Edit Status", interactive=False)
                
                # Event handlers for prompt management
                add_btn.click(
                    add_new_prompt,
                    inputs=[prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt],
                    outputs=[prompt_status, gr.Textbox(), gr.Dropdown(), gr.Dropdown(), prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt]
                )
                
                load_edit_btn.click(
                    load_prompt_for_editing,
                    inputs=[edit_prompt_name],
                    outputs=[prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt, edit_status]
                )
                
                update_btn.click(
                    update_existing_prompt,
                    inputs=[edit_prompt_name, prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt],
                    outputs=[prompt_status, gr.Textbox(), gr.Dropdown(), gr.Dropdown(), prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt, edit_status]
                )
                
                delete_btn.click(
                    delete_existing_prompt,
                    inputs=[delete_prompt_name],
                    outputs=[edit_status, gr.Textbox(), gr.Dropdown(), gr.Dropdown()]
                )
                
                clear_btn.click(
                    lambda: ("", "", "", "", "", False, ""),
                    outputs=[prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt, prompt_status]
                )
            
            # Prompt Library Tab
            with gr.TabItem("📚 Prompt Library"):
                gr.Markdown("### Browse and Search Prompts")
                
                with gr.Row():
                    search_box = gr.Textbox(label="Search Prompts", placeholder="Search by name, title, content, or tags...")
                    category_filter = gr.Dropdown(
                        choices=categories,
                        value="All",
                        label="Filter by Category"
                    )
                    refresh_btn = gr.Button("🔄 Refresh")
                
                prompts_display = gr.Textbox(
                    label="Prompts Tree View",
                    value=tree_view,
                    lines=20,
                    max_lines=25,
                    interactive=False
                )
                
                # Event handlers for library
                search_box.change(
                    refresh_prompts_display,
                    inputs=[search_box, category_filter],
                    outputs=prompts_display
                )
                
                category_filter.change(
                    refresh_prompts_display,
                    inputs=[search_box, category_filter],
                    outputs=prompts_display
                )
                
                refresh_btn.click(
                    refresh_prompts_display,
                    inputs=[search_box, category_filter],
                    outputs=prompts_display
                )
            
            # Prompt Execution Tab
            with gr.TabItem("🚀 Prompt Execution"):
                gr.Markdown("### Execute AI Prompts")
                
                with gr.Row():
                    with gr.Column():
                        execution_prompt = gr.Textbox(
                            label="Prompt to Execute",
                            lines=8,
                            placeholder="Enter a prompt or load one by name..."
                        )
                        
                        with gr.Row():
                            load_prompt_name = gr.Textbox(label="Load Prompt by Name", placeholder="Enter prompt name")
                            load_prompt_btn = gr.Button("📋 Load Prompt")
                        
                        execute_btn = gr.Button("🚀 Execute Prompt", variant="primary", size="lg")
                    
                    with gr.Column():
                        ai_response = gr.Textbox(
                            label="AI Response",
                            lines=12,
                            placeholder="AI response will appear here...",
                            interactive=False
                        )
                
                # Event handlers for execution
                load_prompt_btn.click(
                    select_prompt_for_execution,
                    inputs=[load_prompt_name],
                    outputs=execution_prompt
                )
                
                execute_btn.click(
                    execute_ai_prompt,
                    inputs=[execution_prompt],
                    outputs=ai_response
                )
            
            # Prompt Enhancement Tab
            with gr.TabItem("⚡ Prompt Enhancement"):
                gr.Markdown("### Enhance Your Prompts")
                gr.Markdown("Use a different AI model and enhancement prompt to improve your existing prompts.")
                
                with gr.Row():
                    with gr.Column():
                        original_prompt = gr.Textbox(
                            label="Original Prompt",
                            lines=6,
                            placeholder="Enter the prompt you want to enhance, or load one by name..."
                        )
                        
                        with gr.Row():
                            load_original_name = gr.Textbox(label="Load Original Prompt by Name", placeholder="Enter prompt name")
                            load_original_btn = gr.Button("📋 Load Original")
                        
                        enhancement_prompt_selector = gr.Dropdown(
                            choices=enhancement_choices,
                            label="Enhancement Prompt (optional)",
                            info="Select an enhancement prompt, or leave blank to use default",
                            value=enhancement_config.get('enhancement_prompt_name')
                        )
                        
                        enhance_btn = gr.Button("⚡ Enhance Prompt", variant="primary", size="lg")
                    
                    with gr.Column():
                        enhanced_prompt = gr.Textbox(
                            label="Enhanced Prompt",
                            lines=12,
                            placeholder="Enhanced prompt will appear here...",
                            interactive=False
                        )
                        
                        with gr.Row():
                            copy_enhanced_btn = gr.Button("📋 Copy to Execution", variant="secondary")
                            save_enhanced_name = gr.Textbox(label="Name for Enhanced Prompt", placeholder="Enter name to save enhanced prompt")
                            save_enhanced_btn = gr.Button("💾 Save Enhanced Prompt", variant="secondary")
                
                enhancement_status = gr.Textbox(label="Enhancement Status", interactive=False)
                
                # Event handlers for enhancement
                load_original_btn.click(
                    select_prompt_for_execution,
                    inputs=[load_original_name],
                    outputs=original_prompt
                )
                
                enhance_btn.click(
                    enhance_ai_prompt,
                    inputs=[original_prompt, enhancement_prompt_selector],
                    outputs=enhanced_prompt
                )
                
                def copy_to_execution(enhanced_text):
                    return enhanced_text
                
                copy_enhanced_btn.click(
                    copy_to_execution,
                    inputs=[enhanced_prompt],
                    outputs=execution_prompt
                )
                
                def save_enhanced_as_new(enhanced_text, name):
                    if not enhanced_text.strip():
                        return "No enhanced prompt to save!"
                    
                    if not name.strip():
                        return "Please enter a name for the enhanced prompt!"
                    
                    # Create title from name or use first part of enhanced text
                    title = f"Enhanced: {name}"
                    
                    result = prompt_manager.add_prompt(name.strip(), title, enhanced_text, "Enhanced", "enhanced,improved", False)
                    return result
                
                save_enhanced_btn.click(
                    save_enhanced_as_new,
                    inputs=[enhanced_prompt, save_enhanced_name],
                    outputs=enhancement_status
                )
            
            # Configuration Tab (moved to last)
            with gr.TabItem("⚙️ Configuration"):
                gr.Markdown("### Primary AI Service Configuration")
                
                with gr.Row():
                    service_type = gr.Dropdown(
                        choices=["openai", "lmstudio", "ollama", "llamacpp"],
                        value=config.get('service_type', 'openai'),
                        label="Service Type"
                    )
                    model_name = gr.Textbox(
                        value=config.get('model_name', 'gpt-3.5-turbo'),
                        label="Model Name",
                        placeholder="e.g., gpt-3.5-turbo, llama2"
                    )
                
                api_endpoint = gr.Textbox(
                    value=config.get('api_endpoint', 'http://localhost:1234/v1'),
                    label="API Endpoint",
                    placeholder="http://localhost:1234/v1"
                )
                
                api_key = gr.Textbox(
                    value=config.get('api_key', ''),
                    label="API Key (optional)",
                    type="password",
                    placeholder="Enter API key if required"
                )
                
                config_save_btn = gr.Button("💾 Save Configuration", variant="primary")
                config_status = gr.Textbox(label="Status", interactive=False)
                
                gr.Markdown("---")
                gr.Markdown("### Enhancement Service Configuration")
                gr.Markdown("Configure a separate AI service specifically for prompt enhancement (can be the same or different from primary service)")
                
                with gr.Row():
                    enh_service_type = gr.Dropdown(
                        choices=["openai", "lmstudio", "ollama", "llamacpp"],
                        value=enhancement_config.get('service_type', 'openai'),
                        label="Enhancement Service Type"
                    )
                    enh_model_name = gr.Textbox(
                        value=enhancement_config.get('model_name', 'gpt-4'),
                        label="Enhancement Model Name",
                        placeholder="e.g., gpt-4, claude-3-sonnet"
                    )
                
                enh_api_endpoint = gr.Textbox(
                    value=enhancement_config.get('api_endpoint', 'http://localhost:1234/v1'),
                    label="Enhancement API Endpoint",
                    placeholder="http://localhost:1234/v1"
                )
                
                enh_api_key = gr.Textbox(
                    value=enhancement_config.get('api_key', ''),
                    label="Enhancement API Key (optional)",
                    type="password",
                    placeholder="Enter API key if required"
                )
                
                enh_prompt_dropdown = gr.Dropdown(
                    choices=enhancement_choices,
                    value=enhancement_config.get('enhancement_prompt_name'),
                    label="Default Enhancement Prompt (optional)",
                    info="Select a stored enhancement prompt, or leave blank to use default"
                )
                
                with gr.Row():
                    enh_config_save_btn = gr.Button("💾 Save Enhancement Config", variant="primary")
                    set_as_default_btn = gr.Button("⭐ Save & Set as Default", variant="secondary")
                
                enh_config_status = gr.Textbox(label="Enhancement Config Status", interactive=False)
                
                # Event handlers for configuration
                config_save_btn.click(
                    save_configuration,
                    inputs=[service_type, api_endpoint, api_key, model_name],
                    outputs=config_status
                )
                
                enh_config_save_btn.click(
                    lambda *args: save_enhancement_configuration(*args, False),
                    inputs=[enh_service_type, enh_api_endpoint, enh_api_key, enh_model_name, enh_prompt_dropdown],
                    outputs=enh_config_status
                )
                
                set_as_default_btn.click(
                    lambda *args: save_enhancement_configuration(*args, True),
                    inputs=[enh_service_type, enh_api_endpoint, enh_api_key, enh_model_name, enh_prompt_dropdown],
                    outputs=enh_config_status
                )
        
        gr.Markdown("""
        ---
        **Instructions:**
        1. **Configuration**: Set up your primary AI service and enhancement service (can be different models)
        2. **Prompt Management**: Add regular prompts and enhancement prompts using unique names
        3. **Prompt Library**: Browse and search your prompts in a tree view organized by category and sorted by name
        4. **Prompt Execution**: Execute prompts against your primary AI service using prompt names
        5. **Prompt Enhancement**: Use your enhancement service to improve existing prompts
        
        **Name-Based System:**
        - **Names are required** and must be unique for each prompt
        - Use names for all lookups, editing, and deletion operations
        - Names make it easier to reference and manage your prompts
        - Prompts are sorted by category first, then by name within each category
        
        **Enhancement Features:**
        - Use different AI models for enhancement (e.g., GPT-4 for enhancing prompts that will run on GPT-3.5)
        - Create custom enhancement prompts or use the built-in default
        - Set enhancement configurations as default for future enhancements
        - Save enhanced prompts back to your library with new names
        
        **Tips:**
        - Use descriptive, unique names for easy identification
        - Create enhancement prompts that give specific instructions for improvement
        - Use more powerful models for enhancement (they can improve prompts for smaller models)
        - Enhancement prompts can include placeholders like `{original_prompt}` to insert the original text
        - Mark prompts as "Enhancement Prompts" to organize them separately in the tree view
        """)
    
    return app

# Launch the application
if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
