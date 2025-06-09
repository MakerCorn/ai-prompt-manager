"""
MIT License

Copyright (c) 2025 MakerCorn

Multi-tenant AI Prompt Manager with authentication, SSO/ADFS support, and admin interface.
"""

import gradio as gr
import json
import requests
import os
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs
from prompt_data_manager import PromptDataManager
from auth_manager import AuthManager, User, Tenant

class AIPromptManager:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.auth_manager = AuthManager(db_path)
        self.current_user = None
        self.current_tenant = None
        
        # Initialize data manager without tenant context initially
        self.data = None
        
    def get_data_manager(self) -> Optional[PromptDataManager]:
        """Get tenant-aware data manager"""
        if self.current_user:
            if not self.data or self.data.tenant_id != self.current_user.tenant_id:
                self.data = PromptDataManager(
                    db_path=self.db_path,
                    tenant_id=self.current_user.tenant_id,
                    user_id=self.current_user.id
                )
            return self.data
        return None
    
    def set_current_user(self, user: User):
        """Set current user and initialize tenant-aware data manager"""
        self.current_user = user
        self.data = PromptDataManager(
            db_path=self.db_path,
            tenant_id=user.tenant_id,
            user_id=user.id
        )
        
        # Load configurations
        self.config = self.load_config()
        self.enhancement_config = self.load_enhancement_config()
    
    def clear_current_user(self):
        """Clear current user session"""
        self.current_user = None
        self.data = None
        self.config = {}
        self.enhancement_config = {}
    
    def login(self, email: str, password: str, subdomain: str = "localhost") -> Tuple[bool, str, Optional[str]]:
        """Authenticate user and return success, message, and session token"""
        success, user, message = self.auth_manager.authenticate_user(email, password, subdomain)
        
        if success and user:
            self.set_current_user(user)
            token = self.auth_manager.create_session(user.id)
            return True, f"Welcome, {user.first_name}!", token
        else:
            return False, message, None
    
    def validate_session(self, token: str) -> bool:
        """Validate session token and set current user"""
        if not token:
            return False
            
        success, user = self.auth_manager.validate_session(token)
        if success and user:
            self.set_current_user(user)
            return True
        else:
            self.clear_current_user()
            return False
    
    def logout(self, token: str) -> bool:
        """Logout user"""
        if token:
            self.auth_manager.logout_user(token)
        self.clear_current_user()
        return True
    
    def save_config(self, service_type: str, api_endpoint: str, api_key: str, model_name: str) -> str:
        """Save AI service configuration"""
        if not self.current_user:
            return "Error: User not authenticated!"
        
        config = {
            'service_type': service_type,
            'api_endpoint': api_endpoint,
            'api_key': api_key,
            'model_name': model_name
        }
        
        data_manager = self.get_data_manager()
        if data_manager and data_manager.save_config('ai_service', json.dumps(config)):
            self.config = config
            return "Configuration saved successfully!"
        return "Error saving configuration!"
    
    def save_enhancement_config(self, service_type: str, api_endpoint: str, api_key: str, 
                               model_name: str, enhancement_prompt_name: Optional[str] = None) -> str:
        """Save enhancement service configuration"""
        if not self.current_user:
            return "Error: User not authenticated!"
        
        config = {
            'service_type': service_type,
            'api_endpoint': api_endpoint,
            'api_key': api_key,
            'model_name': model_name,
            'enhancement_prompt_name': enhancement_prompt_name
        }
        
        data_manager = self.get_data_manager()
        if data_manager and data_manager.save_config('enhancement_service', json.dumps(config)):
            self.enhancement_config = config
            return "Enhancement configuration saved successfully!"
        return "Error saving enhancement configuration!"
    
    def load_config(self) -> Dict:
        """Load AI service configuration"""
        if not self.current_user:
            return self._get_default_config()
        
        data_manager = self.get_data_manager()
        if data_manager:
            config_str = data_manager.get_config('ai_service')
            if config_str:
                try:
                    return json.loads(config_str)
                except json.JSONDecodeError:
                    pass
        
        return self._get_default_config()
    
    def load_enhancement_config(self) -> Dict:
        """Load enhancement service configuration"""
        if not self.current_user:
            return self._get_default_enhancement_config()
        
        data_manager = self.get_data_manager()
        if data_manager:
            config_str = data_manager.get_config('enhancement_service')
            if config_str:
                try:
                    return json.loads(config_str)
                except json.JSONDecodeError:
                    pass
        
        return self._get_default_enhancement_config()
    
    def _get_default_config(self) -> Dict:
        return {
            'service_type': 'openai',
            'api_endpoint': 'http://localhost:1234/v1',
            'api_key': '',
            'model_name': 'gpt-3.5-turbo'
        }
    
    def _get_default_enhancement_config(self) -> Dict:
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
                created_by = f" 👤 {prompt.get('user_id', 'Unknown')[:8]}..." if prompt.get('user_id') else ""
                output.append(f"  └── ⚡ **{prompt['name']}** - {prompt['title']}{tags_str}{created_by}")
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
                created_by = f" 👤 {prompt.get('user_id', 'Unknown')[:8]}..." if prompt.get('user_id') else ""
                output.append(f"  └── 📄 **{prompt['name']}** - {prompt['title']}{tags_str}{created_by}")
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
        if not self.current_user:
            return "Error: User not authenticated!"
        
        if not prompt_text.strip():
            return "Error: No prompt provided!"
        
        if not self.config.get('api_endpoint') or not self.config.get('model_name'):
            return "Error: AI service not configured! Please configure the service first."
        
        return self.call_ai_service(prompt_text, self.config)
    
    def enhance_prompt(self, original_prompt: str, enhancement_prompt_name: Optional[str] = None) -> str:
        """Enhance a prompt using the enhancement service and prompt"""
        if not self.current_user:
            return "Error: User not authenticated!"
        
        if not original_prompt.strip():
            return "Error: No original prompt provided!"
        
        if not self.enhancement_config.get('api_endpoint') or not self.enhancement_config.get('model_name'):
            return "Error: Enhancement service not configured! Please configure the enhancement service first."
        
        data_manager = self.get_data_manager()
        if not data_manager:
            return "Error: Data manager not available!"
        
        # Get enhancement prompt
        if enhancement_prompt_name:
            enhancement_prompt_data = data_manager.get_prompt_by_name(enhancement_prompt_name)
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
    
    # Admin functions
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_user and self.current_user.role == 'admin'
    
    def create_tenant(self, name: str, subdomain: str, max_users: int) -> Tuple[bool, str]:
        """Create new tenant (admin only)"""
        if not self.is_admin():
            return False, "Access denied: Admin privileges required"
        
        return self.auth_manager.create_tenant(name, subdomain, max_users)
    
    def create_user(self, tenant_id: str, email: str, password: str, first_name: str, 
                   last_name: str, role: str) -> Tuple[bool, str]:
        """Create new user (admin only)"""
        if not self.is_admin():
            return False, "Access denied: Admin privileges required"
        
        return self.auth_manager.create_user(tenant_id, email, password, first_name, last_name, role)
    
    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants (admin only)"""
        if not self.is_admin():
            return []
        
        return self.auth_manager.get_all_tenants()
    
    def get_tenant_users(self, tenant_id: str) -> List[User]:
        """Get users for a tenant (admin only)"""
        if not self.is_admin():
            return []
        
        return self.auth_manager.get_tenant_users(tenant_id)

# Initialize the prompt manager
prompt_manager = AIPromptManager()

# Session state management
session_store = {}

def get_session_token(request: gr.Request) -> Optional[str]:
    """Extract session token from request"""
    if hasattr(request, 'headers') and 'authorization' in request.headers:
        auth_header = request.headers['authorization']
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
    
    # Fallback to cookies or query params
    if hasattr(request, 'query_params') and 'token' in request.query_params:
        return request.query_params['token']
    
    return None

def check_authentication(request: gr.Request) -> Tuple[bool, str]:
    """Check if user is authenticated"""
    token = get_session_token(request)
    if token and prompt_manager.validate_session(token):
        user_info = f"{prompt_manager.current_user.first_name} {prompt_manager.current_user.last_name} ({prompt_manager.current_user.email})"
        role_badge = "🛡️ Admin" if prompt_manager.is_admin() else "👤 User"
        return True, f"✅ {role_badge} | {user_info}"
    else:
        prompt_manager.clear_current_user()
        return False, "❌ Not authenticated"

# Authentication functions
def login_user(email, password, subdomain):
    """Login user"""
    success, message, token = prompt_manager.login(email, password, subdomain)
    if success:
        return (
            gr.update(visible=False),  # Hide login
            gr.update(visible=True),   # Show main app
            gr.update(visible=prompt_manager.is_admin()),  # Show admin if admin
            message,
            f"✅ {'🛡️ Admin' if prompt_manager.is_admin() else '👤 User'} | {prompt_manager.current_user.first_name} {prompt_manager.current_user.last_name}",
            token
        )
    else:
        return (
            gr.update(visible=True),   # Keep login visible
            gr.update(visible=False),  # Hide main app
            gr.update(visible=False),  # Hide admin
            message,
            "❌ Not authenticated",
            ""
        )

def logout_user(token):
    """Logout user"""
    prompt_manager.logout(token)
    return (
        gr.update(visible=True),   # Show login
        gr.update(visible=False),  # Hide main app
        gr.update(visible=False),  # Hide admin
        "Logged out successfully",
        "❌ Not authenticated",
        ""
    )

def handle_sso_login(subdomain):
    """Handle SSO login"""
    login_url = prompt_manager.auth_manager.get_sso_login_url(subdomain)
    if login_url:
        return f"Please visit: {login_url}"
    else:
        return "SSO not configured"

# Prompt management functions
def add_new_prompt(name, title, content, category, tags, is_enhancement_prompt):
    """Add new prompt"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!", "", "", "", "", "", False
    
    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!", "", "", "", "", "", False
    
    result = data_manager.add_prompt(name, title, content, category, tags, is_enhancement_prompt)
    
    # Refresh the prompts display
    prompts = data_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + data_manager.get_categories()
    
    # Update enhancement prompts dropdown
    enhancement_prompts = data_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    return result, tree_view, gr.update(choices=categories), gr.update(choices=enhancement_choices), "", "", "", "", "", False

