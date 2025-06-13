"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Modern UI Components and Theme System for AI Prompt Manager
Responsive design with consistent styling and accessibility

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import gradio as gr
from typing import Dict, Any, Optional, List, Tuple, Union
from i18n import i18n, t

class ModernTheme:
    """
    Modern, accessible theme with consistent color palette and spacing
    """
    
    @staticmethod
    def create_theme():
        """Create a modern, accessible Gradio theme"""
        return gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate",
            spacing_size="sm",
            radius_size="md",
            text_size="sm",
        ).set(
            # Color palette
            color_accent="*primary_500",
            color_accent_soft="*primary_50",
            
            # Buttons
            button_primary_background_fill="*primary_600",
            button_primary_background_fill_hover="*primary_700",
            button_primary_text_color="white",
            button_secondary_background_fill="*neutral_50",
            button_secondary_background_fill_hover="*neutral_100",
            button_secondary_border_color="*neutral_200",
            
            # Form elements
            input_background_fill="*neutral_50",
            input_border_color="*neutral_200",
            input_border_color_focus="*primary_500",
            input_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1)",
            input_shadow_focus="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            
            # Layout
            background_fill_primary="white",
            background_fill_secondary="*neutral_50",
            block_background_fill="white",
            block_border_color="*neutral_200",
            block_border_width="1px",
            block_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1)",
            
            # Typography
            body_text_color="*neutral_800",
            body_text_size="*text_sm",
            button_small_text_size="*text_xs",
            button_large_text_size="*text_md",
        )

