# 🎯 RakshaNetra Defence Features - Implementation Plan

## 📊 Implementation Timeline: 12 Features in Phases

---

## 🔴 PHASE 1: CRITICAL FOUNDATION (Day 1-2)

### ✅ Task 11: Database Schema Migration
**Priority: CRITICAL**
**Estimated Time: 2-3 hours**

**Database Changes:**
```sql
-- Add new columns to incidents table
ALTER TABLE incidents ADD COLUMN frequency_count INTEGER DEFAULT 1;
ALTER TABLE incidents ADD COLUMN related_incident_ids TEXT; -- JSON array
ALTER TABLE incidents ADD COLUMN cluster_id TEXT;
ALTER TABLE incidents ADD COLUMN geo_region TEXT;
ALTER TABLE incidents ADD COLUMN escalated_flag INTEGER DEFAULT 0;
ALTER TABLE incidents ADD COLUMN escalation_reason TEXT;
ALTER TABLE incidents ADD COLUMN escalate_timestamp TEXT;
ALTER TABLE incidents ADD COLUMN assigned_officer TEXT;
ALTER TABLE incidents ADD COLUMN status_history TEXT; -- JSON array

-- Create threat_clusters table
CREATE TABLE threat_clusters (
    id TEXT PRIMARY KEY,
    cluster_type TEXT, -- domain, message_template, indicator_pattern
    cluster_summary TEXT,
    cluster_size INTEGER DEFAULT 1,
    first_seen TEXT,
    last_seen TEXT,
    sample_incidents TEXT, -- JSON array of incident IDs
    threat_level TEXT,
    created_at TEXT
);

-- Create incident_timeline table
CREATE TABLE incident_timeline (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    event_type TEXT, -- created, assigned, status_changed, escalated, resolved
    event_description TEXT,
    performed_by TEXT,
    timestamp TEXT,
    FOREIGN KEY (incident_id) REFERENCES incidents(id)
);

-- Create geo_statistics table
CREATE TABLE geo_statistics (
    id TEXT PRIMARY KEY,
    region TEXT NOT NULL,
    date TEXT NOT NULL,
    incident_count INTEGER DEFAULT 0,
    high_severity_count INTEGER DEFAULT 0,
    escalated_count INTEGER DEFAULT 0,
    updated_at TEXT
);
```

**Implementation Steps:**
1. Create `backend/migrations/upgrade_schema.py`
2. Update `server.py` init_db() function
3. Add indexes for performance
4. Test migration with existing data
5. Backup database before migration

---

## 🟠 PHASE 2: HIGH-VALUE INTELLIGENCE (Day 2-4)

### ✅ Task 1: Threat Repetition & Pattern Recognition
**Priority: HIGH**
**Estimated Time: 4-5 hours**

**Module: `backend/modules/threat_matcher.py`**

**Algorithm:**
```python
def find_similar_threats(new_incident):
    """
    Similarity Detection Logic:
    1. Content Hash Match (exact duplicates)
    2. Domain Match (same malicious domain)
    3. Message Template Match (80%+ similarity)
    4. Indicator Overlap (3+ common indicators)
    """
    
    # Check existing incidents
    similar = []
    
    # 1. Exact content match
    exact_matches = db.query("SELECT * FROM incidents WHERE content = ?")
    
    # 2. Domain extraction and match
    if incident.type == 'url':
        domain = extract_domain(incident.content)
        domain_matches = db.query("SELECT * FROM incidents WHERE content LIKE ?", f"%{domain}%")
    
    # 3. Message template similarity (using difflib or embedding)
    if incident.type in ['sms', 'email']:
        template_matches = find_template_matches(incident.content)
    
    # 4. Indicator overlap
    indicator_matches = find_indicator_overlap(incident.indicators)
    
    return similar, frequency_count, related_ids
```

**API Integration:**
- Modify `POST /api/incidents` to call threat matcher
- Return frequency insights: `"⚠️ This threat has been reported 14 times in last 7 days"`
- Update incident with `frequency_count` and `related_incident_ids`

