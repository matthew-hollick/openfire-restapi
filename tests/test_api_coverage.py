#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for verifying API coverage against OpenAPI specification.
This script analyzes the Python client implementation and compares it with
the OpenAPI specification to identify missing endpoints.
"""

import os
import sys
import yaml
import inspect
import argparse
from typing import Dict, Any, List, Tuple

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users, Groups, System, Sessions, Messages, Muc


def load_openapi_spec(spec_file: str) -> Dict[str, Any]:
    """
    Load OpenAPI specification from YAML file.
    
    Args:
        spec_file: Path to OpenAPI YAML file
        
    Returns:
        Dictionary containing the OpenAPI specification
    """
    try:
        with open(spec_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading OpenAPI spec: {e}")
        sys.exit(1)


def extract_endpoints_from_spec(spec: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract endpoints from OpenAPI specification.
    
    Args:
        spec: OpenAPI specification dictionary
        
    Returns:
        Dictionary mapping endpoint paths to their methods and operations
    """
    endpoints = {}
    
    for path, path_item in spec.get('paths', {}).items():
        if path.startswith('/restapi/v1/'):
            endpoints[path] = []
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete']:
                    endpoints[path].append({
                        'method': method,
                        'operationId': operation.get('operationId', ''),
                        'summary': operation.get('summary', ''),
                        'tags': operation.get('tags', [])
                    })
    
    return endpoints


def extract_endpoints_from_client(module_classes: List[Tuple[str, type]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract endpoints from Python client implementation.
    
    Args:
        module_classes: List of (name, class) tuples from the client library
        
    Returns:
        Dictionary mapping endpoint paths to their methods
    """
    endpoints = {}
    
    for name, cls in module_classes:
        # Skip base class
        if name == 'Base':
            continue
            
        # Create instance with dummy values to inspect
        instance = cls('http://localhost', 'dummy_secret')
        base_endpoint = instance.endpoint
        
        # Get all methods that are not internal or inherited from object
        for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not method_name.startswith('_') and method_name not in dir(object):
                # Inspect the method source code to find endpoints
                source = inspect.getsource(method)
                
                # Extract endpoint construction patterns
                if "endpoint = '/'.join([self.endpoint" in source:
                    # This is a method that constructs an endpoint
                    endpoints.setdefault(base_endpoint, []).append({
                        'method_name': method_name,
                        'source': source
                    })
                elif "return self._submit_request" in source and "self.endpoint" in source:
                    # This is a method that uses the base endpoint directly
                    endpoints.setdefault(base_endpoint, []).append({
                        'method_name': method_name,
                        'source': source
                    })
    
    return endpoints


def analyze_coverage(spec_endpoints: Dict[str, List[Dict[str, Any]]], 
                    client_endpoints: Dict[str, List[Dict[str, Any]]]) -> Tuple[List[str], List[str]]:
    """
    Analyze API coverage by comparing OpenAPI spec with client implementation.
    
    Args:
        spec_endpoints: Endpoints from OpenAPI spec
        client_endpoints: Endpoints from client implementation
        
    Returns:
        Tuple of (covered_endpoints, missing_endpoints)
    """
    covered = []
    missing = []
    
    # Convert client endpoints to a set of base paths
    client_base_paths = set(client_endpoints.keys())
    
    # Check each spec endpoint
    for path, operations in spec_endpoints.items():
        # Extract the base path (e.g., /restapi/v1/users)
        parts = path.split('/')
        if len(parts) >= 4:
            base_path = '/'.join(parts[:4])
            
            # Check if this base path is covered by the client
            if any(base_path in client_path for client_path in client_base_paths):
                covered.append(path)
            else:
                missing.append(path)
    
    return covered, missing


def main():
    parser = argparse.ArgumentParser(description='Analyze API coverage against OpenAPI spec')
    parser.add_argument('--spec', default='openapi.yaml',
                        help='Path to OpenAPI specification file (default: openapi.yaml)')
    
    args = parser.parse_args()
    
    # Load OpenAPI spec
    spec = load_openapi_spec(args.spec)
    spec_endpoints = extract_endpoints_from_spec(spec)
    
    # Get client modules
    client_modules = [
        ('Users', Users),
        ('Groups', Groups),
        ('System', System),
        ('Sessions', Sessions),
        ('Messages', Messages),
        ('Muc', Muc)
    ]
    client_endpoints = extract_endpoints_from_client(client_modules)
    
    # Analyze coverage
    covered, missing = analyze_coverage(spec_endpoints, client_endpoints)
    
    # Print results
    print("=== API Coverage Analysis ===")
    print(f"Total endpoints in OpenAPI spec: {len(spec_endpoints)}")
    print(f"Endpoints covered by client: {len(covered)}")
    print(f"Endpoints missing from client: {len(missing)}")
    
    if missing:
        print("\n=== Missing Endpoints ===")
        for path in sorted(missing):
            operations = spec_endpoints[path]
            for op in operations:
                print(f"{op['method'].upper()} {path} - {op['summary']} (tags: {', '.join(op['tags'])})")
    
    # Calculate coverage percentage
    coverage_pct = (len(covered) / len(spec_endpoints)) * 100 if spec_endpoints else 0
    print(f"\nAPI Coverage: {coverage_pct:.2f}%")
    
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
