"""
Sandbox Analyzer Module for RakshaNetra
Static file analysis, malware detection, VirusTotal integration
Analyzes files in isolated environment without execution
NOW WITH EVIDENCE VAULT INTEGRATION - Retains all analyzed files for forensics
"""

import os
import hashlib
import magic
from typing import Dict, Any, Optional
from datetime import datetime
import io

# Import Evidence Vault
try:
    from .evidence_vault import vault as evidence_vault
    EVIDENCE_VAULT_AVAILABLE = True
except:
    EVIDENCE_VAULT_AVAILABLE = False
    print("[WARNING] Evidence Vault not available")

# Optional imports (may not be available)
try:
    import pefile
    PEFILE_AVAILABLE = True
except:
    PEFILE_AVAILABLE = False

try:
    import olefile
    OLEFILE_AVAILABLE = True
except:
    OLEFILE_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except:
    PYPDF2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

# VirusTotal API (Optional - requires API key)
import os
from dotenv import load_dotenv
load_dotenv()

VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')
VIRUSTOTAL_ENABLED = False

try:
    import vt
    if VIRUSTOTAL_API_KEY:
        VIRUSTOTAL_ENABLED = True
        print(f"✅ VirusTotal integration ENABLED")
    else:
        print(f"⚠️  VirusTotal API key not set (optional)")
except ImportError:
    print(f"⚠️  VirusTotal library not available")
    pass

# YARA Rules (Using pattern matching as fallback for Windows compatibility)
YARA_AVAILABLE = False
YARA_RULES = None

# Pattern-based malware detection (YARA alternative)
MALWARE_PATTERNS = {
    "ransomware": {
        "patterns": [b"encrypt", b"decrypt", b"bitcoin", b"ransom", b"payment", b".locked"],
        "severity": "critical",
        "description": "Ransomware indicators detected"
    },
    "keylogger": {
        "patterns": [b"GetAsyncKeyState", b"GetKeyboardState", b"SetWindowsHookEx", b"keylog"],
        "severity": "high",
        "description": "Keylogger patterns detected"
    },
    "trojan": {
        "patterns": [b"backdoor", b"shell", b"schtasks", b"TeamViewer", b"AnyDesk"],
        "severity": "high",
        "description": "Trojan/backdoor indicators found"
    },
    "network_attack": {
        "patterns": [b"cmd.exe", b"powershell", b".onion", b"wget", b"curl"],
        "severity": "medium",
        "description": "Suspicious network activity patterns"
    },
    "crypto_miner": {
        "patterns": [b"stratum+tcp://", b"xmrig", b"ethminer", b"monero", b"pool"],
        "severity": "medium",
        "description": "Cryptocurrency mining indicators"
    },
    "phishing_doc": {
        "patterns": [b"Auto_Open", b"AutoOpen", b"CreateObject", b"WScript"],
        "severity": "medium",
        "description": "Suspicious macro/script in document"
    },
    "army_targeted": {
        "patterns": [b"Indian Army", b"Ministry of Defence", b"soldier", b"officer", b"WhatsApp", b"Telegram"],
        "severity": "critical",
        "description": "Content targeting Indian defense personnel"
    }
}

print(f"✅ Pattern-based malware detection ENABLED ({len(MALWARE_PATTERNS)} signatures)")