**New Endpoint:**
```python
@app.get("/api/incidents/{id}/similar")
async def get_similar_incidents(id: str):
    """Return all similar incidents"""
    pass
```

---

### ✅ Task 3: Auto-Escalation Engine
**Priority: HIGH**
**Estimated Time: 2-3 hours**

**Module: `backend/modules/auto_escalation.py`**

**Escalation Rules:**
```python
def should_escalate(incident):
    """
    Auto-escalation conditions:
    1. risk_score >= 85
    2. frequency_count > 5 (within 7 days)
    3. Army/Defence keyword detected + high severity
    4. Government domain impersonation
    5. Manual escalation request
    """
    
    if incident.risk_score >= 85:
        return True, "Critical risk score (>=85)"
    
    if incident.frequency_count > 5:
        return True, f"Repeated threat ({incident.frequency_count} reports)"
    
    if incident.army_relevant and incident.severity == 'high':
        return True, "Defence-targeted high-severity threat"
    
    if 'gov.in' in incident.content and incident.is_threat:
        return True, "Government domain impersonation detected"
    
    return False, None
```

**New Endpoints:**
```python
@app.get("/api/incidents/escalated")
async def get_escalated_incidents():
    """Return all escalated incidents for CERT officer review"""
    pass

@app.post("/api/incidents/{id}/escalate")
async def manual_escalate(id: str, reason: str):
    """Manually escalate an incident"""
    pass
```

---

### ✅ Task 6: Army-Aware AI Analysis Mode
**Priority: HIGH**
**Estimated Time: 3-4 hours**

**Module: `backend/modules/army_ai_context.py`**

**Defence-Specific Patterns:**
```python
ARMY_SCAM_PATTERNS = {
    'csd_card': [
        'CSD card', 'canteen card', 'defence canteen',
        'army canteen', 'CSD renewal', 'canteen membership'
    ],
    'fake_recruitment': [
        'army recruitment', 'defence job', 'soldier vacancy',
        'BSF recruitment', 'CRPF job', 'military hiring',
        'defence job quota', 'ex-serviceman quota'
    ],
    'rank_impersonation': [
        'Colonel', 'Major', 'Captain', 'Lieutenant', 'General',
        'Brigadier', 'Subedar', 'Havildar', 'Sepoy',
        'army officer', 'defence personnel'
    ],
    'cantonment_scams': [
        'cantonment pass', 'gate pass', 'MES', 'Military Engineering',
        'army quarters', 'defence accommodation',
        'cantonment board', 'station HQ'
    ],
    'honeytrap': [
        'lonely', 'friendship', 'chatting', 'meet you',
        'nice profile', 'army wife', 'defence family',
        'service person', 'regiment', 'battalion'
    ]
}

ARMY_RANKS = [
    'Field Marshal', 'General', 'Lieutenant General', 'Major General',
    'Brigadier', 'Colonel', 'Lieutenant Colonel', 'Major',
    'Captain', 'Lieutenant', 'Second Lieutenant',
    'Subedar Major', 'Subedar', 'Naib Subedar',
    'Havildar', 'Naik', 'Lance Naik', 'Sepoy'
]
```

**Enhanced AI Prompt:**
```python
def enhance_ai_with_army_context(content, content_type):
    """Add defence-specific context to AI analysis"""
    
    army_context = f"""
    SPECIAL CONTEXT: This is being analyzed for Indian Defence personnel.
    
    Common defence-targeted scams to check for:
    1. CSD Card Scams - Fake canteen card renewal/application
    2. Fake Army Recruitment - Fraudulent job offers
    3. Rank Impersonation - Scammers posing as Army officers
    4. Cantonment Scams - Fake gate passes, MES contracts
    5. Honeytrap Attacks - Social engineering targeting servicemen
    6. Aadhaar/PAN Linking - Fake urgent linking messages
    
    If any defence-related scam is detected:
    - Mark as military_relevant: true
    - Upgrade severity if needed
    - Add specific defence recommendations
    """
    
    return army_context
```