def refresh_prompts_display(search_term="", category_filter="All"):
    """Refresh prompts display"""
    if not prompt_manager.current_user:
        return "No prompts found - not authenticated."
    
    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Data manager not available."
    
    if search_term:
        prompts = data_manager.search_prompts(search_term)
    else:
        prompts = data_manager.get_prompts_by_category(category_filter if category_filter != "All" else None)
    
    return prompt_manager.format_prompts_for_display(prompts)

def load_prompt_for_editing(prompt_name):
    """Load prompt for editing"""
    if not prompt_manager.current_user:
        return "", "", "", "", "", False, "Error: User not authenticated!"
    
    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "", "", "", "", "", False, "Error: Data manager not available!"
    
    if not prompt_name.strip():
        return "", "", "", "", "", False, "Please enter a prompt name!"
    
    prompt = data_manager.get_prompt_by_name(prompt_name.strip())
    if prompt:
        return (prompt['name'], prompt['title'], prompt['content'], prompt['category'], 
               prompt['tags'] or "", prompt.get('is_enhancement_prompt', False),
               f"Loaded prompt '{prompt['name']}' for editing")
    else:
        return "", "", "", "", "", False, f"Prompt '{prompt_name}' not found!"

def update_existing_prompt(original_name, new_name, title, content, category, tags, is_enhancement_prompt):
    """Update existing prompt"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!", "", gr.update(), gr.update(), "", "", "", "", "", False, ""
    
    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!", "", gr.update(), gr.update(), "", "", "", "", "", False, ""
    
    if not original_name.strip():
        return "Please enter the original prompt name!", "", gr.update(), gr.update(), "", "", "", "", "", False, ""
    
    result = data_manager.update_prompt(original_name, new_name, title, content, category, tags, is_enhancement_prompt)
    
    # Refresh the prompts display
    prompts = data_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + data_manager.get_categories()
    
    # Update enhancement prompts dropdown
    enhancement_prompts = data_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    return result, tree_view, gr.update(choices=categories), gr.update(choices=enhancement_choices), "", "", "", "", "", False, ""

def delete_existing_prompt(prompt_name):
    """Delete existing prompt"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!", "", gr.update(), gr.update()
    
    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!", "", gr.update(), gr.update()
    
    if not prompt_name.strip():
        return "Please enter a prompt name!", "", gr.update(), gr.update()
    
    result = data_manager.delete_prompt(prompt_name.strip())
    
    # Refresh the prompts display
    prompts = data_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + data_manager.get_categories()
    
    # Update enhancement prompts dropdown
    enhancement_prompts = data_manager.get_enhancement_prompts()
    enhancement_choices = [(f"{p['name']} - {p['title']}", p['name']) for p in enhancement_prompts]
    
    return result, tree_view, gr.update(choices=categories), gr.update(choices=enhancement_choices)

