"""
REST API Endpoints for Prompt Management

This module provides FastAPI endpoints for managing prompts with support for
visibility filtering in multi-tenant environments.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api_token_manager import APITokenManager
from auth_manager import AuthManager
from prompt_data_manager import PromptDataManager

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses


class PromptRequest(BaseModel):
    """Request model for creating/updating prompts"""

    name: str = Field(..., min_length=1, max_length=255, description="Prompt name")
    title: Optional[str] = Field(None, max_length=255, description="Prompt title")
    content: str = Field(..., min_length=1, description="Prompt content")
    category: str = Field(
        ..., min_length=1, max_length=100, description="Prompt category"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Prompt description"
    )
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    visibility: str = Field(
        "private", pattern="^(private|public)$", description="Prompt visibility"
    )
    is_enhancement_prompt: bool = Field(
        False, description="Whether this is an enhancement prompt"
    )


class PromptResponse(BaseModel):
    """Response model for prompt data"""

    id: int
    tenant_id: str
    user_id: str
    name: str
    title: Optional[str]
    content: str
    category: str
    description: Optional[str]
    tags: Optional[str]
    visibility: str
    is_enhancement_prompt: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class PromptListResponse(BaseModel):
    """Response model for list of prompts"""

    success: bool = True
    prompts: List[PromptResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


class PromptFilterParams(BaseModel):
    """Filter parameters for prompt search"""

    category: Optional[str] = None
    visibility: Optional[str] = None
    include_enhancement_prompts: bool = True
    include_public_from_tenant: bool = True
    search: Optional[str] = None
    tags: Optional[List[str]] = None


def get_auth_manager(db_path: str = "prompts.db") -> AuthManager:
    """Get authentication manager instance"""
    return AuthManager(db_path)


def get_api_token_manager(db_path: str = "prompts.db") -> APITokenManager:
    """Get API token manager instance"""
    return APITokenManager(db_path)


def get_data_manager(
    token_manager: APITokenManager = Depends(get_api_token_manager),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> PromptDataManager:
    """Get data manager with authenticated user context"""
    # For now, return a basic data manager
    # In a real implementation, this would extract user context from the token
    return PromptDataManager(tenant_id="default", user_id="default")


def create_prompt_router(db_path: str = "prompts.db") -> APIRouter:
    """Create and configure the prompt API router"""
    router = APIRouter(prefix="/api/prompts", tags=["prompts"])

    # Configure dependencies with the database path
    def get_auth_manager_configured() -> AuthManager:
        return AuthManager(db_path)

    def get_api_token_manager_configured() -> APITokenManager:
        return APITokenManager(db_path)

    def get_data_manager_configured(
        token_manager: APITokenManager = Depends(get_api_token_manager_configured),
        auth_manager: AuthManager = Depends(get_auth_manager_configured),
    ) -> PromptDataManager:
        """Get data manager with authenticated user context"""
        # For now, return a basic data manager
        # In a real implementation, this would extract user context from the token
        return PromptDataManager(
            tenant_id="default", user_id="default", db_path=db_path
        )

    @router.get("/", response_model=PromptListResponse)
    async def list_prompts(
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        category: Optional[str] = Query(None, description="Filter by category"),
        visibility: Optional[str] = Query(
            None, description="Filter by visibility (private|public|mine|all)"
        ),
        search: Optional[str] = Query(
            None, description="Search in name, content, description"
        ),
        include_enhancement_prompts: bool = Query(
            True, description="Include enhancement prompts"
        ),
        include_public_from_tenant: bool = Query(
            True, description="Include public prompts from tenant"
        ),
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> PromptListResponse:
        """
        List prompts with filtering and pagination support.

        Supports visibility filtering:
        - private: Only user's private prompts
        - public: Only public prompts from tenant
        - mine: Only user's own prompts (private + public)
        - all: All accessible prompts (default)
        """
        try:
            # Get prompts based on visibility filter
            if visibility == "public":
                prompts = data_manager.get_public_prompts_in_tenant(
                    include_enhancement_prompts
                )
            elif visibility == "private":
                # Get only user's private prompts
                all_user_prompts = data_manager.get_all_prompts(
                    include_enhancement_prompts
                )
                prompts = [
                    p
                    for p in all_user_prompts
                    if p.get("visibility", "private") == "private"
                ]
            elif visibility == "mine":
                prompts = data_manager.get_all_prompts(include_enhancement_prompts)
            else:  # "all" or None
                prompts = data_manager.get_all_prompts_with_visibility(
                    include_enhancement_prompts, include_public_from_tenant
                )

            # Apply category filter
            if category:
                prompts = [p for p in prompts if p.get("category") == category]

            # Apply search filter
            if search:
                search_lower = search.lower()
                prompts = [
                    p
                    for p in prompts
                    if search_lower in p.get("name", "").lower()
                    or search_lower in p.get("content", "").lower()
                    or search_lower in p.get("description", "").lower()
                ]

            # Apply pagination
            total = len(prompts)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_prompts = prompts[start_idx:end_idx]

            # Convert to response models
            prompt_responses = []
            for prompt in paginated_prompts:
                prompt_responses.append(
                    PromptResponse(
                        id=prompt["id"],
                        tenant_id=prompt["tenant_id"],
                        user_id=prompt["user_id"],
                        name=prompt["name"],
                        title=prompt.get("title"),
                        content=prompt["content"],
                        category=prompt["category"],
                        description=prompt.get("description"),
                        tags=prompt.get("tags"),
                        visibility=prompt.get("visibility", "private"),
                        is_enhancement_prompt=prompt.get(
                            "is_enhancement_prompt", False
                        ),
                        created_at=prompt.get("created_at"),
                        updated_at=prompt.get("updated_at"),
                    )
                )

            return PromptListResponse(
                prompts=prompt_responses,
                total=total,
                page=page,
                per_page=per_page,
                has_more=end_idx < total,
            )

        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve prompts")

    @router.post("/", response_model=Dict[str, Any])
    async def create_prompt(
        prompt_request: PromptRequest,
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> Dict[str, Any]:
        """Create a new prompt with visibility settings"""
        try:
            result = data_manager.add_prompt(
                name=prompt_request.name,
                title=prompt_request.title or prompt_request.name,
                content=prompt_request.content,
                category=prompt_request.category,
                tags=prompt_request.tags or "",
                is_enhancement_prompt=prompt_request.is_enhancement_prompt,
                visibility=prompt_request.visibility,
            )

            if result.startswith("Error:"):
                raise HTTPException(status_code=400, detail=result)

            return {
                "success": True,
                "message": "Prompt created successfully",
                "prompt_name": prompt_request.name,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            raise HTTPException(status_code=500, detail="Failed to create prompt")

    @router.get("/categories", response_model=List[str])
    async def get_categories(
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> List[str]:
        """Get all available prompt categories"""
        try:
            categories = data_manager.get_categories()
            return categories
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve categories")

    @router.get("/visibility-stats", response_model=Dict[str, Any])
    async def get_visibility_stats(
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> Dict[str, Any]:
        """Get statistics about prompt visibility distribution"""
        try:
            all_prompts = data_manager.get_all_prompts_with_visibility()

            stats = {
                "total": len(all_prompts),
                "private": len(
                    [
                        p
                        for p in all_prompts
                        if p.get("visibility", "private") == "private"
                    ]
                ),
                "public": len(
                    [
                        p
                        for p in all_prompts
                        if p.get("visibility", "private") == "public"
                    ]
                ),
                "by_category": {},
            }

            # Group by category
            for prompt in all_prompts:
                category = prompt.get("category", "Unknown")
                if category not in stats["by_category"]:
                    stats["by_category"][category] = {
                        "total": 0,
                        "private": 0,
                        "public": 0,
                    }

                stats["by_category"][category]["total"] += 1
                visibility = prompt.get("visibility", "private")
                stats["by_category"][category][visibility] += 1

            return {
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting visibility stats: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve visibility statistics"
            )

    @router.get("/search", response_model=PromptListResponse)
    async def search_prompts(
        q: str = Query(..., min_length=1, description="Search query"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        category: Optional[str] = Query(None, description="Filter by category"),
        visibility: Optional[str] = Query(
            None, description="Filter by visibility (private|public|mine|all)"
        ),
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> PromptListResponse:
        """Search prompts with text query and filters"""
        try:
            # Get prompts based on visibility filter
            if visibility == "public":
                prompts = data_manager.get_public_prompts_in_tenant()
            elif visibility == "private":
                all_user_prompts = data_manager.get_all_prompts()
                prompts = [
                    p
                    for p in all_user_prompts
                    if p.get("visibility", "private") == "private"
                ]
            elif visibility == "mine":
                prompts = data_manager.get_all_prompts()
            else:  # "all" or None
                prompts = data_manager.get_all_prompts_with_visibility()

            # Apply search filter
            search_lower = q.lower()
            filtered_prompts = [
                p
                for p in prompts
                if search_lower in p.get("name", "").lower()
                or search_lower in p.get("content", "").lower()
                or search_lower in p.get("description", "").lower()
                or search_lower in p.get("tags", "").lower()
                or search_lower in p.get("category", "").lower()
            ]

            # Apply category filter
            if category:
                filtered_prompts = [
                    p for p in filtered_prompts if p.get("category") == category
                ]

            # Apply pagination
            total = len(filtered_prompts)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_prompts = filtered_prompts[start_idx:end_idx]

            # Convert to response models
            prompt_responses = []
            for prompt in paginated_prompts:
                prompt_responses.append(
                    PromptResponse(
                        id=prompt["id"],
                        tenant_id=prompt["tenant_id"],
                        user_id=prompt["user_id"],
                        name=prompt["name"],
                        title=prompt.get("title"),
                        content=prompt["content"],
                        category=prompt["category"],
                        description=prompt.get("description"),
                        tags=prompt.get("tags"),
                        visibility=prompt.get("visibility", "private"),
                        is_enhancement_prompt=prompt.get(
                            "is_enhancement_prompt", False
                        ),
                        created_at=prompt.get("created_at"),
                        updated_at=prompt.get("updated_at"),
                    )
                )

            return PromptListResponse(
                prompts=prompt_responses,
                total=total,
                page=page,
                per_page=per_page,
                has_more=end_idx < total,
            )

        except Exception as e:
            logger.error(f"Error searching prompts: {e}")
            raise HTTPException(status_code=500, detail="Failed to search prompts")

    @router.get("/{prompt_id}", response_model=PromptResponse)
    async def get_prompt(
        prompt_id: int,
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> PromptResponse:
        """Get a specific prompt by ID"""
        try:
            # Get all accessible prompts (respecting visibility)
            prompts = data_manager.get_all_prompts_with_visibility()
            prompt = next((p for p in prompts if p["id"] == prompt_id), None)

            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            return PromptResponse(
                id=prompt["id"],
                tenant_id=prompt["tenant_id"],
                user_id=prompt["user_id"],
                name=prompt["name"],
                title=prompt.get("title"),
                content=prompt["content"],
                category=prompt["category"],
                description=prompt.get("description"),
                tags=prompt.get("tags"),
                visibility=prompt.get("visibility", "private"),
                is_enhancement_prompt=prompt.get("is_enhancement_prompt", False),
                created_at=prompt.get("created_at"),
                updated_at=prompt.get("updated_at"),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve prompt")

    @router.put("/{prompt_id}", response_model=Dict[str, Any])
    async def update_prompt(
        prompt_id: int,
        prompt_request: PromptRequest,
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> Dict[str, Any]:
        """Update an existing prompt"""
        try:
            # Get the original prompt to get its name
            all_prompts = data_manager.get_all_prompts_with_visibility()
            original_prompt = next(
                (p for p in all_prompts if p["id"] == prompt_id), None
            )

            if not original_prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            # Check if user can modify this prompt (must be owner for now)
            # In a full implementation, this would check user permissions

            result = data_manager.update_prompt(
                original_name=original_prompt["name"],
                new_name=prompt_request.name,
                title=prompt_request.title or prompt_request.name,
                content=prompt_request.content,
                category=prompt_request.category,
                tags=prompt_request.tags or "",
                visibility=prompt_request.visibility,
            )

            if result.startswith("Error:"):
                raise HTTPException(status_code=400, detail=result)

            return {
                "success": True,
                "message": "Prompt updated successfully",
                "prompt_id": prompt_id,
                "prompt_name": prompt_request.name,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating prompt {prompt_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update prompt")

    @router.delete("/{prompt_id}", response_model=Dict[str, Any])
    async def delete_prompt(
        prompt_id: int,
        data_manager: PromptDataManager = Depends(get_data_manager_configured),
    ) -> Dict[str, Any]:
        """Delete a prompt"""
        try:
            # Get the prompt to delete
            all_prompts = data_manager.get_all_prompts_with_visibility()
            prompt = next((p for p in all_prompts if p["id"] == prompt_id), None)

            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            # Check if user can delete this prompt (must be owner for now)
            # In a full implementation, this would check user permissions

            success = data_manager.delete_prompt(prompt["name"])

            if not success:
                raise HTTPException(status_code=400, detail="Failed to delete prompt")

            return {
                "success": True,
                "message": "Prompt deleted successfully",
                "prompt_id": prompt_id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete prompt")

    return router