---

### ✅ Task 2: Geo-Intelligence Heatmap Data
**Priority: HIGH**
**Estimated Time: 3-4 hours**

**Module: `backend/modules/geo_intelligence.py`**

**Defence Command Regions:**
```python
DEFENCE_REGIONS = {
    'Northern Command': ['Jammu & Kashmir', 'Ladakh', 'Himachal Pradesh', 'Punjab', 'Chandigarh'],
    'Western Command': ['Rajasthan', 'Gujarat', 'Maharashtra (parts)'],
    'Eastern Command': ['West Bengal', 'Bihar', 'Jharkhand', 'Sikkim', 'Assam', 'Arunachal Pradesh'],
    'Southern Command': ['Karnataka', 'Kerala', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana'],
    'South Western Command': ['Maharashtra', 'Madhya Pradesh', 'Chhattisgarh', 'Goa'],
    'Central Command': ['Uttar Pradesh', 'Uttarakhand'],
    'Delhi Area': ['Delhi', 'NCR']
}

def map_location_to_command(location):
    """Map user location to defence command"""
    for command, states in DEFENCE_REGIONS.items():
        if any(state.lower() in location.lower() for state in states):
            return command
    return 'Unknown Region'
```

**New Endpoints:**
```python
@app.get("/api/geo/heatmap")
async def get_geo_heatmap():
    """
    Return incident count by defence command
    {
        "Northern Command": 12,
        "Western Command": 4,
        "Delhi Area": 9,
        ...
    }
    """
    pass

@app.get("/api/geo/trends")
async def get_geo_trends(days: int = 7):
    """Return geo trends over time"""
    pass
```

---

## 🟡 PHASE 3: OPERATIONAL FEATURES (Day 4-6)

### ✅ Task 7: Incident Lifecycle Management
**Priority: HIGH**
**Estimated Time: 4-5 hours**

**Module: `backend/modules/lifecycle_manager.py`**

**Status Workflow:**
```
pending → investigating → info_required → resolved
                ↓
            escalated → CERT review
```

**New Endpoints:**
```python
@app.post("/api/incidents/{id}/update_status")
async def update_status(id: str, status: str, notes: str):
    """
    Update incident status and log to timeline
    Status: pending, investigating, info_required, resolved, escalated
    """
    pass

@app.post("/api/incidents/{id}/assign")
async def assign_officer(id: str, officer_name: str):
    """Assign incident to CERT officer"""
    pass

@app.get("/api/incidents/{id}/timeline")
async def get_timeline(id: str):
    """
    Get full incident history
    [
        {"event": "created", "time": "...", "by": "citizen"},
        {"event": "assigned", "time": "...", "to": "Officer XYZ"},
        {"event": "status_changed", "from": "pending", "to": "investigating"}
    ]
    """
    pass
```

---

### ✅ Task 4: Fake Army Profile Detection
**Priority: MEDIUM**
**Estimated Time: 3-4 hours**

**Module: `backend/modules/army_profile_detector.py`**