class UIComponents:
    """
    Reusable UI components with consistent styling and internationalization
    """
    
    @staticmethod
    def create_header(title_key: str, subtitle_key: Optional[str] = None) -> gr.Markdown:
        """Create a consistent page header"""
        title = t(title_key)
        subtitle = t(subtitle_key) if subtitle_key else ""
        
        header_html = f"""
        <div style="text-align: center; padding: 2rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #1e293b; margin: 0 0 0.5rem 0;">
                🤖 {title}
            </h1>
            {f'<p style="font-size: 1.125rem; color: #64748b; margin: 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """
        return gr.Markdown(header_html)
    
    @staticmethod
    def create_section_header(title_key: str, icon: str = "📝") -> gr.Markdown:
        """Create a section header with icon"""
        title = t(title_key)
        header_html = f"""
        <div style="display: flex; align-items: center; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #e2e8f0;">
            <span style="font-size: 1.5rem; margin-right: 0.75rem;">{icon}</span>
            <h2 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0;">{title}</h2>
        </div>
        """
        return gr.Markdown(header_html)
    
    @staticmethod
    def create_card(content: Union[str, gr.Component], title: Optional[str] = None) -> gr.Column:
        """Create a card-like container"""
        with gr.Column(
            elem_classes=["ui-card"],
            elem_id="card",
            variant="panel"
        ) as card:
            if title:
                gr.Markdown(f"**{title}**", elem_classes=["card-title"])
            if isinstance(content, str):
                gr.Markdown(content)
            else:
                content.render()
        return card
    
    @staticmethod
    def create_input_group(
        label_key: str,
        input_type: str = "text",
        placeholder_key: Optional[str] = None,
        required: bool = False,
        **kwargs
    ) -> gr.Component:
        """Create a labeled input with consistent styling"""
        label = t(label_key)
        if required:
            label += f" <span style='color: #ef4444;'>*</span>"
        
        placeholder = t(placeholder_key) if placeholder_key else ""
        
        # Extract elem_classes from kwargs to avoid conflict and merge with default classes
        extra_classes = kwargs.pop('elem_classes', [])
        
        if input_type == "text":
            css_classes = ["modern-input"]
            if extra_classes:
                css_classes.extend(extra_classes)
            return gr.Textbox(
                label=label,
                placeholder=placeholder,
                elem_classes=css_classes,
                **kwargs
            )
        elif input_type == "textarea":
            # Extract lines from kwargs to avoid conflict
            lines = kwargs.pop('lines', 4)
            css_classes = ["modern-textarea"]
            if extra_classes:
                css_classes.extend(extra_classes)
            return gr.Textbox(
                label=label,
                placeholder=placeholder,
                lines=lines,
                elem_classes=css_classes,
                **kwargs
            )
        elif input_type == "password":
            css_classes = ["modern-input"]
            if extra_classes:
                css_classes.extend(extra_classes)
            return gr.Textbox(
                label=label,
                placeholder=placeholder,
                type="password",
                elem_classes=css_classes,
                **kwargs
            )
        elif input_type == "dropdown":
            css_classes = ["modern-dropdown"]
            if extra_classes:
                css_classes.extend(extra_classes)
            return gr.Dropdown(
                label=label,
                elem_classes=css_classes,
                **kwargs
            )
        elif input_type == "number":
            css_classes = ["modern-input"]
            if extra_classes:
                css_classes.extend(extra_classes)
            return gr.Number(
                label=label,
                elem_classes=css_classes,
                **kwargs
            )
    
    @staticmethod
    def create_button(
        label_key: str,
        variant: str = "primary",
        icon: Optional[str] = None,
        size: str = "medium",
        **kwargs
    ) -> gr.Button:
        """Create a button with consistent styling"""
        label = t(label_key)
        if icon:
            label = f"{icon} {label}"
        
        # Extract elem_classes from kwargs to avoid conflict and merge with default classes
        extra_classes = kwargs.pop('elem_classes', [])
        css_classes = ["modern-button", f"btn-{variant}", f"btn-{size}"]
        if extra_classes:
            css_classes.extend(extra_classes)
        
        return gr.Button(
            label,
            variant=variant,
            elem_classes=css_classes,
            **kwargs
        )
    
    @staticmethod
    def create_status_display(
        label_key: str,
        status_type: str = "info",
        **kwargs
    ) -> gr.Textbox:
        """Create a status display field"""
        label = t(label_key)
        css_classes = ["status-display", f"status-{status_type}"]
        
        # Extract elem_classes from kwargs to avoid conflict
        extra_classes = kwargs.pop('elem_classes', [])
        if extra_classes:
            css_classes.extend(extra_classes)
        
        return gr.Textbox(
            label=label,
            interactive=False,
            elem_classes=css_classes,
            **kwargs
        )
    
    @staticmethod
    def create_tabs(tabs_config: List[Dict[str, Any]]) -> gr.Tabs:
        """Create tabs with consistent styling"""
        with gr.Tabs(elem_classes=["modern-tabs"]) as tabs:
            for tab_config in tabs_config:
                title = t(tab_config["title_key"])
                icon = tab_config.get("icon", "")
                tab_title = f"{icon} {title}" if icon else title
                
                with gr.TabItem(tab_title, elem_classes=["modern-tab"]):
                    if "content_fn" in tab_config:
                        tab_config["content_fn"]()
        return tabs
    
    @staticmethod
    def create_language_selector() -> gr.Dropdown:
        """Create language selector dropdown"""
        languages = i18n.get_available_languages()
        choices = [(f"{flag} {name}", code) for code, name in languages.items() for flag in ["🇺🇸", "🇪🇸", "🇫🇷", "🇩🇪", "🇨🇳", "🇯🇵", "🇵🇹", "🇷🇺", "🇸🇦", "🇮🇳"]]
        
        return gr.Dropdown(
            choices=list(languages.values()),
            value="English",
            label="🌐 Language",  # Use direct text since this is a meta-UI element
            elem_classes=["language-selector"],
            interactive=True,
            scale=1
        )
    
    @staticmethod
    def create_responsive_layout(
        left_content_fn,
        right_content_fn,
        left_scale: int = 2,
        right_scale: int = 1
    ) -> gr.Row:
        """Create a responsive two-column layout"""
        with gr.Row(elem_classes=["responsive-layout"]) as layout:
            with gr.Column(scale=left_scale, elem_classes=["main-content"]):
                left_content_fn()
            with gr.Column(scale=right_scale, elem_classes=["sidebar-content"]):
                right_content_fn()
        return layout
    
    @staticmethod
    def create_action_bar(actions: List[Dict[str, Any]]) -> gr.Row:
        """Create a horizontal action bar with buttons"""
        with gr.Row(elem_classes=["action-bar"]) as action_row:
            for action in actions:
                UIComponents.create_button(
                    action["label_key"],
                    variant=action.get("variant", "secondary"),
                    icon=action.get("icon"),
                    size=action.get("size", "medium")
                )
        return action_row
    
    @staticmethod
    def create_info_panel(info_items: List[Dict[str, str]]) -> gr.Column:
        """Create an information panel with key-value pairs"""
        with gr.Column(elem_classes=["info-panel"]) as panel:
            for item in info_items:
                label = t(item["label_key"])
                value = item.get("value", "")
                gr.Markdown(f"**{label}:** {value}", elem_classes=["info-item"])
        return panel
    
    @staticmethod
    def create_search_bar(
        placeholder_key: str = "form.placeholder.search",
        with_filters: bool = True
    ) -> Tuple[gr.Textbox, Optional[gr.Dropdown]]:
        """Create a search bar with optional filters"""
        with gr.Row(elem_classes=["search-bar"]):
            search_input = UIComponents.create_input_group(
                "prompt.search",
                placeholder_key=placeholder_key,
                elem_classes=["search-input"]
            )
            
            filter_dropdown = None
            if with_filters:
                filter_dropdown = gr.Dropdown(
                    label=t("nav.category"),
                    choices=["All"],
                    value="All",
                    elem_classes=["search-filter"],
                    scale=1
                )
        
        return search_input, filter_dropdown
    
    @staticmethod
    def create_prompt_card(prompt_data: Dict[str, Any], selectable: bool = True) -> gr.HTML:
        """Create a prompt card component for the builder"""
        prompt_id = prompt_data.get('id', '')
        name = prompt_data.get('name', 'Untitled')
        title = prompt_data.get('title', '')
        category = prompt_data.get('category', 'General')
        preview = prompt_data.get('preview', '')
        length = prompt_data.get('length', 0)
        is_enhancement = prompt_data.get('is_enhancement', False)
        
        # Determine card styling based on type
        card_class = "enhancement-prompt-card" if is_enhancement else "regular-prompt-card"
        icon = "⚡" if is_enhancement else "📄"
        
        # Build the card HTML
        card_html = f"""
        <div class="prompt-card {card_class}" data-prompt-id="{prompt_id}" {'draggable="true"' if selectable else ''}>
            <div class="prompt-card-header">
                <span class="prompt-icon">{icon}</span>
                <h4 class="prompt-name">{name}</h4>
                <span class="prompt-category">{category}</span>
            </div>
            <div class="prompt-card-body">
                <p class="prompt-title">{title}</p>
                <p class="prompt-preview">{preview}</p>
                <div class="prompt-meta">
                    <span class="prompt-length">{length} chars</span>
                    {'<span class="enhancement-badge">Enhancement</span>' if is_enhancement else ''}
                </div>
            </div>
        </div>
        """
        
        return gr.HTML(card_html)
    
    @staticmethod
    def create_drop_zone(zone_type: str = "add", message_key: str = "builder.drag.add") -> gr.HTML:
        """Create a drag-and-drop zone"""
        message = t(message_key)
        
        drop_zone_html = f"""
        <div class="drop-zone drop-zone-{zone_type}" data-zone-type="{zone_type}">
            <div class="drop-zone-content">
                <div class="drop-zone-icon">📥</div>
                <p class="drop-zone-message">{message}</p>
            </div>
        </div>
        """
        
        return gr.HTML(drop_zone_html)
    
    @staticmethod
    def create_template_selector() -> gr.Radio:
        """Create template selector for prompt combination"""
        from prompt_builder import prompt_builder
        
        templates = prompt_builder.get_combination_templates()
        choices = []
        
        for key, template in templates.items():
            label = f"{template['icon']} {template['name']}"
            choices.append((label, key))
        
        return gr.Radio(
            choices=choices,
            value="sequential",
            label=t("builder.template"),
            elem_classes=["template-selector"]
        )