def analyze_file(file_content: bytes, filename: str, file_size: int) -> Dict[str, Any]:
    """
    Comprehensive static file analysis without execution
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        file_size: File size in bytes
    
    Returns:
        Dictionary with sandbox analysis results
    """
    print(f"\n🔬 SANDBOX ANALYSIS START")
    print(f"{'='*60}")
    print(f"File: {filename}")
    print(f"Size: {format_file_size(file_size)}")
    
    result = {
        "filename": filename,
        "file_size": file_size,
        "file_size_formatted": format_file_size(file_size),
        "file_hash": calculate_hashes(file_content),
        "file_type": detect_file_type(file_content),
        "suspicious_behaviors": [],
        "threat_level": "LOW",
        "malware_indicators": [],
        "metadata": {},
        "virustotal_results": None,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Detect file type
    mime_type = result["file_type"]["mime_type"]
    file_ext = os.path.splitext(filename)[1].lower()
    
    print(f"Type: {mime_type}")
    print(f"Hash (SHA256): {result['file_hash']['sha256'][:32]}...")
    
    # Perform type-specific analysis
    if mime_type.startswith('application/') and 'executable' in mime_type:
        result.update(analyze_executable(file_content, filename))
    elif mime_type == 'application/pdf':
        result.update(analyze_pdf(file_content))
    elif mime_type.startswith('application/vnd.ms-') or mime_type.startswith('application/vnd.openxmlformats'):
        result.update(analyze_office_document(file_content, filename))
    elif mime_type.startswith('image/'):
        result.update(analyze_image(file_content))
    elif mime_type.startswith('text/'):
        result.update(analyze_text_file(file_content))
    
    # General suspicious indicators
    check_suspicious_patterns(file_content, filename, result)
    
    # Calculate threat level
    result["threat_level"] = calculate_threat_level(result)
    
    # Pattern-based malware detection (YARA alternative)
    result["malware_matches"] = scan_malware_patterns(file_content)
    if result["malware_matches"]:
        for match in result["malware_matches"]:
            result["malware_indicators"].append(f"{match['category'].upper()}: {match['description']}")
            # Escalate threat level if critical malware detected
            if match["severity"] == "critical":
                result["threat_level"] = "CRITICAL"
            elif match["severity"] == "high" and result["threat_level"] not in ["CRITICAL"]:
                result["threat_level"] = "HIGH"
    
    # VirusTotal check (if enabled)
    if VIRUSTOTAL_ENABLED:
        result["virustotal_results"] = check_virustotal(result["file_hash"]["sha256"])
    
    # 🔒 STORE IN EVIDENCE VAULT (Judge's Feedback #1)
    if EVIDENCE_VAULT_AVAILABLE:
        try:
            evidence_result = evidence_vault.store_evidence(
                file_data=file_content,
                original_filename=filename,
                file_type=result["file_type"]["mime_type"],
                threat_level=result["threat_level"],
                analysis_results=result,
                incident_id=None,  # Will be linked later if needed
                retention_policy="90_days" if result["threat_level"] in ["LOW", "MEDIUM"] else "1_year",
                analyst="sandbox_system"
            )
            result["evidence_id"] = evidence_result.get("evidence_id")
            result["evidence_stored"] = True
            print(f"[EVIDENCE] ✅ File stored: {evidence_result.get('evidence_id')}")
        except Exception as e:
            print(f"[EVIDENCE] ❌ Storage failed: {e}")
            result["evidence_stored"] = False
    else:
        result["evidence_stored"] = False
    
    print(f"\n[OK] Sandbox Analysis Complete")
    print(f"Threat Level: {result['threat_level']}")
    print(f"Suspicious Behaviors: {len(result['suspicious_behaviors'])}")
    print(f"Evidence Vault: {'✅ Stored' if result.get('evidence_stored') else '❌ Not stored'}")
    print(f"{'='*60}\n")
    
    return result


def calculate_hashes(file_content: bytes) -> Dict[str, str]:
    """Calculate multiple hash values for file"""
    return {
        "md5": hashlib.md5(file_content).hexdigest(),
        "sha1": hashlib.sha1(file_content).hexdigest(),
        "sha256": hashlib.sha256(file_content).hexdigest()
    }


def detect_file_type(file_content: bytes) -> Dict[str, str]:
    """Detect file type using magic numbers"""
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_content)
        
        mime_desc = magic.Magic()
        description = mime_desc.from_buffer(file_content)
        
        return {
            "mime_type": mime_type,
            "description": description
        }
    except Exception as e:
        return {
            "mime_type": "application/octet-stream",
            "description": f"Unknown file type: {str(e)}"
        }


