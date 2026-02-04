#!/usr/bin/env python3
"""
FleetBringUp CLI entry point.
Orchestrates server bring-up validation workflows.
"""

import click
import sys
import logging
from pathlib import Path
from datetime import datetime

from runner.test_orchestrator import TestOrchestrator
from runner.config_loader import ConfigLoader


def setup_logging(server_id: str, output_dir: Path) -> logging.Logger:
    """Configure structured logging for validation run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = output_dir / f"{server_id}_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("fleetbringup")
    logger.info(f"Logging to {log_file}")
    return logger


@click.group()
def cli():
    """FleetBringUp - Automated server bring-up validation framework."""
    pass


@cli.command()
@click.option('--server-id', required=True, help='Server identifier (e.g., svr-12345)')
@click.option('--config', required=True, type=click.Path(exists=True), help='Test plan YAML config')
@click.option('--output-dir', default='reports', help='Output directory for results')
def validate(server_id: str, config: str, output_dir: str):
    """Run validation suite on a single server."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    logger = setup_logging(server_id, output_path)
    logger.info(f"Starting validation for {server_id}")
    logger.info(f"Test plan: {config}")
    
    try:
        # Load test configuration
        config_loader = ConfigLoader(config)
        test_plan = config_loader.load()
        
        # Initialize orchestrator
        orchestrator = TestOrchestrator(server_id, test_plan, output_path)
        
        # Run validation
        results = orchestrator.run()
        
        # Report outcome
        if results['overall_status'] == 'PASS':
            logger.info(f"✓ Validation PASSED for {server_id}")
            sys.exit(0)
        else:
            logger.error(f"✗ Validation FAILED for {server_id}")
            if 'failure_summary' in results:
                logger.error(f"  Subsystem: {results['failure_summary']['subsystem']}")
                logger.error(f"  Root cause: {results['failure_summary']['root_cause']}")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"Validation failed with exception: {e}")
        sys.exit(2)


@cli.command()
@click.option('--server-list', required=True, type=click.Path(exists=True), 
              help='File containing server IDs (one per line)')
@click.option('--config', required=True, type=click.Path(exists=True), help='Test plan YAML config')
@click.option('--output-dir', default='reports', help='Output directory for results')
def validate_fleet(server_list: str, config: str, output_dir: str):
    """Run validation suite on multiple servers (batch mode)."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Read server list
    with open(server_list, 'r') as f:
        servers = [line.strip() for line in f if line.strip()]
    
    logger = logging.getLogger("fleetbringup")
    logger.info(f"Fleet validation: {len(servers)} servers")
    
    passed = 0
    failed = 0
    
    for server_id in servers:
        logger.info(f"\n{'='*60}")
        logger.info(f"Validating {server_id}")
        logger.info(f"{'='*60}")
        
        try:
            config_loader = ConfigLoader(config)
            test_plan = config_loader.load()
            
            orchestrator = TestOrchestrator(server_id, test_plan, output_path)
            results = orchestrator.run()
            
            if results['overall_status'] == 'PASS':
                passed += 1
                logger.info(f"✓ {server_id} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {server_id} FAILED")
                
        except Exception as e:
            failed += 1
            logger.exception(f"✗ {server_id} FAILED with exception: {e}")
    
    # Fleet summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Fleet Validation Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Total servers: {len(servers)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {100*passed/len(servers):.1f}%")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    cli()
