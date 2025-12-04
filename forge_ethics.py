#!/usr/bin/env python3
"""
THE FORGE AI - Ethics and Safety Module
=========================================

Implements ethical safeguards for "ChatGPT 2.0" including:
- Content filtering and moderation
- Bias detection and mitigation
- Privacy protection
- Usage monitoring
- Compliance checking
- Transparency logging

This module ensures responsible AI behavior.
"""

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware way"""
    return datetime.now(timezone.utc)


class ContentCategory(Enum):
    """Categories of potentially sensitive content"""
    SAFE = "safe"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    ADULT_CONTENT = "adult_content"
    MISINFORMATION = "misinformation"
    PERSONAL_INFO = "personal_info"
    MALICIOUS_CODE = "malicious_code"
    SELF_HARM = "self_harm"
    ILLEGAL = "illegal"


class RiskLevel(Enum):
    """Risk level classification"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Action(Enum):
    """Actions to take on flagged content"""
    ALLOW = "allow"
    WARN = "warn"
    MODIFY = "modify"
    BLOCK = "block"
    ESCALATE = "escalate"


@dataclass
class ContentAnalysis:
    """Result of content safety analysis"""
    is_safe: bool
    categories: List[ContentCategory]
    risk_level: RiskLevel
    action: Action
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "categories": [c.value for c in self.categories],
            "risk_level": self.risk_level.value,
            "action": self.action.value,
            "details": self.details,
            "suggestions": self.suggestions
        }


@dataclass
class BiasAnalysis:
    """Result of bias detection analysis"""
    has_bias: bool
    bias_types: List[str]
    confidence: float
    affected_groups: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PrivacyAnalysis:
    """Result of privacy protection analysis"""
    has_pii: bool
    pii_types: List[str]
    risk_level: RiskLevel
    redacted_content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_pii": self.has_pii,
            "pii_types": self.pii_types,
            "risk_level": self.risk_level.value,
            "redacted_content": self.redacted_content
        }


@dataclass
class AuditLogEntry:
    """Audit log entry for transparency"""
    entry_id: str
    timestamp: str
    action: str
    user_id: Optional[str]
    content_type: str
    risk_level: str
    decision: str
    details: Dict[str, Any] = field(default_factory=dict)


class ContentModerator:
    """
    Content moderation and filtering
    
    Analyzes content for safety and compliance.
    """
    
    # Pattern categories for detection
    # NOTE: These are simplified patterns for demonstration.
    # Production systems should use more sophisticated NLP.
    PATTERNS: Dict[ContentCategory, List[str]] = {
        ContentCategory.VIOLENCE: [
            r'\b(kill|murder|attack|bomb|weapon)\b',
        ],
        ContentCategory.HATE_SPEECH: [
            r'\b(hate|racist|bigot)\b',
        ],
        ContentCategory.PERSONAL_INFO: [
            r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',  # SSN-like
            r'\b\d{16}\b',  # Credit card-like
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        ],
        ContentCategory.MALICIOUS_CODE: [
            r'\b(eval|exec|__import__|subprocess)\s*\(',
            r'\brm\s+-rf\b',
            r'\bsudo\s+rm\b',
        ],
    }
    
    def __init__(self, strict_mode: bool = False):
        """Initialize content moderator"""
        self.strict_mode = strict_mode
        self.blocked_terms: Set[str] = set()
        self.warned_terms: Set[str] = set()
    
    def analyze(self, content: str) -> ContentAnalysis:
        """
        Analyze content for safety issues
        
        Args:
            content: The content to analyze
            
        Returns:
            ContentAnalysis with results
        """
        categories = []
        details = {}
        suggestions = []
        
        content_lower = content.lower()
        
        # Check each category
        for category, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    categories.append(category)
                    if category not in details:
                        details[category.value] = []
                    details[category.value].append(f"Pattern match: {pattern}")
                    break
        
        # Check blocked terms
        for term in self.blocked_terms:
            if term.lower() in content_lower:
                categories.append(ContentCategory.ILLEGAL)
                details["blocked_term"] = term
        
        # Determine risk level
        if ContentCategory.MALICIOUS_CODE in categories:
            risk_level = RiskLevel.CRITICAL
        elif ContentCategory.VIOLENCE in categories or ContentCategory.HATE_SPEECH in categories:
            risk_level = RiskLevel.HIGH
        elif ContentCategory.PERSONAL_INFO in categories:
            risk_level = RiskLevel.MEDIUM
        elif categories:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.NONE
        
        # Determine action
        if risk_level == RiskLevel.CRITICAL:
            action = Action.BLOCK
            suggestions.append("Content contains potentially malicious elements")
        elif risk_level == RiskLevel.HIGH:
            action = Action.BLOCK if self.strict_mode else Action.WARN
            suggestions.append("Content may violate community guidelines")
        elif risk_level == RiskLevel.MEDIUM:
            action = Action.WARN
            suggestions.append("Consider reviewing content for sensitive information")
        else:
            action = Action.ALLOW
        
        is_safe = risk_level in (RiskLevel.NONE, RiskLevel.LOW)
        
        return ContentAnalysis(
            is_safe=is_safe,
            categories=categories if categories else [ContentCategory.SAFE],
            risk_level=risk_level,
            action=action,
            details=details,
            suggestions=suggestions
        )
    
    def add_blocked_term(self, term: str):
        """Add a term to the blocklist"""
        self.blocked_terms.add(term.lower())
    
    def remove_blocked_term(self, term: str):
        """Remove a term from the blocklist"""
        self.blocked_terms.discard(term.lower())