def analyze_executable(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Analyze executable files (PE files on Windows)"""
    analysis = {
        "is_executable": True,
        "pe_analysis": None
    }
    
    if not PEFILE_AVAILABLE:
        analysis["suspicious_behaviors"] = ["Unable to perform PE analysis - pefile not available"]
        return analysis
    
    try:
        pe = pefile.PE(data=file_content)
        
        pe_info = {
            "is_dll": pe.is_dll(),
            "is_exe": pe.is_exe(),
            "machine_type": hex(pe.FILE_HEADER.Machine),
            "timestamp": datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp).isoformat(),
            "sections": [],
            "imports": []
        }
        
        # Check sections
        for section in pe.sections:
            section_name = section.Name.decode().strip('\x00')
            pe_info["sections"].append({
                "name": section_name,
                "virtual_size": section.Misc_VirtualSize,
                "entropy": section.get_entropy()
            })
            
            # High entropy = possible encryption/packing
            if section.get_entropy() > 7.0:
                analysis.setdefault("suspicious_behaviors", []).append(
                    f"High entropy in section '{section_name}' ({section.get_entropy():.2f}) - possible packed/encrypted code"
                )
        
        # Check imports (suspicious APIs)
        suspicious_imports = [
            'CreateRemoteThread', 'WriteProcessMemory', 'VirtualAllocEx',
            'SetWindowsHookEx', 'GetAsyncKeyState', 'RegSetValueEx',
            'WinExec', 'ShellExecute', 'URLDownloadToFile'
        ]
        
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode()
                for imp in entry.imports:
                    if imp.name:
                        func_name = imp.name.decode()
                        pe_info["imports"].append(f"{dll_name}::{func_name}")
                        
                        if func_name in suspicious_imports:
                            analysis.setdefault("malware_indicators", []).append(
                                f"Suspicious API: {func_name} (used in code injection/keylogging)"
                            )
        
        analysis["pe_analysis"] = pe_info
        
    except Exception as e:
        analysis.setdefault("suspicious_behaviors", []).append(f"PE analysis failed: {str(e)}")
    
    return analysis


def analyze_pdf(file_content: bytes) -> Dict[str, Any]:
    """Analyze PDF files for suspicious content"""
    analysis = {
        "is_pdf": True,
        "pdf_analysis": None
    }
    
    if not PYPDF2_AVAILABLE:
        return analysis
    
    try:
        pdf_file = io.BytesIO(file_content)
        pdf = PdfReader(pdf_file)
        
        pdf_info = {
            "num_pages": len(pdf.pages),
            "encrypted": pdf.is_encrypted,
            "metadata": {}
        }
        
        # Check metadata
        if pdf.metadata:
            pdf_info["metadata"] = {
                "title": pdf.metadata.get('/Title', 'N/A'),
                "author": pdf.metadata.get('/Author', 'N/A'),
                "creator": pdf.metadata.get('/Creator', 'N/A')
            }
        
        # Check for JavaScript (common in malicious PDFs)
        has_js = False
        for page in pdf.pages:
            if '/JS' in page or '/JavaScript' in page:
                has_js = True
                break
        
        if has_js:
            analysis.setdefault("suspicious_behaviors", []).append(
                "PDF contains embedded JavaScript - potential exploit vector"
            )
        
        # Check for launch actions (auto-execute)
        if '/Launch' in str(pdf):
            analysis.setdefault("malware_indicators", []).append(
                "PDF contains Launch action - may execute external files"
            )
        
        analysis["pdf_analysis"] = pdf_info
        
    except Exception as e:
        analysis.setdefault("suspicious_behaviors", []).append(f"PDF analysis failed: {str(e)}")
    
    return analysis


def analyze_office_document(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Analyze Microsoft Office documents for macros"""
    analysis = {
        "is_office_doc": True,
        "office_analysis": None
    }
    
    if not OLEFILE_AVAILABLE:
        return analysis
    
    try:
        ole = olefile.OleFileIO(file_content)
        
        doc_info = {
            "has_macros": False,
            "macro_streams": []
        }
        
        # Check for VBA macros
        if ole.exists('Macros') or ole.exists('VBA'):
            doc_info["has_macros"] = True
            analysis.setdefault("malware_indicators", []).append(
                "Document contains VBA macros - common malware delivery method"
            )
        
        # List all streams
        for stream in ole.listdir():
            stream_name = '/'.join(stream)
            if 'macro' in stream_name.lower() or 'vba' in stream_name.lower():
                doc_info["macro_streams"].append(stream_name)
        
        analysis["office_analysis"] = doc_info
        ole.close()
        
    except Exception as e:
        # Not an OLE file, might be newer Office format (OOXML)
        if filename.endswith(('.docx', '.xlsx', '.pptx')):
            analysis.setdefault("suspicious_behaviors", []).append(
                "Modern Office format - macro analysis limited"
            )
    
    return analysis


def analyze_image(file_content: bytes) -> Dict[str, Any]:
    """Analyze image files for suspicious content"""
    analysis = {
        "is_image": True,
        "image_analysis": None
    }
    
    if not PIL_AVAILABLE:
        return analysis
    
    try:
        img = Image.open(io.BytesIO(file_content))
        
        img_info = {
            "format": img.format,
            "size": img.size,
            "mode": img.mode
        }
        
        # Check EXIF data for GPS or suspicious metadata
        if hasattr(img, '_getexif') and img._getexif():
            exif_data = img._getexif()
            if exif_data:
                img_info["has_exif"] = True
                analysis.setdefault("metadata", {})["exif_tags_count"] = len(exif_data)
        
        analysis["image_analysis"] = img_info
        
    except Exception as e:
        analysis.setdefault("suspicious_behaviors", []).append(f"Image analysis failed: {str(e)}")
    
    return analysis


def analyze_text_file(file_content: bytes) -> Dict[str, Any]:
    """Analyze text files for suspicious patterns"""
    analysis = {
        "is_text": True
    }
    
    try:
        text = file_content.decode('utf-8', errors='ignore')
        
        # Check for script patterns
        suspicious_patterns = [
            ('powershell', 'PowerShell script detected'),
            ('cmd.exe', 'Command prompt script detected'),
            ('eval(', 'Eval function detected (code execution)'),
            ('exec(', 'Exec function detected (code execution)'),
            ('<script>', 'JavaScript detected'),
            ('base64', 'Base64 encoding detected (possible obfuscation)'),
        ]
        
        for pattern, message in suspicious_patterns:
            if pattern.lower() in text.lower():
                analysis.setdefault("suspicious_behaviors", []).append(message)
        
    except Exception as e:
        pass
    
    return analysis


def check_suspicious_patterns(file_content: bytes, filename: str, result: Dict[str, Any]):
    """Check for general suspicious patterns"""
    
    # Check file extension mismatch
    declared_ext = os.path.splitext(filename)[1].lower()
    actual_mime = result["file_type"]["mime_type"]
    
    extension_mime_map = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats',
        '.xls': 'application/vnd.ms-excel',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.exe': 'application/x-dosexec'
    }
    
    if declared_ext in extension_mime_map:
        if extension_mime_map[declared_ext] not in actual_mime:
            result["suspicious_behaviors"].append(
                f"File extension mismatch: {declared_ext} declared but actual type is {actual_mime}"
            )
    
    # Check for suspicious strings in binary
    try:
        content_str = file_content.decode('utf-8', errors='ignore')
        suspicious_strings = [
            'cmd.exe', 'powershell.exe', 'malware', 'trojan', 
            'keylog', 'ransom', 'cryptlock', 'payload'
        ]
        
        for sus_str in suspicious_strings:
            if sus_str.lower() in content_str.lower():
                result["malware_indicators"].append(
                    f"Suspicious string found: '{sus_str}'"
                )
    except:
        pass
    
    # Check file size anomalies
    file_size = result.get("file_size", 0)
    if file_size < 100:  # Very small files
        result["suspicious_behaviors"].append("Unusually small file size")
    elif file_size > 100 * 1024 * 1024:  # >100MB
        result["suspicious_behaviors"].append("Unusually large file size")


