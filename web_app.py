#!/usr/bin/env python3
"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

AI Prompt Manager Web Application
FastAPI-based web interface replacing Gradio

This software is licensed for non-commercial use only.
See LICENSE file for details.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from api_token_manager import APITokenManager
from auth_manager import AuthManager, User
from i18n import i18n
from langwatch_optimizer import langwatch_optimizer
from prompt_data_manager import PromptDataManager
from text_translator import text_translator
from token_calculator import token_calculator


class WebApp:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.auth_manager = AuthManager(db_path)
        self.api_token_manager = APITokenManager(db_path)

        # Check if running in single-user mode
        self.single_user_mode = os.getenv("MULTITENANT_MODE", "true").lower() == "false"

        # Initialize FastAPI app
        self.app = FastAPI(
            title="AI Prompt Manager",
            description="Modern web interface for AI prompt management",
            version="1.0.0",
        )

        # Add session middleware
        self.app.add_middleware(
            SessionMiddleware, secret_key=os.getenv("SECRET_KEY", secrets.token_hex(32))
        )

        # Set up templates and static files
        self.templates = Jinja2Templates(directory="web_templates")

        # Mount static files
        self.app.mount(
            "/static", StaticFiles(directory="web_templates/static"), name="static"
        )

        # Set up routes
        self._setup_routes()

    def _setup_routes(self):
        """Set up all application routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            if self.single_user_mode:
                # In single-user mode, bypass authentication
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                prompts = data_manager.get_all_prompts()[:5]  # Latest 5 prompts

                return self.templates.TemplateResponse(
                    "prompts/dashboard.html",
                    {
                        "request": request,
                        "user": None,
                        "prompts": prompts,
                        "page_title": "Dashboard",
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
                )

            # Multi-tenant mode - require authentication
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Get recent prompts
            prompts = data_manager.get_all_prompts()[:5]  # Latest 5 prompts

            return self.templates.TemplateResponse(
                "prompts/dashboard.html",
                self.get_template_context(
                    request, user, prompts=prompts, page_title="Dashboard"
                ),
            )

        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, redirect to dashboard
                return RedirectResponse(url="/", status_code=302)

            return self.templates.TemplateResponse(
                "auth/login.html",
                self.get_template_context(request, page_title="Login"),
            )

        @self.app.post("/login")
        async def login_submit(
            request: Request,
            email: str = Form(...),
            password: str = Form(...),
            subdomain: str = Form(default="localhost"),
        ):
            success, user, message = self.auth_manager.authenticate_user(
                email, password, subdomain
            )

            if success and user:
                # Set session
                request.session["user_id"] = user.id
                request.session["tenant_id"] = user.tenant_id
                request.session["login_time"] = datetime.now().isoformat()

                return RedirectResponse(url="/", status_code=302)
            else:
                return self.templates.TemplateResponse(
                    "auth/login.html",
                    {
                        "request": request,
                        "error": message,
                        "page_title": "Login",
                        "email": email,
                        "subdomain": subdomain,
                    },
                )

        @self.app.get("/logout")
        async def logout(request: Request):
            request.session.clear()
            return RedirectResponse(url="/login", status_code=302)

        # Prompts routes
        @self.app.get("/prompts", response_class=HTMLResponse)
        async def prompts_list(request: Request):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            prompts = data_manager.get_all_prompts()
            categories = data_manager.get_categories()

            context = {
                "request": request,
                "user": user,
                "prompts": prompts,
                "categories": categories,
                "page_title": "Prompts",
            }

            if self.single_user_mode:
                context.update(
                    {
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    }
                )

            return self.templates.TemplateResponse("prompts/list.html", context)

        @self.app.get("/prompts/new", response_class=HTMLResponse)
        async def new_prompt(request: Request):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                categories = data_manager.get_categories()

                return self.templates.TemplateResponse(
                    "prompts/form.html",
                    {
                        "request": request,
                        "user": None,
                        "categories": categories,
                        "page_title": "New Prompt",
                        "action": "create",
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
                )

            # Multi-tenant mode
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/form.html",
                {
                    "request": request,
                    "user": user,
                    "categories": categories,
                    "page_title": "New Prompt",
                    "action": "create",
                },
            )

        @self.app.post("/prompts/new")
        async def create_prompt(
            request: Request,
            name: str = Form(...),
            content: str = Form(...),
            category: str = Form(...),
            description: str = Form(default=""),
            tags: str = Form(default=""),
        ):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Process tags
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

            result = data_manager.add_prompt(
                name=name,
                title=name,  # Using name as title
                content=content,
                category=category,
                tags=", ".join(tag_list),  # Convert list to string
            )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/prompts", status_code=302)
            else:
                categories = data_manager.get_categories()
                context = {
                    "request": request,
                    "user": user,
                    "categories": categories,
                    "error": result,  # Show the actual error message
                    "page_title": "New Prompt",
                    "action": "create",
                    "name": name,
                    "content": content,
                    "category": category,
                    "description": description,
                    "tags": tags,
                }

                # Add single-user mode context if needed
                if self.single_user_mode:
                    context.update(
                        {
                            "single_user_mode": True,
                            "i18n": i18n,
                            "current_language": i18n.current_language,
                            "available_languages": i18n.get_available_languages(),
                        }
                    )

                return self.templates.TemplateResponse("prompts/form.html", context)

        @self.app.get("/prompts/{prompt_name}/edit", response_class=HTMLResponse)
        async def edit_prompt(request: Request, prompt_name: str):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompt = data_manager.get_prompt_by_name(prompt_name)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/form.html",
                {
                    "request": request,
                    "user": user,
                    "categories": categories,
                    "page_title": "Edit Prompt",
                    "action": "edit",
                    "name": prompt.get("name", ""),
                    "content": prompt.get("content", ""),
                    "category": prompt.get("category", ""),
                    "description": prompt.get("description", ""),
                    "tags": (
                        ", ".join(prompt.get("tags", [])) if prompt.get("tags") else ""
                    ),
                },
            )

        @self.app.post("/prompts/{prompt_name}/edit")
        async def update_prompt(
            request: Request,
            prompt_name: str,
            name: str = Form(...),
            content: str = Form(...),
            category: str = Form(...),
            description: str = Form(default=""),
            tags: str = Form(default=""),
        ):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Process tags
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

            # Get the original prompt to update
            original_prompt = data_manager.get_prompt_by_name(prompt_name)
            if not original_prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            result = data_manager.update_prompt(
                original_name=original_prompt["name"],
                new_name=name,
                title=name,  # Using name as title
                content=content,
                category=category,
                tags=", ".join(tag_list),  # convert list back to string
            )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/prompts", status_code=302)
            else:
                categories = data_manager.get_categories()
                return self.templates.TemplateResponse(
                    "prompts/form.html",
                    {
                        "request": request,
                        "user": user,
                        "categories": categories,
                        "error": result,  # Show the actual error message
                        "page_title": "Edit Prompt",
                        "action": "edit",
                        "name": name,
                        "content": content,
                        "category": category,
                        "description": description,
                        "tags": tags,
                    },
                )

        @self.app.delete("/prompts/{prompt_name}")
        async def delete_prompt(request: Request, prompt_name: str):
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            success = data_manager.delete_prompt(
                prompt_name
            )  # delete_prompt takes name as string
            if success:
                # Return updated prompts list for HTMX
                prompts = data_manager.get_all_prompts()
                categories = data_manager.get_categories()

                return self.templates.TemplateResponse(
                    "prompts/list.html",
                    {
                        "request": request,
                        "user": user,
                        "prompts": prompts,
                        "categories": categories,
                        "page_title": "Prompts",
                    },
                )
            else:
                raise HTTPException(status_code=404, detail="Prompt not found")

        @self.app.get("/prompts/search")
        async def search_prompts(request: Request, q: str = ""):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Simple search implementation
            all_prompts = data_manager.get_all_prompts()
            if q:
                prompts = [
                    p
                    for p in all_prompts
                    if q.lower() in p["name"].lower()
                    or q.lower() in p.get("content", "").lower()
                    or q.lower() in p.get("description", "").lower()
                ]
            else:
                prompts = all_prompts

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/_list_partial.html",
                {
                    "request": request,
                    "user": user,
                    "prompts": prompts,
                    "categories": categories,
                },
            )

        @self.app.get("/prompts/filter")
        async def filter_prompts(
            request: Request, category: str = "", sort: str = "created_desc"
        ):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Get and filter prompts
            prompts = data_manager.get_all_prompts()

            if category:
                prompts = [p for p in prompts if p.get("category") == category]

            # Sort prompts
            if sort == "name_asc":
                prompts.sort(key=lambda p: p.get("name", "").lower())
            elif sort == "name_desc":
                prompts.sort(key=lambda p: p.get("name", "").lower(), reverse=True)
            elif sort == "category_asc":
                prompts.sort(key=lambda p: p.get("category", "").lower())
            elif sort == "created_asc":
                prompts.sort(key=lambda p: p.get("created_at", ""))
            else:  # created_desc (default)
                prompts.sort(key=lambda p: p.get("created_at", ""), reverse=True)

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/_list_partial.html",
                {
                    "request": request,
                    "user": user,
                    "prompts": prompts,
                    "categories": categories,
                },
            )

        # Language switching route
        @self.app.post("/language")
        async def change_language(request: Request, language: str = Form(...)):
            """Change the interface language"""
            if i18n.set_language(language):
                request.session["language"] = language
            return RedirectResponse(
                url=request.headers.get("referer", "/"), status_code=302
            )

        # Translation route
        @self.app.post("/translate")
        async def translate_text(
            request: Request,
            text: str = Form(...),
            target_lang: str = Form(default="en"),
        ):
            """Translate text to target language"""
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            success, translated_text, error = text_translator.translate_to_english(text)

            return {
                "success": success,
                "translated_text": translated_text,
                "error": error,
                "original_text": text,
            }

        # Optimization route
        @self.app.post("/optimize")
        async def optimize_prompt(request: Request, prompt: str = Form(...)):
            """Optimize a prompt using available optimization services"""
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                result = langwatch_optimizer.optimize_prompt(prompt)
                return {
                    "success": result.success,
                    "optimized_prompt": result.optimized_prompt,
                    "suggestions": result.suggestions,
                    "reasoning": result.reasoning,
                    "optimization_score": result.optimization_score,
                    "error": result.error_message,
                }
            except Exception as e:
                return {
                    "success": False,
                    "optimized_prompt": prompt,
                    "suggestions": [],
                    "reasoning": "Optimization service unavailable",
                    "optimization_score": 0.0,
                    "error": str(e),
                }

        # Token calculation route
        @self.app.post("/calculate-tokens")
        async def calculate_tokens(
            request: Request, text: str = Form(...), model: str = Form(default="gpt-4")
        ):
            """Calculate tokens and estimated cost for text"""
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                result = token_calculator.estimate_tokens(text, model)

                return {
                    "success": True,
                    "token_count": result.prompt_tokens,
                    "estimated_cost": result.cost_estimate or 0.0,
                    "model": model,
                    "text_length": len(text),
                }
            except Exception as e:
                return {
                    "success": False,
                    "token_count": 0,
                    "estimated_cost": 0.0,
                    "model": model,
                    "error": str(e),
                }

        # Admin routes (only for admin users)
        @self.app.get("/admin", response_class=HTMLResponse)
        async def admin_dashboard(request: Request):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            # Check if user is admin
            if user.role != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            # Get admin statistics
            stats = self.auth_manager.get_admin_stats()
            users = self.auth_manager.get_all_users_for_tenant(user.tenant_id)
            tenants = (
                self.auth_manager.get_all_tenants()
                if user.role == "admin"
                else [self.auth_manager.get_tenant_by_id(user.tenant_id)]
            )

            # Mock recent activity (would be from audit log)
            recent_activity = [
                {"description": "New user registered", "timestamp": "2 hours ago"},
                {
                    "description": "Prompt optimization completed",
                    "timestamp": "4 hours ago",
                },
                {"description": "API token created", "timestamp": "1 day ago"},
            ]

            # Mock system info
            system_info = {
                "version": "1.0.0",
                "database_type": "SQLite" if "sqlite" in self.db_path else "PostgreSQL",
                "multitenant_mode": self.auth_manager.is_multitenant_mode(),
                "api_enabled": True,  # Would check actual API status
                "uptime": "2 days 14 hours",
                "environment": "Development" if os.getenv("DEBUG") else "Production",
            }

            return self.templates.TemplateResponse(
                "admin/dashboard.html",
                self.get_template_context(
                    request,
                    user,
                    stats=stats,
                    users=users,
                    tenants=tenants,
                    recent_activity=recent_activity,
                    system_info=system_info,
                    page_title="Admin Dashboard",
                ),
            )

        # Prompt Builder route
        @self.app.get("/prompts/builder", response_class=HTMLResponse)
        async def prompt_builder(request: Request):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompts = data_manager.get_all_prompts()
            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/builder.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    categories=categories,
                    page_title="Prompt Builder",
                ),
            )

        # Prompt execution route
        @self.app.get("/prompts/{prompt_name}/execute", response_class=HTMLResponse)
        async def execute_prompt(request: Request, prompt_name: str):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompt = data_manager.get_prompt_by_name(prompt_name)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            return self.templates.TemplateResponse(
                "prompts/execute.html",
                {
                    "request": request,
                    "user": user,
                    "prompt": prompt,
                    "page_title": f"Execute: {prompt['name']}",
                },
            )

        # Templates routes
        @self.app.get("/templates", response_class=HTMLResponse)
        async def templates_page(request: Request):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "templates/list.html",
                {"request": request, "user": user, "page_title": "Templates"},
            )

        # Settings routes
        @self.app.get("/settings", response_class=HTMLResponse)
        async def settings_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, redirect to main page or show simplified settings
                return RedirectResponse(url="/", status_code=302)

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "settings/index.html",
                {"request": request, "user": user, "page_title": "Settings"},
            )

        # Profile routes
        @self.app.get("/profile", response_class=HTMLResponse)
        async def profile_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, there's no user profile concept
                return RedirectResponse(url="/", status_code=302)

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "settings/profile.html",
                {"request": request, "user": user, "page_title": "Profile"},
            )

        # API Tokens routes
        @self.app.get("/api-tokens", response_class=HTMLResponse)
        async def api_tokens_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, API tokens are not user-specific
                return RedirectResponse(url="/", status_code=302)

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            # Get user's API tokens
            tokens = self.api_token_manager.get_user_tokens(user.id)

            return self.templates.TemplateResponse(
                "settings/api_tokens.html",
                {
                    "request": request,
                    "user": user,
                    "tokens": tokens,
                    "page_title": "API Tokens",
                },
            )

        @self.app.post("/api-tokens/create")
        async def create_api_token(
            request: Request,
            name: str = Form(...),
            expires_days: int = Form(default=30),
        ):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            try:
                expiry_date = (
                    datetime.now() + timedelta(days=expires_days)
                    if expires_days > 0
                    else None
                )
                token_info = self.api_token_manager.create_token(
                    user_id=user.id,
                    tenant_id=user.tenant_id,
                    name=name,
                    expires_at=expiry_date,
                )

                # Show token once to user
                request.session["new_token"] = token_info
                return RedirectResponse(url="/api-tokens?created=1", status_code=302)

            except Exception as e:
                return RedirectResponse(
                    url=f"/api-tokens?error={str(e)}", status_code=302
                )

        @self.app.post("/api-tokens/{token_id}/revoke")
        async def revoke_api_token(request: Request, token_id: str):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            try:
                self.api_token_manager.revoke_token(token_id, user.id)
                return RedirectResponse(url="/api-tokens?revoked=1", status_code=302)
            except Exception as e:
                return RedirectResponse(
                    url=f"/api-tokens?error={str(e)}", status_code=302
                )

        # AI Services Configuration
        @self.app.get("/ai-services", response_class=HTMLResponse)
        async def ai_services_page(request: Request):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "ai_services/config.html",
                {"request": request, "user": user, "page_title": "AI Services"},
            )

        @self.app.post("/ai-services/test")
        async def test_ai_service(
            request: Request,
            service_type: str = Form(...),
            api_endpoint: str = Form(...),
            api_key: str = Form(...),
            model: str = Form(...),
            test_prompt: str = Form("Hello, world!"),
        ):
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                # This would integrate with your AI service testing logic
                # For now, return a mock response
                return {
                    "success": True,
                    "response": (
                        f"Test successful for {service_type} with model {model}"
                    ),
                    "latency": "1.2s",
                    "tokens_used": 15,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Prompt execution with AI services
        @self.app.post("/prompts/{prompt_name}/execute")
        async def execute_prompt_with_ai(
            request: Request, prompt_name: str, variables: dict = Form(default={})
        ):
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompt = data_manager.get_prompt_by_name(prompt_name)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            try:
                # Replace variables in prompt content
                content = prompt["content"]
                for key, value in variables.items():
                    content = content.replace(f"{{{key}}}", str(value))

                # This would integrate with your AI service execution logic
                # For now, return a mock response
                return {
                    "success": True,
                    "prompt_content": content,
                    "response": f"Mock AI response for: {content[:100]}...",
                    "tokens_used": len(content.split()) * 1.3,
                    "execution_time": "2.1s",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_current_user_or_default(
        self, request: Request
    ) -> tuple[Optional[User], PromptDataManager]:
        """Get current user and data manager, or defaults for single-user mode"""
        if self.single_user_mode:
            # In single-user mode, use default values
            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id="default", user_id="default"
            )
            return None, data_manager

        user = await self.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        data_manager = PromptDataManager(
            db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
        )
        return user, data_manager

    async def get_current_user(self, request: Request) -> Optional[User]:
        """Get current authenticated user from session"""
        user_id = request.session.get("user_id")
        tenant_id = request.session.get("tenant_id")
        login_time_str = request.session.get("login_time")

        # Set language from session if available
        language = request.session.get("language", "en")
        i18n.set_language(language)

        if not all([user_id, tenant_id, login_time_str]):
            return None

        # Check session expiry (24 hours)
        try:
            login_time = datetime.fromisoformat(login_time_str)
            if datetime.now() - login_time > timedelta(hours=24):
                return None
        except ValueError:
            return None

        # Get user from database
        user = self.auth_manager.get_user_by_id(user_id)
        if user and user.tenant_id == tenant_id and user.is_active:
            return user

        return None

    def get_template_context(
        self, request: Request, user: Optional[User] = None, **kwargs
    ):
        """Get common template context with i18n support"""
        context = {
            "request": request,
            "user": user,
            "i18n": i18n,
            "current_language": i18n.current_language,
            "available_languages": i18n.get_available_languages(),
            **kwargs,
        }
        return context


# Create the web application instance
def create_web_app(db_path: str = "prompts.db") -> FastAPI:
    """Create and configure the web application"""
    web_app = WebApp(db_path)
    return web_app.app


if __name__ == "__main__":
    import uvicorn

    app = create_web_app()
    # Binding to all interfaces is intentional for web application
    # deployment  # nosec B104
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # nosec B104
