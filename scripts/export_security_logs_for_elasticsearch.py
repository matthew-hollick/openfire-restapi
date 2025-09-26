#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export Openfire security audit logs and send them to a Filebeat HTTP endpoint.

This script connects to an Openfire server, retrieves security audit logs,
and sends them to a Filebeat HTTP endpoint for further processing.
"""

import sys
import os
import json
import socket
import requests
import click
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import re

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import SecurityAuditLog, System


def parse_relative_time(time_str: str) -> Tuple[int, int]:
    """
    Parse a relative time string and return start and end timestamps.
    
    Supported formats:
    - Xm: X minutes ago
    - Xh: X hours ago
    - Xd: X days ago
    - Xw: X weeks ago
    
    Args:
        time_str: Relative time string (e.g., '1h', '30m', '2d')
        
    Returns:
        Tuple of (start_timestamp, end_timestamp) in seconds since epoch
    
    Raises:
        ValueError: If the time string format is invalid
    """
    # Regular expression to match the time string format
    pattern = re.compile(r'^(\d+)([mhdw])$')
    match = pattern.match(time_str)
    
    if not match:
        raise ValueError(f"Invalid time format: {time_str}. Expected format: <number><unit> (e.g., '1h', '30m', '2d', '1w')")
    
    value = int(match.group(1))
    unit = match.group(2)
    
    # Current time
    now = datetime.now()
    
    # Calculate start time based on the unit
    if unit == 'm':  # minutes
        start_time = now - timedelta(minutes=value)
    elif unit == 'h':  # hours
        start_time = now - timedelta(hours=value)
    elif unit == 'd':  # days
        start_time = now - timedelta(days=value)
    elif unit == 'w':  # weeks
        start_time = now - timedelta(weeks=value)
    else:
        raise ValueError(f"Invalid time unit: {unit}. Expected one of: m, h, d, w")
    
    # Convert to timestamps (seconds since epoch)
    start_timestamp = int(start_time.timestamp())
    end_timestamp = int(now.timestamp())
    
    return start_timestamp, end_timestamp


def prepare_log_for_filebeat(log: Dict[str, Any], host_info: Dict[str, str]) -> Dict[str, Any]:
    """
    Prepare a security audit log entry for Filebeat.
    
    Args:
        log: The security audit log entry
        host_info: Dictionary with hostname and server information
        
    Returns:
        Dictionary with the log entry formatted for Filebeat
    """
    # Get the raw timestamp value (in seconds) from the log
    timestamp_seconds = log.get('timestamp', 0)
    # Ensure it's a number
    try:
        timestamp_seconds = int(timestamp_seconds)
    except (ValueError, TypeError):
        timestamp_seconds = 0
        
    # Create an ISO-formatted timestamp
    timestamp = datetime.fromtimestamp(timestamp_seconds, timezone.utc).isoformat()
    
    result = {
        "log_id": log.get("logId"),
        "username": log.get("username"),
        "summary": log.get("summary"),
        "details": log.get("details"),
        "node": log.get("node"),
        "timestamp_ms": log.get("timestamp"),
        "@timestamp": timestamp,
        "host": {
            "name": host_info.get("hostname"),
        },
        "openfire": {
            "server": host_info.get("server")
        }
    }
    
    # Add xmpp_domain if available
    if host_info.get("xmpp_domain"):
        result["openfire"]["domain"] = host_info.get("xmpp_domain")
        
    return result


def send_to_filebeat(logs: List[Dict[str, Any]], url: Optional[str], host_info: Dict[str, str], insecure: bool, dry_run: bool = False) -> Dict[str, Any]:
    """
    Send security audit log entries to a Filebeat HTTP endpoint.
    
    Args:
        logs: List of security audit log entries
        url: URL of the Filebeat HTTP endpoint
        host_info: Dictionary with hostname and server information
        insecure: Whether to disable SSL certificate validation
        dry_run: If True, only show the data that would be sent without actually sending it
        
    Returns:
        Dictionary with success and failure counts
    """
    results = {"success": 0, "failure": 0, "failed_logs": []}
    
    for log in logs:
        try:
            # Prepare the log data for Filebeat
            data = prepare_log_for_filebeat(log, host_info)
            
            # In dry run mode, just print the data without sending
            if dry_run:
                click.echo(f"\nDRY RUN: Data that would be sent for log ID {log.get('logId')}:")
                click.echo(json.dumps(data, indent=2))
                results["success"] += 1
                continue
            
            # For actual sending, URL must be provided
            if not url:
                # This should never happen due to earlier checks, but just in case
                click.echo(f"Error: Cannot send log {log.get('logId')} - URL is required", err=True)
                results["failure"] += 1
                results["failed_logs"].append(log.get("logId"))
                continue
                
            # Send the data to Filebeat
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                verify=not insecure,
                timeout=10  # Add timeout to prevent hanging on network issues
            )
            
            # Check if the request was successful
            if response.status_code >= 200 and response.status_code < 300:
                results["success"] += 1
            else:
                results["failure"] += 1
                results["failed_logs"].append(log.get("logId"))
                click.echo(f"Failed to send log {log.get('logId')}: {response.status_code} {response.text}", err=True)
        except Exception as e:
            results["failure"] += 1
            results["failed_logs"].append(log.get("logId"))
            click.echo(f"Error sending log {log.get('logId')}: {e}", err=True)
    
    return results


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
    "--username",
    help="Optional username to filter logs",
)
@click.option(
    "--limit",
    default=100,
    help="Maximum number of logs to retrieve",
)
@click.option(
    "--start-time",
    type=int,
    help="Start timestamp in seconds since epoch",
    envvar="EXPORT_SECURITY_LOGS_START_TIME",
)
@click.option(
    "--end-time",
    type=int,
    help="End timestamp in seconds since epoch",
    envvar="EXPORT_SECURITY_LOGS_END_TIME",
)
@click.option(
    "--since",
    help="Relative time to fetch logs from (e.g., '1h' for 1 hour, '30m' for 30 minutes, '2d' for 2 days, '1w' for 1 week). Cannot be used with --start-time or --end-time. Can be set via EXPORT_SECURITY_LOGS_SINCE environment variable.",
    envvar="EXPORT_SECURITY_LOGS_SINCE",
)
@click.option(
    "--insecure/--secure",
    default=False,
    help="Disable SSL certificate validation (for self-signed certificates)",
)
@click.option(
    "--url",
    help="URL of the Filebeat HTTP endpoint (if specified, data will be sent to this URL)",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Dry run mode: show data that would be sent without actually sending it",
)
def export_security_logs(
    host: str,
    token: str,
    username: Optional[str],
    limit: int,
    start_time: Optional[int],
    end_time: Optional[int],
    since: Optional[str],
    insecure: bool,
    url: Optional[str],
    dry_run: bool,
) -> None:
    """
    Export Openfire security audit logs and send them to a Filebeat HTTP endpoint.
    
    This script connects to an Openfire server, retrieves security audit logs, and sends them
    to a Filebeat HTTP endpoint for further processing.
    
    All command-line options can also be provided via environment variables with the
    prefix EXPORT_SECURITY_LOGS_ followed by the option name in uppercase. For example:
      --host can be set with EXPORT_SECURITY_LOGS_HOST
      --token can be set with EXPORT_SECURITY_LOGS_TOKEN
      --url can be set with EXPORT_SECURITY_LOGS_URL
    
    Boolean flags like --dry-run can be set with EXPORT_SECURITY_LOGS_DRY_RUN=true/false.
    """
    try:
        # Create SecurityAuditLog API client
        security_api = SecurityAuditLog(host, token)
        security_api.verify_ssl = not insecure
        
        # Get hostname for identification
        hostname = socket.gethostname()
        
        # Get xmpp.domain from system properties if available
        xmpp_domain = None
        try:
            # Create System API client (reusing host and token)
            system_api = System(host, token)
            system_api.verify_ssl = not insecure
            
            # Get all properties in a single request
            props = system_api.get_props()
            
            # Extract xmpp.domain if available
            if "property" in props:
                for prop in props["property"]:
                    if prop.get("key") == "xmpp.domain":
                        xmpp_domain = prop.get("value")
                        break
        except Exception:
            # If we can't get the domain, continue without it
            pass
        
        # Prepare server information
        server_info = {
            "hostname": hostname,
            "server": host,
            "xmpp_domain": xmpp_domain
        }
        
        # Handle relative time option
        calculated_start_time = start_time
        calculated_end_time = end_time
        
        if since and (start_time is not None or end_time is not None):
            click.echo("Error: --since cannot be used with --start-time or --end-time", err=True)
            sys.exit(1)
        
        if since:
            # Parse the relative time string
            try:
                calculated_start_time, calculated_end_time = parse_relative_time(since)
                click.echo(f"Using relative time: {since} (from {datetime.fromtimestamp(calculated_start_time)} to {datetime.fromtimestamp(calculated_end_time)})", err=True)
            except ValueError as e:
                click.echo(f"Error parsing relative time: {e}", err=True)
                sys.exit(1)
        
        # Get security audit logs with optional filtering
        logs_response = security_api.get_logs(
            username=username,
            limit=limit,
            start_time=calculated_start_time,
            end_time=calculated_end_time
        )
        
        # Extract log entries
        logs_list = security_api.extract_log_entries(logs_response)
        
        if not logs_list:
            click.echo("No security audit logs found.", err=True)
            return
            
        # Handle dry run mode first
        if dry_run:
            # For dry run, URL is optional
            if url:
                click.echo(f"DRY RUN: Would send data to Filebeat at {url}", err=True)
            else:
                click.echo("DRY RUN: Would send data to Filebeat", err=True)
        else:
            # For actual sending, URL is required
            if not url:
                click.echo("Error: --url is required for sending data", err=True)
                sys.exit(1)
            click.echo(f"Sending data to Filebeat at {url}", err=True)
            
        results = send_to_filebeat(logs_list, url, server_info, insecure, dry_run)
        
        if dry_run:
            click.echo(f"DRY RUN: Would have sent {results['success']} security audit logs", err=True)
        else:
            click.echo(f"Sent {results['success']} security audit logs successfully, {results['failure']} failed", err=True)
            if results['failure'] > 0:
                click.echo(f"Failed logs: {', '.join(map(str, results['failed_logs']))}", err=True)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    export_security_logs()
