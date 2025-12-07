"""
Database Schema Upgrade for RakshaNetra Defence Features
Adds columns for threat repetition, geo-intelligence, escalation, clustering, and lifecycle management
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rakshanetra.db")

def backup_database():
    """Create backup before migration"""
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    return None

def upgrade_incidents_table(conn):
    """Add new columns to incidents table"""
    print("📊 Upgrading incidents table...")
    
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(incidents)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Define new columns to add
    new_columns = [
        ("frequency_count", "INTEGER DEFAULT 1"),
        ("related_incident_ids", "TEXT"),  # JSON array
        ("cluster_id", "TEXT"),
        ("geo_region", "TEXT"),
        ("escalated_flag", "INTEGER DEFAULT 0"),
        ("escalation_reason", "TEXT"),
        ("escalate_timestamp", "TEXT"),
        ("assigned_officer", "TEXT"),
        ("status_history", "TEXT"),  # JSON array
        ("military_relevant", "INTEGER DEFAULT 0"),
        ("fake_profile_detected", "INTEGER DEFAULT 0"),
        ("unit_name", "TEXT"),
        ("officer_notes", "TEXT")
    ]
    
    # Add columns that don't exist
    added_count = 0
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE incidents ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added column: {col_name}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  Column {col_name} might already exist: {e}")
    
    conn.commit()
    print(f"✅ Added {added_count} new columns to incidents table")

def create_threat_clusters_table(conn):
    """Create threat_clusters table"""
    print("📊 Creating threat_clusters table...")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS threat_clusters (
            id TEXT PRIMARY KEY,
            cluster_type TEXT,
            cluster_summary TEXT,
            cluster_size INTEGER DEFAULT 1,
            first_seen TEXT,
            last_seen TEXT,
            sample_incidents TEXT,
            threat_level TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    print("✅ threat_clusters table created")

def create_incident_timeline_table(conn):
    """Create incident_timeline table"""
    print("📊 Creating incident_timeline table...")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incident_timeline (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            event_type TEXT,
            event_description TEXT,
            performed_by TEXT,
            timestamp TEXT,
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
        )
    """)
    conn.commit()
    print("✅ incident_timeline table created")

def create_geo_statistics_table(conn):
    """Create geo_statistics table"""
    print("📊 Creating geo_statistics table...")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS geo_statistics (
            id TEXT PRIMARY KEY,
            region TEXT NOT NULL,
            date TEXT NOT NULL,
            incident_count INTEGER DEFAULT 0,
            high_severity_count INTEGER DEFAULT 0,
            escalated_count INTEGER DEFAULT 0,
            updated_at TEXT,
            UNIQUE(region, date)
        )
    """)
    conn.commit()
    print("✅ geo_statistics table created")

def create_indexes(conn):
    """Create indexes for better performance"""
    print("📊 Creating indexes...")
    
    indexes = [
        ("idx_cluster_id", "incidents", "cluster_id"),
        ("idx_geo_region", "incidents", "geo_region"),
        ("idx_escalated", "incidents", "escalated_flag"),
        ("idx_created_at", "incidents", "created_at"),
        ("idx_status", "incidents", "status"),
        ("idx_severity", "incidents", "severity"),
        ("idx_timeline_incident", "incident_timeline", "incident_id"),
        ("idx_geo_stats_region", "geo_statistics", "region"),
        ("idx_geo_stats_date", "geo_statistics", "date")
    ]
    
    for idx_name, table_name, column_name in indexes:
        try:
            conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
            print(f"  ✅ Created index: {idx_name}")
        except sqlite3.OperationalError as e:
            print(f"  ⚠️  Index {idx_name} might already exist: {e}")
    
    conn.commit()
    print("✅ Indexes created")

def run_migration():
    """Run the complete migration"""
    print("\n" + "="*60)
    print("🚀 RakshaNetra Defence Features - Database Migration")
    print("="*60 + "\n")
    
    # Backup database
    backup_path = backup_database()
    
    # Connect to database
    if not os.path.exists(DB_PATH):
        print("❌ Database not found! Please run server.py first to create initial database.")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Run all migrations
        upgrade_incidents_table(conn)
        create_threat_clusters_table(conn)
        create_incident_timeline_table(conn)
        create_geo_statistics_table(conn)
        create_indexes(conn)
        
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        
        if backup_path:
            print(f"\n💾 Backup available at: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"💾 Database backup available at: {backup_path}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