**Detection Logic:**
```python
def detect_fake_army_profile(content):
    """
    Check for fake Army profile indicators:
    1. Rank mentioned + suspicious behavior
    2. Wrong phone number format (not 10 digits)
    3. Romance/honeytrap language
    4. Impersonation keywords
    5. Request for money/sensitive info
    """
    
    result = {
        'is_fake_profile': False,
        'confidence': 0,
        'identified_rank': None,
        'suspicious_behaviors': [],
        'reasoning': ''
    }
    
    # Check for Army ranks
    for rank in ARMY_RANKS:
        if rank.lower() in content.lower():
            result['identified_rank'] = rank
            result['confidence'] += 20
    
    # Check for honeytrap patterns
    honeytrap_score = 0
    for pattern in HONEYTRAP_PATTERNS:
        if pattern in content.lower():
            honeytrap_score += 15
            result['suspicious_behaviors'].append(f"Honeytrap pattern: {pattern}")
    
    # Check for money requests
    if any(word in content.lower() for word in ['money', 'transfer', 'payment', 'urgent help']):
        result['confidence'] += 30
        result['suspicious_behaviors'].append("Financial request detected")
    
    # Check phone number format
    phone_matches = re.findall(r'\d{10}', content)
    if not phone_matches and result['identified_rank']:
        result['confidence'] += 10
        result['suspicious_behaviors'].append("No valid phone number")
    
    if result['confidence'] >= 50:
        result['is_fake_profile'] = True
        result['reasoning'] = f"High confidence ({result['confidence']}%) fake Army profile detection"
    
    return result
```

---

### ✅ Task 5: Threat Clustering Engine
**Priority: MEDIUM**
**Estimated Time: 4-5 hours**

**Module: `backend/modules/threat_clustering.py`**

**Clustering Algorithm:**
```python
def cluster_threats():
    """
    Cluster incidents by:
    1. Domain similarity (same root domain)
    2. Message template (80%+ text similarity)
    3. Indicator patterns (overlapping red flags)
    4. Threat type + severity
    """
    
    # Get all unclustured incidents
    incidents = db.query("SELECT * FROM incidents WHERE cluster_id IS NULL")
    
    clusters = {}
    
    for incident in incidents:
        matched = False
        
        # Try to match with existing clusters
        for cluster_id, cluster_data in clusters.items():
            similarity = calculate_similarity(incident, cluster_data['samples'])
            
            if similarity > 0.8:  # 80% threshold
                # Add to cluster
                cluster_data['incidents'].append(incident.id)
                cluster_data['size'] += 1
                incident.cluster_id = cluster_id
                matched = True
                break
        
        if not matched:
            # Create new cluster
            new_cluster_id = f"CLU-{uuid.uuid4().hex[:8].upper()}"
            clusters[new_cluster_id] = {
                'id': new_cluster_id,
                'type': incident.type,
                'samples': [incident],
                'size': 1,
                'threat_level': incident.severity
            }
            incident.cluster_id = new_cluster_id
    
    # Save clusters to database
    for cluster_id, data in clusters.items():
        save_cluster(cluster_id, data)
    
    return clusters
```

**New Endpoint:**
```python
@app.get("/api/clusters")
async def get_clusters():
    """
    Return all threat clusters
    [
        {
            "id": "CLU-A1B2C3D4",
            "type": "sms",
            "summary": "KBC Lottery Scam Template",
            "size": 14,
            "threat_level": "high",
            "sample_content": "You won 50 lakh..."
        }
    ]
    """
    pass

@app.get("/api/clusters/{id}")
async def get_cluster_details(id: str):
    """Get all incidents in a cluster"""
    pass
```

---

## 🟢 PHASE 4: INTELLIGENCE & REPORTING (Day 6-8)

### ✅ Task 8: Weekly Threat Intelligence Summary
**Priority: MEDIUM**
**Estimated Time: 2-3 hours**

**Module: `backend/modules/intelligence_summary.py`**

**New Endpoint:**
```python
@app.get("/api/intelligence/weekly")
async def get_weekly_summary(days: int = 7):
    """
    Generate weekly threat intelligence briefing
    {
        "period": "Last 7 days",
        "total_incidents": 156,
        "most_reported_threat": {
            "content": "SBI phishing SMS",
            "count": 23,
            "cluster_id": "CLU-123"
        },
        "most_frequent_domain": {
            "domain": "fake-sbi.tk",
            "count": 18
        },
        "most_targeted_region": {
            "region": "Northern Command",
            "count": 34
        },
        "most_dangerous_cluster": {
            "id": "CLU-456",
            "size": 27,
            "threat_level": "critical"
        },
        "escalated_threats": 8,
        "defence_relevant_threats": 12
    }
    """
    pass
```

