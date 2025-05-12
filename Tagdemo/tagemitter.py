#!/usr/bin/env python
from datahub.emitter.mce_builder import make_tag_urn
from datahub.metadata.schema_classes import TagPropertiesClass
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig

def create_tag(
    graph,
    tag_name,
    description=None,
    color=None
):
    """
    Create a tag using the DataHub emitter.
    
    Args:
        graph: DataHubGraph instance
        tag_name: Name of the tag
        description: Optional description for the tag
        color: Optional color for the tag (hex format e.g. "#FF0000")
    """
    # Create tag URN
    tag_urn = make_tag_urn(tag_name)
    
    # Create tag properties aspect
    tag_properties = TagPropertiesClass(
        name=tag_name,
        description=description if description else "",
        colorHex=color if color else "#000000"
    )
    
    # Create metadata change proposal
    event = MetadataChangeProposalWrapper(
        entityUrn=tag_urn,
        aspectName="tagProperties",
        aspect=tag_properties
    )
    
    # Emit the event
    print(f"Creating tag: {tag_name}")
    graph.emit(event)
    print(f"Tag '{tag_name}' created successfully!")
    
    return tag_urn

def main():
    # DataHub connection configuration
    server = "https://test-environment.acryl.io/gms"
    token = "token"  # Replace with your actual token
    
    # Create DataHub graph client
    graph = DataHubGraph(DatahubClientConfig(
        server=server,
        token=token
    ))
    
    # Define tags to create
    tags_to_create = [
        {
            "name": "PII",
            "description": "Contains personally identifiable information",
            "color": "#FF0000"  # Red color
        },
        {
            "name": "Deprecated",
            "description": "Resource marked for deprecation",
            "color": "#FFA500"  # Orange color
        },
        {
            "name": "Important",
            "description": "Critical business data",
            "color": "#0000FF"  # Blue color
        },
        {
            "name": "Tested",
            "description": "Validated data",
            "color": "#008000"  # Green color
        },
        {
            "name": "Experimental",
            "description": "Data in experimental stage",
            "color": "#800080"  # Purple color
        },
    ]
    
    # Create each tag
    created_tags = []
    for tag_info in tags_to_create:
        try:
            tag_urn = create_tag(
                graph=graph,
                tag_name=tag_info["name"],
                description=tag_info["description"],
                color=tag_info["color"]
            )
            created_tags.append((tag_info["name"], tag_urn))
        except Exception as e:
            print(f"Error creating tag '{tag_info['name']}': {e}")
    
    # Print summary
    print("\nCreated tags summary:")
    for name, urn in created_tags:
        print(f"- {name} (URN: {urn})")

if __name__ == "__main__":
    main()
