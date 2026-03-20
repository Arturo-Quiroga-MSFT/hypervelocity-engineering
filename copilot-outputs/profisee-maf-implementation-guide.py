"""
PROFISEE Multi-Agent MDM System - Microsoft Agent Framework Implementation

This module provides the core implementation for PROFISEE's Master Data Management
multi-agent system using Microsoft Agent Framework (MAF) and Azure AI services.

Author: Arturo Quiroga, Partner Solutions Architect
Partner: PROFISEE  
Date: March 2026
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Microsoft Agent Framework imports
from autogen import ConversableAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent

# Azure SDK imports  
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.ai.textanalytics import TextAnalyticsClient
import openai

# Configuration and logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models and Enums
# ============================================================================

class DataQualityScore(Enum):
    """Data quality assessment scores"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%  
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # 0-49%


class ProcessingStatus(Enum):
    """Record processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class DataRecord:
    """Master data record structure"""
    id: str
    entity_type: str  # customer, product, supplier, etc.
    source_system: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass  
class QualityAssessment:
    """Data quality assessment result"""
    record_id: str
    overall_score: float
    completeness_score: float  
    accuracy_score: float
    consistency_score: float
    validity_score: float
    issues: List[str]
    recommendations: List[str]
    assessment_timestamp: datetime


@dataclass
class ValidationResult:
    """Data validation result"""
    record_id: str
    is_valid: bool
    validation_errors: List[str]
    business_rule_violations: List[str]
    compliance_status: Dict[str, bool]
    confidence_score: float
    validation_timestamp: datetime


@dataclass
class EnrichmentResult:
    """Data enrichment result"""
    record_id: str
    original_data: Dict[str, Any]
    enriched_data: Dict[str, Any]
    enrichment_sources: List[str]
    confidence_scores: Dict[str, float]
    enrichment_timestamp: datetime


@dataclass
class ResolutionResult:
    """Data resolution and deduplication result"""  
    record_id: str
    master_record_id: str
    duplicate_records: List[str]
    merge_strategy: str
    confidence_score: float
    resolution_timestamp: datetime


@dataclass
class ProcessingResult:
    """Complete processing result"""
    record_id: str
    status: ProcessingStatus
    quality_assessment: Optional[QualityAssessment]
    validation_result: Optional[ValidationResult] 
    enrichment_result: Optional[EnrichmentResult]
    resolution_result: Optional[ResolutionResult]
    audit_trail: List[str]
    processing_time_ms: int


# ============================================================================
# Configuration Management
# ============================================================================

class ConfigurationManager:
    """Manages configuration from Azure Key Vault and environment variables"""
    
    def __init__(self, key_vault_url: Optional[str] = None):
        """Initialize configuration manager with optional Key Vault"""
        self.key_vault_url = key_vault_url
        self.credential = DefaultAzureCredential()
        self._secret_client = None
        
        if self.key_vault_url:
            self._secret_client = SecretClient(
                vault_url=self.key_vault_url,
                credential=self.credential
            )
        
        # Load configuration
        self.config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from Key Vault and environment variables"""
        config = {}
        
        # Azure OpenAI configuration
        config["azure_openai"] = {
            "api_base": self._get_secret_or_env("AZURE_OPENAI_ENDPOINT"),
            "api_key": self._get_secret_or_env("AZURE_OPENAI_API_KEY"),
            "api_version": "2024-02-01",
            "deployment_name": "gpt-4o-profisee",
            "embedding_deployment": "text-embedding-ada-002"
        }
        
        # Azure AI Search configuration
        config["azure_search"] = {
            "service_name": self._get_secret_or_env("AZURE_SEARCH_SERVICE_NAME"),
            "api_key": self._get_secret_or_env("AZURE_SEARCH_API_KEY"),
            "index_name": "master-data-entities"
        }
        
        # Azure Cosmos DB configuration  
        config["cosmos_db"] = {
            "endpoint": self._get_secret_or_env("COSMOS_DB_ENDPOINT"),
            "key": self._get_secret_or_env("COSMOS_DB_KEY"),
            "database_name": "ProfiseeMDM",
            "containers": {
                "entities": "MasterEntities",
                "relationships": "EntityRelationships",
                "audit": "AuditTrail"
            }
        }
        
        # Azure Text Analytics configuration
        config["text_analytics"] = {
            "endpoint": self._get_secret_or_env("TEXT_ANALYTICS_ENDPOINT"),
            "key": self._get_secret_or_env("TEXT_ANALYTICS_API_KEY")
        }
        
        return config
    
    def _get_secret_or_env(self, key: str) -> str:
        """Get value from Key Vault or environment variable"""
        # Try environment variable first
        value = os.getenv(key)
        if value:
            return value
            
        # Try Key Vault if available
        if self._secret_client:
            try:
                secret = self._secret_client.get_secret(key.replace("_", "-").lower())
                return secret.value
            except Exception as e:
                logger.warning(f"Could not retrieve secret {key} from Key Vault: {e}")
        
        raise ValueError(f"Configuration value {key} not found in environment or Key Vault")


