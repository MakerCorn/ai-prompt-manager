"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Modern UI Interface for AI Prompt Manager
Rebuilt with internationalization, responsive design, and modern components

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import gradio as gr

from i18n import t
from token_calculator import token_calculator
from ui_components import UIComponents, create_modern_interface


class ModernInterface:
    """Modern, responsive interface with internationalization support"""

    @staticmethod
    def create_login_section():
        """Create modern login interface"""
        with gr.Column(elem_classes=["login-container"]) as login_section:
            UIComponents.create_header("app.title", "app.subtitle")

            # Language selector at top
            with gr.Row():
                with gr.Column(scale=3):
                    pass  # Spacer
                with gr.Column(scale=1):
                    language_selector = UIComponents.create_language_selector()

            # Login tabs
            with UIComponents.create_card(""):
                with gr.Tabs(elem_classes=["login-tabs"]):
                    # Email login tab
                    with gr.TabItem(
                        f"📧 {t('auth.login')}", elem_classes=["login-tab"]
                    ):
                        login_email = UIComponents.create_input_group(
                            "auth.email",
                            placeholder_key="form.placeholder.email",
                            required=True,
                        )
                        login_password = UIComponents.create_input_group(
                            "auth.password", input_type="password", required=True
                        )
                        login_subdomain = UIComponents.create_input_group(
                            "auth.tenant", value="localhost"
                        )

                        login_btn = UIComponents.create_button(
                            "auth.login", variant="primary", icon="🔑", size="large"
                        )

                        login_message = UIComponents.create_status_display(
                            "status.info"
                        )

                    # SSO login tab
                    with gr.TabItem(f"🔗 {t('auth.sso')}", elem_classes=["login-tab"]):
                        sso_subdomain = UIComponents.create_input_group(
                            "auth.tenant", placeholder_key="form.placeholder.name"
                        )
                        sso_btn = UIComponents.create_button(
                            "auth.sso", variant="secondary", icon="🚀", size="large"
                        )
                        sso_message = UIComponents.create_status_display("status.info")

        return (
            login_section,
            login_email,
            login_password,
            login_subdomain,
            login_btn,
            login_message,
            sso_subdomain,
            sso_btn,
            sso_message,
            language_selector,
        )

    @staticmethod
    def create_main_interface():
        """Create the main application interface"""
        with gr.Column(visible=False, elem_classes=["main-interface"]) as main_section:
            # Header with auth status and logout
            with gr.Row(elem_classes=["app-header"]):
                with gr.Column(scale=3):
                    auth_status = gr.Markdown(t("app.status.not_authenticated"))
                with gr.Column(scale=1):
                    logout_btn = UIComponents.create_button(
                        "auth.logout", variant="secondary", icon="🚪", size="small"
                    )

            # Navigation tabs
            tabs_config = [
                {
                    "title_key": "nav.prompts",
                    "icon": "📝",
                    "content_fn": ModernInterface.create_prompts_tab,
                },
                {
                    "title_key": "nav.library",
                    "icon": "📚",
                    "content_fn": ModernInterface.create_library_tab,
                },
                {
                    "title_key": "calc.title",
                    "icon": "🧮",
                    "content_fn": ModernInterface.create_calculator_tab,
                },
                {
                    "title_key": "nav.tokens",
                    "icon": "🔑",
                    "content_fn": ModernInterface.create_tokens_tab,
                },
                {
                    "title_key": "nav.settings",
                    "icon": "⚙️",
                    "content_fn": ModernInterface.create_settings_tab,
                },
            ]

            main_tabs = UIComponents.create_tabs(tabs_config)

        return main_section, auth_status, logout_btn, main_tabs

    @staticmethod
    def create_prompts_tab():
        """Create the prompt management tab"""
        UIComponents.create_section_header("nav.prompts", "📝")

        def create_prompt_form():
            with UIComponents.create_card(t("prompt.add")):
                # Basic prompt info
                prompt_name = UIComponents.create_input_group(
                    "prompt.name",
                    placeholder_key="form.placeholder.name",
                    required=True,
                )
                prompt_title = UIComponents.create_input_group(
                    "prompt.title", placeholder_key="form.placeholder.name"
                )
                prompt_category = UIComponents.create_input_group(
                    "prompt.category",
                    input_type="dropdown",
                    choices=["General", "Writing", "Analysis", "Creative", "Technical"],
                    value="General",
                )
                prompt_content = UIComponents.create_input_group(
                    "prompt.content", input_type="textarea", lines=8, required=True
                )
                prompt_tags = UIComponents.create_input_group(
                    "prompt.tags", placeholder_key="form.placeholder.name"
                )

                is_enhancement_prompt = gr.Checkbox(
                    label=t("prompt.enhancement"),
                    value=False,
                    elem_classes=["modern-checkbox"],
                )

                # Action buttons
                actions = [
                    {"label_key": "prompt.add", "variant": "primary", "icon": "➕"},
                    {"label_key": "prompt.update", "variant": "secondary", "icon": "✏️"},
                    {"label_key": "prompt.clear", "variant": "secondary", "icon": "🗑️"},
                ]
                UIComponents.create_action_bar(actions)

                prompt_status = UIComponents.create_status_display("status.info")

            return (
                prompt_name,
                prompt_title,
                prompt_category,
                prompt_content,
                prompt_tags,
                is_enhancement_prompt,
                prompt_status,
            )

        def create_quick_actions():
            with UIComponents.create_card(t("action.edit")):
                edit_prompt_name = UIComponents.create_input_group(
                    "prompt.name", placeholder_key="form.placeholder.name"
                )
                load_edit_btn = UIComponents.create_button(
                    "prompt.load", variant="secondary", icon="📝"
                )

                delete_prompt_name = UIComponents.create_input_group(
                    "prompt.name", placeholder_key="form.placeholder.name"
                )
                delete_btn = UIComponents.create_button(
                    "prompt.delete", variant="stop", icon="🗑️"
                )

                edit_status = UIComponents.create_status_display("status.info")

            return (
                edit_prompt_name,
                load_edit_btn,
                delete_prompt_name,
                delete_btn,
                edit_status,
            )

        # Create responsive layout
        prompt_components = UIComponents.create_responsive_layout(
            create_prompt_form, create_quick_actions
        )

        return prompt_components

    @staticmethod
    def create_library_tab():
        """Create the prompt library tab"""
        UIComponents.create_section_header("nav.library", "📚")

        # Search and filter
        search_input, category_filter = UIComponents.create_search_bar()
        refresh_btn = UIComponents.create_button(
            "action.refresh", variant="secondary", icon="🔄"
        )

        # Prompts display
        with UIComponents.create_card(t("nav.library")):
            prompts_display = gr.Textbox(
                label=t("nav.library"),
                value=t("msg.loading_data"),
                lines=20,
                interactive=False,
                elem_classes=["prompts-display"],
            )

        return search_input, category_filter, refresh_btn, prompts_display

    @staticmethod
    def create_calculator_tab():
        """Create the token calculator tab"""
        UIComponents.create_section_header("calc.title", "🧮")

        with UIComponents.create_card(t("calc.title")):
            gr.Markdown(t("calc.estimate"))

            with gr.Row():
                calc_model = UIComponents.create_input_group(
                    "calc.model",
                    input_type="dropdown",
                    choices=token_calculator.get_supported_models(),
                    value="gpt-4",
                )
                max_completion_tokens = UIComponents.create_input_group(
                    "calc.tokens",
                    input_type="number",
                    value=1000,
                    minimum=1,
                    maximum=8000,
                )

            calculate_tokens_btn = UIComponents.create_button(
                "calc.estimate", variant="primary", icon="🧮"
            )

            token_calc_status = UIComponents.create_status_display("calc.cost")

        return (
            calc_model,
            max_completion_tokens,
            calculate_tokens_btn,
            token_calc_status,
        )

    @staticmethod
    def create_optimization_section():
        """Create LangWatch optimization section"""
        with UIComponents.create_card(t("opt.title")):
            UIComponents.create_section_header("opt.title", "🚀")

            with gr.Row():
                optimization_context = UIComponents.create_input_group(
                    "opt.context", input_type="textarea", lines=3
                )
                target_model = UIComponents.create_input_group(
                    "opt.target",
                    input_type="dropdown",
                    choices=["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"],
                    value="gpt-4",
                )

            optimize_btn = UIComponents.create_button(
                "opt.optimize", variant="primary", icon="🚀"
            )

            langwatch_status = UIComponents.create_status_display("status.info")

            # Optimization results (initially hidden)
            with gr.Column(
                visible=False, elem_classes=["optimization-results"]
            ) as optimization_results:
                with gr.Row():
                    optimization_score = UIComponents.create_input_group(
                        "opt.score", input_type="number", interactive=False
                    )
                    optimization_suggestions = UIComponents.create_input_group(
                        "opt.suggestions",
                        input_type="textarea",
                        lines=3,
                        interactive=False,
                    )

                optimized_prompt_display = UIComponents.create_input_group(
                    "prompt.content", input_type="textarea", lines=6, interactive=False
                )

                optimization_reasoning = UIComponents.create_input_group(
                    "status.info", input_type="textarea", lines=2, interactive=False
                )

                # Optimization action buttons
                opt_actions = [
                    {"label_key": "opt.accept", "variant": "primary", "icon": "✅"},
                    {"label_key": "opt.retry", "variant": "secondary", "icon": "🔄"},
                    {"label_key": "opt.reject", "variant": "stop", "icon": "❌"},
                ]
                UIComponents.create_action_bar(opt_actions)

                optimization_status = UIComponents.create_status_display("status.info")

        return (
            optimization_context,
            target_model,
            optimize_btn,
            langwatch_status,
            optimization_results,
            optimization_score,
            optimization_suggestions,
            optimized_prompt_display,
            optimization_reasoning,
            optimization_status,
        )

    @staticmethod
    def create_tokens_tab():
        """Create API tokens management tab"""
        UIComponents.create_section_header("nav.tokens", "🔑")

        with UIComponents.create_card(t("nav.tokens")):
            gr.Markdown(t("msg.loading_data"))

            # Token creation
            token_name = UIComponents.create_input_group(
                "prompt.name", placeholder_key="form.placeholder.name", required=True
            )

            token_expiry = UIComponents.create_input_group(
                "form.optional",
                input_type="dropdown",
                choices=["30 days", "60 days", "90 days", "Never"],
                value="30 days",
            )

            create_token_btn = UIComponents.create_button(
                "action.save", variant="primary", icon="🔑"
            )

            tokens_display = gr.Textbox(
                label=t("nav.tokens"),
                value=t("msg.loading_data"),
                lines=10,
                interactive=False,
                elem_classes=["tokens-display"],
            )

        return token_name, token_expiry, create_token_btn, tokens_display

    @staticmethod
    def create_settings_tab():
        """Create settings and configuration tab"""
        UIComponents.create_section_header("nav.settings", "⚙️")

        with UIComponents.create_card(t("nav.settings")):
            # Language selection
            language_selector = UIComponents.create_language_selector()

            # AI service configuration
            with gr.Group():
                gr.Markdown(f"### {t('nav.settings')}")

                service_type = UIComponents.create_input_group(
                    "calc.model",
                    input_type="dropdown",
                    choices=["OpenAI", "LM Studio", "Ollama", "Custom"],
                    value="OpenAI",
                )

                api_endpoint = UIComponents.create_input_group(
                    "form.required", placeholder_key="form.placeholder.name"
                )

                api_key = UIComponents.create_input_group(
                    "form.required", input_type="password"
                )

                model_name = UIComponents.create_input_group(
                    "calc.model", placeholder_key="form.placeholder.name"
                )

                save_config_btn = UIComponents.create_button(
                    "action.save", variant="primary", icon="💾"
                )

                config_status = UIComponents.create_status_display("status.info")

        return (
            language_selector,
            service_type,
            api_endpoint,
            api_key,
            model_name,
            save_config_btn,
            config_status,
        )

    @staticmethod
    def create_admin_section():
        """Create admin interface (conditionally visible)"""
        with gr.Column(visible=False, elem_classes=["admin-section"]) as admin_section:
            UIComponents.create_section_header("nav.admin", "👥")

            with UIComponents.create_card(t("nav.admin")):
                gr.Markdown(t("msg.loading_data"))

                # User management
                users_display = gr.Textbox(
                    label=t("nav.admin"),
                    value=t("msg.loading_data"),
                    lines=15,
                    interactive=False,
                    elem_classes=["users-display"],
                )

                refresh_users_btn = UIComponents.create_button(
                    "action.refresh", variant="secondary", icon="🔄"
                )

        return admin_section, users_display, refresh_users_btn


