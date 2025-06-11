#!/bin/bash
# Docker container validation script
# Tests both legacy and new architecture components in Docker environment

set -e

echo "🐳 Docker Container Validation Script"
echo "======================================"

# Function to test container health
test_container_health() {
    local container_name=$1
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $container_name to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker ps --filter "name=$container_name" --filter "health=healthy" | grep -q $container_name; then
            echo "✅ $container_name is healthy"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "   Attempt $attempt/$max_attempts..."
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $container_name failed to become healthy"
    docker logs $container_name --tail 20
    return 1
}

# Function to test API endpoints
test_api_endpoints() {
    local base_url=$1
    
    echo "🧪 Testing API endpoints..."
    
    # Test health endpoint
    echo "  Testing health endpoint..."
    if curl -s --max-time 10 "$base_url/api/health" | grep -q "status"; then
        echo "  ✅ Health endpoint working"
    else
        echo "  ❌ Health endpoint failed"
        return 1
    fi
    
    # Test authentication requirement
    echo "  Testing authentication requirement..."
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$base_url/api/prompts")
    if [ "$http_code" = "403" ] || [ "$http_code" = "401" ]; then
        echo "  ✅ Authentication properly required (HTTP $http_code)"
    else
        echo "  ⚠️  Authentication check returned HTTP $http_code"
    fi
}

# Function to test import capabilities
test_imports() {
    local container_name=$1
    
    echo "🔍 Testing import capabilities..."
    
    # Test legacy imports
    echo "  Testing legacy imports..."
    if docker exec $container_name python -c "
import prompt_manager, auth_manager, api_endpoints
print('✅ Legacy imports successful')
"; then
        echo "  ✅ Legacy imports working"
    else
        echo "  ❌ Legacy imports failed"
        return 1
    fi
    
    # Test new architecture imports and functionality
    echo "  Testing new architecture imports and repository functionality..."
    if docker exec $container_name python -c "
import sys
import tempfile
sys.path.insert(0, '/app/src')
from src.core.config.settings import AppConfig, DatabaseConfig, DatabaseType
from src.prompts.models.prompt import Prompt
from src.prompts.services.prompt_service import PromptService
from src.core.base.database_manager import DatabaseManager

# Test repository save functionality in Docker
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db.close()

try:
    db_config = DatabaseConfig(db_type=DatabaseType.SQLITE, db_path=temp_db.name)
    db_manager = DatabaseManager(db_config)
    prompt_service = PromptService(db_manager)
    
    # Test the fixed repository save functionality
    result = prompt_service.create_prompt(
        tenant_id='docker-test-tenant',
        user_id='docker-test-user',
        name='docker_test_prompt',
        title='Docker Test Prompt',
        content='Testing repository fixes in Docker container'
    )
    
    if result.success and result.data and result.data.id:
        print('✅ New architecture and repository save working in Docker')
    else:
        print(f'❌ Repository save test failed in Docker: {result.error}')
        exit(1)
except Exception as e:
    print(f'❌ Docker test failed with exception: {e}')
    exit(1)
finally:
    import os
    try:
        os.unlink(temp_db.name)
    except:
        pass
"; then
        echo "  ✅ New architecture and repository functionality working"
    else
        echo "  ❌ New architecture functionality failed"
        return 1
    fi
}

# Test development setup
test_development_setup() {
    echo "🧪 Testing development setup..."
    
    # Start development services
    docker-compose up -d
    
    # Wait for services
    test_container_health "ai-prompt-manager-app-1" || test_container_health "ai-prompt-manager_app_1"
    
    # Test imports
    test_imports "ai-prompt-manager-app-1" || test_imports "ai-prompt-manager_app_1"
    
    # Test API
    test_api_endpoints "http://localhost:7860"
    
    echo "✅ Development setup tests passed"
    
    # Cleanup
    docker-compose down
}

# Test production setup
test_production_setup() {
    echo "🏭 Testing production setup..."
    
    # Start production services
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services
    test_container_health "ai-prompt-manager-app-1" || test_container_health "ai-prompt-manager_app_1"
    
    # Test imports
    test_imports "ai-prompt-manager-app-1" || test_imports "ai-prompt-manager_app_1"
    
    # Test API
    test_api_endpoints "http://localhost:7860"
    
    echo "✅ Production setup tests passed"
    
    # Cleanup
    docker-compose -f docker-compose.prod.yml down
}

# Main execution
main() {
    case "${1:-all}" in
        "dev")
            test_development_setup
            ;;
        "prod")
            test_production_setup
            ;;
        "all")
            test_development_setup
            echo ""
            test_production_setup
            ;;
        *)
            echo "Usage: $0 [dev|prod|all]"
            echo "  dev  - Test development setup"
            echo "  prod - Test production setup"
            echo "  all  - Test both setups (default)"
            exit 1
            ;;
    esac
    
    echo ""
    echo "🎉 All Docker tests completed successfully!"
}

# Run main function
main "$@"