# ============================================================================
# Azure Service Clients
# ============================================================================

class AzureServiceManager:
    """Manages connections to Azure services"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Azure service clients"""
        self.config = config
        self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self._cosmos_client = None
        self._search_client = None
        self._blob_client = None
        self._text_analytics_client = None
        
        # Configure OpenAI
        openai.api_type = "azure"
        openai.api_base = config["azure_openai"]["api_base"]
        openai.api_key = config["azure_openai"]["api_key"]
        openai.api_version = config["azure_openai"]["api_version"]
    
    @property
    def cosmos_client(self) -> CosmosClient:
        """Get Cosmos DB client (lazy initialization)"""
        if not self._cosmos_client:
            self._cosmos_client = CosmosClient(
                self.config["cosmos_db"]["endpoint"],
                credential=self.config["cosmos_db"]["key"]
            )
        return self._cosmos_client
    
    @property  
    def search_client(self) -> SearchClient:
        """Get Azure AI Search client (lazy initialization)"""
        if not self._search_client:
            from azure.core.credentials import AzureKeyCredential
            credential = AzureKeyCredential(self.config["azure_search"]["api_key"])
            
            self._search_client = SearchClient(
                endpoint=f"https://{self.config['azure_search']['service_name']}.search.windows.net",
                index_name=self.config["azure_search"]["index_name"],
                credential=credential
            )
        return self._search_client
    
    @property
    def text_analytics_client(self) -> TextAnalyticsClient:
        """Get Text Analytics client (lazy initialization)"""
        if not self._text_analytics_client:
            from azure.core.credentials import AzureKeyCredential
            credential = AzureKeyCredential(self.config["text_analytics"]["key"])
            
            self._text_analytics_client = TextAnalyticsClient(
                endpoint=self.config["text_analytics"]["endpoint"],
                credential=credential
            )
        return self._text_analytics_client


# ============================================================================
# MAF Agent Implementations  
# ============================================================================

