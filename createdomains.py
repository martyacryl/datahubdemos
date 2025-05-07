import logging
import yaml
import sys
from datahub.emitter.mce_builder import make_domain_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import ChangeTypeClass, DomainPropertiesClass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def create_domain(emitter, domain_id, name, description=None, parent_domain_id=None):
    """
    Create a domain in DataHub
    
    Args:
        emitter: The DataHub REST emitter
        domain_id: The ID of the domain to create
        name: The display name of the domain
        description: Optional description of the domain
        parent_domain_id: Optional parent domain ID
    """
    domain_urn = make_domain_urn(domain_id)
    
    # Create parent domain reference if specified
    parent_domain_urn = make_domain_urn(parent_domain_id) if parent_domain_id else None
    
    # Create domain properties
    domain_properties = DomainPropertiesClass(
        name=name,
        description=description or "",
        parentDomain=parent_domain_urn
    )
    
    # Create metadata change proposal
    event = MetadataChangeProposalWrapper(
        entityType="domain",
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=domain_urn,
        aspect=domain_properties
    )
    
    # Emit the event
    emitter.emit(event)
    
    # Log creation
    if parent_domain_id:
        log.info(f"Created domain '{name}' (id: {domain_id}) as subdomain of {parent_domain_id}")
    else:
        log.info(f"Created domain '{name}' (id: {domain_id})")
    
    return domain_urn

def main(config_file):
    """
    Main function to read config and create domains
    
    Args:
        config_file: Path to the YAML config file
    """
    try:
        # Load the configuration file
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize the DataHub REST emitter
        # Initialize the DataHub REST emitter
        gms_server = config.get('gms_server', 'http://test-environment.acryl.io/gms')
        token = config.get('token')  # Get token from config
        
        emitter_kwargs = {'gms_server': gms_server}
        if token:
            emitter_kwargs['token'] = token
        
        emitter = DatahubRestEmitter(**emitter_kwargs)
        
        # Test connection
        try:
            emitter.test_connection()
            log.info(f"Successfully connected to DataHub at {gms_server}")
        except Exception as e:
            log.error(f"Failed to connect to DataHub: {e}")
            return 1
        
        # Process domains
        domains_created = 0
        
        # First pass: create all top-level domains
        for domain in config.get('domains', []):
            if not domain.get('parent_domain'):
                try:
                    create_domain(
                        emitter=emitter,
                        domain_id=domain['id'],
                        name=domain['name'],
                        description=domain.get('description')
                    )
                    domains_created += 1
                except Exception as e:
                    log.error(f"Error creating domain {domain['id']}: {e}")
        
        # Second pass: create all subdomains
        for domain in config.get('domains', []):
            if domain.get('parent_domain'):
                try:
                    create_domain(
                        emitter=emitter,
                        domain_id=domain['id'],
                        name=domain['name'],
                        description=domain.get('description'),
                        parent_domain_id=domain['parent_domain']
                    )
                    domains_created += 1
                except Exception as e:
                    log.error(f"Error creating subdomain {domain['id']}: {e}")
        
        log.info(f"Created {domains_created} domains/subdomains successfully")
        return 0
    
    except Exception as e:
        log.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_domains.py <config_file.yaml>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    sys.exit(main(config_file))