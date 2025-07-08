import click
import os
import sys
import json
from .config import Config
from .metadata_generator import MetadataGenerator

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """DataHub Metadata Generator CLI"""
    pass

@cli.command()
@click.option('--output', '-o', default='generated_metadata.json', help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate(output, verbose):
    """Generate metadata for DataHub ingestion"""
    
    if verbose:
        click.echo("🔧 Configuration:")
        click.echo(f"  Output file: {output}")
        click.echo()
    
    config = Config()
    config.generator.output_file = output
    
    try:
        generator = MetadataGenerator(config)
        click.echo("🚀 Starting metadata generation...")
        metadata_records = generator.generate()
        output_path = generator.save_to_file(output)
        stats = generator.get_statistics()
        
        click.echo("\n📊 Generation Statistics:")
        click.echo(f"  Total records: {stats['total_records']}")
        click.echo(f"  Entity types: {stats['entity_types']}")
        click.echo(f"  Output file: {output_path}")
        
        click.echo("\n✅ Metadata generation completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error generating metadata: {e}", err=True)
        sys.exit(1)

@cli.command()
def config():
    """Show current configuration"""
    config = Config()
    config.print_config()

@cli.command()
@click.option('--file', '-f', default='generated_metadata.json', help='Metadata file to preview')
@click.option('--lines', '-n', default=5, type=int, help='Number of lines to preview')
def preview(file, lines):
    """Preview generated metadata file"""
    
    if not os.path.exists(file):
        click.echo(f"❌ Metadata file not found: {file}", err=True)
        sys.exit(1)
    
    try:
        click.echo(f"👀 Previewing first {lines} records from {file}:")
        click.echo("=" * 50)
        
        with open(file, 'r') as f:
            for i, line in enumerate(f):
                if i >= lines:
                    break
                
                record = json.loads(line.strip())
                click.echo(f"Record {i+1}:")
                click.echo(f"  Entity Type: {record.get('entityType', 'N/A')}")
                click.echo(f"  Entity URN: {record.get('entityUrn', 'N/A')}")
                click.echo(f"  Aspect: {record.get('aspectName', 'N/A')}")
                click.echo()
            
    except Exception as e:
        click.echo(f"❌ Error previewing file: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
