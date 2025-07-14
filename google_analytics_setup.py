#!/usr/bin/env python3
"""
Google Analytics 4 Setup Helper for NeuraScale
This script helps you set up and test your GA4 connection.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    RunRealtimeReportRequest,
)


def load_credentials():
    """Load GA4 credentials from environment or service account file."""
    # Check for service account file
    service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if service_account_path and os.path.exists(service_account_path):
        print(f"✅ Using service account: {service_account_path}")
        return BetaAnalyticsDataClient()
    
    # Otherwise, use default credentials
    try:
        client = BetaAnalyticsDataClient()
        print("✅ Using Application Default Credentials")
        return client
    except Exception as e:
        print(f"❌ Failed to authenticate: {str(e)}")
        print("\nTo authenticate, either:")
        print("1. Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file")
        print("2. Run: gcloud auth application-default login")
        return None


def list_properties(client):
    """List all GA4 properties accessible to the authenticated account."""
    print("\n📊 Accessible GA4 Properties:")
    print("-" * 50)
    
    # Note: The Admin API is needed to list properties
    # For now, you'll need to provide the property ID directly
    print("Please provide your GA4 property ID (format: properties/XXXXXXXXX)")
    print("You can find this in Google Analytics > Admin > Property Settings")


def get_realtime_data(client, property_id):
    """Get real-time data from GA4."""
    try:
        request = RunRealtimeReportRequest(
            property=property_id,
            dimensions=[
                Dimension(name="country"),
                Dimension(name="deviceCategory"),
            ],
            metrics=[
                Metric(name="activeUsers"),
            ],
        )
        
        response = client.run_realtime_report(request)
        
        print(f"\n🔴 Real-time Active Users:")
        print("-" * 50)
        
        total_users = 0
        for row in response.rows:
            country = row.dimension_values[0].value
            device = row.dimension_values[1].value
            users = row.metric_values[0].value
            total_users += int(users)
            print(f"{country} - {device}: {users} users")
        
        print(f"\nTotal active users: {total_users}")
        
    except Exception as e:
        print(f"❌ Failed to get real-time data: {str(e)}")


def get_today_data(client, property_id):
    """Get today's data from GA4."""
    try:
        request = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date="today", end_date="today")],
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="deviceCategory"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
            ],
        )
        
        response = client.run_report(request)
        
        print(f"\n📈 Today's Analytics:")
        print("-" * 80)
        print(f"{'Page':<40} {'Device':<15} {'Sessions':<10} {'Users':<10} {'Views':<10}")
        print("-" * 80)
        
        for row in response.rows:
            page = row.dimension_values[0].value[:40]
            device = row.dimension_values[1].value
            sessions = row.metric_values[0].value
            users = row.metric_values[1].value
            views = row.metric_values[2].value
            
            print(f"{page:<40} {device:<15} {sessions:<10} {users:<10} {views:<10}")
        
    except Exception as e:
        print(f"❌ Failed to get today's data: {str(e)}")


def get_weekly_summary(client, property_id):
    """Get last 7 days summary from GA4."""
    try:
        request = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[
                Dimension(name="date"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
            ],
        )
        
        response = client.run_report(request)
        
        print(f"\n📊 Last 7 Days Summary:")
        print("-" * 90)
        print(f"{'Date':<12} {'Sessions':<10} {'Users':<10} {'New Users':<12} {'Page Views':<12} {'Avg Duration':<15}")
        print("-" * 90)
        
        for row in response.rows:
            date = row.dimension_values[0].value
            sessions = row.metric_values[0].value
            users = row.metric_values[1].value
            new_users = row.metric_values[2].value
            views = row.metric_values[3].value
            duration = float(row.metric_values[4].value)
            
            # Format duration as MM:SS
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            print(f"{date:<12} {sessions:<10} {users:<10} {new_users:<12} {views:<12} {duration_str:<15}")
        
    except Exception as e:
        print(f"❌ Failed to get weekly summary: {str(e)}")


def get_top_pages(client, property_id):
    """Get top pages from GA4."""
    try:
        request = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle"),
            ],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="totalUsers"),
                Metric(name="averageSessionDuration"),
            ],
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
            limit=10,
        )
        
        response = client.run_report(request)
        
        print(f"\n🏆 Top 10 Pages (Last 30 Days):")
        print("-" * 100)
        print(f"{'Path':<40} {'Title':<30} {'Views':<10} {'Users':<10} {'Avg Time':<10}")
        print("-" * 100)
        
        for row in response.rows:
            path = row.dimension_values[0].value[:40]
            title = row.dimension_values[1].value[:30]
            views = row.metric_values[0].value
            users = row.metric_values[1].value
            duration = float(row.metric_values[2].value)
            
            # Format duration
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            print(f"{path:<40} {title:<30} {views:<10} {users:<10} {duration_str:<10}")
        
    except Exception as e:
        print(f"❌ Failed to get top pages: {str(e)}")


def create_ga4_config():
    """Create a GA4 configuration file."""
    print("\n🔧 GA4 Configuration Setup")
    print("-" * 50)
    
    property_id = input("Enter your GA4 Property ID (e.g., properties/123456789): ").strip()
    measurement_id = input("Enter your GA4 Measurement ID (e.g., G-XXXXXXXXXX): ").strip()
    
    config = {
        "property_id": property_id,
        "measurement_id": measurement_id,
        "created_at": datetime.now().isoformat(),
    }
    
    with open("ga4-config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to ga4-config.json")
    print(f"\nAdd this to your Vercel environment variables:")
    print(f"NEXT_PUBLIC_GA4_MEASUREMENT_ID={measurement_id}")
    
    return property_id


def main():
    print("🚀 Google Analytics 4 Setup Helper")
    print("=" * 50)
    
    # Load or create configuration
    config_file = "ga4-config.json"
    property_id = None
    
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            property_id = config.get("property_id")
            print(f"✅ Loaded configuration from {config_file}")
    else:
        print(f"ℹ️  No configuration found. Let's set it up!")
        property_id = create_ga4_config()
    
    if not property_id:
        print("❌ No property ID configured. Run the setup again.")
        return
    
    # Authenticate
    client = load_credentials()
    if not client:
        return
    
    print(f"\n📊 Using GA4 Property: {property_id}")
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. View real-time data")
        print("2. View today's data")
        print("3. View last 7 days summary")
        print("4. View top 10 pages")
        print("5. Configure new property")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            get_realtime_data(client, property_id)
        elif choice == "2":
            get_today_data(client, property_id)
        elif choice == "3":
            get_weekly_summary(client, property_id)
        elif choice == "4":
            get_top_pages(client, property_id)
        elif choice == "5":
            property_id = create_ga4_config()
        else:
            print("❌ Invalid choice. Please try again.")
    
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()