class BiasDetector:
    """
    Bias detection and mitigation
    
    Identifies potential biases in AI-generated content.
    """
    
    # Simplified bias indicators
    BIAS_INDICATORS: Dict[str, List[str]] = {
        "gender": [
            r'\b(he|she|him|her)\s+(?:always|never)\b',
            r'\b(men|women)\s+(?:can\'t|cannot|shouldn\'t)\b',
        ],
        "age": [
            r'\b(old|young)\s+(?:people|person)\s+(?:can\'t|cannot)\b',
        ],
        "cultural": [
            r'\ball\s+\w+\s+(?:are|always)\b',
        ],
        "professional": [
            r'\b(?:only|real)\s+(?:experts|professionals)\b',
        ],
    }
    
    def __init__(self):
        """Initialize bias detector"""
        self.detection_count = 0
    
    def analyze(self, content: str) -> BiasAnalysis:
        """
        Analyze content for potential biases
        
        Args:
            content: The content to analyze
            
        Returns:
            BiasAnalysis with results
        """
        bias_types = []
        affected_groups = []
        suggestions = []
        
        for bias_type, patterns in self.BIAS_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    bias_types.append(bias_type)
                    affected_groups.append(f"{bias_type}_related")
                    break
        
        has_bias = len(bias_types) > 0
        confidence = min(0.3 * len(bias_types), 0.9) if has_bias else 0.1
        
        if has_bias:
            self.detection_count += 1
            suggestions.append("Consider rephrasing to be more inclusive")
            suggestions.append("Review content for unintentional stereotypes")
        
        return BiasAnalysis(
            has_bias=has_bias,
            bias_types=bias_types,
            confidence=confidence,
            affected_groups=affected_groups,
            suggestions=suggestions
        )
    
    def get_mitigation_suggestions(self, bias_type: str) -> List[str]:
        """Get mitigation suggestions for a bias type"""
        suggestions = {
            "gender": [
                "Use gender-neutral pronouns (they/them)",
                "Avoid generalizations about genders",
                "Focus on individual capabilities, not gender"
            ],
            "age": [
                "Avoid age-based generalizations",
                "Focus on individual skills and experience",
                "Use inclusive language for all age groups"
            ],
            "cultural": [
                "Avoid cultural stereotypes",
                "Represent diverse perspectives",
                "Use culturally sensitive language"
            ],
            "professional": [
                "Acknowledge diverse expertise",
                "Avoid gatekeeping language",
                "Encourage learning at all levels"
            ]
        }
        return suggestions.get(bias_type, ["Review content for inclusivity"])