---

### ✅ Task 9: Bulk Reporting API
**Priority: MEDIUM**
**Estimated Time: 2-3 hours**

**New Endpoint:**
```python
@app.post("/api/incidents/bulk")
async def bulk_report(
    incidents: List[dict],
    unit_name: str = None,
    region: str = None
):
    """
    Bulk incident submission for Army units
    
    Input:
    {
        "unit_name": "32 Armoured Regiment",
        "region": "Northern Command",
        "incidents": [
            {"type": "sms", "content": "..."},
            {"type": "url", "content": "..."},
            {"type": "email", "content": "..."}
        ]
    }
    
    Output:
    {
        "total_submitted": 15,
        "analyzed": 15,
        "high_risk_count": 3,
        "escalated_count": 1,
        "results": [
            {"id": "INC-...", "risk_score": 85, ...}
        ]
    }
    """
    
    results = []
    for incident_data in incidents:
        # Analyze each incident
        analysis = await analyze_content(incident_data['content'], incident_data['type'])
        
        # Add metadata
        analysis['unit_name'] = unit_name
        analysis['geo_region'] = region
        
        # Save to DB
        incident_id = create_incident(analysis)
        results.append({"id": incident_id, **analysis})
    
    return {
        "total_submitted": len(incidents),
        "results": results,
        "high_risk_count": sum(1 for r in results if r['risk_score'] >= 60),
        "escalated_count": sum(1 for r in results if r.get('escalated_flag'))
    }
```

---

### ✅ Task 10: PDF Export Reports
**Priority: LOW (Optional)**
**Estimated Time: 4-5 hours**

**Module: `backend/modules/report_generator.py`**

**Dependencies:**
```bash
pip install reportlab
```

**New Endpoint:**
```python
@app.get("/api/incidents/{id}/export/pdf")
async def export_pdf_report(id: str):
    """
    Generate forensic PDF report
    
    Sections:
    1. Incident Header (ID, Date, Status, Risk Score)
    2. Content Analysis (Raw content, Type, Description)
    3. AI Analysis (Summary, Threat Type, Detailed Analysis)
    4. Indicators (Red flags list)
    5. Recommendations (Security advice)
    6. Technical Details (DNS info, URL check, Domain info)
    7. Timeline (Event history)
    8. Related Incidents (Similar threats)
    9. Cluster Information (If part of cluster)
    10. Officer Notes (If assigned)
    """
    
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    
    # Generate PDF
    pdf_path = f"/tmp/incident_{id}_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    
    # Add content sections
    # ... (PDF generation logic)
    
    c.save()
    
    return FileResponse(pdf_path, filename=f"RakshaNetra_Report_{id}.pdf")
```

---

## 🔵 PHASE 5: TESTING & VALIDATION (Day 8-9)

### ✅ Task 12: Testing & Validation
**Priority: HIGH**
**Estimated Time: 4-6 hours**

**Test Cases:**

```python
# Test 1: Threat Repetition Detection
def test_threat_repetition():
    # Submit same SMS 5 times
    # Verify frequency_count increases
    # Check related_incident_ids populated
    pass

# Test 2: Auto-Escalation
def test_auto_escalation():
    # Submit high-risk incident (score >= 85)
    # Verify escalated_flag = 1
    # Check escalation_reason
    pass

# Test 3: Geo-Mapping
def test_geo_intelligence():
    # Submit incidents from different regions
    # Call /api/geo/heatmap
    # Verify correct command mapping
    pass

# Test 4: Fake Army Profile
def test_army_profile_detection():
    content = "Hello, I am Colonel Sharma from 32 Armoured. Please send money urgently."
    result = detect_fake_army_profile(content)
    assert result['is_fake_profile'] == True
    assert result['identified_rank'] == 'Colonel'
    pass

# Test 5: Threat Clustering
def test_clustering():
    # Submit 10 similar KBC scam messages
    # Run clustering
    # Verify all assigned same cluster_id
    pass

# Test 6: Lifecycle Management
def test_lifecycle():
    # Create incident
    # Assign officer
    # Update status
    # Check timeline
    pass

# Test 7: Bulk API
def test_bulk_reporting():
    incidents = [
        {"type": "sms", "content": "scam1"},
        {"type": "url", "content": "http://fake.tk"}
    ]
    response = bulk_report(incidents, unit="Test Unit", region="Delhi Area")
    assert response['total_submitted'] == 2
    pass

# Test 8: PDF Export
def test_pdf_export():
    # Create incident
    # Generate PDF
    # Verify file exists and is valid PDF
    pass
```

