"""
Sync MITRE ATT&CK data from TAXII server into local database
Run this script to populate techniques, sub-techniques, detection strategies, etc.
"""

from taxii2client.v21 import Server, as_pages
from stix2 import MemoryStore
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.attack_data import (
    Technique, SubTechnique, DetectionStrategy, 
    Analytic, DataComponent, ThreatGroup
)
from datetime import datetime
import os

# TAXII Configuration
TAXII_SERVER = os.getenv("ATTACK_TAXII_SERVER", "https://cti-taxii.mitre.org/taxii/")
COLLECTION_ID = os.getenv("ATTACK_COLLECTION_ID", "95ecc380-afe9-11e4-9b6c-751b66dd541e")

def fetch_attack_data():
    """Fetch all ATT&CK objects from TAXII server"""
    print(f"Connecting to TAXII server: {TAXII_SERVER}")
    server = Server(TAXII_SERVER)
    api_root = server.api_roots[0]
    collection = api_root.get_collection(COLLECTION_ID)
    
    print(f"Fetching ATT&CK data from collection: {collection.title}")
    store = MemoryStore()
    
    # Fetch all objects
    for bundle in as_pages(collection.get_objects, per_request=100):
        store.add(bundle)
    
    return store

def sync_techniques(db: Session, store: MemoryStore):
    """Sync techniques and sub-techniques"""
    print("Syncing techniques...")
    
    # Clear existing data
    db.query(SubTechnique).delete()
    db.query(Technique).delete()
    
    # Get all attack-patterns (techniques)
    patterns = store.query([("type", "=", "attack-pattern")])
    
    for pattern in patterns:
        # Check if it's a sub-technique (has x_mitre_is_subtechnique)
        is_sub = pattern.get('x_mitre_is_subtechnique', False)
        
        # Extract external references for technique ID
        ext_refs = pattern.get('external_references', [])
        tech_id = None
        for ref in ext_refs:
            if ref.get('source_name') == 'mitre-attack':
                tech_id = ref.get('external_id')
                break
        
        if not tech_id:
            continue
        
        # Extract platforms
        platforms = pattern.get('x_mitre_platforms', [])
        
        if is_sub:
            # It's a sub-technique
            parent_id = tech_id.split('.')[0] if '.' in tech_id else None
            sub_tech = SubTechnique(
                technique_id=tech_id,
                parent_technique_id=parent_id,
                name=pattern.get('name', ''),
                description=pattern.get('description', ''),
                platforms=platforms
            )
            db.add(sub_tech)
        else:
            # It's a main technique
            # Extract tactics (kill chain phases)
            tactics = []
            for phase in pattern.get('kill_chain_phases', []):
                if phase.get('kill_chain_name') == 'mitre-attack':
                    tactics.append(phase.get('phase_name', ''))
            
            tech = Technique(
                technique_id=tech_id,
                name=pattern.get('name', ''),
                description=pattern.get('description', ''),
                tactics=tactics,
                platforms=platforms,
                detection_description=pattern.get('x_mitre_detection', ''),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(tech)
    
    db.commit()
    print(f"Synced {db.query(Technique).count()} techniques and {db.query(SubTechnique).count()} sub-techniques")

def sync_data_components(db: Session, store: MemoryStore):
    """Sync data components and data sources"""
    print("Syncing data components...")
    
    db.query(DataComponent).delete()
    
    # Get all data components (x-mitre-data-component)
    components = store.query([("type", "=", "x-mitre-data-component")])
    
    for comp in components:
        ext_refs = comp.get('external_references', [])
        comp_id = None
        for ref in ext_refs:
            if ref.get('source_name') == 'mitre-attack':
                comp_id = ref.get('external_id')
                break
        
        if not comp_id:
            continue
        
        data_comp = DataComponent(
            component_id=comp_id,
            name=comp.get('name', ''),
            description=comp.get('description', ''),
            data_source_name=comp.get('x_mitre_data_source_ref', ''),
            log_source_type='',
            collection_requirements={}
        )
        db.add(data_comp)
    
    db.commit()
    print(f"Synced {db.query(DataComponent).count()} data components")

def sync_threat_groups(db: Session, store: MemoryStore):
    """Sync threat groups (intrusion sets)"""
    print("Syncing threat groups...")
    
    db.query(ThreatGroup).delete()
    
    groups = store.query([("type", "=", "intrusion-set")])
    
    for group in groups:
        ext_refs = group.get('external_references', [])
        group_id = None
        for ref in ext_refs:
            if ref.get('source_name') == 'mitre-attack':
                group_id = ref.get('external_id')
                break
        
        if not group_id:
            continue
        
        threat_group = ThreatGroup(
            group_id=group_id,
            name=group.get('name', ''),
            aliases=group.get('aliases', []),
            description=group.get('description', ''),
            target_industries=[],
            techniques_used=[]
        )
        db.add(threat_group)
    
    db.commit()
    print(f"Synced {db.query(ThreatGroup).count()} threat groups")

def main():
    """Main sync function"""
    print("Starting MITRE ATT&CK data sync...")
    
    # Fetch data from TAXII
    store = fetch_attack_data()
    
    # Create DB session
    db = SessionLocal()
    
    try:
        # Sync all entities
        sync_techniques(db, store)
        sync_data_components(db, store)
        sync_threat_groups(db, store)
        
        print("\n✅ MITRE ATT&CK data sync completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
