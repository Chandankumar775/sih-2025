"""
Incident Response Playbook for RakshaNetra
Judge's Feedback #6 & #7: Zero-Day Protection & Incident Response Framework
Automated incident response workflows with escalation procedures
Based on NIST Cybersecurity Framework and military protocols
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    ZERO_DAY = "ZERO_DAY"  # Unknown exploits


class IncidentCategory(Enum):
    """Incident classification"""
    PHISHING = "PHISHING"
    MALWARE = "MALWARE"
    RANSOMWARE = "RANSOMWARE"
    DATA_BREACH = "DATA_BREACH"
    DDOS = "DDOS"
    ZERO_DAY_EXPLOIT = "ZERO_DAY_EXPLOIT"
    INSIDER_THREAT = "INSIDER_THREAT"
    SOCIAL_ENGINEERING = "SOCIAL_ENGINEERING"
    APT = "APT"  # Advanced Persistent Threat
    SUPPLY_CHAIN = "SUPPLY_CHAIN"


class ResponseAction(Enum):
    """Response actions"""
    CONTAIN = "CONTAIN"
    ISOLATE = "ISOLATE"
    BLOCK = "BLOCK"
    ALERT = "ALERT"
    ESCALATE = "ESCALATE"
    INVESTIGATE = "INVESTIGATE"
    REMEDIATE = "REMEDIATE"
    NOTIFY = "NOTIFY"
    DOCUMENT = "DOCUMENT"


@dataclass
class PlaybookStep:
    """Single step in incident response playbook"""
    step_id: int
    action: ResponseAction
    description: str
    responsible: str  # Role responsible for action
    sla_minutes: int  # Time to complete
    automation_available: bool
    required_tools: List[str]
    success_criteria: str
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['action'] = self.action.value
        return result


@dataclass
class EscalationRule:
    """Escalation conditions and targets"""
    condition: str
    escalate_to: str  # Role or team
    notification_channels: List[str]  # email, sms, pager
    escalation_delay_minutes: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IncidentResponsePlaybook:
    """
    Automated incident response system
    - Predefined playbooks for each threat type
    - Automated escalation based on severity and time
    - Integration with military cyber command
    - Zero-day exploit handling procedures
    """
    
    def __init__(self):
        self.playbooks = self._load_playbooks()
        self.escalation_rules = self._load_escalation_rules()
    
    def _load_playbooks(self) -> Dict[str, List[PlaybookStep]]:
        """Load incident response playbooks"""
        return {
            IncidentCategory.PHISHING.value: self._create_phishing_playbook(),
            IncidentCategory.MALWARE.value: self._create_malware_playbook(),
            IncidentCategory.RANSOMWARE.value: self._create_ransomware_playbook(),
            IncidentCategory.ZERO_DAY_EXPLOIT.value: self._create_zero_day_playbook(),
            IncidentCategory.DATA_BREACH.value: self._create_data_breach_playbook(),
            IncidentCategory.APT.value: self._create_apt_playbook(),
        }
    
    def _create_phishing_playbook(self) -> List[PlaybookStep]:
        """Phishing incident response"""
        return [
            PlaybookStep(
                step_id=1,
                action=ResponseAction.ALERT,
                description="Alert Security Operations Center (SOC)",
                responsible="Automated System",
                sla_minutes=5,
                automation_available=True,
                required_tools=["SIEM", "Email Gateway"],
                success_criteria="SOC notified and incident logged"
            ),
            PlaybookStep(
                step_id=2,
                action=ResponseAction.CONTAIN,
                description="Quarantine suspicious email and block sender",
                responsible="Email Security Admin",
                sla_minutes=15,
                automation_available=True,
                required_tools=["Email Gateway", "Firewall"],
                success_criteria="Email blocked, sender blacklisted"
            ),
            PlaybookStep(
                step_id=3,
                action=ResponseAction.INVESTIGATE,
                description="Analyze email headers, links, attachments for IOCs",
                responsible="Security Analyst",
                sla_minutes=30,
                automation_available=True,
                required_tools=["Sandbox", "Threat Intelligence", "WHOIS"],
                success_criteria="IOCs identified and documented"
            ),
            PlaybookStep(
                step_id=4,
                action=ResponseAction.BLOCK,
                description="Block malicious domains/IPs across network",
                responsible="Network Security Team",
                sla_minutes=45,
                automation_available=True,
                required_tools=["Firewall", "DNS Filter", "Proxy"],
                success_criteria="Malicious infrastructure blocked"
            ),
            PlaybookStep(
                step_id=5,
                action=ResponseAction.NOTIFY,
                description="Notify affected users and provide awareness training",
                responsible="Security Awareness Team",
                sla_minutes=120,
                automation_available=False,
                required_tools=["Email System", "Training Platform"],
                success_criteria="Users notified, training scheduled"
            ),
            PlaybookStep(
                step_id=6,
                action=ResponseAction.DOCUMENT,
                description="Document incident, IOCs, and lessons learned",
                responsible="Incident Commander",
                sla_minutes=1440,  # 24 hours
                automation_available=False,
                required_tools=["Incident Management System"],
                success_criteria="Incident report completed"
            )
        ]
    
    def _create_malware_playbook(self) -> List[PlaybookStep]:
        """Malware incident response"""
        return [
            PlaybookStep(
                step_id=1,
                action=ResponseAction.ISOLATE,
                description="Isolate infected system from network immediately",
                responsible="Automated System / Network Admin",
                sla_minutes=5,
                automation_available=True,
                required_tools=["NAC", "Firewall", "EDR"],
                success_criteria="System isolated, no lateral movement"
            ),
            PlaybookStep(
                step_id=2,
                action=ResponseAction.CONTAIN,
                description="Block malware hash/signature across all endpoints",
                responsible="Endpoint Security Team",
                sla_minutes=15,
                automation_available=True,
                required_tools=["EDR", "Antivirus", "SIEM"],
                success_criteria="Malware signature blocked organization-wide"
            ),
            PlaybookStep(
                step_id=3,
                action=ResponseAction.INVESTIGATE,
                description="Forensic analysis of malware sample and system",
                responsible="Malware Analyst",
                sla_minutes=60,
                automation_available=False,
                required_tools=["Sandbox", "Forensic Tools", "Memory Analysis"],
                success_criteria="Malware behavior and C2 identified"
            ),
            PlaybookStep(
                step_id=4,
                action=ResponseAction.REMEDIATE,
                description="Clean or reimage infected systems",
                responsible="System Administrator",
                sla_minutes=240,
                automation_available=False,
                required_tools=["Imaging Tools", "Backup System"],
                success_criteria="Systems cleaned and validated"
            ),
            PlaybookStep(
                step_id=5,
                action=ResponseAction.ESCALATE,
                description="Escalate to Cyber Command if military data accessed",
                responsible="Security Manager",
                sla_minutes=60,
                automation_available=False,
                required_tools=["Secure Communication Channels"],
                success_criteria="Cyber Command notified if data breach"
            )
        ]
    
    def _create_ransomware_playbook(self) -> List[PlaybookStep]:
        """Ransomware incident response (CRITICAL)"""
        return [
            PlaybookStep(
                step_id=1,
                action=ResponseAction.ISOLATE,
                description="IMMEDIATE ISOLATION: Disconnect all systems from network",
                responsible="Automated System / Emergency Response",
                sla_minutes=2,
                automation_available=True,
                required_tools=["Network Kill Switch", "Firewall"],
                success_criteria="All systems isolated, encryption stopped"
            ),
            PlaybookStep(
                step_id=2,
                action=ResponseAction.ALERT,
                description="Activate Crisis Management Team and Cyber Command",
                responsible="Automated System",
                sla_minutes=5,
                automation_available=True,
                required_tools=["Emergency Notification System"],
                success_criteria="Crisis team assembled"
            ),
            PlaybookStep(
                step_id=3,
                action=ResponseAction.CONTAIN,
                description="Identify patient zero and affected systems",
                responsible="Incident Response Team",
                sla_minutes=30,
                automation_available=False,
                required_tools=["EDR", "SIEM", "Network Monitoring"],
                success_criteria="Infection scope determined"
            ),
            PlaybookStep(
                step_id=4,
                action=ResponseAction.BLOCK,
                description="Block ransomware C2 servers and payment sites",
                responsible="Network Security",
                sla_minutes=15,
                automation_available=True,
                required_tools=["Firewall", "DNS Filter", "Threat Intel"],
                success_criteria="C2 communication blocked"
            ),
            PlaybookStep(
                step_id=5,
                action=ResponseAction.REMEDIATE,
                description="Restore from backups (DO NOT PAY RANSOM)",
                responsible="Backup Team / System Administrators",
                sla_minutes=480,  # 8 hours
                automation_available=False,
                required_tools=["Backup System", "Recovery Tools"],
                success_criteria="Critical systems restored from clean backups"
            ),
            PlaybookStep(
                step_id=6,
                action=ResponseAction.NOTIFY,
                description="Notify law enforcement and regulatory authorities",
                responsible="Legal / Compliance",
                sla_minutes=120,
                automation_available=False,
                required_tools=["Secure Communication"],
                success_criteria="Authorities notified per regulations"
            )
        ]
    
    def _create_zero_day_playbook(self) -> List[PlaybookStep]:
        """Zero-day exploit response (UNKNOWN THREAT)"""
        return [
            PlaybookStep(
                step_id=1,
                action=ResponseAction.ALERT,
                description="ZERO-DAY DETECTED: Alert Cyber Command immediately",
                responsible="Automated System",
                sla_minutes=1,
                automation_available=True,
                required_tools=["Emergency Alerts"],
                success_criteria="Highest priority alert sent"
            ),
            PlaybookStep(
                step_id=2,
                action=ResponseAction.ISOLATE,
                description="Isolate affected systems and network segment",
                responsible="Network Security",
                sla_minutes=5,
                automation_available=True,
                required_tools=["Network Segmentation", "Firewall"],
                success_criteria="Threat contained in isolated segment"
            ),
            PlaybookStep(
                step_id=3,
                action=ResponseAction.INVESTIGATE,
                description="Emergency threat analysis and vulnerability research",
                responsible="Advanced Threat Team",
                sla_minutes=30,
                automation_available=False,
                required_tools=["Sandbox", "Reverse Engineering Tools", "IDA Pro"],
                success_criteria="Exploit mechanism understood"
            ),
            PlaybookStep(
                step_id=4,
                action=ResponseAction.CONTAIN,
                description="Implement emergency patches or compensating controls",
                responsible="System Architects",
                sla_minutes=120,
                automation_available=False,
                required_tools=["Patch Management", "WAF", "IPS"],
                success_criteria="Vulnerability mitigated"
            ),
            PlaybookStep(
                step_id=5,
                action=ResponseAction.NOTIFY,
                description="Share IOCs with CERT-In and military cyber community",
                responsible="Threat Intelligence Team",
                sla_minutes=60,
                automation_available=False,
                required_tools=["STIX/TAXII", "Threat Sharing Platform"],
                success_criteria="Threat intelligence shared"
            ),
            PlaybookStep(
                step_id=6,
                action=ResponseAction.ESCALATE,
                description="Escalate to National Cyber Coordination Centre (NCCC)",
                responsible="Security Director",
                sla_minutes=120,
                automation_available=False,
                required_tools=["Secure Government Channels"],
                success_criteria="National authorities engaged"
            )
        ]
    
    def _create_data_breach_playbook(self) -> List[PlaybookStep]:
        """Data breach incident response"""
        return [
            PlaybookStep(
                step_id=1,
                action=ResponseAction.CONTAIN,
                description="Stop data exfiltration immediately",
                responsible="Network Security",
                sla_minutes=10,
                automation_available=True,
                required_tools=["DLP", "Firewall", "Network Monitoring"],
                success_criteria="Data flow stopped"
            ),
            PlaybookStep(
                step_id=2,
                action=ResponseAction.INVESTIGATE,
                description="Determine scope: what data, how much, who accessed",
                responsible="Forensics Team",
                sla_minutes=120,
                automation_available=False,
                required_tools=["SIEM", "Database Audit Logs", "DLP Logs"],
                success_criteria="Breach scope documented"
            ),
            PlaybookStep(
                step_id=3,
                action=ResponseAction.NOTIFY,
                description="Notify affected personnel and legal/compliance teams",
                responsible="Legal / HR",
                sla_minutes=240,
                automation_available=False,
                required_tools=["Communication Systems"],
                success_criteria="Mandatory notifications completed"
            ),
            PlaybookStep(
                step_id=4,
                action=ResponseAction.REMEDIATE,
                description="Revoke compromised credentials, rotate secrets",
                responsible="IAM Team",
                sla_minutes=60,
                automation_available=True,
                required_tools=["IAM", "Secret Management", "PKI"],
                success_criteria="All compromised credentials invalidated"
            )
        ]
    
    def _create_apt_playbook(self) -> List[PlaybookStep]:
        """Advanced Persistent Threat response"""
        return [
            PlaybookStep(
                step_id=1,
                action=ResponseAction.ALERT,
                description="APT detected - Activate Advanced Threat Response Team",
                responsible="Automated System",
                sla_minutes=10,
                automation_available=True,
                required_tools=["Threat Detection Platform"],
                success_criteria="Specialized APT team activated"
            ),
            PlaybookStep(
                step_id=2,
                action=ResponseAction.INVESTIGATE,
                description="Hunt for APT indicators across all systems",
                responsible="Threat Hunting Team",
                sla_minutes=240,
                automation_available=False,
                required_tools=["EDR", "SIEM", "Threat Hunting Platform"],
                success_criteria="Full APT campaign mapped"
            ),
            PlaybookStep(
                step_id=3,
                action=ResponseAction.CONTAIN,
                description="Coordinated removal of APT infrastructure",
                responsible="Incident Response Team",
                sla_minutes=360,
                automation_available=False,
                required_tools=["EDR", "Network Tools", "Forensics"],
                success_criteria="APT completely eradicated"
            ),
            PlaybookStep(
                step_id=4,
                action=ResponseAction.ESCALATE,
                description="Escalate to Military Intelligence and CERT-In",
                responsible="Security Director",
                sla_minutes=120,
                automation_available=False,
                required_tools=["Classified Communication Channels"],
                success_criteria="Military intelligence engaged"
            )
        ]
    
    def _load_escalation_rules(self) -> Dict[str, List[EscalationRule]]:
        """Load escalation rules for each threat level"""
        return {
            ThreatLevel.CRITICAL.value: [
                EscalationRule(
                    condition="Immediate escalation required",
                    escalate_to="Cyber Command Duty Officer",
                    notification_channels=["sms", "phone_call", "secure_chat"],
                    escalation_delay_minutes=0
                ),
                EscalationRule(
                    condition="No response in 15 minutes",
                    escalate_to="Cyber Command Director",
                    notification_channels=["phone_call", "emergency_pager"],
                    escalation_delay_minutes=15
                )
            ],
            ThreatLevel.HIGH.value: [
                EscalationRule(
                    condition="High severity incident detected",
                    escalate_to="Security Operations Manager",
                    notification_channels=["email", "sms"],
                    escalation_delay_minutes=30
                ),
                EscalationRule(
                    condition="No resolution in 2 hours",
                    escalate_to="CISO",
                    notification_channels=["phone_call", "email"],
                    escalation_delay_minutes=120
                )
            ],
            ThreatLevel.MEDIUM.value: [
                EscalationRule(
                    condition="Incident not resolved in 4 hours",
                    escalate_to="Security Team Lead",
                    notification_channels=["email"],
                    escalation_delay_minutes=240
                )
            ]
        }
    
    def execute_playbook(
        self,
        incident_category: IncidentCategory,
        threat_level: ThreatLevel,
        incident_id: str,
        auto_execute: bool = True
    ) -> Dict[str, Any]:
        """
        Execute incident response playbook
        
        Args:
            incident_category: Type of incident
            threat_level: Severity level
            incident_id: Unique incident identifier
            auto_execute: Automatically execute automated steps
            
        Returns:
            Execution plan with timeline and responsibilities
        """
        
        playbook = self.playbooks.get(incident_category.value, [])
        escalation_rules = self.escalation_rules.get(threat_level.value, [])
        
        execution_plan = {
            "incident_id": incident_id,
            "incident_category": incident_category.value,
            "threat_level": threat_level.value,
            "playbook_initiated": datetime.utcnow().isoformat(),
            "total_steps": len(playbook),
            "estimated_completion": self._calculate_completion_time(playbook),
            "steps": [],
            "escalation_rules": [rule.to_dict() for rule in escalation_rules],
            "auto_execution_enabled": auto_execute
        }
        
        for step in playbook:
            step_info = step.to_dict()
            step_info["due_by"] = (
                datetime.utcnow() + timedelta(minutes=step.sla_minutes)
            ).isoformat()
            step_info["status"] = "pending"
            
            if auto_execute and step.automation_available:
                step_info["status"] = "auto_executing"
                # Here you would call actual automation functions
                print(f"[PLAYBOOK] 🤖 Auto-executing: {step.description}")
            else:
                print(f"[PLAYBOOK] 👤 Manual action required: {step.description}")
            
            execution_plan["steps"].append(step_info)
        
        return execution_plan
    
    def _calculate_completion_time(self, playbook: List[PlaybookStep]) -> str:
        """Calculate estimated completion time"""
        total_minutes = sum(step.sla_minutes for step in playbook)
        completion_time = datetime.utcnow() + timedelta(minutes=total_minutes)
        return completion_time.isoformat()
    
    def check_escalation(
        self,
        incident_id: str,
        threat_level: ThreatLevel,
        incident_start_time: datetime,
        current_status: str
    ) -> Optional[Dict[str, Any]]:
        """Check if incident should be escalated based on rules"""
        
        escalation_rules = self.escalation_rules.get(threat_level.value, [])
        elapsed_minutes = (datetime.utcnow() - incident_start_time).total_seconds() / 60
        
        for rule in escalation_rules:
            if elapsed_minutes >= rule.escalation_delay_minutes:
                if current_status not in ["resolved", "escalated"]:
                    return {
                        "should_escalate": True,
                        "escalate_to": rule.escalate_to,
                        "notification_channels": rule.notification_channels,
                        "reason": rule.condition,
                        "elapsed_minutes": int(elapsed_minutes)
                    }
        
        return None


# Global playbook instance
incident_playbook = IncidentResponsePlaybook()


# Convenience function
def trigger_incident_response(
    incident_category: str,
    threat_level: str,
    incident_id: str
) -> Dict[str, Any]:
    """Trigger incident response playbook"""
    category = IncidentCategory[incident_category.upper()]
    level = ThreatLevel[threat_level.upper()]
    return incident_playbook.execute_playbook(category, level, incident_id)