class PrivacyProtector:
    """
    Privacy protection and PII detection
    
    Identifies and protects personal information.
    """
    
    # PII patterns
    PII_PATTERNS: Dict[str, str] = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone_us": r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "ssn": r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
        "credit_card": r'\b(?:\d{4}[-.\s]?){3}\d{4}\b',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "date_of_birth": r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
        "address": r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr)\b',
    }
    
    def __init__(self, auto_redact: bool = True):
        """Initialize privacy protector"""
        self.auto_redact = auto_redact
    
    def analyze(self, content: str) -> PrivacyAnalysis:
        """
        Analyze content for PII
        
        Args:
            content: The content to analyze
            
        Returns:
            PrivacyAnalysis with results
        """
        pii_types = []
        redacted_content = content
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                pii_types.append(pii_type)
                
                if self.auto_redact:
                    redacted_content = re.sub(
                        pattern,
                        f"[REDACTED-{pii_type.upper()}]",
                        redacted_content,
                        flags=re.IGNORECASE
                    )
        
        has_pii = len(pii_types) > 0
        
        # Determine risk level
        high_risk_types = {"ssn", "credit_card"}
        medium_risk_types = {"email", "phone_us", "date_of_birth"}
        
        if any(t in high_risk_types for t in pii_types):
            risk_level = RiskLevel.HIGH
        elif any(t in medium_risk_types for t in pii_types):
            risk_level = RiskLevel.MEDIUM
        elif pii_types:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.NONE
        
        return PrivacyAnalysis(
            has_pii=has_pii,
            pii_types=pii_types,
            risk_level=risk_level,
            redacted_content=redacted_content if has_pii else None
        )
    
    def redact_all(self, content: str) -> str:
        """Redact all detected PII from content"""
        result = content
        for pii_type, pattern in self.PII_PATTERNS.items():
            result = re.sub(
                pattern,
                f"[REDACTED-{pii_type.upper()}]",
                result,
                flags=re.IGNORECASE
            )
        return result