def calculate_threat_level(result: Dict[str, Any]) -> str:
    """Calculate overall threat level based on findings"""
    threat_score = 0
    
    # Count indicators
    threat_score += len(result.get("suspicious_behaviors", [])) * 2
    threat_score += len(result.get("malware_indicators", [])) * 5
    
    # PE file with suspicious imports
    if result.get("pe_analysis") and result.get("malware_indicators"):
        threat_score += 10
    
    # Office doc with macros
    if result.get("office_analysis", {}).get("has_macros"):
        threat_score += 15
    
    # PDF with JavaScript
    if result.get("pdf_analysis") and any('JavaScript' in str(b) for b in result.get("suspicious_behaviors", [])):
        threat_score += 12
    
    # Determine level
    if threat_score >= 20:
        return "CRITICAL"
    elif threat_score >= 10:
        return "HIGH"
    elif threat_score >= 5:
        return "MEDIUM"
    else:
        return "LOW"


def check_virustotal(file_hash: str) -> Optional[Dict[str, Any]]:
    """Check file hash against VirusTotal database"""
    if not VIRUSTOTAL_ENABLED:
        return None
    
    try:
        with vt.Client(VIRUSTOTAL_API_KEY) as client:
            file_info = client.get_object(f"/files/{file_hash}")
            
            stats = file_info.last_analysis_stats
            return {
                "scanned": True,
                "malicious": stats.get('malicious', 0),
                "suspicious": stats.get('suspicious', 0),
                "undetected": stats.get('undetected', 0),
                "harmless": stats.get('harmless', 0),
                "total_engines": sum(stats.values()),
                "scan_date": file_info.last_analysis_date.isoformat() if file_info.last_analysis_date else None,
                "permalink": f"https://www.virustotal.com/gui/file/{file_hash}"
            }
    except vt.error.APIError as e:
        if e.code == "NotFoundError":
            return {"scanned": False, "message": "File not found in VirusTotal database"}
        else:
            return {"scanned": False, "error": str(e)}
    except Exception as e:
        print(f"[ERROR] VirusTotal check failed: {e}")
        return {"scanned": False, "error": str(e)}