def select_prompt_for_execution(prompt_name):
    """Select prompt for execution"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!"
    
    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!"
    
    if not prompt_name.strip():
        return "Please enter a prompt name!"
    
    prompt = data_manager.get_prompt_by_name(prompt_name.strip())
    if prompt:
        return prompt['content']
    else:
        return f"Prompt '{prompt_name}' not found!"

def execute_ai_prompt(prompt_text):
    """Execute AI prompt"""
    if not prompt_text.strip():
        return "Please enter a prompt to execute!"
    
    return prompt_manager.execute_prompt(prompt_text)

def enhance_ai_prompt(original_prompt, enhancement_prompt_name):
    """Enhance AI prompt"""
    if not original_prompt.strip():
        return "Please enter a prompt to enhance!"
    
    return prompt_manager.enhance_prompt(original_prompt, enhancement_prompt_name)

def save_configuration(service_type, api_endpoint, api_key, model_name):
    """Save the AI service configuration"""
    return prompt_manager.save_config(service_type, api_endpoint, api_key, model_name)

def save_enhancement_configuration(service_type, api_endpoint, api_key, model_name, enhancement_prompt_name):
    """Save enhancement configuration"""
    return prompt_manager.save_enhancement_config(service_type, api_endpoint, api_key, model_name, enhancement_prompt_name)

# Admin functions
def admin_create_tenant(name, subdomain, max_users):
    """Create new tenant"""
    try:
        max_users_int = int(max_users) if max_users else 100
        success, message = prompt_manager.create_tenant(name, subdomain, max_users_int)
        
        # Refresh tenant list
        tenants = prompt_manager.get_all_tenants()
        tenant_choices = [(f"{t.name} ({t.subdomain})", t.id) for t in tenants]
        
        return message, gr.update(choices=tenant_choices), "", "", ""
    except ValueError:
        return "Error: Max users must be a number", gr.update(), "", "", ""

def admin_create_user(tenant_id, email, password, first_name, last_name, role):
    """Create new user"""
    success, message = prompt_manager.create_user(tenant_id, email, password, first_name, last_name, role)
    
    # Refresh user list for selected tenant
    users = prompt_manager.get_tenant_users(tenant_id) if tenant_id else []
    user_list = "\n".join([f"👤 {u.first_name} {u.last_name} ({u.email}) - {u.role}" for u in users])
    
    return message, user_list, "", "", "", "", ""

def admin_refresh_tenant_users(tenant_id):
    """Refresh user list for selected tenant"""
    if not tenant_id:
        return "Select a tenant first"
    
    users = prompt_manager.get_tenant_users(tenant_id)
    user_list = "\n".join([f"👤 {u.first_name} {u.last_name} ({u.email}) - {u.role}" for u in users])
    
    return user_list

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Multi-Tenant AI Prompt Manager", theme=gr.themes.Soft()) as app:
        # Store session token
        session_token = gr.State("")
        
        gr.Markdown("""
        # 🤖 Multi-Tenant AI Prompt Manager
        
        Secure, multi-tenant AI prompt management with authentication, SSO/ADFS support, and admin capabilities.
        """)
        
        # Authentication status
        auth_status = gr.Markdown("❌ Not authenticated")
        
        # Login interface
        with gr.Row(visible=True) as login_section:
            with gr.Column():
                gr.Markdown("## 🔐 Login")
                
                with gr.Tabs():
                    with gr.TabItem("📧 Email Login"):
                        login_email = gr.Textbox(label="Email", placeholder="user@domain.com")
                        login_password = gr.Textbox(label="Password", type="password")
                        login_subdomain = gr.Textbox(
                            label="Tenant Domain", 
                            value="localhost",
                            placeholder="your-tenant-domain"
                        )
                        login_btn = gr.Button("🔑 Login", variant="primary")
                        login_message = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.TabItem("🔗 SSO Login"):
                        sso_subdomain = gr.Textbox(
                            label="Tenant Domain", 
                            placeholder="your-tenant-domain"
                        )
                        sso_btn = gr.Button("🚀 Login with SSO")
                        sso_message = gr.Textbox(label="SSO Login URL", interactive=False)
        
        # Main application interface
        with gr.Row(visible=False) as main_section:
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
                
                # Prompt Library Tab
                with gr.TabItem("📚 Prompt Library"):
                    gr.Markdown("### Browse and Search Prompts")
                    
                    with gr.Row():
                        search_box = gr.Textbox(label="Search Prompts", placeholder="Search by name, title, content, or tags...")
                        category_filter = gr.Dropdown(
                            choices=["All"],
                            value="All",
                            label="Filter by Category"
                        )
                        refresh_btn = gr.Button("🔄 Refresh")
                    
                    prompts_display = gr.Textbox(
                        label="Prompts Tree View",
                        value="Login to view your prompts...",
                        lines=20,
                        max_lines=25,
                        interactive=False
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
                                choices=[],
                                label="Enhancement Prompt (optional)",
                                info="Select an enhancement prompt, or leave blank to use default"
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
                
                # Configuration Tab
                with gr.TabItem("⚙️ Configuration"):
                    gr.Markdown("### Primary AI Service Configuration")
                    
                    with gr.Row():
                        service_type = gr.Dropdown(
                            choices=["openai", "lmstudio", "ollama", "llamacpp"],
                            value="openai",
                            label="Service Type"
                        )
                        model_name = gr.Textbox(
                            value="gpt-3.5-turbo",
                            label="Model Name",
                            placeholder="e.g., gpt-3.5-turbo, llama2"
                        )
                    
                    api_endpoint = gr.Textbox(
                        value="http://localhost:1234/v1",
                        label="API Endpoint",
                        placeholder="http://localhost:1234/v1"
                    )
                    
                    api_key = gr.Textbox(
                        label="API Key (optional)",
                        type="password",
                        placeholder="Enter API key if required"
                    )
                    
                    config_save_btn = gr.Button("💾 Save Configuration", variant="primary")
                    config_status = gr.Textbox(label="Status", interactive=False)
                    
                    gr.Markdown("---")
                    gr.Markdown("### Enhancement Service Configuration")
                    gr.Markdown("Configure a separate AI service specifically for prompt enhancement")
                    
                    with gr.Row():
                        enh_service_type = gr.Dropdown(
                            choices=["openai", "lmstudio", "ollama", "llamacpp"],
                            value="openai",
                            label="Enhancement Service Type"
                        )
                        enh_model_name = gr.Textbox(
                            value="gpt-4",
                            label="Enhancement Model Name",
                            placeholder="e.g., gpt-4, claude-3-sonnet"
                        )
                    
                    enh_api_endpoint = gr.Textbox(
                        value="http://localhost:1234/v1",
                        label="Enhancement API Endpoint",
                        placeholder="http://localhost:1234/v1"
                    )
                    
                    enh_api_key = gr.Textbox(
                        label="Enhancement API Key (optional)",
                        type="password",
                        placeholder="Enter API key if required"
                    )
                    
                    enh_prompt_dropdown = gr.Dropdown(
                        choices=[],
                        label="Default Enhancement Prompt (optional)",
                        info="Select a stored enhancement prompt, or leave blank to use default"
                    )
                    
                    enh_config_save_btn = gr.Button("💾 Save Enhancement Config", variant="primary")
                    enh_config_status = gr.Textbox(label="Enhancement Config Status", interactive=False)
        
        # Admin interface (only visible to admins)
        with gr.Row(visible=False) as admin_section:
            with gr.Tabs():
                with gr.TabItem("🛡️ Admin Panel"):
                    gr.Markdown("### System Administration")
                    
                    with gr.Row():
                        # Tenant Management
                        with gr.Column():
                            gr.Markdown("#### Tenant Management")
                            
                            tenant_name = gr.Textbox(label="Tenant Name", placeholder="Company Name")
                            tenant_subdomain = gr.Textbox(label="Subdomain", placeholder="company-slug")
                            tenant_max_users = gr.Number(label="Max Users", value=100, precision=0)
                            create_tenant_btn = gr.Button("🏢 Create Tenant", variant="primary")
                            tenant_status = gr.Textbox(label="Tenant Status", interactive=False)
                        
                        # User Management
                        with gr.Column():
                            gr.Markdown("#### User Management")
                            
                            user_tenant_selector = gr.Dropdown(
                                choices=[],
                                label="Select Tenant",
                                info="Choose tenant for new user"
                            )
                            user_email = gr.Textbox(label="Email", placeholder="user@company.com")
                            user_password = gr.Textbox(label="Password", type="password")
                            user_first_name = gr.Textbox(label="First Name")
                            user_last_name = gr.Textbox(label="Last Name")
                            user_role = gr.Dropdown(
                                choices=["user", "admin", "readonly"],
                                value="user",
                                label="Role"
                            )
                            create_user_btn = gr.Button("👤 Create User", variant="primary")
                            user_status = gr.Textbox(label="User Status", interactive=False)
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### Tenant Users")
                            refresh_users_btn = gr.Button("🔄 Refresh Users")
                            tenant_users_display = gr.Textbox(
                                label="Users in Selected Tenant",
                                lines=10,
                                interactive=False,
                                placeholder="Select a tenant to view users..."
                            )
        
        # Logout button
        logout_btn = gr.Button("🚪 Logout", variant="secondary", visible=False)
        
        # Event handlers for authentication
        login_btn.click(
            login_user,
            inputs=[login_email, login_password, login_subdomain],
            outputs=[login_section, main_section, admin_section, login_message, auth_status, session_token]
        ).then(
            lambda: gr.update(visible=True),
            outputs=logout_btn
        )
        
        logout_btn.click(
            logout_user,
            inputs=[session_token],
            outputs=[login_section, main_section, admin_section, login_message, auth_status, session_token]
        ).then(
            lambda: gr.update(visible=False),
            outputs=logout_btn
        )
        
        sso_btn.click(
            handle_sso_login,
            inputs=[sso_subdomain],
            outputs=sso_message
        )
        
        # Event handlers for prompt management
        add_btn.click(
            add_new_prompt,
            inputs=[prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt],
            outputs=[prompt_status, prompts_display, category_filter, enhancement_prompt_selector, 
                    prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt]
        )
        
        load_edit_btn.click(
            load_prompt_for_editing,
            inputs=[edit_prompt_name],
            outputs=[prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt, edit_status]
        )
        
        update_btn.click(
            update_existing_prompt,
            inputs=[edit_prompt_name, prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt],
            outputs=[prompt_status, prompts_display, category_filter, enhancement_prompt_selector, 
                    prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt, edit_status]
        )
        
        delete_btn.click(
            delete_existing_prompt,
            inputs=[delete_prompt_name],
            outputs=[edit_status, prompts_display, category_filter, enhancement_prompt_selector]
        )
        
        clear_btn.click(
            lambda: ("", "", "", "", "", False, ""),
            outputs=[prompt_name, prompt_title, prompt_content, prompt_category, prompt_tags, is_enhancement_prompt, prompt_status]
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
        
        copy_enhanced_btn.click(
            lambda enhanced_text: enhanced_text,
            inputs=[enhanced_prompt],
            outputs=execution_prompt
        )
        
        def save_enhanced_as_new(enhanced_text, name):
            if not enhanced_text.strip():
                return "No enhanced prompt to save!"
            
            if not name.strip():
                return "Please enter a name for the enhanced prompt!"
            
            if not prompt_manager.current_user:
                return "Error: User not authenticated!"
            
            data_manager = prompt_manager.get_data_manager()
            if not data_manager:
                return "Error: Data manager not available!"
            
            # Create title from name
            title = f"Enhanced: {name}"
            
            result = data_manager.add_prompt(name.strip(), title, enhanced_text, "Enhanced", "enhanced,improved", False)
            return result
        
        save_enhanced_btn.click(
            save_enhanced_as_new,
            inputs=[enhanced_prompt, save_enhanced_name],
            outputs=enhancement_status
        )
        
        # Event handlers for configuration
        config_save_btn.click(
            save_configuration,
            inputs=[service_type, api_endpoint, api_key, model_name],
            outputs=config_status
        )
        
        enh_config_save_btn.click(
            save_enhancement_configuration,
            inputs=[enh_service_type, enh_api_endpoint, enh_api_key, enh_model_name, enh_prompt_dropdown],
            outputs=enh_config_status
        )
        
        # Event handlers for admin functions
        create_tenant_btn.click(
            admin_create_tenant,
            inputs=[tenant_name, tenant_subdomain, tenant_max_users],
            outputs=[tenant_status, user_tenant_selector, tenant_name, tenant_subdomain, tenant_max_users]
        )
        
        create_user_btn.click(
            admin_create_user,
            inputs=[user_tenant_selector, user_email, user_password, user_first_name, user_last_name, user_role],
            outputs=[user_status, tenant_users_display, user_email, user_password, user_first_name, user_last_name, user_role]
        )
        
        user_tenant_selector.change(
            admin_refresh_tenant_users,
            inputs=[user_tenant_selector],
            outputs=tenant_users_display
        )
        
        refresh_users_btn.click(
            admin_refresh_tenant_users,
            inputs=[user_tenant_selector],
            outputs=tenant_users_display
        )
        
        gr.Markdown("""
        ---
        **Multi-Tenant Features:**
        - 🔐 **Secure Authentication**: Email/password + SSO/ADFS support
        - 🏢 **Tenant Isolation**: Complete data separation between organizations
        - 👥 **User Management**: Role-based access control (admin, user, readonly)
        - 🛡️ **Admin Panel**: Tenant and user management for administrators
        - 🌐 **Local Development**: Localhost tenant with admin@localhost / admin123
        - 📊 **Session Management**: Secure JWT-based sessions with expiration
        
        **Instructions:**
        1. **Login**: Use email/password or SSO to authenticate
        2. **Tenant Context**: All prompts are isolated to your tenant
        3. **User Roles**: Admins can manage tenants and users
        4. **Configuration**: AI service configs are per-user
        5. **Data Isolation**: Complete separation between tenants
        
        **Local Development:**
        - Default admin: admin@localhost / admin123
        - Tenant: localhost (automatically created)
        - Access admin panel with admin credentials
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