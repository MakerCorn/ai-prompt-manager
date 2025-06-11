"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Internationalization (i18n) system for AI Prompt Manager
Multi-language support with dynamic label switching

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import json
import os
from typing import Dict, Any, Optional
from functools import lru_cache

class I18nManager:
    """
    Internationalization manager for multi-language support
    Supports dynamic language switching and fallback to English
    """
    
    def __init__(self, default_language: str = "en"):
        # Check for environment variable override
        import os
        env_lang = os.getenv('DEFAULT_LANGUAGE', '').lower()
        if env_lang and env_lang in ['en', 'es', 'fr', 'de', 'zh', 'ja', 'pt', 'ru', 'ar', 'hi']:
            default_language = env_lang
        
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all available translation files"""
        # Base translations embedded in code for reliability
        self.translations = {
            "en": self._get_english_translations(),
            "es": self._get_spanish_translations(),
            "fr": self._get_french_translations(),
            "de": self._get_german_translations(),
            "zh": self._get_chinese_translations(),
            "ja": self._get_japanese_translations(),
            "pt": self._get_portuguese_translations(),
            "ru": self._get_russian_translations(),
            "ar": self._get_arabic_translations(),
            "hi": self._get_hindi_translations()
        }
    
    def set_language(self, language_code: str) -> bool:
        """Set current language, returns True if successful"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages with native names"""
        return {
            "en": "English",
            "es": "Español",
            "fr": "Français", 
            "de": "Deutsch",
            "zh": "中文",
            "ja": "日本語",
            "pt": "Português",
            "ru": "Русский",
            "ar": "العربية",
            "hi": "हिन्दी"
        }
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to current language with optional formatting
        
        Args:
            key: Translation key (e.g., 'login.title')
            **kwargs: Optional formatting parameters
            
        Returns:
            Translated string or key if not found
        """
        # Get translation from current language or fallback to English
        current_trans = self.translations.get(self.current_language, {})
        english_trans = self.translations.get(self.default_language, {})
        
        # Try current language first, then English, then return key
        text = current_trans.get(key) or english_trans.get(key) or key
        
        # Format with provided kwargs if any
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return unformatted text if formatting fails
                
        return text
    
    def _get_english_translations(self) -> Dict[str, str]:
        """English translations (base language)"""
        return {
            # Application
            "app.title": "AI Prompt Manager",
            "app.subtitle": "Secure, multi-tenant AI prompt management",
            "app.status.authenticated": "✅ Authenticated as {user}",
            "app.status.not_authenticated": "❌ Not authenticated",
            
            # Navigation
            "nav.prompts": "Prompts",
            "nav.library": "Library", 
            "nav.tokens": "Tokens",
            "nav.settings": "Settings",
            "nav.admin": "Admin",
            
            # Authentication
            "auth.login": "Login",
            "auth.logout": "Logout",
            "auth.email": "Email",
            "auth.password": "Password",
            "auth.tenant": "Tenant",
            "auth.sso": "SSO Login",
            "auth.welcome": "Welcome, {name}!",
            "auth.invalid": "Invalid credentials",
            
            # Prompts
            "prompt.name": "Name",
            "prompt.title": "Title", 
            "prompt.category": "Category",
            "prompt.content": "Content",
            "prompt.tags": "Tags",
            "prompt.add": "Add",
            "prompt.update": "Update",
            "prompt.delete": "Delete",
            "prompt.clear": "Clear",
            "prompt.load": "Load",
            "prompt.search": "Search",
            "prompt.enhancement": "Enhancement Prompt",
            
            # Actions
            "action.save": "Save",
            "action.cancel": "Cancel",
            "action.refresh": "Refresh",
            "action.edit": "Edit",
            "action.view": "View",
            "action.copy": "Copy",
            "action.export": "Export",
            "action.import": "Import",
            
            # Status
            "status.success": "Success",
            "status.error": "Error",
            "status.loading": "Loading...",
            "status.saved": "Saved successfully",
            "status.deleted": "Deleted successfully",
            
            # Calculator
            "calc.title": "Token Calculator",
            "calc.model": "Model",
            "calc.tokens": "Tokens",
            "calc.cost": "Cost",
            "calc.estimate": "Estimate",
            "calc.input": "Input",
            "calc.output": "Output",
            
            # Optimization
            "opt.title": "Optimization",
            "opt.context": "Context",
            "opt.target": "Target Model",
            "opt.optimize": "Optimize",
            "opt.score": "Score",
            "opt.suggestions": "Suggestions",
            "opt.accept": "Accept",
            "opt.reject": "Reject",
            "opt.retry": "Retry",
            
            # Forms
            "form.required": "Required",
            "form.optional": "Optional",
            "form.placeholder.name": "Enter name",
            "form.placeholder.search": "Search...",
            "form.placeholder.email": "user@domain.com",
            
            # Messages
            "msg.select_item": "Please select an item",
            "msg.confirm_delete": "Are you sure you want to delete this?",
            "msg.no_results": "No results found",
            "msg.loading_data": "Loading data...",
            
            # Translation
            "translate.to_english": "Translate to English",
            "translate.status": "Translation Status",
            "translate.help": "Translate your prompt to English for better AI enhancement",
            
            # Testing
            "test.prompt": "Test Prompt",
            "test.status": "Test Status",
            
            # Prompt Builder
            "builder.title": "Prompt Builder",
            "builder.subtitle": "Combine existing prompts to create new ones",
            "builder.available": "Available Prompts",
            "builder.selected": "Selected Prompts",
            "builder.preview": "Preview",
            "builder.template": "Combination Template",
            "builder.template.sequential": "Sequential",
            "builder.template.sequential.desc": "Combine prompts one after another",
            "builder.template.sections": "Sections",
            "builder.template.sections.desc": "Combine prompts as distinct sections",
            "builder.template.layered": "Layered",
            "builder.template.layered.desc": "Build context in layers",
            "builder.template.custom": "Custom",
            "builder.template.custom.desc": "Use custom formatting template",
            "builder.combine": "Combine Prompts",
            "builder.clear": "Clear Selection",
            "builder.edit": "Open in Editor",
            "builder.error.no_prompts": "No prompts selected",
            "builder.error.min_prompts": "Select at least 2 prompts",
            "builder.error.duplicates": "Duplicate prompts found",
            "builder.error.too_long": "Combined prompt too long",
            "builder.error.combination": "Combination failed",
            "builder.preview.empty": "Select prompts to see preview",
            "builder.preview.error": "Preview error",
            "builder.drag.add": "Drag here to add",
            "builder.drag.reorder": "Drag to reorder",
            "builder.search.placeholder": "Search prompts...",
            "builder.filter.category": "Filter by category",
            "builder.filter.all": "All Categories",
        }
    
    def _get_spanish_translations(self) -> Dict[str, str]:
        """Spanish translations"""
        return {
            # Application
            "app.title": "Gestor de Prompts IA",
            "app.subtitle": "Gestión segura y multi-inquilino de prompts IA",
            "app.status.authenticated": "✅ Autenticado como {user}",
            "app.status.not_authenticated": "❌ No autenticado",
            
            # Navigation
            "nav.prompts": "Prompts",
            "nav.library": "Biblioteca",
            "nav.tokens": "Tokens",
            "nav.settings": "Configuración",
            "nav.admin": "Admin",
            
            # Authentication
            "auth.login": "Iniciar Sesión",
            "auth.logout": "Cerrar Sesión",
            "auth.email": "Correo",
            "auth.password": "Contraseña",
            "auth.tenant": "Inquilino",
            "auth.sso": "Login SSO",
            "auth.welcome": "¡Bienvenido, {name}!",
            "auth.invalid": "Credenciales inválidas",
            
            # Prompts
            "prompt.name": "Nombre",
            "prompt.title": "Título",
            "prompt.category": "Categoría",
            "prompt.content": "Contenido",
            "prompt.tags": "Etiquetas",
            "prompt.add": "Agregar",
            "prompt.update": "Actualizar",
            "prompt.delete": "Eliminar",
            "prompt.clear": "Limpiar",
            "prompt.load": "Cargar",
            "prompt.search": "Buscar",
            "prompt.enhancement": "Prompt de Mejora",
            
            # Actions
            "action.save": "Guardar",
            "action.cancel": "Cancelar",
            "action.refresh": "Actualizar",
            "action.edit": "Editar",
            "action.view": "Ver",
            "action.copy": "Copiar",
            "action.export": "Exportar",
            "action.import": "Importar",
            
            # Status
            "status.success": "Éxito",
            "status.error": "Error",
            "status.loading": "Cargando...",
            "status.saved": "Guardado exitosamente",
            "status.deleted": "Eliminado exitosamente",
            
            # Calculator
            "calc.title": "Calculadora de Tokens",
            "calc.model": "Modelo",
            "calc.tokens": "Tokens",
            "calc.cost": "Costo",
            "calc.estimate": "Estimar",
            "calc.input": "Entrada",
            "calc.output": "Salida",
            
            # Optimization
            "opt.title": "Optimización",
            "opt.context": "Contexto",
            "opt.target": "Modelo Objetivo",
            "opt.optimize": "Optimizar",
            "opt.score": "Puntuación",
            "opt.suggestions": "Sugerencias",
            "opt.accept": "Aceptar",
            "opt.reject": "Rechazar",
            "opt.retry": "Reintentar",
            
            # Forms
            "form.required": "Requerido",
            "form.optional": "Opcional",
            "form.placeholder.name": "Ingrese nombre",
            "form.placeholder.search": "Buscar...",
            "form.placeholder.email": "usuario@dominio.com",
            
            # Messages
            "msg.select_item": "Por favor seleccione un elemento",
            "msg.confirm_delete": "¿Está seguro de que desea eliminar esto?",
            "msg.no_results": "No se encontraron resultados",
            "msg.loading_data": "Cargando datos...",
            
            # Translation
            "translate.to_english": "Traducir al Inglés",
            "translate.status": "Estado de Traducción",
            "translate.help": "Traduzca su prompt al inglés para una mejor mejora con IA",
            
            # Prompt Builder
            "builder.title": "Constructor de Prompts",
            "builder.subtitle": "Combine prompts existentes para crear nuevos",
            "builder.available": "Prompts Disponibles",
            "builder.selected": "Prompts Seleccionados",
            "builder.preview": "Vista Previa",
            "builder.template": "Plantilla de Combinación",
            "builder.template.sequential": "Secuencial",
            "builder.template.sequential.desc": "Combinar prompts uno tras otro",
            "builder.template.sections": "Secciones",
            "builder.template.sections.desc": "Combinar prompts como secciones distintas",
            "builder.template.layered": "Por Capas",
            "builder.template.layered.desc": "Construir contexto en capas",
            "builder.template.custom": "Personalizado",
            "builder.template.custom.desc": "Usar plantilla de formato personalizada",
            "builder.combine": "Combinar Prompts",
            "builder.clear": "Limpiar Selección",
            "builder.edit": "Abrir en Editor",
            "builder.error.no_prompts": "No hay prompts seleccionados",
            "builder.error.min_prompts": "Seleccione al menos 2 prompts",
            "builder.error.duplicates": "Se encontraron prompts duplicados",
            "builder.error.too_long": "Prompt combinado demasiado largo",
            "builder.error.combination": "Falló la combinación",
            "builder.preview.empty": "Seleccione prompts para ver vista previa",
            "builder.preview.error": "Error de vista previa",
            "builder.drag.add": "Arrastre aquí para agregar",
            "builder.drag.reorder": "Arrastre para reordenar",
            "builder.search.placeholder": "Buscar prompts...",
            "builder.filter.category": "Filtrar por categoría",
            "builder.filter.all": "Todas las Categorías",
        }
    
    def _get_french_translations(self) -> Dict[str, str]:
        """French translations"""
        return {
            # Application
            "app.title": "Gestionnaire de Prompts IA",
            "app.subtitle": "Gestion sécurisée et multi-locataire de prompts IA",
            "app.status.authenticated": "✅ Authentifié en tant que {user}",
            "app.status.not_authenticated": "❌ Non authentifié",
            
            # Navigation
            "nav.prompts": "Prompts",
            "nav.library": "Bibliothèque",
            "nav.tokens": "Jetons",
            "nav.settings": "Paramètres",
            "nav.admin": "Admin",
            
            # Authentication
            "auth.login": "Connexion",
            "auth.logout": "Déconnexion",
            "auth.email": "Email",
            "auth.password": "Mot de passe",
            "auth.tenant": "Locataire",
            "auth.sso": "Connexion SSO",
            "auth.welcome": "Bienvenue, {name}!",
            "auth.invalid": "Identifiants invalides",
            
            # Prompts
            "prompt.name": "Nom",
            "prompt.title": "Titre",
            "prompt.category": "Catégorie",
            "prompt.content": "Contenu",
            "prompt.tags": "Étiquettes",
            "prompt.add": "Ajouter",
            "prompt.update": "Mettre à jour",
            "prompt.delete": "Supprimer",
            "prompt.clear": "Effacer",
            "prompt.load": "Charger",
            "prompt.search": "Rechercher",
            "prompt.enhancement": "Prompt d'Amélioration",
            
            # Actions
            "action.save": "Sauvegarder",
            "action.cancel": "Annuler",
            "action.refresh": "Actualiser",
            "action.edit": "Modifier",
            "action.view": "Voir",
            "action.copy": "Copier",
            "action.export": "Exporter",
            "action.import": "Importer",
            
            # Status
            "status.success": "Succès",
            "status.error": "Erreur",
            "status.loading": "Chargement...",
            "status.saved": "Sauvegardé avec succès",
            "status.deleted": "Supprimé avec succès",
            
            # Calculator
            "calc.title": "Calculateur de Jetons",
            "calc.model": "Modèle",
            "calc.tokens": "Jetons",
            "calc.cost": "Coût",
            "calc.estimate": "Estimer",
            "calc.input": "Entrée",
            "calc.output": "Sortie",
            
            # Optimization
            "opt.title": "Optimisation",
            "opt.context": "Contexte",
            "opt.target": "Modèle Cible",
            "opt.optimize": "Optimiser",
            "opt.score": "Score",
            "opt.suggestions": "Suggestions",
            "opt.accept": "Accepter",
            "opt.reject": "Rejeter",
            "opt.retry": "Réessayer",
            
            # Forms
            "form.required": "Requis",
            "form.optional": "Optionnel",
            "form.placeholder.name": "Entrez le nom",
            "form.placeholder.search": "Rechercher...",
            "form.placeholder.email": "utilisateur@domaine.com",
            
            # Messages
            "msg.select_item": "Veuillez sélectionner un élément",
            "msg.confirm_delete": "Êtes-vous sûr de vouloir supprimer ceci?",
            "msg.no_results": "Aucun résultat trouvé",
            "msg.loading_data": "Chargement des données...",
            
            # Translation
            "translate.to_english": "Traduire en Anglais",
            "translate.status": "Statut de Traduction",
            "translate.help": "Traduisez votre prompt en anglais pour une meilleure amélioration IA",
            
            # Prompt Builder
            "builder.title": "Constructeur de Prompts",
            "builder.subtitle": "Combinez des prompts existants pour en créer de nouveaux",
            "builder.available": "Prompts Disponibles",
            "builder.selected": "Prompts Sélectionnés",
            "builder.preview": "Aperçu",
            "builder.template": "Modèle de Combinaison",
            "builder.template.sequential": "Séquentiel",
            "builder.template.sequential.desc": "Combiner les prompts l'un après l'autre",
            "builder.template.sections": "Sections",
            "builder.template.sections.desc": "Combiner les prompts en sections distinctes",
            "builder.template.layered": "En Couches",
            "builder.template.layered.desc": "Construire le contexte en couches",
            "builder.template.custom": "Personnalisé",
            "builder.template.custom.desc": "Utiliser un modèle de formatage personnalisé",
            "builder.combine": "Combiner les Prompts",
            "builder.clear": "Effacer la Sélection",
            "builder.edit": "Ouvrir dans l'Éditeur",
            "builder.error.no_prompts": "Aucun prompt sélectionné",
            "builder.error.min_prompts": "Sélectionnez au moins 2 prompts",
            "builder.error.duplicates": "Prompts en double trouvés",
            "builder.error.too_long": "Prompt combiné trop long",
            "builder.error.combination": "Échec de la combinaison",
            "builder.preview.empty": "Sélectionnez des prompts pour voir l'aperçu",
            "builder.preview.error": "Erreur d'aperçu",
            "builder.drag.add": "Glissez ici pour ajouter",
            "builder.drag.reorder": "Glissez pour réorganiser",
            "builder.search.placeholder": "Rechercher des prompts...",
            "builder.filter.category": "Filtrer par catégorie",
            "builder.filter.all": "Toutes les Catégories",
        }
    
    def _get_german_translations(self) -> Dict[str, str]:
        """German translations"""
        return {
            # Application
            "app.title": "KI-Prompt-Manager",
            "app.subtitle": "Sichere, mandantenfähige KI-Prompt-Verwaltung",
            "app.status.authenticated": "✅ Angemeldet als {user}",
            "app.status.not_authenticated": "❌ Nicht angemeldet",
            
            # Navigation
            "nav.prompts": "Prompts",
            "nav.library": "Bibliothek",
            "nav.tokens": "Tokens",
            "nav.settings": "Einstellungen",
            "nav.admin": "Admin",
            
            # Authentication
            "auth.login": "Anmelden",
            "auth.logout": "Abmelden",
            "auth.email": "E-Mail",
            "auth.password": "Passwort",
            "auth.tenant": "Mandant",
            "auth.sso": "SSO-Anmeldung",
            "auth.welcome": "Willkommen, {name}!",
            "auth.invalid": "Ungültige Anmeldedaten",
            
            # Prompts
            "prompt.name": "Name",
            "prompt.title": "Titel",
            "prompt.category": "Kategorie",
            "prompt.content": "Inhalt",
            "prompt.tags": "Tags",
            "prompt.add": "Hinzufügen",
            "prompt.update": "Aktualisieren",
            "prompt.delete": "Löschen",
            "prompt.clear": "Löschen",
            "prompt.load": "Laden",
            "prompt.search": "Suchen",
            "prompt.enhancement": "Verbesserungs-Prompt",
            
            # Actions
            "action.save": "Speichern",
            "action.cancel": "Abbrechen",
            "action.refresh": "Aktualisieren",
            "action.edit": "Bearbeiten",
            "action.view": "Anzeigen",
            "action.copy": "Kopieren",
            "action.export": "Exportieren",
            "action.import": "Importieren",
            
            # Status
            "status.success": "Erfolg",
            "status.error": "Fehler",
            "status.loading": "Laden...",
            "status.saved": "Erfolgreich gespeichert",
            "status.deleted": "Erfolgreich gelöscht",
            
            # Calculator
            "calc.title": "Token-Rechner",
            "calc.model": "Modell",
            "calc.tokens": "Tokens",
            "calc.cost": "Kosten",
            "calc.estimate": "Schätzen",
            "calc.input": "Eingabe",
            "calc.output": "Ausgabe",
            
            # Optimization
            "opt.title": "Optimierung",
            "opt.context": "Kontext",
            "opt.target": "Zielmodell",
            "opt.optimize": "Optimieren",
            "opt.score": "Bewertung",
            "opt.suggestions": "Vorschläge",
            "opt.accept": "Akzeptieren",
            "opt.reject": "Ablehnen",
            "opt.retry": "Wiederholen",
            
            # Forms
            "form.required": "Erforderlich",
            "form.optional": "Optional",
            "form.placeholder.name": "Name eingeben",
            "form.placeholder.search": "Suchen...",
            "form.placeholder.email": "benutzer@domain.com",
            
            # Messages
            "msg.select_item": "Bitte wählen Sie ein Element aus",
            "msg.confirm_delete": "Sind Sie sicher, dass Sie dies löschen möchten?",
            "msg.no_results": "Keine Ergebnisse gefunden",
            "msg.loading_data": "Daten werden geladen...",
            
            # Translation
            "translate.to_english": "Ins Englische übersetzen",
            "translate.status": "Übersetzungsstatus",
            "translate.help": "Übersetzen Sie Ihren Prompt ins Englische für bessere KI-Verbesserung",
            
            # Prompt Builder
            "builder.title": "Prompt-Builder",
            "builder.subtitle": "Kombinieren Sie vorhandene Prompts zu neuen",
            "builder.available": "Verfügbare Prompts",
            "builder.selected": "Ausgewählte Prompts",
            "builder.preview": "Vorschau",
            "builder.template": "Kombinationsvorlage",
            "builder.template.sequential": "Sequenziell",
            "builder.template.sequential.desc": "Prompts nacheinander kombinieren",
            "builder.template.sections": "Abschnitte",
            "builder.template.sections.desc": "Prompts als unterschiedliche Abschnitte kombinieren",
            "builder.template.layered": "Geschichtet",
            "builder.template.layered.desc": "Kontext in Schichten aufbauen",
            "builder.template.custom": "Benutzerdefiniert",
            "builder.template.custom.desc": "Benutzerdefinierte Formatierungsvorlage verwenden",
            "builder.combine": "Prompts kombinieren",
            "builder.clear": "Auswahl löschen",
            "builder.edit": "Im Editor öffnen",
            "builder.error.no_prompts": "Keine Prompts ausgewählt",
            "builder.error.min_prompts": "Wählen Sie mindestens 2 Prompts aus",
            "builder.error.duplicates": "Doppelte Prompts gefunden",
            "builder.error.too_long": "Kombinierter Prompt zu lang",
            "builder.error.combination": "Kombinierung fehlgeschlagen",
            "builder.preview.empty": "Wählen Sie Prompts aus, um die Vorschau zu sehen",
            "builder.preview.error": "Vorschau-Fehler",
            "builder.drag.add": "Hierher ziehen zum Hinzufügen",
            "builder.drag.reorder": "Ziehen zum Neuordnen",
            "builder.search.placeholder": "Prompts suchen...",
            "builder.filter.category": "Nach Kategorie filtern",
            "builder.filter.all": "Alle Kategorien",
        }
    
    def _get_chinese_translations(self) -> Dict[str, str]:
        """Chinese translations"""
        return {
            # Application
            "app.title": "AI提示管理器",
            "app.subtitle": "安全的多租户AI提示管理",
            "app.status.authenticated": "✅ 已认证为 {user}",
            "app.status.not_authenticated": "❌ 未认证",
            
            # Navigation
            "nav.prompts": "提示",
            "nav.library": "库",
            "nav.tokens": "令牌",
            "nav.settings": "设置",
            "nav.admin": "管理",
            
            # Authentication
            "auth.login": "登录",
            "auth.logout": "登出",
            "auth.email": "邮箱",
            "auth.password": "密码",
            "auth.tenant": "租户",
            "auth.sso": "SSO登录",
            "auth.welcome": "欢迎，{name}！",
            "auth.invalid": "无效凭据",
            
            # Prompts
            "prompt.name": "名称",
            "prompt.title": "标题",
            "prompt.category": "类别",
            "prompt.content": "内容",
            "prompt.tags": "标签",
            "prompt.add": "添加",
            "prompt.update": "更新",
            "prompt.delete": "删除",
            "prompt.clear": "清除",
            "prompt.load": "加载",
            "prompt.search": "搜索",
            "prompt.enhancement": "增强提示",
            
            # Actions
            "action.save": "保存",
            "action.cancel": "取消",
            "action.refresh": "刷新",
            "action.edit": "编辑",
            "action.view": "查看",
            "action.copy": "复制",
            "action.export": "导出",
            "action.import": "导入",
            
            # Status
            "status.success": "成功",
            "status.error": "错误",
            "status.loading": "加载中...",
            "status.saved": "保存成功",
            "status.deleted": "删除成功",
            
            # Calculator
            "calc.title": "令牌计算器",
            "calc.model": "模型",
            "calc.tokens": "令牌",
            "calc.cost": "成本",
            "calc.estimate": "估算",
            "calc.input": "输入",
            "calc.output": "输出",
            
            # Optimization
            "opt.title": "优化",
            "opt.context": "上下文",
            "opt.target": "目标模型",
            "opt.optimize": "优化",
            "opt.score": "评分",
            "opt.suggestions": "建议",
            "opt.accept": "接受",
            "opt.reject": "拒绝",
            "opt.retry": "重试",
            
            # Forms
            "form.required": "必需",
            "form.optional": "可选",
            "form.placeholder.name": "输入名称",
            "form.placeholder.search": "搜索...",
            "form.placeholder.email": "用户@域名.com",
            
            # Messages
            "msg.select_item": "请选择一个项目",
            "msg.confirm_delete": "您确定要删除这个吗？",
            "msg.no_results": "未找到结果",
            "msg.loading_data": "正在加载数据...",
            
            # Translation
            "translate.to_english": "翻译为英文",
            "translate.status": "翻译状态",
            "translate.help": "将您的提示翻译为英文以获得更好的AI增强效果",
            
            # Prompt Builder
            "builder.title": "提示构建器",
            "builder.subtitle": "组合现有提示创建新的提示",
            "builder.available": "可用提示",
            "builder.selected": "选中的提示",
            "builder.preview": "预览",
            "builder.template": "组合模板",
            "builder.template.sequential": "顺序",
            "builder.template.sequential.desc": "按顺序组合提示",
            "builder.template.sections": "分段",
            "builder.template.sections.desc": "将提示组合为不同的段落",
            "builder.template.layered": "分层",
            "builder.template.layered.desc": "分层构建上下文",
            "builder.template.custom": "自定义",
            "builder.template.custom.desc": "使用自定义格式模板",
            "builder.combine": "组合提示",
            "builder.clear": "清除选择",
            "builder.edit": "在编辑器中打开",
            "builder.error.no_prompts": "未选择提示",
            "builder.error.min_prompts": "至少选择2个提示",
            "builder.error.duplicates": "发现重复的提示",
            "builder.error.too_long": "组合提示过长",
            "builder.error.combination": "组合失败",
            "builder.preview.empty": "选择提示以查看预览",
            "builder.preview.error": "预览错误",
            "builder.drag.add": "拖拽到此处添加",
            "builder.drag.reorder": "拖拽重新排序",
            "builder.search.placeholder": "搜索提示...",
            "builder.filter.category": "按类别筛选",
            "builder.filter.all": "所有类别",
        }
    
    def _get_japanese_translations(self) -> Dict[str, str]:
        """Japanese translations"""
        return {
            # Application
            "app.title": "AIプロンプトマネージャー",
            "app.subtitle": "安全なマルチテナントAIプロンプト管理",
            "app.status.authenticated": "✅ {user}として認証済み",
            "app.status.not_authenticated": "❌ 未認証",
            
            # Navigation
            "nav.prompts": "プロンプト",
            "nav.library": "ライブラリ",
            "nav.tokens": "トークン",
            "nav.settings": "設定",
            "nav.admin": "管理者",
            
            # Authentication
            "auth.login": "ログイン",
            "auth.logout": "ログアウト",
            "auth.email": "メール",
            "auth.password": "パスワード",
            "auth.tenant": "テナント",
            "auth.sso": "SSOログイン",
            "auth.welcome": "ようこそ、{name}さん！",
            "auth.invalid": "無効な認証情報",
            
            # Prompts
            "prompt.name": "名前",
            "prompt.title": "タイトル",
            "prompt.category": "カテゴリ",
            "prompt.content": "内容",
            "prompt.tags": "タグ",
            "prompt.add": "追加",
            "prompt.update": "更新",
            "prompt.delete": "削除",
            "prompt.clear": "クリア",
            "prompt.load": "読み込み",
            "prompt.search": "検索",
            "prompt.enhancement": "拡張プロンプト",
            
            # Actions
            "action.save": "保存",
            "action.cancel": "キャンセル",
            "action.refresh": "更新",
            "action.edit": "編集",
            "action.view": "表示",
            "action.copy": "コピー",
            "action.export": "エクスポート",
            "action.import": "インポート",
            
            # Status
            "status.success": "成功",
            "status.error": "エラー",
            "status.loading": "読み込み中...",
            "status.saved": "正常に保存されました",
            "status.deleted": "正常に削除されました",
            
            # Calculator
            "calc.title": "トークン計算機",
            "calc.model": "モデル",
            "calc.tokens": "トークン",
            "calc.cost": "コスト",
            "calc.estimate": "推定",
            "calc.input": "入力",
            "calc.output": "出力",
            
            # Optimization
            "opt.title": "最適化",
            "opt.context": "コンテキスト",
            "opt.target": "対象モデル",
            "opt.optimize": "最適化",
            "opt.score": "スコア",
            "opt.suggestions": "提案",
            "opt.accept": "承認",
            "opt.reject": "拒否",
            "opt.retry": "再試行",
            
            # Forms
            "form.required": "必須",
            "form.optional": "任意",
            "form.placeholder.name": "名前を入力",
            "form.placeholder.search": "検索...",
            "form.placeholder.email": "ユーザー@ドメイン.com",
            
            # Messages
            "msg.select_item": "項目を選択してください",
            "msg.confirm_delete": "本当に削除しますか？",
            "msg.no_results": "結果が見つかりません",
            "msg.loading_data": "データを読み込み中...",
            
            # Translation
            "translate.to_english": "英語に翻訳",
            "translate.status": "翻訳ステータス",
            "translate.help": "より良いAI強化のためにプロンプトを英語に翻訳してください",
            
            # Prompt Builder
            "builder.title": "プロンプトビルダー",
            "builder.subtitle": "既存のプロンプトを組み合わせて新しいものを作成",
            "builder.available": "利用可能なプロンプト",
            "builder.selected": "選択されたプロンプト",
            "builder.preview": "プレビュー",
            "builder.template": "組み合わせテンプレート",
            "builder.template.sequential": "順次",
            "builder.template.sequential.desc": "プロンプトを順番に組み合わせる",
            "builder.template.sections": "セクション",
            "builder.template.sections.desc": "プロンプトを異なるセクションとして組み合わせる",
            "builder.template.layered": "階層",
            "builder.template.layered.desc": "階層でコンテキストを構築",
            "builder.template.custom": "カスタム",
            "builder.template.custom.desc": "カスタムフォーマットテンプレートを使用",
            "builder.combine": "プロンプトを組み合わせる",
            "builder.clear": "選択をクリア",
            "builder.edit": "エディターで開く",
            "builder.error.no_prompts": "プロンプトが選択されていません",
            "builder.error.min_prompts": "少なくとも2つのプロンプトを選択してください",
            "builder.error.duplicates": "重複したプロンプトが見つかりました",
            "builder.error.too_long": "組み合わせたプロンプトが長すぎます",
            "builder.error.combination": "組み合わせに失敗しました",
            "builder.preview.empty": "プレビューを見るためにプロンプトを選択してください",
            "builder.preview.error": "プレビューエラー",
            "builder.drag.add": "追加するためにここにドラッグ",
            "builder.drag.reorder": "並び替えるためにドラッグ",
            "builder.search.placeholder": "プロンプトを検索...",
            "builder.filter.category": "カテゴリでフィルター",
            "builder.filter.all": "全カテゴリ",
        }
    
    def _get_portuguese_translations(self) -> Dict[str, str]:
        """Portuguese translations"""
        return {
            # Application
            "app.title": "Gerenciador de Prompts IA",
            "app.subtitle": "Gerenciamento seguro e multi-inquilino de prompts IA",
            "app.status.authenticated": "✅ Autenticado como {user}",
            "app.status.not_authenticated": "❌ Não autenticado",
            
            # Navigation
            "nav.prompts": "Prompts",
            "nav.library": "Biblioteca",
            "nav.tokens": "Tokens",
            "nav.settings": "Configurações",
            "nav.admin": "Admin",
            
            # Authentication
            "auth.login": "Entrar",
            "auth.logout": "Sair",
            "auth.email": "Email",
            "auth.password": "Senha",
            "auth.tenant": "Inquilino",
            "auth.sso": "Login SSO",
            "auth.welcome": "Bem-vindo, {name}!",
            "auth.invalid": "Credenciais inválidas",
            
            # Prompts
            "prompt.name": "Nome",
            "prompt.title": "Título",
            "prompt.category": "Categoria",
            "prompt.content": "Conteúdo",
            "prompt.tags": "Tags",
            "prompt.add": "Adicionar",
            "prompt.update": "Atualizar",
            "prompt.delete": "Excluir",
            "prompt.clear": "Limpar",
            "prompt.load": "Carregar",
            "prompt.search": "Buscar",
            "prompt.enhancement": "Prompt de Melhoria",
            
            # Actions
            "action.save": "Salvar",
            "action.cancel": "Cancelar",
            "action.refresh": "Atualizar",
            "action.edit": "Editar",
            "action.view": "Ver",
            "action.copy": "Copiar",
            "action.export": "Exportar",
            "action.import": "Importar",
            
            # Status
            "status.success": "Sucesso",
            "status.error": "Erro",
            "status.loading": "Carregando...",
            "status.saved": "Salvo com sucesso",
            "status.deleted": "Excluído com sucesso",
            
            # Calculator
            "calc.title": "Calculadora de Tokens",
            "calc.model": "Modelo",
            "calc.tokens": "Tokens",
            "calc.cost": "Custo",
            "calc.estimate": "Estimar",
            "calc.input": "Entrada",
            "calc.output": "Saída",
            
            # Optimization
            "opt.title": "Otimização",
            "opt.context": "Contexto",
            "opt.target": "Modelo Alvo",
            "opt.optimize": "Otimizar",
            "opt.score": "Pontuação",
            "opt.suggestions": "Sugestões",
            "opt.accept": "Aceitar",
            "opt.reject": "Rejeitar",
            "opt.retry": "Tentar Novamente",
            
            # Forms
            "form.required": "Obrigatório",
            "form.optional": "Opcional",
            "form.placeholder.name": "Digite o nome",
            "form.placeholder.search": "Buscar...",
            "form.placeholder.email": "usuario@dominio.com",
            
            # Messages
            "msg.select_item": "Por favor selecione um item",
            "msg.confirm_delete": "Tem certeza que deseja excluir isso?",
            "msg.no_results": "Nenhum resultado encontrado",
            "msg.loading_data": "Carregando dados...",
            
            # Translation
            "translate.to_english": "Traduzir para Inglês",
            "translate.status": "Status da Tradução",
            "translate.help": "Traduza seu prompt para inglês para melhor aprimoramento com IA",
            
            # Prompt Builder
            "builder.title": "Construtor de Prompts",
            "builder.subtitle": "Combine prompts existentes para criar novos",
            "builder.available": "Prompts Disponíveis",
            "builder.selected": "Prompts Selecionados",
            "builder.preview": "Visualização",
            "builder.template": "Modelo de Combinação",
            "builder.template.sequential": "Sequencial",
            "builder.template.sequential.desc": "Combinar prompts um após o outro",
            "builder.template.sections": "Seções",
            "builder.template.sections.desc": "Combinar prompts como seções distintas",
            "builder.template.layered": "Em Camadas",
            "builder.template.layered.desc": "Construir contexto em camadas",
            "builder.template.custom": "Personalizado",
            "builder.template.custom.desc": "Usar modelo de formatação personalizado",
            "builder.combine": "Combinar Prompts",
            "builder.clear": "Limpar Seleção",
            "builder.edit": "Abrir no Editor",
            "builder.error.no_prompts": "Nenhum prompt selecionado",
            "builder.error.min_prompts": "Selecione pelo menos 2 prompts",
            "builder.error.duplicates": "Prompts duplicados encontrados",
            "builder.error.too_long": "Prompt combinado muito longo",
            "builder.error.combination": "Falha na combinação",
            "builder.preview.empty": "Selecione prompts para ver a visualização",
            "builder.preview.error": "Erro de visualização",
            "builder.drag.add": "Arraste aqui para adicionar",
            "builder.drag.reorder": "Arraste para reordenar",
            "builder.search.placeholder": "Buscar prompts...",
            "builder.filter.category": "Filtrar por categoria",
            "builder.filter.all": "Todas as Categorias",
        }
    
    def _get_russian_translations(self) -> Dict[str, str]:
        """Russian translations"""
        return {
            # Application
            "app.title": "Менеджер AI-промптов",
            "app.subtitle": "Безопасное мультитенантное управление AI-промптами",
            "app.status.authenticated": "✅ Аутентифицирован как {user}",
            "app.status.not_authenticated": "❌ Не аутентифицирован",
            
            # Navigation
            "nav.prompts": "Промпты",
            "nav.library": "Библиотека",
            "nav.tokens": "Токены",
            "nav.settings": "Настройки",
            "nav.admin": "Админ",
            
            # Authentication
            "auth.login": "Войти",
            "auth.logout": "Выйти",
            "auth.email": "Email",
            "auth.password": "Пароль",
            "auth.tenant": "Арендатор",
            "auth.sso": "Вход через SSO",
            "auth.welcome": "Добро пожаловать, {name}!",
            "auth.invalid": "Неверные учетные данные",
            
            # Prompts
            "prompt.name": "Имя",
            "prompt.title": "Заголовок",
            "prompt.category": "Категория",
            "prompt.content": "Содержание",
            "prompt.tags": "Теги",
            "prompt.add": "Добавить",
            "prompt.update": "Обновить",
            "prompt.delete": "Удалить",
            "prompt.clear": "Очистить",
            "prompt.load": "Загрузить",
            "prompt.search": "Поиск",
            "prompt.enhancement": "Промпт улучшения",
            
            # Actions
            "action.save": "Сохранить",
            "action.cancel": "Отмена",
            "action.refresh": "Обновить",
            "action.edit": "Редактировать",
            "action.view": "Просмотр",
            "action.copy": "Копировать",
            "action.export": "Экспорт",
            "action.import": "Импорт",
            
            # Status
            "status.success": "Успех",
            "status.error": "Ошибка",
            "status.loading": "Загрузка...",
            "status.saved": "Успешно сохранено",
            "status.deleted": "Успешно удалено",
            
            # Calculator
            "calc.title": "Калькулятор токенов",
            "calc.model": "Модель",
            "calc.tokens": "Токены",
            "calc.cost": "Стоимость",
            "calc.estimate": "Оценить",
            "calc.input": "Ввод",
            "calc.output": "Вывод",
            
            # Optimization
            "opt.title": "Оптимизация",
            "opt.context": "Контекст",
            "opt.target": "Целевая модель",
            "opt.optimize": "Оптимизировать",
            "opt.score": "Оценка",
            "opt.suggestions": "Предложения",
            "opt.accept": "Принять",
            "opt.reject": "Отклонить",
            "opt.retry": "Повторить",
            
            # Forms
            "form.required": "Обязательно",
            "form.optional": "Необязательно",
            "form.placeholder.name": "Введите имя",
            "form.placeholder.search": "Поиск...",
            "form.placeholder.email": "пользователь@домен.com",
            
            # Messages
            "msg.select_item": "Пожалуйста, выберите элемент",
            "msg.confirm_delete": "Вы уверены, что хотите удалить это?",
            "msg.no_results": "Результаты не найдены",
            "msg.loading_data": "Загрузка данных...",
            
            # Translation
            "translate.to_english": "Перевести на английский",
            "translate.status": "Статус перевода",
            "translate.help": "Переведите ваш промпт на английский для лучшего улучшения ИИ",
            
            # Prompt Builder
            "builder.title": "Конструктор Промптов",
            "builder.subtitle": "Объедините существующие промпты для создания новых",
            "builder.available": "Доступные Промпты",
            "builder.selected": "Выбранные Промпты",
            "builder.preview": "Предпросмотр",
            "builder.template": "Шаблон Комбинации",
            "builder.template.sequential": "Последовательный",
            "builder.template.sequential.desc": "Объединить промпты один за другим",
            "builder.template.sections": "Секции",
            "builder.template.sections.desc": "Объединить промпты как отдельные секции",
            "builder.template.layered": "Слоистый",
            "builder.template.layered.desc": "Строить контекст послойно",
            "builder.template.custom": "Пользовательский",
            "builder.template.custom.desc": "Использовать пользовательский шаблон форматирования",
            "builder.combine": "Объединить Промпты",
            "builder.clear": "Очистить Выбор",
            "builder.edit": "Открыть в Редакторе",
            "builder.error.no_prompts": "Промпты не выбраны",
            "builder.error.min_prompts": "Выберите как минимум 2 промпта",
            "builder.error.duplicates": "Найдены дублированные промпты",
            "builder.error.too_long": "Объединенный промпт слишком длинный",
            "builder.error.combination": "Объединение не удалось",
            "builder.preview.empty": "Выберите промпты для просмотра предпросмотра",
            "builder.preview.error": "Ошибка предпросмотра",
            "builder.drag.add": "Перетащите сюда для добавления",
            "builder.drag.reorder": "Перетащите для изменения порядка",
            "builder.search.placeholder": "Поиск промптов...",
            "builder.filter.category": "Фильтр по категории",
            "builder.filter.all": "Все Категории",
        }
    
    def _get_arabic_translations(self) -> Dict[str, str]:
        """Arabic translations"""
        return {
            # Application
            "app.title": "مدير الذكاء الاصطناعي",
            "app.subtitle": "إدارة آمنة ومتعددة المستأجرين للذكاء الاصطناعي",
            "app.status.authenticated": "✅ مصادق عليه كـ {user}",
            "app.status.not_authenticated": "❌ غير مصادق عليه",
            
            # Navigation
            "nav.prompts": "المطالبات",
            "nav.library": "المكتبة",
            "nav.tokens": "الرموز",
            "nav.settings": "الإعدادات",
            "nav.admin": "المدير",
            
            # Authentication
            "auth.login": "تسجيل الدخول",
            "auth.logout": "تسجيل الخروج",
            "auth.email": "البريد الإلكتروني",
            "auth.password": "كلمة المرور",
            "auth.tenant": "المستأجر",
            "auth.sso": "تسجيل دخول SSO",
            "auth.welcome": "مرحباً، {name}!",
            "auth.invalid": "بيانات اعتماد غير صحيحة",
            
            # Prompts
            "prompt.name": "الاسم",
            "prompt.title": "العنوان",
            "prompt.category": "الفئة",
            "prompt.content": "المحتوى",
            "prompt.tags": "العلامات",
            "prompt.add": "إضافة",
            "prompt.update": "تحديث",
            "prompt.delete": "حذف",
            "prompt.clear": "مسح",
            "prompt.load": "تحميل",
            "prompt.search": "بحث",
            "prompt.enhancement": "مطالبة التحسين",
            
            # Actions
            "action.save": "حفظ",
            "action.cancel": "إلغاء",
            "action.refresh": "تحديث",
            "action.edit": "تحرير",
            "action.view": "عرض",
            "action.copy": "نسخ",
            "action.export": "تصدير",
            "action.import": "استيراد",
            
            # Status
            "status.success": "نجح",
            "status.error": "خطأ",
            "status.loading": "جاري التحميل...",
            "status.saved": "تم الحفظ بنجاح",
            "status.deleted": "تم الحذف بنجاح",
            
            # Calculator
            "calc.title": "حاسبة الرموز",
            "calc.model": "النموذج",
            "calc.tokens": "الرموز",
            "calc.cost": "التكلفة",
            "calc.estimate": "تقدير",
            "calc.input": "الإدخال",
            "calc.output": "الإخراج",
            
            # Optimization
            "opt.title": "التحسين",
            "opt.context": "السياق",
            "opt.target": "النموذج المستهدف",
            "opt.optimize": "تحسين",
            "opt.score": "النتيجة",
            "opt.suggestions": "الاقتراحات",
            "opt.accept": "قبول",
            "opt.reject": "رفض",
            "opt.retry": "إعادة المحاولة",
            
            # Forms
            "form.required": "مطلوب",
            "form.optional": "اختياري",
            "form.placeholder.name": "أدخل الاسم",
            "form.placeholder.search": "بحث...",
            "form.placeholder.email": "المستخدم@النطاق.com",
            
            # Messages
            "msg.select_item": "يرجى تحديد عنصر",
            "msg.confirm_delete": "هل أنت متأكد من أنك تريد حذف هذا؟",
            "msg.no_results": "لم يتم العثور على نتائج",
            "msg.loading_data": "جاري تحميل البيانات...",
            
            # Translation
            "translate.to_english": "ترجمة إلى الإنجليزية",
            "translate.status": "حالة الترجمة",
            "translate.help": "ترجم موجهك إلى الإنجليزية للحصول على تحسين أفضل للذكاء الاصطناعي",
            
            # Prompt Builder
            "builder.title": "منشئ المطالبات",
            "builder.subtitle": "ادمج المطالبات الموجودة لإنشاء مطالبات جديدة",
            "builder.available": "المطالبات المتاحة",
            "builder.selected": "المطالبات المحددة",
            "builder.preview": "معاينة",
            "builder.template": "قالب الدمج",
            "builder.template.sequential": "تسلسلي",
            "builder.template.sequential.desc": "دمج المطالبات واحدة تلو الأخرى",
            "builder.template.sections": "أقسام",
            "builder.template.sections.desc": "دمج المطالبات كأقسام منفصلة",
            "builder.template.layered": "طبقات",
            "builder.template.layered.desc": "بناء السياق في طبقات",
            "builder.template.custom": "مخصص",
            "builder.template.custom.desc": "استخدام قالب تنسيق مخصص",
            "builder.combine": "دمج المطالبات",
            "builder.clear": "مسح التحديد",
            "builder.edit": "فتح في المحرر",
            "builder.error.no_prompts": "لا توجد مطالبات محددة",
            "builder.error.min_prompts": "حدد على الأقل مطالبتين",
            "builder.error.duplicates": "تم العثور على مطالبات مكررة",
            "builder.error.too_long": "المطالبة المدمجة طويلة جداً",
            "builder.error.combination": "فشل الدمج",
            "builder.preview.empty": "حدد المطالبات لرؤية المعاينة",
            "builder.preview.error": "خطأ في المعاينة",
            "builder.drag.add": "اسحب هنا للإضافة",
            "builder.drag.reorder": "اسحب لإعادة الترتيب",
            "builder.search.placeholder": "البحث في المطالبات...",
            "builder.filter.category": "تصفية حسب الفئة",
            "builder.filter.all": "جميع الفئات",
        }
    
    def _get_hindi_translations(self) -> Dict[str, str]:
        """Hindi translations"""
        return {
            # Application
            "app.title": "AI प्रॉम्प्ट मैनेजर",
            "app.subtitle": "सुरक्षित, मल्टी-टेनेंट AI प्रॉम्प्ट प्रबंधन",
            "app.status.authenticated": "✅ {user} के रूप में प्रमाणित",
            "app.status.not_authenticated": "❌ प्रमाणित नहीं",
            
            # Navigation
            "nav.prompts": "प्रॉम्प्ट्स",
            "nav.library": "लाइब्रेरी",
            "nav.tokens": "टोकन",
            "nav.settings": "सेटिंग्स",
            "nav.admin": "एडमिन",
            
            # Authentication
            "auth.login": "लॉगिन",
            "auth.logout": "लॉगआउट",
            "auth.email": "ईमेल",
            "auth.password": "पासवर्ड",
            "auth.tenant": "टेनेंट",
            "auth.sso": "SSO लॉगिन",
            "auth.welcome": "स्वागत है, {name}!",
            "auth.invalid": "अमान्य क्रेडेंशियल",
            
            # Prompts
            "prompt.name": "नाम",
            "prompt.title": "शीर्षक",
            "prompt.category": "श्रेणी",
            "prompt.content": "सामग्री",
            "prompt.tags": "टैग",
            "prompt.add": "जोड़ें",
            "prompt.update": "अपडेट",
            "prompt.delete": "हटाएं",
            "prompt.clear": "साफ करें",
            "prompt.load": "लोड करें",
            "prompt.search": "खोजें",
            "prompt.enhancement": "वृद्धि प्रॉम्प्ट",
            
            # Actions
            "action.save": "सेव करें",
            "action.cancel": "रद्द करें",
            "action.refresh": "रिफ्रेश",
            "action.edit": "संपादित करें",
            "action.view": "देखें",
            "action.copy": "कॉपी करें",
            "action.export": "निर्यात",
            "action.import": "आयात",
            
            # Status
            "status.success": "सफल",
            "status.error": "त्रुटि",
            "status.loading": "लोड हो रहा है...",
            "status.saved": "सफलतापूर्वक सेव किया गया",
            "status.deleted": "सफलतापूर्वक हटाया गया",
            
            # Calculator
            "calc.title": "टोकन कैलकुलेटर",
            "calc.model": "मॉडल",
            "calc.tokens": "टोकन",
            "calc.cost": "लागत",
            "calc.estimate": "अनुमान",
            "calc.input": "इनपुट",
            "calc.output": "आउटपुट",
            
            # Optimization
            "opt.title": "अनुकूलन",
            "opt.context": "संदर्भ",
            "opt.target": "लक्ष्य मॉडल",
            "opt.optimize": "अनुकूलित करें",
            "opt.score": "स्कोर",
            "opt.suggestions": "सुझाव",
            "opt.accept": "स्वीकार करें",
            "opt.reject": "अस्वीकार करें",
            "opt.retry": "पुनः प्रयास करें",
            
            # Forms
            "form.required": "आवश्यक",
            "form.optional": "वैकल्पिक",
            "form.placeholder.name": "नाम दर्ज करें",
            "form.placeholder.search": "खोजें...",
            "form.placeholder.email": "उपयोगकर्ता@डोमेन.com",
            
            # Messages
            "msg.select_item": "कृपया एक आइटम चुनें",
            "msg.confirm_delete": "क्या आप वाकई इसे हटाना चाहते हैं?",
            "msg.no_results": "कोई परिणाम नहीं मिला",
            "msg.loading_data": "डेटा लोड हो रहा है...",
            
            # Translation
            "translate.to_english": "अंग्रेजी में अनुवाद करें",
            "translate.status": "अनुवाद स्थिति",
            "translate.help": "बेहतर AI सुधार के लिए अपने प्रॉम्प्ट को अंग्रेजी में अनुवाद करें",
            
            # Prompt Builder
            "builder.title": "प्रॉम्प्ट बिल्डर",
            "builder.subtitle": "नए प्रॉम्प्ट बनाने के लिए मौजूदा प्रॉम्प्ट्स को जोड़ें",
            "builder.available": "उपलब्ध प्रॉम्प्ट्स",
            "builder.selected": "चुने गए प्रॉम्प्ट्स",
            "builder.preview": "पूर्वावलोकन",
            "builder.template": "संयोजन टेम्प्लेट",
            "builder.template.sequential": "क्रमिक",
            "builder.template.sequential.desc": "प्रॉम्प्ट्स को एक के बाद एक जोड़ें",
            "builder.template.sections": "खंड",
            "builder.template.sections.desc": "प्रॉम्प्ट्स को अलग खंडों के रूप में जोड़ें",
            "builder.template.layered": "परतदार",
            "builder.template.layered.desc": "परतों में संदर्भ बनाएं",
            "builder.template.custom": "कस्टम",
            "builder.template.custom.desc": "कस्टम फॉर्मेटिंग टेम्प्लेट का उपयोग करें",
            "builder.combine": "प्रॉम्प्ट्स को जोड़ें",
            "builder.clear": "चयन साफ़ करें",
            "builder.edit": "एडिटर में खोलें",
            "builder.error.no_prompts": "कोई प्रॉम्प्ट चुना नहीं गया",
            "builder.error.min_prompts": "कम से कम 2 प्रॉम्प्ट्स चुनें",
            "builder.error.duplicates": "डुप्लिकेट प्रॉम्प्ट्स मिले",
            "builder.error.too_long": "संयुक्त प्रॉम्प्ट बहुत लंबा है",
            "builder.error.combination": "संयोजन असफल",
            "builder.preview.empty": "पूर्वावलोकन देखने के लिए प्रॉम्प्ट्स चुनें",
            "builder.preview.error": "पूर्वावलोकन त्रुटि",
            "builder.drag.add": "जोड़ने के लिए यहाँ खींचें",
            "builder.drag.reorder": "पुनः क्रमबद्ध करने के लिए खींचें",
            "builder.search.placeholder": "प्रॉम्प्ट्स खोजें...",
            "builder.filter.category": "श्रेणी के अनुसार फ़िल्टर करें",
            "builder.filter.all": "सभी श्रेणियां",
        }

# Global i18n instance
i18n = I18nManager()

# Convenience function for templates
def t(key: str, **kwargs) -> str:
    """Shorthand for i18n.t()"""
    return i18n.t(key, **kwargs)