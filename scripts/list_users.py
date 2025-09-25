#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to list all users from an Openfire server using the ofrestapi library.
"""

import sys
import os
import json
import click
from typing import Optional

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users


@click.command()
@click.option(
    "--host",
    default="https://localhost:9091",
    help="Openfire server URL (e.g., https://localhost:9091)",
)
@click.option(
    "--token",
    required=True,
    help="API token for authentication",
)
@click.option(
    "--search",
    help="Optional search filter for usernames (acts like wildcard search)",
)
@click.option(
    "--insecure/--secure",
    default=False,
    help="Disable SSL certificate validation (for self-signed certificates)",
)
@click.option(
    "--output",
    type=click.Choice(["json", "table", "csv"]),
    default="table",
    help="Output format",
)
def list_users(host: str, token: str, search: Optional[str], insecure: bool, output: str) -> None:
    """
    List all users from the Openfire server.
    
    This script connects to an Openfire server and retrieves a list of all users,
    with an optional search filter.
    """
    try:
        # Create Users API client
        users_api = Users(host, token)
        
        # Handle SSL verification
        if insecure:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Monkey patch the requests module
            import requests
            old_request = requests.Session.request
            def new_request(self, method, url, **kwargs):
                kwargs['verify'] = False
                return old_request(self, method, url, **kwargs)
            requests.Session.request = new_request
            
            # Also patch the base requests functions
            old_get = requests.get
            old_post = requests.post
            old_put = requests.put
            old_delete = requests.delete
            
            def new_get(url, **kwargs):
                kwargs['verify'] = False
                return old_get(url, **kwargs)
            
            def new_post(url, **kwargs):
                kwargs['verify'] = False
                return old_post(url, **kwargs)
            
            def new_put(url, **kwargs):
                kwargs['verify'] = False
                return old_put(url, **kwargs)
            
            def new_delete(url, **kwargs):
                kwargs['verify'] = False
                return old_delete(url, **kwargs)
            
            requests.get = new_get
            requests.post = new_post
            requests.put = new_put
            requests.delete = new_delete
            
            click.echo("Warning: SSL certificate validation is disabled", err=True)
        
        # Get users with optional search filter
        result = users_api.get_users(search)
        
        # Process the result based on its structure
        users_list = []
        if isinstance(result, dict) and 'users' in result:
            if isinstance(result['users'], list):
                users_list = result['users']
            elif isinstance(result['users'], dict) and 'user' in result['users']:
                users_list = result['users']['user']
        elif isinstance(result, list):
            users_list = result
        
        # Display results in the requested format
        if output == "json":
            click.echo(json.dumps(users_list, indent=2))
        elif output == "csv":
            # Print CSV header
            if users_list:
                headers = ["username", "name", "email"]
                click.echo(",".join(headers))
                
                # Print each user as a CSV row
                for user in users_list:
                    values = [
                        user.get("username", ""),
                        user.get("name", ""),
                        user.get("email", "")
                    ]
                    click.echo(",".join(values))
        else:  # table format
            if not users_list:
                click.echo("No users found.")
                return
                
            # Determine column widths
            username_width = max(8, max(len(user.get("username", "")) for user in users_list))
            name_width = max(4, max(len(user.get("name", "")) for user in users_list))
            email_width = max(5, max(len(user.get("email", "")) for user in users_list))
            
            # Print table header
            click.echo(f"{'USERNAME':<{username_width}} | {'NAME':<{name_width}} | {'EMAIL':<{email_width}}")
            click.echo(f"{'-' * username_width} | {'-' * name_width} | {'-' * email_width}")
            
            # Print each user
            for user in users_list:
                username = user.get("username", "")
                name = user.get("name", "")
                email = user.get("email", "")
                click.echo(f"{username:<{username_width}} | {name:<{name_width}} | {email:<{email_width}}")
            
            # Print summary
            click.echo(f"\nTotal users: {len(users_list)}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    list_users()