def scan_with_yara(file_content: bytes) -> list:
    """
    Scan file content with YARA malware detection rules
    
    Returns:
        List of matched rules with metadata
    """
    if not YARA_AVAILABLE or not YARA_RULES:
        return []
    
    try:
        matches = YARA_RULES.match(data=file_content)
        results = []
        
        for match in matches:
            rule_info = {
                "rule": match.rule,
                "description": match.meta.get('description', 'No description'),
                "severity": match.meta.get('severity', 'medium'),
                "category": match.meta.get('category', 'unknown'),
                "strings_matched": [str(s) for s in match.strings[:5]]  # First 5 matches
            }
            results.append(rule_info)
            print(f"[YARA] ⚠️  Matched: {match.rule} ({rule_info['severity']}) - {rule_info['description']}")
        
        return results
    except Exception as e:
        print(f"[ERROR] YARA scanning failed: {e}")
        return []


def scan_malware_patterns(file_content: bytes) -> list:
    """
    Pattern-based malware detection (YARA alternative for Windows)
    Scans file content for known malware signatures and behaviors
    
    Returns:
        List of detected malware patterns
    """
    results = []
    
    for category, config in MALWARE_PATTERNS.items():
        matched_patterns = []
        for pattern in config["patterns"]:
            if pattern in file_content:
                matched_patterns.append(pattern.decode('utf-8', errors='ignore'))
        
        # If at least 2 patterns match, consider it a detection
        if len(matched_patterns) >= 2:
            result = {
                "category": category,
                "description": config["description"],
                "severity": config["severity"],
                "matched_patterns": matched_patterns[:5]  # First 5 matches
            }
            results.append(result)
            print(f"[MALWARE] ⚠️  Detected: {category.upper()} ({config['severity']}) - {config['description']}")
            print(f"          Patterns: {', '.join(matched_patterns[:3])}")
    
    return results


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


# For testing
if __name__ == "__main__":
    print("Sandbox Analyzer Module")
    print("=" * 60)
    print(f"pefile available: {PEFILE_AVAILABLE}")
    print(f"olefile available: {OLEFILE_AVAILABLE}")
    print(f"PyPDF2 available: {PYPDF2_AVAILABLE}")
    print(f"PIL available: {PIL_AVAILABLE}")
    print(f"VirusTotal enabled: {VIRUSTOTAL_ENABLED}")