class ResponsiveCSS:
    """
    CSS styles for responsive design and modern appearance
    """
    
    @staticmethod
    def get_css() -> str:
        """Get comprehensive CSS for the application"""
        return """
        /* Root variables for consistent theming */
        :root {
            --primary-50: #eff6ff;
            --primary-100: #dbeafe;
            --primary-500: #3b82f6;
            --primary-600: #2563eb;
            --primary-700: #1d4ed8;
            
            --neutral-50: #f8fafc;
            --neutral-100: #f1f5f9;
            --neutral-200: #e2e8f0;
            --neutral-300: #cbd5e1;
            --neutral-500: #64748b;
            --neutral-800: #1e293b;
            --neutral-900: #0f172a;
            
            --success-50: #f0fdf4;
            --success-500: #22c55e;
            --warning-50: #fffbeb;
            --warning-500: #f59e0b;
            --error-50: #fef2f2;
            --error-500: #ef4444;
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            
            --transition: all 0.2s ease-in-out;
        }
        
        /* Base styles */
        .gradio-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Modern card styling */
        .ui-card {
            background: white;
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-sm);
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: var(--transition);
        }
        
        .ui-card:hover {
            box-shadow: var(--shadow-md);
            border-color: var(--primary-200);
        }
        
        /* Input styling */
        .modern-input textarea,
        .modern-input input {
            border: 1px solid var(--neutral-200) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.875rem !important;
            transition: var(--transition) !important;
            background: var(--neutral-50) !important;
        }
        
        .modern-input textarea:focus,
        .modern-input input:focus {
            border-color: var(--primary-500) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            background: white !important;
        }
        
        .modern-textarea textarea {
            min-height: 100px !important;
            resize: vertical !important;
        }
        
        /* Button styling */
        .modern-button {
            border-radius: var(--radius-md) !important;
            font-weight: 500 !important;
            transition: var(--transition) !important;
            border: none !important;
            cursor: pointer !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.5rem !important;
        }
        
        .btn-primary {
            background: var(--primary-600) !important;
            color: white !important;
        }
        
        .btn-primary:hover {
            background: var(--primary-700) !important;
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        .btn-secondary {
            background: var(--neutral-100) !important;
            color: var(--neutral-800) !important;
            border: 1px solid var(--neutral-200) !important;
        }
        
        .btn-secondary:hover {
            background: var(--neutral-200) !important;
            transform: translateY(-1px) !important;
        }
        
        .btn-small {
            padding: 0.5rem 1rem !important;
            font-size: 0.875rem !important;
        }
        
        .btn-medium {
            padding: 0.75rem 1.5rem !important;
            font-size: 0.875rem !important;
        }
        
        .btn-large {
            padding: 1rem 2rem !important;
            font-size: 1rem !important;
        }
        
        /* Tab styling */
        .modern-tabs .tab-nav {
            border-bottom: 2px solid var(--neutral-200) !important;
            background: var(--neutral-50) !important;
            border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
        }
        
        .modern-tab {
            padding: 1rem 1.5rem !important;
            border: none !important;
            background: transparent !important;
            color: var(--neutral-600) !important;
            font-weight: 500 !important;
            transition: var(--transition) !important;
        }
        
        .modern-tab.selected {
            color: var(--primary-600) !important;
            border-bottom: 2px solid var(--primary-600) !important;
            background: white !important;
        }
        
        /* Status displays */
        .status-display {
            border-radius: var(--radius-md) !important;
            padding: 0.75rem !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.875rem !important;
        }
        
        .status-success {
            background: var(--success-50) !important;
            border: 1px solid var(--success-500) !important;
            color: var(--success-700) !important;
        }
        
        .status-error {
            background: var(--error-50) !important;
            border: 1px solid var(--error-500) !important;
            color: var(--error-700) !important;
        }
        
        .status-warning {
            background: var(--warning-50) !important;
            border: 1px solid var(--warning-500) !important;
            color: var(--warning-700) !important;
        }
        
        .status-info {
            background: var(--primary-50) !important;
            border: 1px solid var(--primary-500) !important;
            color: var(--primary-700) !important;
        }
        
        /* Language selector */
        .language-selector {
            min-width: 150px !important;
        }
        
        /* Responsive layout */
        .responsive-layout {
            gap: 2rem !important;
        }
        
        .main-content {
            min-width: 0 !important;
        }
        
        .sidebar-content {
            min-width: 250px !important;
        }
        
        /* Action bar */
        .action-bar {
            gap: 1rem !important;
            padding: 1rem 0 !important;
            border-top: 1px solid var(--neutral-200) !important;
            margin-top: 1rem !important;
        }
        
        /* Search bar */
        .search-bar {
            gap: 1rem !important;
            align-items: end !important;
            margin-bottom: 1rem !important;
        }
        
        .search-input {
            flex: 1 !important;
        }
        
        .search-filter {
            min-width: 150px !important;
        }
        
        /* Info panel */
        .info-panel {
            background: var(--neutral-50) !important;
            border: 1px solid var(--neutral-200) !important;
            border-radius: var(--radius-md) !important;
            padding: 1rem !important;
        }
        
        .info-item {
            margin: 0.5rem 0 !important;
            padding: 0.25rem 0 !important;
            border-bottom: 1px solid var(--neutral-200) !important;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .gradio-container {
                padding: 0.5rem;
            }
            
            .responsive-layout {
                flex-direction: column !important;
            }
            
            .sidebar-content {
                min-width: unset !important;
                order: -1;
            }
            
            .action-bar {
                flex-direction: column !important;
                gap: 0.5rem !important;
            }
            
            .modern-button {
                width: 100% !important;
            }
            
            .search-bar {
                flex-direction: column !important;
                align-items: stretch !important;
            }
            
            .ui-card {
                padding: 1rem !important;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            :root {
                --neutral-50: #1e293b;
                --neutral-100: #334155;
                --neutral-200: #475569;
                --neutral-800: #f1f5f9;
                --neutral-900: #ffffff;
            }
            
            .gradio-container {
                background: #0f172a !important;
                color: var(--neutral-800) !important;
            }
            
            .ui-card {
                background: var(--neutral-50) !important;
                border-color: var(--neutral-200) !important;
            }
        }
        
        /* Prompt Builder Styles */
        .prompt-card {
            background: white;
            border: 2px solid var(--neutral-200);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: var(--shadow-sm);
        }
        
        .prompt-card:hover {
            border-color: var(--primary-500);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .prompt-card.dragging {
            opacity: 0.5;
            transform: rotate(5deg);
        }
        
        .prompt-card-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .prompt-icon {
            font-size: 1.2rem;
        }
        
        .prompt-name {
            font-weight: 600;
            margin: 0;
            flex: 1;
            color: var(--neutral-800);
        }
        
        .prompt-category {
            background: var(--primary-100);
            color: var(--primary-700);
            padding: 0.25rem 0.5rem;
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .prompt-title {
            font-size: 0.9rem;
            color: var(--neutral-600);
            margin: 0.25rem 0;
        }
        
        .prompt-preview {
            font-size: 0.85rem;
            color: var(--neutral-500);
            margin: 0.5rem 0;
            line-height: 1.4;
        }
        
        .prompt-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--neutral-400);
        }
        
        .enhancement-badge {
            background: var(--warning-100);
            color: var(--warning-700);
            padding: 0.125rem 0.375rem;
            border-radius: var(--radius-sm);
            font-weight: 500;
        }
        
        .enhancement-prompt-card {
            border-color: var(--warning-300);
            background: var(--warning-50);
        }
        
        .enhancement-prompt-card:hover {
            border-color: var(--warning-500);
        }
        
        /* Drop Zone Styles */
        .drop-zone {
            border: 2px dashed var(--neutral-300);
            border-radius: var(--radius-lg);
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
            background: var(--neutral-50);
            transition: var(--transition);
        }
        
        .drop-zone.drag-over {
            border-color: var(--primary-500);
            background: var(--primary-50);
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        }
        
        .drop-zone-content {
            pointer-events: none;
        }
        
        .drop-zone-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            opacity: 0.6;
        }
        
        .drop-zone-message {
            color: var(--neutral-600);
            margin: 0;
            font-weight: 500;
        }
        
        /* Builder Layout */
        .builder-section {
            background: white;
            border-radius: var(--radius-lg);
            border: 1px solid var(--neutral-200);
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .builder-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--neutral-100);
        }
        
        .builder-header h3 {
            margin: 0;
            color: var(--neutral-800);
        }
        
        .available-prompts {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-md);
            padding: 1rem;
        }
        
        .selected-prompts {
            min-height: 200px;
            border: 2px dashed var(--neutral-300);
            border-radius: var(--radius-md);
            padding: 1rem;
        }
        
        .selected-prompts.has-items {
            border-style: solid;
            border-color: var(--primary-300);
            background: var(--primary-50);
        }
        
        /* Template Selector */
        .template-selector {
            background: var(--neutral-50);
            padding: 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--neutral-200);
        }
        
        .template-selector label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            margin: 0.25rem 0;
            background: white;
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: var(--transition);
        }
        
        .template-selector label:hover {
            border-color: var(--primary-500);
            background: var(--primary-50);
        }
        
        .template-selector input:checked + label {
            border-color: var(--primary-600);
            background: var(--primary-100);
            font-weight: 600;
        }
        
        /* Preview Area */
        .preview-area {
            background: var(--neutral-50);
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-md);
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.875rem;
            line-height: 1.5;
            max-height: 300px;
            overflow-y: auto;
        }
        
        /* Sortable Styles */
        .sortable-item {
            position: relative;
        }
        
        .sortable-item .sort-handle {
            position: absolute;
            left: -1.5rem;
            top: 50%;
            transform: translateY(-50%);
            cursor: grab;
            opacity: 0;
            transition: var(--transition);
            color: var(--neutral-400);
        }
        
        .sortable-item:hover .sort-handle {
            opacity: 1;
        }
        
        .sortable-item .sort-handle:active {
            cursor: grabbing;
        }
        
        /* Accessibility improvements */
        .modern-button:focus,
        .modern-input input:focus,
        .modern-input textarea:focus,
        .prompt-card:focus {
            outline: 2px solid var(--primary-500) !important;
            outline-offset: 2px !important;
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            * {
                transition: none !important;
                animation: none !important;
            }
            
            .prompt-card:hover {
                transform: none !important;
            }
        }
        
        /* Print styles */
        @media print {
            .modern-button,
            .action-bar,
            .drop-zone {
                display: none !important;
            }
            
            .ui-card,
            .prompt-card {
                border: 1px solid #000 !important;
                box-shadow: none !important;
                page-break-inside: avoid !important;
            }
        }
        """

# Export commonly used components
def create_modern_interface():
    """Create a modern interface with the responsive theme and components"""
    return gr.Blocks(
        theme=ModernTheme.create_theme(),
        css=ResponsiveCSS.get_css(),
        title=t("app.title")
    )