def create_modern_ui():
    """Create the complete modern UI interface"""
    with create_modern_interface() as app:
        # Store session token
        session_token = gr.State("")

        # Create main sections
        login_components = ModernInterface.create_login_section()
        main_components = ModernInterface.create_main_interface()
        admin_components = ModernInterface.create_admin_section()

        # Extract components for easy access
        (
            login_section,
            login_email,
            login_password,
            login_subdomain,
            login_btn,
            login_message,
            sso_subdomain,
            sso_btn,
            sso_message,
            language_selector,
        ) = login_components

        (main_section, auth_status, logout_btn, main_tabs) = main_components
        (admin_section, users_display, refresh_users_btn) = admin_components

        # Return app and all components for event binding
        return app, {
            "session_token": session_token,
            "login_section": login_section,
            "main_section": main_section,
            "admin_section": admin_section,
            "login_email": login_email,
            "login_password": login_password,
            "login_subdomain": login_subdomain,
            "login_btn": login_btn,
            "login_message": login_message,
            "sso_subdomain": sso_subdomain,
            "sso_btn": sso_btn,
            "sso_message": sso_message,
            "language_selector": language_selector,
            "auth_status": auth_status,
            "logout_btn": logout_btn,
            "main_tabs": main_tabs,
            "users_display": users_display,
            "refresh_users_btn": refresh_users_btn,
        }