class DataQualityAgent(ConversableAgent):
    """Agent specialized in data quality assessment for MDM"""
    
    def __init__(self, azure_manager: AzureServiceManager):
        """Initialize Data Quality Agent"""
        
        system_message = """You are a Master Data Management data quality specialist. Your role is to:

1. Analyze data records for completeness, accuracy, consistency, and validity
2. Identify data quality issues and assign severity levels
3. Provide actionable recommendations for data improvement  
4. Calculate comprehensive quality scores with detailed breakdowns

Focus on MDM-specific quality dimensions:
- Entity completeness (required fields populated)
- Data accuracy (format compliance, valid values)
- Cross-system consistency (same entity, different sources)
- Business rule compliance (MDM governance rules)
- Temporal consistency (data freshness, versioning)

Always provide structured output with specific quality scores and remediation steps."""

        super().__init__(
            name="DataQualityAgent",
            system_message=system_message,
            llm_config={
                "config_list": [{
                    "model": azure_manager.config["azure_openai"]["deployment_name"],
                    "api_base": azure_manager.config["azure_openai"]["api_base"],
                    "api_key": azure_manager.config["azure_openai"]["api_key"], 
                    "api_version": azure_manager.config["azure_openai"]["api_version"],
                    "api_type": "azure"
                }],
                "temperature": 0.1
            }
        )
        
        self.azure_manager = azure_manager
    
    async def assess_quality(self, record: DataRecord) -> QualityAssessment:
        """Perform comprehensive data quality assessment"""
        
        # Prepare analysis prompt
        analysis_prompt = f"""
        Analyze this MDM record for data quality:
        
        Entity Type: {record.entity_type}
        Source System: {record.source_system}  
        Data: {json.dumps(record.data, indent=2)}
        
        Provide assessment in this JSON format:
        {{
            "overall_score": 0.85,
            "completeness_score": 0.90,
            "accuracy_score": 0.88,
            "consistency_score": 0.82,
            "validity_score": 0.91,
            "issues": ["Missing middle_name field", "Phone format inconsistent"],
            "recommendations": ["Add middle_name validation", "Standardize phone format"]
        }}
        """
        
        # Get AI assessment
        response = await self.a_send(analysis_prompt, recipient=self, request_reply=True)
        
        try:
            # Parse structured response
            result_data = json.loads(response.content)
            
            return QualityAssessment(
                record_id=record.id,
                overall_score=result_data["overall_score"],
                completeness_score=result_data["completeness_score"],
                accuracy_score=result_data["accuracy_score"], 
                consistency_score=result_data["consistency_score"],
                validity_score=result_data["validity_score"],
                issues=result_data["issues"],
                recommendations=result_data["recommendations"],
                assessment_timestamp=datetime.now(timezone.utc)
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse quality assessment response: {e}")
            # Return default low-quality assessment
            return QualityAssessment(
                record_id=record.id,
                overall_score=0.0,
                completeness_score=0.0,
                accuracy_score=0.0,
                consistency_score=0.0, 
                validity_score=0.0,
                issues=["Assessment parsing failed"],
                recommendations=["Manual review required"],
                assessment_timestamp=datetime.now(timezone.utc)
            )


class DataValidationAgent(ConversableAgent):
    """Agent specialized in data validation against business rules and schemas"""
    
    def __init__(self, azure_manager: AzureServiceManager):
        """Initialize Data Validation Agent"""
        
        system_message = """You are a Master Data Management validation specialist. Your role is to:

1. Validate data records against defined schemas and business rules
2. Check compliance with regulatory requirements (GDPR, CCPA, industry standards)
3. Perform cross-reference validation with authoritative sources
4. Assign confidence scores to validation results

Focus on MDM-specific validation:
- Schema compliance (data types, constraints, required fields)  
- Business rule enforcement (custom validation logic)
- Referential integrity (relationships between entities)
- Regulatory compliance (data protection, industry regulations)
- Cross-system validation (consistency across source systems)

Always provide detailed validation results with specific error descriptions and remediation guidance."""

        super().__init__(
            name="DataValidationAgent",
            system_message=system_message,
            llm_config={
                "config_list": [{
                    "model": azure_manager.config["azure_openai"]["deployment_name"],
                    "api_base": azure_manager.config["azure_openai"]["api_base"],
                    "api_key": azure_manager.config["azure_openai"]["api_key"],
                    "api_version": azure_manager.config["azure_openai"]["api_version"],
                    "api_type": "azure"
                }],
                "temperature": 0.0  # Deterministic validation
            }
        )
        
        self.azure_manager = azure_manager
    
    async def validate_record(self, record: DataRecord) -> ValidationResult:
        """Perform comprehensive record validation"""
        
        # Use Text Analytics for PII detection
        pii_results = await self._detect_pii(record.data)
        
        # Prepare validation prompt
        validation_prompt = f"""
        Validate this MDM record against business rules:
        
        Entity Type: {record.entity_type}
        Source System: {record.source_system}
        Data: {json.dumps(record.data, indent=2)}
        PII Detected: {pii_results}
        
        Apply these validation rules:
        1. Required fields present and non-null
        2. Data formats match expected patterns (email, phone, etc.)
        3. Value ranges within acceptable limits  
        4. Cross-field consistency (e.g., birth_date vs age)
        5. Business logic compliance
        6. GDPR compliance for PII handling
        
        Provide validation result in this JSON format:
        {{
            "is_valid": true,
            "validation_errors": [],
            "business_rule_violations": [],
            "compliance_status": {{"gdpr": true, "ccpa": true}},
            "confidence_score": 0.95
        }}
        """
        
        response = await self.a_send(validation_prompt, recipient=self, request_reply=True)
        
        try:
            result_data = json.loads(response.content)
            
            return ValidationResult(
                record_id=record.id,
                is_valid=result_data["is_valid"],
                validation_errors=result_data["validation_errors"],
                business_rule_violations=result_data["business_rule_violations"],
                compliance_status=result_data["compliance_status"],
                confidence_score=result_data["confidence_score"],
                validation_timestamp=datetime.now(timezone.utc)
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse validation response: {e}")
            return ValidationResult(
                record_id=record.id,
                is_valid=False,
                validation_errors=["Validation parsing failed"],
                business_rule_violations=[],
                compliance_status={"gdpr": False, "ccpa": False},
                confidence_score=0.0,
                validation_timestamp=datetime.now(timezone.utc)
            )
    
    async def _detect_pii(self, data: Dict[str, Any]) -> List[str]:
        """Detect PII in record data using Azure Text Analytics"""
        try:
            text_to_analyze = json.dumps(data)
            
            response = self.azure_manager.text_analytics_client.recognize_pii_entities(
                documents=[text_to_analyze],
                language="en"
            )
            
            pii_entities = []
            for doc in response:
                for entity in doc.entities:
                    pii_entities.append(f"{entity.category}: {entity.text}")
            
            return pii_entities
            
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return ["PII detection unavailable"]


class DataEnrichmentAgent(ConversableAgent):
    """Agent specialized in data enrichment and missing information inference"""
    
    def __init__(self, azure_manager: AzureServiceManager):
        """Initialize Data Enrichment Agent"""
        
        system_message = """You are a Master Data Management enrichment specialist. Your role is to:

1. Identify missing or incomplete data fields in master records
2. Infer missing information from available context and patterns
3. Enhance records with additional relevant information
4. Provide confidence scores for enriched data

Focus on MDM-specific enrichment:
- Missing field inference based on existing data patterns
- Hierarchical data completion (parent-child relationships)  
- Standardization of data formats and values
- Geographic and demographic inference
- Industry and classification code assignment

Always provide enrichment results with confidence scores and data sources."""

        super().__init__(
            name="DataEnrichmentAgent", 
            system_message=system_message,
            llm_config={
                "config_list": [{
                    "model": azure_manager.config["azure_openai"]["deployment_name"],
                    "api_base": azure_manager.config["azure_openai"]["api_base"], 
                    "api_key": azure_manager.config["azure_openai"]["api_key"],
                    "api_version": azure_manager.config["azure_openai"]["api_version"],
                    "api_type": "azure"
                }],
                "temperature": 0.2  # Some creativity for inference
            }
        )
        
        self.azure_manager = azure_manager
    
    async def enrich_record(self, record: DataRecord) -> EnrichmentResult:
        """Perform data enrichment on the record"""
        
        # Search for similar records for context
        similar_records = await self._find_similar_records(record)
        
        enrichment_prompt = f"""
        Enrich this MDM record with missing information:
        
        Current Record:
        Entity Type: {record.entity_type}
        Data: {json.dumps(record.data, indent=2)}
        
        Similar Records (for context):
        {json.dumps(similar_records[:3], indent=2)}
        
        Enrichment tasks:
        1. Fill missing standard fields based on patterns
        2. Standardize formats (phone, address, etc.)
        3. Infer classification codes or categories
        4. Add geographic information if location data present
        5. Calculate derived fields (full_name, age, etc.)
        
        Provide enrichment result in JSON format:
        {{
            "enriched_data": {{"field_name": "new_value"}},
            "enrichment_sources": ["pattern_inference", "similar_records"],
            "confidence_scores": {{"field_name": 0.85}}
        }}
        """
        
        response = await self.a_send(enrichment_prompt, recipient=self, request_reply=True)
        
        try:
            result_data = json.loads(response.content)
            
            # Merge original data with enrichments
            enriched_data = {**record.data, **result_data["enriched_data"]}
            
            return EnrichmentResult(
                record_id=record.id,
                original_data=record.data,
                enriched_data=enriched_data,
                enrichment_sources=result_data["enrichment_sources"],
                confidence_scores=result_data["confidence_scores"],
                enrichment_timestamp=datetime.now(timezone.utc)
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse enrichment response: {e}")
            return EnrichmentResult(
                record_id=record.id,
                original_data=record.data,
                enriched_data=record.data,  # No changes
                enrichment_sources=["enrichment_failed"],
                confidence_scores={},
                enrichment_timestamp=datetime.now(timezone.utc)
            )
    
    async def _find_similar_records(self, record: DataRecord) -> List[Dict[str, Any]]:
        """Find similar records using vector search"""
        try:
            # Create search query from record data
            search_text = " ".join(str(v) for v in record.data.values() if v)
            
            results = self.azure_manager.search_client.search(
                search_text=search_text,
                top=5,
                search_fields=["content"],
                select=["id", "entity_type", "data"]
            )
            
            similar_records = []
            for result in results:
                similar_records.append({
                    "id": result["id"],
                    "entity_type": result["entity_type"], 
                    "data": result["data"]
                })
            
            return similar_records
            
        except Exception as e:
            logger.error(f"Similar record search failed: {e}")
            return []


class DataResolutionAgent(ConversableAgent):
    """Agent specialized in duplicate detection and entity resolution"""
    
    def __init__(self, azure_manager: AzureServiceManager):
        """Initialize Data Resolution Agent"""
        
        system_message = """You are a Master Data Management resolution specialist. Your role is to:

1. Detect duplicate entities across different sources and systems
2. Calculate similarity scores between entities  
3. Resolve conflicts between duplicate records
4. Apply survivorship rules to create master records
5. Maintain data lineage and audit trails

Focus on MDM-specific resolution:
- Cross-system duplicate detection
- Fuzzy matching algorithms for entity similarity
- Survivorship rule application (most recent, most complete, most trusted source)
- Relationship preservation during merges
- Audit trail generation for all resolution activities

Always provide resolution results with confidence scores and detailed merge rationale."""

        super().__init__(
            name="DataResolutionAgent",
            system_message=system_message, 
            llm_config={
                "config_list": [{
                    "model": azure_manager.config["azure_openai"]["deployment_name"],
                    "api_base": azure_manager.config["azure_openai"]["api_base"],
                    "api_key": azure_manager.config["azure_openai"]["api_key"],
                    "api_version": azure_manager.config["azure_openai"]["api_version"],
                    "api_type": "azure"
                }],
                "temperature": 0.1
            }
        )
        
        self.azure_manager = azure_manager
    
    async def resolve_duplicates(self, record: DataRecord) -> ResolutionResult:
        """Detect and resolve duplicate entities"""
        
        # Find potential duplicates using vector search
        duplicates = await self._find_duplicate_candidates(record)
        
        if not duplicates:
            # No duplicates found - record is unique
            return ResolutionResult(
                record_id=record.id,
                master_record_id=record.id,
                duplicate_records=[],
                merge_strategy="no_duplicates",
                confidence_score=1.0,
                resolution_timestamp=datetime.now(timezone.utc)
            )
        
        resolution_prompt = f"""
        Analyze these records for duplicate entity detection and resolution:
        
        Primary Record: 
        {json.dumps(record.data, indent=2)}
        
        Potential Duplicates:
        {json.dumps([d["data"] for d in duplicates], indent=2)}
        
        Tasks:
        1. Calculate similarity scores between primary and each candidate
        2. Identify true duplicates (similarity > 0.8)
        3. Apply survivorship rules to create master record:
           - Most complete data wins
           - Most recent timestamp wins  
           - Trusted source systems prioritized
        4. Provide merge strategy and confidence score
        
        Respond in JSON format:
        {{
            "duplicate_records": ["id1", "id2"],
            "merge_strategy": "most_complete_wins",
            "confidence_score": 0.92,
            "master_record_data": {{"merged": "data"}}
        }}
        """
        
        response = await self.a_send(resolution_prompt, recipient=self, request_reply=True)
        
        try:
            result_data = json.loads(response.content)
            
            return ResolutionResult(
                record_id=record.id,
                master_record_id=record.id,  # Assuming primary becomes master
                duplicate_records=result_data["duplicate_records"],
                merge_strategy=result_data["merge_strategy"],
                confidence_score=result_data["confidence_score"],
                resolution_timestamp=datetime.now(timezone.utc)
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse resolution response: {e}")
            return ResolutionResult(
                record_id=record.id,
                master_record_id=record.id,
                duplicate_records=[],
                merge_strategy="resolution_failed",
                confidence_score=0.0,
                resolution_timestamp=datetime.now(timezone.utc)
            )
    
    async def _find_duplicate_candidates(self, record: DataRecord) -> List[Dict[str, Any]]:
        """Find potential duplicate records using hybrid search"""
        try:
            # Combine key fields for search
            key_fields = []
            if "name" in record.data:
                key_fields.append(record.data["name"])
            if "email" in record.data:
                key_fields.append(record.data["email"])
            if "phone" in record.data:
                key_fields.append(record.data["phone"])
            
            search_text = " ".join(str(field) for field in key_fields if field)
            
            results = self.azure_manager.search_client.search(
                search_text=search_text,
                top=10,
                search_fields=["content"],
                select=["id", "entity_type", "data", "source_system"],
                filter=f"entity_type eq '{record.entity_type}' and id ne '{record.id}'"
            )
            
            candidates = []
            for result in results:
                candidates.append({
                    "id": result["id"],
                    "entity_type": result["entity_type"],
                    "data": result["data"],
                    "source_system": result["source_system"]
                })
            
            return candidates
            
        except Exception as e:
            logger.error(f"Duplicate candidate search failed: {e}")
            return []


class DataGovernanceAgent(ConversableAgent):
    """Agent specialized in data governance, compliance, and audit trail management"""
    
    def __init__(self, azure_manager: AzureServiceManager):
        """Initialize Data Governance Agent"""
        
        system_message = """You are a Master Data Management governance specialist. Your role is to:

1. Ensure compliance with data governance policies and regulations
2. Generate comprehensive audit trails for all data operations  
3. Monitor data stewardship activities and workflows
4. Manage data lineage and impact analysis
5. Generate governance reports and compliance documentation

Focus on MDM-specific governance:
- Data lineage tracking across all transformations
- Policy compliance monitoring (retention, access, quality)
- Stewardship workflow management and escalation
- Regulatory compliance reporting (GDPR, CCPA, SOX)
- Data classification and sensitivity management

Always provide detailed governance results with full audit trails and compliance status."""

        super().__init__(
            name="DataGovernanceAgent",
            system_message=system_message,
            llm_config={
                "config_list": [{
                    "model": azure_manager.config["azure_openai"]["deployment_name"],
                    "api_base": azure_manager.config["azure_openai"]["api_base"],
                    "api_key": azure_manager.config["azure_openai"]["api_key"],
                    "api_version": azure_manager.config["azure_openai"]["api_version"], 
                    "api_type": "azure"
                }],
                "temperature": 0.0  # Deterministic governance
            }
        )
        
        self.azure_manager = azure_manager
    
    async def create_audit_trail(self, processing_result: ProcessingResult) -> str:
        """Create comprehensive audit trail for processing results"""
        
        audit_prompt = f"""
        Create a comprehensive audit trail for this MDM processing operation:
        
        Record ID: {processing_result.record_id}
        Status: {processing_result.status.value}
        Processing Time: {processing_result.processing_time_ms}ms
        
        Quality Assessment: {processing_result.quality_assessment}
        Validation Result: {processing_result.validation_result}
        Enrichment Result: {processing_result.enrichment_result}  
        Resolution Result: {processing_result.resolution_result}
        
        Generate audit trail including:
        1. Detailed operation log with timestamps
        2. Data lineage information
        3. Compliance verification results
        4. Risk assessment and recommendations
        5. Stewardship notifications if needed
        
        Respond with structured audit trail in JSON format.
        """
        
        response = await self.a_send(audit_prompt, recipient=self, request_reply=True)
        
        # Store audit trail in Cosmos DB
        audit_id = await self._store_audit_trail(processing_result, response.content)
        
        return audit_id
    
    async def _store_audit_trail(self, processing_result: ProcessingResult, audit_content: str) -> str:
        """Store audit trail in Cosmos DB"""
        try:
            database = self.azure_manager.cosmos_client.get_database_client(
                self.azure_manager.config["cosmos_db"]["database_name"]
            )
            container = database.get_container_client(
                self.azure_manager.config["cosmos_db"]["containers"]["audit"]
            )
            
            audit_record = {
                "id": f"audit_{processing_result.record_id}_{datetime.now(timezone.utc).isoformat()}",
                "record_id": processing_result.record_id,
                "processing_status": processing_result.status.value,
                "processing_time_ms": processing_result.processing_time_ms,
                "audit_content": audit_content,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "partition_key": processing_result.record_id
            }
            
            container.create_item(audit_record)
            return audit_record["id"]
            
        except Exception as e:
            logger.error(f"Failed to store audit trail: {e}")
            return f"audit_error_{processing_result.record_id}"


# ============================================================================
# Multi-Agent Orchestrator
# ============================================================================

class MDMAgentOrchestrator:
    """Orchestrates the multi-agent MDM processing workflow"""
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize orchestrator with all agents"""
        self.config_manager = config_manager
        self.azure_manager = AzureServiceManager(config_manager.config)
        
        # Initialize agents
        self.quality_agent = DataQualityAgent(self.azure_manager)
        self.validation_agent = DataValidationAgent(self.azure_manager)
        self.enrichment_agent = DataEnrichmentAgent(self.azure_manager)
        self.resolution_agent = DataResolutionAgent(self.azure_manager)
        self.governance_agent = DataGovernanceAgent(self.azure_manager)
        
        logger.info("MDM Agent Orchestrator initialized successfully")
    
    async def process_record(self, record: DataRecord) -> ProcessingResult:
        """Process a single data record through the complete MDM pipeline"""
        
        start_time = datetime.now()
        audit_trail = [f"Processing started at {start_time.isoformat()}"]
        
        try:
            # Step 1: Data Quality Assessment
            logger.info(f"Starting quality assessment for record {record.id}")
            quality_assessment = await self.quality_agent.assess_quality(record)
            audit_trail.append(f"Quality assessment completed: {quality_assessment.overall_score}")
            
            # Decision: Only proceed if quality is acceptable
            if quality_assessment.overall_score < 0.5:
                return ProcessingResult(
                    record_id=record.id,
                    status=ProcessingStatus.REJECTED,
                    quality_assessment=quality_assessment,
                    validation_result=None,
                    enrichment_result=None,
                    resolution_result=None,
                    audit_trail=audit_trail,
                    processing_time_ms=self._calculate_processing_time(start_time)
                )
            
            # Step 2: Data Validation  
            logger.info(f"Starting validation for record {record.id}")
            validation_result = await self.validation_agent.validate_record(record)
            audit_trail.append(f"Validation completed: {validation_result.is_valid}")
            
            # Decision: Only proceed if validation passes
            if not validation_result.is_valid:
                return ProcessingResult(
                    record_id=record.id,
                    status=ProcessingStatus.FAILED,
                    quality_assessment=quality_assessment,
                    validation_result=validation_result,
                    enrichment_result=None,
                    resolution_result=None,
                    audit_trail=audit_trail,
                    processing_time_ms=self._calculate_processing_time(start_time)
                )
            
            # Step 3: Data Enrichment
            logger.info(f"Starting enrichment for record {record.id}")
            enrichment_result = await self.enrichment_agent.enrich_record(record)
            audit_trail.append(f"Enrichment completed: {len(enrichment_result.enrichment_sources)} sources")
            
            # Update record with enriched data
            enriched_record = DataRecord(
                id=record.id,
                entity_type=record.entity_type,
                source_system=record.source_system,
                data=enrichment_result.enriched_data,
                metadata=record.metadata,
                created_at=record.created_at,
                updated_at=datetime.now(timezone.utc),
                version=record.version + 1
            )
            
            # Step 4: Duplicate Resolution
            logger.info(f"Starting resolution for record {record.id}")
            resolution_result = await self.resolution_agent.resolve_duplicates(enriched_record)
            audit_trail.append(f"Resolution completed: {len(resolution_result.duplicate_records)} duplicates")
            
            # Step 5: Create final result
            processing_result = ProcessingResult(
                record_id=record.id,
                status=ProcessingStatus.COMPLETED,
                quality_assessment=quality_assessment,
                validation_result=validation_result,
                enrichment_result=enrichment_result,
                resolution_result=resolution_result,
                audit_trail=audit_trail,
                processing_time_ms=self._calculate_processing_time(start_time)
            )
            
            # Step 6: Governance and Audit Trail
            logger.info(f"Creating audit trail for record {record.id}")
            audit_id = await self.governance_agent.create_audit_trail(processing_result)
            audit_trail.append(f"Audit trail created: {audit_id}")
            
            logger.info(f"Successfully processed record {record.id} in {processing_result.processing_time_ms}ms")
            return processing_result
            
        except Exception as e:
            logger.error(f"Error processing record {record.id}: {e}")
            audit_trail.append(f"Processing error: {str(e)}")
            
            return ProcessingResult(
                record_id=record.id,
                status=ProcessingStatus.FAILED,
                quality_assessment=None,
                validation_result=None,
                enrichment_result=None,
                resolution_result=None,
                audit_trail=audit_trail,
                processing_time_ms=self._calculate_processing_time(start_time)
            )
    
    async def process_batch(self, records: List[DataRecord]) -> List[ProcessingResult]:
        """Process multiple records concurrently"""
        
        logger.info(f"Starting batch processing of {len(records)} records")
        
        # Process records concurrently
        tasks = [self.process_record(record) for record in records]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception processing record {records[i].id}: {result}")
                final_results.append(ProcessingResult(
                    record_id=records[i].id,
                    status=ProcessingStatus.FAILED,
                    quality_assessment=None,
                    validation_result=None,
                    enrichment_result=None,
                    resolution_result=None,
                    audit_trail=[f"Exception: {str(result)}"],
                    processing_time_ms=0
                ))
            else:
                final_results.append(result)
        
        logger.info(f"Batch processing completed: {len(final_results)} records processed")
        return final_results
    
    def _calculate_processing_time(self, start_time: datetime) -> int:
        """Calculate processing time in milliseconds"""
        end_time = datetime.now()
        delta = end_time - start_time
        return int(delta.total_seconds() * 1000)


# ============================================================================
# Example Usage and Testing
# ============================================================================

async def main():
    """Example usage of the PROFISEE MDM multi-agent system"""
    
    # Initialize configuration (assumes environment variables or Key Vault setup)
    config_manager = ConfigurationManager(
        key_vault_url=os.getenv("AZURE_KEY_VAULT_URL")
    )
    
    # Initialize orchestrator
    orchestrator = MDMAgentOrchestrator(config_manager)
    
    # Example customer record
    sample_record = DataRecord(
        id="customer_12345",
        entity_type="customer",
        source_system="salesforce",
        data={
            "first_name": "John",
            "last_name": "Smith", 
            "email": "john.smith@example.com",
            "phone": "555-123-4567",
            "address": "123 Main St",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101"
        },
        metadata={
            "source_confidence": 0.9,
            "last_updated": "2026-03-20T10:00:00Z"
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        version=1
    )
    
    # Process single record
    logger.info("Processing sample customer record...")
    result = await orchestrator.process_record(sample_record)
    
    logger.info(f"Processing completed with status: {result.status.value}")
    logger.info(f"Quality score: {result.quality_assessment.overall_score if result.quality_assessment else 'N/A'}")
    logger.info(f"Processing time: {result.processing_time_ms}ms")
    
    # Example batch processing
    batch_records = [sample_record]  # In real scenario, load from source systems
    batch_results = await orchestrator.process_batch(batch_records)
    
    logger.info(f"Batch processing completed: {len(batch_results)} results")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())