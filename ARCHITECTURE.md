# 🏗️ AI Prompt Manager - System Architecture

## 📋 Table of Contents

- [🎯 Architectural Overview](#-architectural-overview)
- [🏛️ Modern Architecture Design](#️-modern-architecture-design)
- [🔄 Component Interaction Flow](#-component-interaction-flow)
- [🛡️ Security Architecture](#️-security-architecture)
- [📊 Data Architecture](#-data-architecture)
- [🌐 Deployment Architectures](#-deployment-architectures)
- [🔌 API Architecture](#-api-architecture)
- [🌍 Multi-Language Architecture](#-multi-language-architecture)
- [🧩 Prompt Builder Architecture](#-prompt-builder-architecture)
- [⚡ Performance Considerations](#-performance-considerations)
- [🔮 Future Architecture](#-future-architecture)

---

## 🎯 Architectural Overview

The AI Prompt Manager is built on a **modern, modular architecture** implementing clean separation of concerns through **Service Layer**, **Repository Pattern**, and **Domain-Driven Design (DDD)** principles. The system supports both single-user and multi-tenant deployments through a unified codebase with comprehensive type safety and testing.

### 🔑 Key Architectural Principles

- **🏗️ Modular Design**: Clear separation of concerns with Service, Repository, and Model layers
- **🔐 Multi-Tenant Security**: Complete data isolation with tenant-aware operations
- **📦 Type Safety**: Comprehensive type hints and validation throughout
- **🔌 API-First**: RESTful API with comprehensive OpenAPI documentation
- **🌐 Internationalization**: Multi-language support at the core
- **⚡ Performance**: Efficient queries with caching and optimization strategies
- **🛡️ Modern Security**: JWT, RBAC, and modern password handling
- **🧪 Comprehensive Testing**: Unit and integration tests with dependency injection

---

## 🏛️ Modern Architecture Design

### 📁 New Modular Structure

```
ai-prompt-manager/
├── src/                                    # New modular source code
│   ├── core/                              # Core infrastructure
│   │   ├── base/                          # Base classes
│   │   │   ├── database_manager.py        # Database operations base
│   │   │   ├── service_base.py            # Service layer base
│   │   │   └── repository_base.py         # Repository pattern base
│   │   ├── config/                        # Configuration management
│   │   │   └── settings.py                # Type-safe centralized config
│   │   ├── exceptions/                    # Exception hierarchy
│   │   │   └── base.py                    # Structured exceptions
│   │   └── utils/                         # Shared utilities
│   │       ├── validators.py              # Input validation
│   │       └── logging_config.py          # Centralized logging
│   ├── auth/                              # Authentication module
│   │   ├── models/                        # Data models
│   │   │   ├── user.py                    # User entity with RBAC
│   │   │   └── tenant.py                  # Multi-tenant entity
│   │   ├── services/                      # Authentication business logic
│   │   ├── repositories/                  # Data access layer
│   │   └── security/                      # Security utilities
│   │       ├── password_handler.py        # Modern password hashing
│   │       └── token_manager.py           # JWT management
│   ├── prompts/                           # Prompt management
│   │   ├── models/                        # Prompt data models
│   │   │   └── prompt.py                  # Rich prompt entity
│   │   ├── repositories/                  # Data access
│   │   │   └── prompt_repository.py       # Tenant-aware data operations
│   │   └── services/                      # Business logic
│   │       └── prompt_service.py          # Prompt operations service
│   ├── api/                               # API layer (planned)
│   ├── ui/                                # User interface (planned)
│   └── utils/                             # Shared utilities
├── tests/                                 # Comprehensive test suite
│   ├── unit/                              # Unit tests
│   ├── integration/                       # Integration tests
│   └── fixtures/                          # Test fixtures
├── *.py                                   # Legacy components (being migrated)
└── docs/                                  # Documentation
```

### 🏗️ Architecture Layers

```mermaid
graph TB
    subgraph "🎨 Presentation Layer"
        GRADIO[🎨 Gradio UI]
        API[🔌 REST API]
        CLI[⌨️ CLI Interface]
    end

    subgraph "🧠 Service Layer"
        PROMPT_SVC[📝 Prompt Service]
        AUTH_SVC[🔐 Auth Service]
        USER_SVC[👤 User Service]
        CONFIG_SVC[⚙️ Config Service]
    end

    subgraph "💾 Repository Layer"
        PROMPT_REPO[📄 Prompt Repository]
        USER_REPO[👤 User Repository]
        TENANT_REPO[🏢 Tenant Repository]
        CONFIG_REPO[⚙️ Config Repository]
    end

    subgraph "📊 Model Layer"
        PROMPT_MODEL[📝 Prompt Model]
        USER_MODEL[👤 User Model]
        TENANT_MODEL[🏢 Tenant Model]
        CONFIG_MODEL[⚙️ Config Model]
    end

    subgraph "🗄️ Database Layer"
        SQLITE[(📁 SQLite)]
        POSTGRES[(🐘 PostgreSQL)]
    end

    subgraph "🌍 External Services"
        AI_SERVICES[🤖 AI Models]
        OPT_SERVICES[🚀 Optimization]
        TRANSLATE[🌐 Translation]
    end

    %% Connections
    GRADIO --> PROMPT_SVC
    GRADIO --> AUTH_SVC
    API --> PROMPT_SVC
    API --> AUTH_SVC
    CLI --> PROMPT_SVC

    PROMPT_SVC --> PROMPT_REPO
    AUTH_SVC --> USER_REPO
    USER_SVC --> USER_REPO
    CONFIG_SVC --> CONFIG_REPO

    PROMPT_REPO --> PROMPT_MODEL
    USER_REPO --> USER_MODEL
    TENANT_REPO --> TENANT_MODEL
    CONFIG_REPO --> CONFIG_MODEL

    PROMPT_REPO --> SQLITE
    PROMPT_REPO --> POSTGRES
    USER_REPO --> SQLITE
    USER_REPO --> POSTGRES

    PROMPT_SVC --> AI_SERVICES
    PROMPT_SVC --> OPT_SERVICES
    CONFIG_SVC --> TRANSLATE

    classDef presentation fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef repository fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef model fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef database fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef external fill:#f1f8e9,stroke:#689f38,stroke-width:2px

    class GRADIO,API,CLI presentation
    class PROMPT_SVC,AUTH_SVC,USER_SVC,CONFIG_SVC service
    class PROMPT_REPO,USER_REPO,TENANT_REPO,CONFIG_REPO repository
    class PROMPT_MODEL,USER_MODEL,TENANT_MODEL,CONFIG_MODEL model
    class SQLITE,POSTGRES database
    class AI_SERVICES,OPT_SERVICES,TRANSLATE external
```

### 🔧 Base Class Architecture

```mermaid
graph TB
    subgraph "🏗️ Core Base Classes"
        BASE_DB[🗄️ BaseDatabaseManager]
        BASE_SVC[🧠 BaseService]
        BASE_REPO[💾 BaseRepository]
        TENANT_REPO[🏢 TenantAwareRepository]
    end

    subgraph "🔧 Service Classes"
        PROMPT_SERVICE[📝 PromptService]
        AUTH_SERVICE[🔐 AuthService]
        USER_SERVICE[👤 UserService]
    end

    subgraph "💾 Repository Classes"
        PROMPT_REPO[📄 PromptRepository]
        USER_REPO[👤 UserRepository]
        TENANT_REPO_IMPL[🏢 TenantRepository]
    end

    subgraph "🗄️ Database Managers"
        DB_MANAGER[🗃️ DatabaseManager]
        PROMPT_DB[📝 PromptDatabaseManager]
        AUTH_DB[🔐 AuthDatabaseManager]
    end

    BASE_DB --> DB_MANAGER
    BASE_DB --> PROMPT_DB
    BASE_DB --> AUTH_DB

    BASE_SVC --> PROMPT_SERVICE
    BASE_SVC --> AUTH_SERVICE
    BASE_SVC --> USER_SERVICE

    BASE_REPO --> TENANT_REPO
    TENANT_REPO --> PROMPT_REPO
    BASE_REPO --> USER_REPO
    BASE_REPO --> TENANT_REPO_IMPL

    PROMPT_SERVICE --> PROMPT_REPO
    AUTH_SERVICE --> USER_REPO
    USER_SERVICE --> USER_REPO

    PROMPT_REPO --> DB_MANAGER
    USER_REPO --> DB_MANAGER
    TENANT_REPO_IMPL --> DB_MANAGER

    classDef base fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef service fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef repository fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef database fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class BASE_DB,BASE_SVC,BASE_REPO,TENANT_REPO base
    class PROMPT_SERVICE,AUTH_SERVICE,USER_SERVICE service
    class PROMPT_REPO,USER_REPO,TENANT_REPO_IMPL repository
    class DB_MANAGER,PROMPT_DB,AUTH_DB database
```

---

## 🔄 Component Interaction Flow

### 📝 Modern Prompt Management Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant UI as 🎨 Gradio UI
    participant PS as 📝 PromptService
    participant PR as 📄 PromptRepository
    participant DB as 💾 Database
    participant AI as 🤖 AI Service

    U->>UI: Create/Edit Prompt
    UI->>PS: create_prompt(prompt_data)
    
    PS->>PS: validate_input(data)
    PS->>PR: set_tenant_context(tenant_id)
    PS->>PR: name_exists(name)
    PR->>DB: SELECT with tenant_id filter
    DB-->>PR: result
    PR-->>PS: exists_status
    
    alt Name Available
        PS->>PR: save(prompt_entity)
        PR->>DB: INSERT with tenant isolation
        DB-->>PR: prompt_with_id
        PR-->>PS: saved_prompt
        PS->>AI: calculate_tokens(content)
        AI-->>PS: token_estimate
        PS-->>UI: ServiceResult(success, prompt, metrics)
        UI-->>U: success_notification
    else Name Exists
        PS-->>UI: ServiceResult(error: "Name exists")
        UI-->>U: error_message
    end
```

### 🔐 Modern Authentication Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant UI as 🎨 Login UI
    participant AS as 🔐 AuthService
    participant UR as 👤 UserRepository
    parameter PH as 🔒 PasswordHandler
    participant TM as 🎫 TokenManager
    participant DB as 💾 Database

    U->>UI: Login(email, password, tenant)
    UI->>AS: authenticate(credentials)
    
    AS->>UR: set_tenant_context(tenant_id)
    AS->>UR: find_by_email(email)
    UR->>DB: SELECT user with tenant filter
    DB-->>UR: user_data
    UR-->>AS: user_entity
    
    alt User Found
        AS->>PH: verify_password(password, hash)
        PH-->>AS: verification_result
        
        alt Password Valid
            AS->>TM: create_token(user, tenant)
            TM-->>AS: jwt_token
            AS-->>UI: AuthResult(success, token, user)
            UI-->>U: redirect_to_dashboard
        else Password Invalid
            AS-->>UI: AuthResult(error: "Invalid credentials")
            UI-->>U: error_message
        end
    else User Not Found
        AS-->>UI: AuthResult(error: "User not found")
        UI-->>U: error_message
    end
```

### 🧩 Type-Safe Data Flow

```mermaid
sequenceDiagram
    participant C as 📞 Client
    participant S as 🧠 Service
    parameter V as ✅ Validator
    participant R as 💾 Repository
    participant M as 📊 Model
    participant DB as 🗄️ Database

    C->>S: request(data: Dict)
    S->>V: validate_input(data)
    V-->>S: validated_data: TypedDict
    
    S->>M: create_entity(validated_data)
    M->>M: __post_init__() validation
    M-->>S: entity: DataClass
    
    S->>R: save(entity)
    R->>R: _entity_to_dict(entity)
    R->>DB: INSERT/UPDATE
    DB-->>R: row_data
    R->>R: _row_to_entity(row_data)
    R-->>S: saved_entity: DataClass
    
    S-->>C: ServiceResult[T](success, entity, message)
```

---

## 🛡️ Security Architecture

### 🔐 Modern Security Implementation

```mermaid
graph TB
    subgraph "🌐 Network Security"
        HTTPS[🔒 HTTPS/TLS 1.3]
        RATE[⏱️ Rate Limiting]
        CORS[🔗 CORS Protection]
    end

    subgraph "🔑 Authentication & Authorization"
        JWT[🎫 JWT Tokens]
        RBAC[👥 Role-Based Access Control]
        MFA[📱 Multi-Factor Auth]
        SSO[🔗 SSO Integration]
    end

    subgraph "🏢 Multi-Tenant Security"
        TENANT_CTX[🏢 Tenant Context]
        DATA_ISOLATION[🔐 Data Isolation]
        RESOURCE_AUTH[📄 Resource Authorization]
        AUDIT_LOG[📊 Audit Logging]
    end

    subgraph "🔒 Data Protection"
        MODERN_HASH[#️⃣ Modern Password Hashing]
        ENCRYPT[🔐 Data Encryption]
        SECRETS[🔐 Secrets Management]
        VALIDATION[✅ Input Validation]
    end

    subgraph "🛡️ Security Services"
        PASSWORD_SVC[🔒 PasswordHandler]
        TOKEN_SVC[🎫 TokenManager]
        SECURITY_UTILS[🛡️ SecurityUtils]
        VALIDATORS[✅ ValidatorService]
    end

    HTTPS --> JWT
    RATE --> RBAC
    CORS --> MFA

    JWT --> TENANT_CTX
    RBAC --> DATA_ISOLATION
    MFA --> RESOURCE_AUTH
    SSO --> AUDIT_LOG

    TENANT_CTX --> MODERN_HASH
    DATA_ISOLATION --> ENCRYPT
    RESOURCE_AUTH --> SECRETS
    AUDIT_LOG --> VALIDATION

    MODERN_HASH --> PASSWORD_SVC
    ENCRYPT --> TOKEN_SVC
    SECRETS --> SECURITY_UTILS
    VALIDATION --> VALIDATORS

    classDef network fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef auth fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef tenant fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef data fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef services fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class HTTPS,RATE,CORS network
    class JWT,RBAC,MFA,SSO auth
    class TENANT_CTX,DATA_ISOLATION,RESOURCE_AUTH,AUDIT_LOG tenant
    class MODERN_HASH,ENCRYPT,SECRETS,VALIDATION data
    class PASSWORD_SVC,TOKEN_SVC,SECURITY_UTILS,VALIDATORS services
```

### 🔒 Enhanced Security Features

| **Component** | **Implementation** | **Modern Upgrade** |
|---------------|-------------------|-------------------|
| **Password Hashing** | PBKDF2 (legacy) → Argon2/bcrypt | Configurable algorithms with auto-migration |
| **Session Management** | Basic JWT → Enhanced JWT | Token rotation, refresh tokens, secure storage |
| **Input Validation** | Basic checks → Comprehensive validation | Type-safe validation with custom validators |
| **Tenant Isolation** | Manual filtering → Automatic isolation | Repository-level tenant context enforcement |
| **Audit Logging** | Print statements → Structured logging | Centralized logging with audit trails |
| **Error Handling** | Bare exceptions → Structured exceptions | Exception hierarchy with proper error context |

---

## 📊 Data Architecture

### 🗄️ Modern Database Schema

```mermaid
erDiagram
    TENANTS {
        uuid id PK
        string name
        string subdomain UK
        integer max_users
        boolean is_active
        json metadata
        timestamp created_at
        timestamp updated_at
    }

    USERS {
        uuid id PK
        uuid tenant_id FK
        string email UK
        string password_hash
        string first_name
        string last_name
        enum role
        string sso_id
        boolean is_active
        json permissions
        json metadata
        timestamp created_at
        timestamp last_login
        timestamp updated_at
    }

    PROMPTS {
        integer id PK
        uuid tenant_id FK
        uuid user_id FK
        string name UK
        string title
        text content
        string category
        string tags
        boolean is_enhancement_prompt
        json metadata
        timestamp created_at
        timestamp updated_at
    }

    API_TOKENS {
        uuid id PK
        uuid user_id FK
        uuid tenant_id FK
        string name
        string token_hash
        string token_prefix
        json permissions
        timestamp expires_at
        timestamp last_used
        timestamp created_at
    }

    CONFIG {
        integer id PK
        uuid tenant_id FK
        uuid user_id FK
        string key UK
        text value
        string value_type
        timestamp created_at
        timestamp updated_at
    }

    %% Relationships with proper constraints
    TENANTS ||--o{ USERS : "manages"
    TENANTS ||--o{ PROMPTS : "isolates"
    TENANTS ||--o{ API_TOKENS : "owns"
    TENANTS ||--o{ CONFIG : "configures"
    
    USERS ||--o{ PROMPTS : "creates"
    USERS ||--o{ API_TOKENS : "generates"
    USERS ||--o{ CONFIG : "personalizes"
```

### 📈 Repository Pattern Implementation

```mermaid
graph TB
    subgraph "🏗️ Repository Base Classes"
        BASE_REPO[💾 BaseRepository<T>]
        TENANT_REPO[🏢 TenantAwareRepository<T>]
    end

    subgraph "📊 Entity Models"
        PROMPT_MODEL[📝 Prompt DataClass]
        USER_MODEL[👤 User DataClass]
        TENANT_MODEL[🏢 Tenant DataClass]
    end

    subgraph "💾 Concrete Repositories"
        PROMPT_REPO[📄 PromptRepository]
        USER_REPO[👤 UserRepository]
        TENANT_REPO_IMPL[🏢 TenantRepository]
    end

    subgraph "🔧 Repository Operations"
        CRUD[📋 CRUD Operations]
        SEARCH[🔍 Search & Filter]
        TENANT_FILTER[🏢 Tenant Filtering]
        VALIDATION[✅ Data Validation]
    end

    BASE_REPO --> TENANT_REPO
    TENANT_REPO --> PROMPT_REPO
    BASE_REPO --> USER_REPO
    BASE_REPO --> TENANT_REPO_IMPL

    PROMPT_MODEL --> PROMPT_REPO
    USER_MODEL --> USER_REPO
    TENANT_MODEL --> TENANT_REPO_IMPL

    PROMPT_REPO --> CRUD
    PROMPT_REPO --> SEARCH
    PROMPT_REPO --> TENANT_FILTER
    PROMPT_REPO --> VALIDATION

    classDef base fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef model fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef repository fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef operations fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class BASE_REPO,TENANT_REPO base
    class PROMPT_MODEL,USER_MODEL,TENANT_MODEL model
    class PROMPT_REPO,USER_REPO,TENANT_REPO_IMPL repository
    class CRUD,SEARCH,TENANT_FILTER,VALIDATION operations
```

---

## 🌐 Deployment Architectures

### 🚀 Containerized Development

```mermaid
graph TB
    subgraph "🐳 Docker Development Stack"
        subgraph "🚀 Application Container"
            APP[🎨 AI Prompt Manager<br/>New + Legacy Architecture]
            GRADIO[🖥️ Gradio UI :7860]
            API[🔌 FastAPI :8000]
        end
        
        subgraph "💾 Database Container"
            POSTGRES[🐘 PostgreSQL :5432]
            SQLITE[📁 SQLite Volume]
        end
        
        subgraph "⚡ Cache Container"
            REDIS[⚡ Redis :6379]
        end
        
        subgraph "📁 Persistent Volumes"
            DB_DATA[💾 Database Data]
            APP_LOGS[📋 Application Logs]
            CONFIG_VOL[⚙️ Configuration]
        end
    end

    INTERNET[🌍 Internet] --> GRADIO
    INTERNET --> API
    
    APP --> POSTGRES
    APP --> SQLITE
    APP --> REDIS
    
    POSTGRES --> DB_DATA
    APP --> APP_LOGS
    APP --> CONFIG_VOL

    classDef container fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef volume fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class APP,POSTGRES,REDIS container
    class GRADIO,API,SQLITE service
    class DB_DATA,APP_LOGS,CONFIG_VOL volume
```

### 🏢 Enterprise Production Deployment

```mermaid
graph TB
    subgraph "🌐 Edge Layer"
        CDN[🌍 Global CDN]
        WAF[🛡️ Web Application Firewall]
    end

    subgraph "⚖️ Load Balancer Layer"
        LB1[⚖️ Load Balancer 1]
        LB2[⚖️ Load Balancer 2]
    end

    subgraph "🚀 Application Tier (New Architecture)"
        APP1[🎨 App Instance 1<br/>src/ + legacy/]
        APP2[🎨 App Instance 2<br/>src/ + legacy/]
        APP3[🎨 App Instance 3<br/>src/ + legacy/]
    end

    subgraph "💾 Database Cluster"
        DB_PRIMARY[🐘 PostgreSQL Primary<br/>Write Operations]
        DB_REPLICA1[🐘 PostgreSQL Replica 1<br/>Read Operations]
        DB_REPLICA2[🐘 PostgreSQL Replica 2<br/>Read Operations]
    end

    subgraph "⚡ Cache Cluster"
        REDIS_MASTER[⚡ Redis Master]
        REDIS_SLAVE1[⚡ Redis Slave 1]
        REDIS_SLAVE2[⚡ Redis Slave 2]
    end

    subgraph "📊 Monitoring & Logging"
        PROMETHEUS[📈 Prometheus Metrics]
        GRAFANA[📊 Grafana Dashboard]
        ELK[📋 ELK Stack Logging]
        JAEGER[🔍 Distributed Tracing]
    end

    INTERNET[🌍 Internet] --> CDN
    CDN --> WAF
    WAF --> LB1
    WAF --> LB2
    
    LB1 --> APP1
    LB1 --> APP2
    LB2 --> APP2
    LB2 --> APP3
    
    APP1 --> DB_PRIMARY
    APP2 --> DB_REPLICA1
    APP3 --> DB_REPLICA2
    
    APP1 --> REDIS_MASTER
    APP2 --> REDIS_SLAVE1
    APP3 --> REDIS_SLAVE2

    APP1 --> PROMETHEUS
    APP2 --> GRAFANA
    APP3 --> ELK
    APP1 --> JAEGER

    classDef edge fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef lb fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef app fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef database fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef monitoring fill:#e1f5fe,stroke:#0277bd,stroke-width:2px

    class CDN,WAF edge
    class LB1,LB2 lb
    class APP1,APP2,APP3 app
    class DB_PRIMARY,DB_REPLICA1,DB_REPLICA2 database
    class REDIS_MASTER,REDIS_SLAVE1,REDIS_SLAVE2 cache
    class PROMETHEUS,GRAFANA,ELK,JAEGER monitoring
```

---

## 🔌 API Architecture

### 📋 Modern API Design

```mermaid
graph TB
    subgraph "🌐 API Gateway Layer"
        GATEWAY[🚀 FastAPI Gateway]
        AUTH_MW[🔐 Auth Middleware]
        TENANT_MW[🏢 Tenant Middleware]
        RATE_MW[⏱️ Rate Limit Middleware]
        CORS_MW[🔗 CORS Middleware]
    end

    subgraph "🎯 API Routers"
        PROMPT_ROUTER[📝 /api/prompts]
        AUTH_ROUTER[🔐 /api/auth]
        USER_ROUTER[👤 /api/users]
        CONFIG_ROUTER[⚙️ /api/config]
        HEALTH_ROUTER[❤️ /api/health]
    end

    subgraph "🧠 Service Integration"
        PROMPT_SVC[📝 PromptService]
        AUTH_SVC[🔐 AuthService]
        USER_SVC[👤 UserService]
        CONFIG_SVC[⚙️ ConfigService]
    end

    subgraph "📊 Response Handling"
        SUCCESS_RESP[✅ Success Response]
        ERROR_RESP[❌ Error Response]
        VALIDATION_RESP[⚠️ Validation Response]
        SCHEMA_RESP[📋 OpenAPI Schema]
    end

    CLIENT[👤 API Client] --> GATEWAY
    GATEWAY --> AUTH_MW
    AUTH_MW --> TENANT_MW
    TENANT_MW --> RATE_MW
    RATE_MW --> CORS_MW
    
    CORS_MW --> PROMPT_ROUTER
    CORS_MW --> AUTH_ROUTER
    CORS_MW --> USER_ROUTER
    CORS_MW --> CONFIG_ROUTER
    CORS_MW --> HEALTH_ROUTER
    
    PROMPT_ROUTER --> PROMPT_SVC
    AUTH_ROUTER --> AUTH_SVC
    USER_ROUTER --> USER_SVC
    CONFIG_ROUTER --> CONFIG_SVC
    
    PROMPT_SVC --> SUCCESS_RESP
    AUTH_SVC --> ERROR_RESP
    USER_SVC --> VALIDATION_RESP
    CONFIG_SVC --> SCHEMA_RESP

    classDef gateway fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef router fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef service fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef response fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class GATEWAY,AUTH_MW,TENANT_MW,RATE_MW,CORS_MW gateway
    class PROMPT_ROUTER,AUTH_ROUTER,USER_ROUTER,CONFIG_ROUTER,HEALTH_ROUTER router
    class PROMPT_SVC,AUTH_SVC,USER_SVC,CONFIG_SVC service
    class SUCCESS_RESP,ERROR_RESP,VALIDATION_RESP,SCHEMA_RESP response
```

---

## 🌍 Multi-Language Architecture

### 🔄 Enhanced I18N System

```mermaid
graph TB
    subgraph "🌐 Language Detection & Management"
        URL_LANG[🔗 URL Language Parameter]
        USER_PREF[👤 User Preference]
        BROWSER_LANG[🌐 Browser Language]
        TENANT_DEFAULT[🏢 Tenant Default]
    end

    subgraph "🏗️ I18N Service Architecture"
        I18N_SERVICE[🔧 I18nService]
        LANG_MANAGER[📚 LanguageManager]
        TRANSLATOR_SVC[🔄 TranslatorService]
        FALLBACK_SVC[🔄 FallbackService]
    end

    subgraph "📚 Translation Storage & Cache"
        LANG_FILES[📁 Language Files]
        REDIS_CACHE[⚡ Redis Translation Cache]
        DB_TRANSLATIONS[💾 Database Translations]
        REMOTE_API[🌍 Remote Translation APIs]
    end

    subgraph "🎨 UI Integration"
        GRADIO_I18N[🎨 Gradio I18N Components]
        DYNAMIC_LABELS[🏷️ Dynamic Labels]
        ERROR_MESSAGES[❌ Localized Errors]
        HELP_TEXT[❓ Contextual Help]
    end

    URL_LANG --> I18N_SERVICE
    USER_PREF --> I18N_SERVICE
    BROWSER_LANG --> I18N_SERVICE
    TENANT_DEFAULT --> I18N_SERVICE
    
    I18N_SERVICE --> LANG_MANAGER
    I18N_SERVICE --> TRANSLATOR_SVC
    I18N_SERVICE --> FALLBACK_SVC
    
    LANG_MANAGER --> LANG_FILES
    LANG_MANAGER --> REDIS_CACHE
    TRANSLATOR_SVC --> DB_TRANSLATIONS
    TRANSLATOR_SVC --> REMOTE_API
    
    I18N_SERVICE --> GRADIO_I18N
    I18N_SERVICE --> DYNAMIC_LABELS
    I18N_SERVICE --> ERROR_MESSAGES
    I18N_SERVICE --> HELP_TEXT

    classDef detection fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef ui fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class URL_LANG,USER_PREF,BROWSER_LANG,TENANT_DEFAULT detection
    class I18N_SERVICE,LANG_MANAGER,TRANSLATOR_SVC,FALLBACK_SVC service
    class LANG_FILES,REDIS_CACHE,DB_TRANSLATIONS,REMOTE_API storage
    class GRADIO_I18N,DYNAMIC_LABELS,ERROR_MESSAGES,HELP_TEXT ui
```

---

## 🧩 Prompt Builder Architecture

### 🔧 Enhanced Builder System

```mermaid
graph TB
    subgraph "🎨 Modern UI Components"
        DRAG_DROP[🖱️ Drag & Drop Interface]
        LIVE_PREVIEW[👁️ Live Preview]
        TEMPLATE_GALLERY[🎨 Template Gallery]
        OPTIONS_PANEL[⚙️ Advanced Options]
    end

    subgraph "🧠 Builder Service Layer"
        BUILDER_SVC[🧩 PromptBuilderService]
        TEMPLATE_SVC[🎨 TemplateService]
        COMBINER_SVC[🔗 CombinerService]
        VALIDATOR_SVC[✅ ValidationService]
    end

    subgraph "📊 State Management"
        BUILDER_STATE[📊 Builder State Manager]
        SELECTION_STATE[🎯 Selection State]
        PREVIEW_STATE[👁️ Preview State]
        HISTORY_STATE[📚 History State]
    end

    subgraph "💾 Data Integration"
        PROMPT_REPO[📄 PromptRepository]
        TEMPLATE_REPO[🎨 TemplateRepository]
        USER_PREFS[👤 User Preferences]
        ANALYTICS[📊 Usage Analytics]
    end

    DRAG_DROP --> BUILDER_SVC
    LIVE_PREVIEW --> BUILDER_SVC
    TEMPLATE_GALLERY --> TEMPLATE_SVC
    OPTIONS_PANEL --> BUILDER_SVC
    
    BUILDER_SVC --> TEMPLATE_SVC
    BUILDER_SVC --> COMBINER_SVC
    BUILDER_SVC --> VALIDATOR_SVC
    
    TEMPLATE_SVC --> BUILDER_STATE
    COMBINER_SVC --> SELECTION_STATE
    VALIDATOR_SVC --> PREVIEW_STATE
    BUILDER_SVC --> HISTORY_STATE
    
    BUILDER_STATE --> PROMPT_REPO
    SELECTION_STATE --> TEMPLATE_REPO
    PREVIEW_STATE --> USER_PREFS
    HISTORY_STATE --> ANALYTICS

    classDef ui fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef state fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class DRAG_DROP,LIVE_PREVIEW,TEMPLATE_GALLERY,OPTIONS_PANEL ui
    class BUILDER_SVC,TEMPLATE_SVC,COMBINER_SVC,VALIDATOR_SVC service
    class BUILDER_STATE,SELECTION_STATE,PREVIEW_STATE,HISTORY_STATE state
    class PROMPT_REPO,TEMPLATE_REPO,USER_PREFS,ANALYTICS data
```

---

## ⚡ Performance Considerations

### 🚀 Modern Performance Architecture

```mermaid
graph TB
    subgraph "🏗️ Architecture Performance"
        TYPE_SAFETY[📊 Type Safety Benefits]
        LAZY_LOADING[🔄 Lazy Component Loading]
        SERVICE_CACHING[💾 Service Layer Caching]
        REPOSITORY_OPT[🔍 Repository Optimization]
    end

    subgraph "💾 Database Optimization"
        CONNECTION_POOL[🏊 Connection Pooling]
        QUERY_OPT[🔍 Query Optimization]
        TENANT_INDEX[🏢 Tenant-Aware Indexing]
        PREPARED_STMT[📋 Prepared Statements]
    end

    subgraph "⚡ Caching Strategy"
        REDIS_CACHE[⚡ Redis Distributed Cache]
        MEMORY_CACHE[🧠 In-Memory Service Cache]
        QUERY_CACHE[🔍 Query Result Cache]
        CONFIG_CACHE[⚙️ Configuration Cache]
    end

    subgraph "📊 Monitoring & Metrics"
        PERFORMANCE_METRICS[📈 Performance Metrics]
        SERVICE_METRICS[🧠 Service Layer Metrics]
        REPOSITORY_METRICS[💾 Repository Metrics]
        CACHE_METRICS[⚡ Cache Hit Rates]
    end

    TYPE_SAFETY --> CONNECTION_POOL
    LAZY_LOADING --> QUERY_OPT
    SERVICE_CACHING --> TENANT_INDEX
    REPOSITORY_OPT --> PREPARED_STMT
    
    CONNECTION_POOL --> REDIS_CACHE
    QUERY_OPT --> MEMORY_CACHE
    TENANT_INDEX --> QUERY_CACHE
    PREPARED_STMT --> CONFIG_CACHE
    
    REDIS_CACHE --> PERFORMANCE_METRICS
    MEMORY_CACHE --> SERVICE_METRICS
    QUERY_CACHE --> REPOSITORY_METRICS
    CONFIG_CACHE --> CACHE_METRICS

    classDef architecture fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef database fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef caching fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef monitoring fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class TYPE_SAFETY,LAZY_LOADING,SERVICE_CACHING,REPOSITORY_OPT architecture
    class CONNECTION_POOL,QUERY_OPT,TENANT_INDEX,PREPARED_STMT database
    class REDIS_CACHE,MEMORY_CACHE,QUERY_CACHE,CONFIG_CACHE caching
    class PERFORMANCE_METRICS,SERVICE_METRICS,REPOSITORY_METRICS,CACHE_METRICS monitoring
```

### 📊 Performance Benefits of New Architecture

| **Component** | **Legacy Performance** | **New Architecture Benefits** |
|---------------|------------------------|-------------------------------|
| **Type Safety** | Runtime errors, debugging overhead | Compile-time validation, reduced errors |
| **Database Operations** | Manual SQL, N+1 queries | Optimized repository patterns, batch operations |
| **Code Reuse** | 75% duplication | Shared base classes, DRY principles |
| **Testing** | Manual testing, brittle tests | Dependency injection, comprehensive test coverage |
| **Error Handling** | Generic exceptions | Structured exceptions with context |
| **Logging** | Print statements | Structured logging with performance metrics |

---

## 🔮 Future Architecture

### 🌟 Migration Roadmap

```mermaid
gantt
    title AI Prompt Manager Architecture Migration
    dateFormat  YYYY-MM-DD
    section Phase 1 - Core Infrastructure
    Base Classes Implementation    :done, phase1a, 2025-06-01, 2025-06-11
    Prompt Management Migration    :done, phase1b, 2025-06-08, 2025-06-11
    Testing Framework             :done, phase1c, 2025-06-09, 2025-06-11
    
    section Phase 2 - Service Layer
    Auth Service Migration        :active, phase2a, 2025-06-11, 2025-06-15
    API Layer Modernization       :phase2b, 2025-06-12, 2025-06-18
    UI Component Migration        :phase2c, 2025-06-15, 2025-06-20
    
    section Phase 3 - Advanced Features
    External Service Integration  :phase3a, 2025-06-18, 2025-06-25
    Performance Optimization      :phase3b, 2025-06-20, 2025-06-30
    Advanced Security Features    :phase3c, 2025-06-22, 2025-07-05
    
    section Phase 4 - Enhancement
    ML Integration               :phase4a, 2025-06-25, 2025-07-10
    Advanced Analytics           :phase4b, 2025-06-30, 2025-07-15
    Global Deployment           :phase4c, 2025-07-05, 2025-07-20
```

### 🚀 Next Generation Features

```mermaid
graph TB
    subgraph "🤖 AI/ML Integration"
        ML_PROMPT_GEN[🧠 AI Prompt Generation]
        SEMANTIC_SEARCH[🔍 Semantic Search]
        AUTO_OPTIMIZATION[⚡ Auto-Optimization]
        PERFORMANCE_ML[📊 Performance ML]
    end

    subgraph "🌍 Global Architecture"
        MULTI_REGION[🌍 Multi-Region Deployment]
        EDGE_COMPUTE[⚡ Edge Computing]
        CDN_INTEGRATION[🌐 Advanced CDN]
        REGIONAL_COMPLIANCE[📋 Regional Compliance]
    end

    subgraph "🔌 Ecosystem Integration"
        PLUGIN_ARCH[🔌 Plugin Architecture]
        MARKETPLACE[🏪 Prompt Marketplace]
        API_ECOSYSTEM[🔗 API Ecosystem]
        WEBHOOK_ENGINE[🪝 Advanced Webhooks]
    end

    subgraph "📊 Advanced Analytics"
        REAL_TIME_ANALYTICS[📈 Real-time Analytics]
        PREDICTIVE_INSIGHTS[🔮 Predictive Insights]
        COST_OPTIMIZATION[💰 Cost Optimization]
        USAGE_PATTERNS[📊 Usage Pattern Analysis]
    end

    ML_PROMPT_GEN --> MULTI_REGION
    SEMANTIC_SEARCH --> EDGE_COMPUTE
    AUTO_OPTIMIZATION --> CDN_INTEGRATION
    PERFORMANCE_ML --> REGIONAL_COMPLIANCE
    
    MULTI_REGION --> PLUGIN_ARCH
    EDGE_COMPUTE --> MARKETPLACE
    CDN_INTEGRATION --> API_ECOSYSTEM
    REGIONAL_COMPLIANCE --> WEBHOOK_ENGINE
    
    PLUGIN_ARCH --> REAL_TIME_ANALYTICS
    MARKETPLACE --> PREDICTIVE_INSIGHTS
    API_ECOSYSTEM --> COST_OPTIMIZATION
    WEBHOOK_ENGINE --> USAGE_PATTERNS

    classDef ai fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef global fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef ecosystem fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef analytics fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class ML_PROMPT_GEN,SEMANTIC_SEARCH,AUTO_OPTIMIZATION,PERFORMANCE_ML ai
    class MULTI_REGION,EDGE_COMPUTE,CDN_INTEGRATION,REGIONAL_COMPLIANCE global
    class PLUGIN_ARCH,MARKETPLACE,API_ECOSYSTEM,WEBHOOK_ENGINE ecosystem
    class REAL_TIME_ANALYTICS,PREDICTIVE_INSIGHTS,COST_OPTIMIZATION,USAGE_PATTERNS analytics
```

---

## 📚 Architecture Documentation

### 📖 Implementation Status

| **Component** | **Status** | **Location** | **Test Coverage** |
|---------------|------------|--------------|-------------------|
| **Core Base Classes** | ✅ Complete | `src/core/base/` | 95% |
| **Configuration System** | ✅ Complete | `src/core/config/` | 90% |
| **Authentication Models** | ✅ Complete | `src/auth/models/` | 85% |
| **Prompt Management** | ✅ Complete | `src/prompts/` | 90% |
| **Security Services** | ✅ Complete | `src/auth/security/` | 88% |
| **Database Abstraction** | ✅ Complete | `src/core/base/database_manager.py` | 92% |
| **Exception Hierarchy** | ✅ Complete | `src/core/exceptions/` | 85% |
| **Testing Framework** | ✅ Complete | `tests/` | 100% |

### 🏗️ Architecture Principles

1. **🔗 Service Layer Pattern**: Clean separation between business logic and data access
2. **💾 Repository Pattern**: Abstracted data access with tenant isolation
3. **🏗️ Dependency Injection**: Testable, mockable components
4. **📊 Type Safety**: Comprehensive type hints throughout the codebase
5. **🔐 Security by Design**: Multi-layer security with modern practices
6. **🏢 Multi-tenancy**: Complete data isolation and resource sharing
7. **⚡ Performance**: Optimized queries and caching strategies
8. **🧪 Test-Driven**: Comprehensive unit and integration testing

---

**🏗️ Modern architecture designed for scale • 🔐 Enhanced security • 🌐 Global accessibility • 🚀 Future-ready with full type safety**