class AuditLogger:
    """
    Audit logging for transparency
    
    Records all safety-related decisions for review.
    """
    
    def __init__(self, db_path: str = "forge_ethics_audit.db"):
        """Initialize audit logger"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for audit logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                entry_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id TEXT,
                content_type TEXT,
                risk_level TEXT,
                decision TEXT,
                details TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON audit_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_risk ON audit_logs(risk_level)')
        
        conn.commit()
        conn.close()
    
    def log(
        self,
        action: str,
        content_type: str,
        risk_level: RiskLevel,
        decision: Action,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an audit entry
        
        Returns:
            Entry ID
        """
        now = utc_now().isoformat()
        entry_id = hashlib.sha256(f"{now}{action}".encode()).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs 
            (entry_id, timestamp, action, user_id, content_type, risk_level, decision, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry_id,
            now,
            action,
            user_id,
            content_type,
            risk_level.value,
            decision.value,
            json.dumps(details or {})
        ))
        
        conn.commit()
        conn.close()
        
        return entry_id
    
    def get_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Get audit log entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = 'SELECT * FROM audit_logs WHERE 1=1'
        params: List[Any] = []
        
        if start_date:
            sql += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            sql += ' AND timestamp <= ?'
            params.append(end_date)
        
        if risk_level:
            sql += ' AND risk_level = ?'
            params.append(risk_level.value)
        
        sql += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        
        entries = []
        for row in cursor.fetchall():
            entry = AuditLogEntry(
                entry_id=row[0],
                timestamp=row[1],
                action=row[2],
                user_id=row[3],
                content_type=row[4],
                risk_level=row[5],
                decision=row[6],
                details=json.loads(row[7]) if row[7] else {}
            )
            entries.append(entry)
        
        conn.close()
        return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit log statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM audit_logs')
        total_entries = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT risk_level, COUNT(*) 
            FROM audit_logs 
            GROUP BY risk_level
        ''')
        by_risk = dict(cursor.fetchall())
        
        cursor.execute('''
            SELECT decision, COUNT(*) 
            FROM audit_logs 
            GROUP BY decision
        ''')
        by_decision = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "by_risk_level": by_risk,
            "by_decision": by_decision
        }


class EthicsGuard:
    """
    Main ethics and safety system
    
    Integrates all safety components for comprehensive protection.
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        auto_redact_pii: bool = True,
        enable_audit: bool = True,
        db_path: str = "forge_ethics_audit.db"
    ):
        """Initialize the ethics guard"""
        self.content_moderator = ContentModerator(strict_mode)
        self.bias_detector = BiasDetector()
        self.privacy_protector = PrivacyProtector(auto_redact_pii)
        self.audit_logger = AuditLogger(db_path) if enable_audit else None
        self.enable_audit = enable_audit
        
        logger.info("🛡️ Ethics Guard initialized")
    
    def analyze_input(
        self,
        content: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze input content for all safety concerns
        
        Args:
            content: The input to analyze
            user_id: Optional user identifier
            
        Returns:
            Combined analysis results
        """
        # Run all analyses
        content_analysis = self.content_moderator.analyze(content)
        bias_analysis = self.bias_detector.analyze(content)
        privacy_analysis = self.privacy_protector.analyze(content)
        
        # Determine overall safety
        is_safe = (
            content_analysis.is_safe and
            not privacy_analysis.has_pii and
            not bias_analysis.has_bias
        )
        
        # Determine overall action
        if content_analysis.action == Action.BLOCK:
            overall_action = Action.BLOCK
        elif privacy_analysis.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            overall_action = Action.BLOCK
        elif content_analysis.action == Action.WARN or bias_analysis.has_bias:
            overall_action = Action.WARN
        else:
            overall_action = Action.ALLOW
        
        result = {
            "is_safe": is_safe,
            "action": overall_action.value,
            "content_safety": content_analysis.to_dict(),
            "bias_detection": bias_analysis.to_dict(),
            "privacy_protection": privacy_analysis.to_dict(),
            "processed_content": privacy_analysis.redacted_content or content
        }
        
        # Log if auditing is enabled
        if self.enable_audit and self.audit_logger:
            self.audit_logger.log(
                action="input_analysis",
                content_type="user_input",
                risk_level=content_analysis.risk_level,
                decision=overall_action,
                user_id=user_id,
                details={
                    "categories": [c.value for c in content_analysis.categories],
                    "has_bias": bias_analysis.has_bias,
                    "has_pii": privacy_analysis.has_pii
                }
            )
        
        return result
    
    def analyze_output(
        self,
        content: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze output content for safety
        
        Args:
            content: The output to analyze
            user_id: Optional user identifier
            
        Returns:
            Combined analysis results
        """
        # Run analyses
        content_analysis = self.content_moderator.analyze(content)
        bias_analysis = self.bias_detector.analyze(content)
        privacy_analysis = self.privacy_protector.analyze(content)
        
        # For output, we're more strict about bias and privacy
        is_safe = content_analysis.is_safe and not privacy_analysis.has_pii
        
        # Determine action
        if content_analysis.action == Action.BLOCK or privacy_analysis.has_pii:
            overall_action = Action.MODIFY
        elif bias_analysis.has_bias:
            overall_action = Action.WARN
        else:
            overall_action = Action.ALLOW
        
        result = {
            "is_safe": is_safe,
            "action": overall_action.value,
            "content_safety": content_analysis.to_dict(),
            "bias_detection": bias_analysis.to_dict(),
            "privacy_protection": privacy_analysis.to_dict(),
            "processed_content": privacy_analysis.redacted_content or content
        }
        
        # Log if auditing is enabled
        if self.enable_audit and self.audit_logger:
            self.audit_logger.log(
                action="output_analysis",
                content_type="ai_output",
                risk_level=content_analysis.risk_level,
                decision=overall_action,
                user_id=user_id,
                details={
                    "categories": [c.value for c in content_analysis.categories],
                    "has_bias": bias_analysis.has_bias,
                    "has_pii": privacy_analysis.has_pii
                }
            )
        
        return result
    
    def get_audit_stats(self) -> Optional[Dict[str, Any]]:
        """Get audit statistics"""
        if self.audit_logger:
            return self.audit_logger.get_stats()
        return None
    
    def add_blocked_term(self, term: str):
        """Add a term to the content blocklist"""
        self.content_moderator.add_blocked_term(term)
    
    def get_guidelines(self) -> Dict[str, Any]:
        """Get ethical guidelines and policies"""
        return {
            "content_policy": {
                "description": "Content must not contain violence, hate speech, or harmful material",
                "enforcement": "Automatic detection and moderation"
            },
            "privacy_policy": {
                "description": "Personal information is automatically detected and protected",
                "enforcement": "PII detection and optional redaction"
            },
            "bias_policy": {
                "description": "Content should be inclusive and avoid stereotypes",
                "enforcement": "Bias detection with suggestions for improvement"
            },
            "transparency": {
                "description": "All safety decisions are logged for accountability",
                "enforcement": "Comprehensive audit logging"
            }
        }


# Convenience function
def create_ethics_guard(
    strict_mode: bool = False,
    auto_redact_pii: bool = True,
    enable_audit: bool = True,
    db_path: str = "forge_ethics_audit.db"
) -> EthicsGuard:
    """Create a new ethics guard instance"""
    return EthicsGuard(strict_mode, auto_redact_pii, enable_audit, db_path)


# ==================== MAIN ====================

def main():
    """Demo the ethics and safety system"""
    print("=" * 60)
    print("🛡️ THE FORGE AI - Ethics and Safety Demo")
    print("=" * 60)
    print()
    
    # Initialize ethics guard
    guard = EthicsGuard()
    
    # Demo: Content moderation
    print("🔍 Demo: Content Moderation")
    print("-" * 40)
    test_contents = [
        "Please help me write a Python function.",
        "Can you help me find someone's SSN: 123-45-6789?",
        "Send me a list of all women can't do.",
    ]
    
    for content in test_contents:
        result = guard.analyze_input(content)
        print(f"  Input: '{content[:50]}...'")
        print(f"  Safe: {result['is_safe']}, Action: {result['action']}")
        if not result['is_safe']:
            print(f"  Categories: {result['content_safety']['categories']}")
        print()
    
    # Demo: Privacy protection
    print("🔐 Demo: Privacy Protection")
    print("-" * 40)
    pii_content = "Contact me at john.doe@email.com or call 555-123-4567"
    result = guard.analyze_input(pii_content)
    print(f"  Original: {pii_content}")
    print(f"  Redacted: {result['processed_content']}")
    print(f"  PII Types: {result['privacy_protection']['pii_types']}")
    print()
    
    # Demo: Bias detection
    print("⚖️ Demo: Bias Detection")
    print("-" * 40)
    biased_content = "All young people can't understand technology properly."
    result = guard.analyze_input(biased_content)
    print(f"  Content: '{biased_content}'")
    print(f"  Has Bias: {result['bias_detection']['has_bias']}")
    print(f"  Bias Types: {result['bias_detection']['bias_types']}")
    print(f"  Suggestions: {result['bias_detection']['suggestions']}")
    print()
    
    # Demo: Guidelines
    print("📜 Demo: Ethical Guidelines")
    print("-" * 40)
    guidelines = guard.get_guidelines()
    for policy_name, policy in guidelines.items():
        print(f"  {policy_name}: {policy['description']}")
    print()
    
    # Demo: Audit stats
    print("📊 Demo: Audit Statistics")
    print("-" * 40)
    stats = guard.get_audit_stats()
    if stats:
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Ethics and Safety Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