---

## 📦 File Structure After Implementation

```
backend/
├── server.py                      # Main FastAPI server (existing)
├── rakshanetra.db                 # SQLite database (upgraded schema)
├── requirements.txt               # Add new dependencies
├── migrations/
│   └── upgrade_schema.py          # Database migration script
├── modules/                       # NEW - Defence feature modules
│   ├── __init__.py
│   ├── threat_matcher.py          # Feature 1: Repetition detection
│   ├── geo_intelligence.py        # Feature 2: Geo heatmap
│   ├── auto_escalation.py         # Feature 3: Auto-escalate
│   ├── army_profile_detector.py   # Feature 4: Fake Army detection
│   ├── threat_clustering.py       # Feature 5: Clustering
│   ├── army_ai_context.py         # Feature 6: Defence-aware AI
│   ├── lifecycle_manager.py       # Feature 7: Status management
│   ├── intelligence_summary.py    # Feature 8: Weekly reports
│   └── report_generator.py        # Feature 10: PDF export
└── tests/
    └── test_defence_features.py   # Feature tests
```

---

## 🚀 Implementation Order

### Critical Path (Must Do First):
1. ✅ **Task 11: Database Migration** (CRITICAL - Foundation)
2. ✅ **Task 1: Threat Repetition** (HIGH - Core intelligence)
3. ✅ **Task 3: Auto-Escalation** (HIGH - Operational workflow)
4. ✅ **Task 6: Army-Aware AI** (HIGH - Defence context)

### High Value (Do Next):
5. ✅ **Task 2: Geo-Intelligence** (HIGH - Command visibility)
6. ✅ **Task 7: Lifecycle Management** (HIGH - Real operations)
7. ✅ **Task 5: Threat Clustering** (MEDIUM - Pattern recognition)

### Medium Priority (Then):
8. ✅ **Task 4: Fake Army Profile** (MEDIUM - Social engineering)
9. ✅ **Task 8: Weekly Summary** (MEDIUM - Briefings)
10. ✅ **Task 9: Bulk API** (MEDIUM - Unit usage)

### Optional (If Time):
11. ✅ **Task 10: PDF Export** (LOW - Nice to have)
12. ✅ **Task 12: Testing** (HIGH - Validation)

---

## 📋 Dependencies to Add

```bash
pip install reportlab  # For PDF generation
pip install difflib    # For text similarity
pip install sklearn    # For advanced clustering (optional)
```

---

## ⚠️ Important Notes

1. **No UI work** - Focus purely on backend logic and APIs
2. **Modular design** - Each feature in separate module
3. **SQLite only** - No external database dependencies
4. **Test incrementally** - Test each feature after implementation
5. **Backward compatible** - Don't break existing functionality
6. **Document APIs** - Update FastAPI docs for new endpoints

---

## 🎯 Success Criteria

- ✅ All 10 defence features working
- ✅ Database schema upgraded without data loss
- ✅ All new API endpoints functional
- ✅ Test cases passing
- ✅ No breaking changes to existing code
- ✅ Performance maintained (< 1s response time)

---

**READY TO START IMPLEMENTATION?**

Say:
- **"START"** to begin with Task 11 (Database Migration)
- **"SKIP TO X"** to start with specific feature
- **"REVIEW PLAN"** if you need clarification
