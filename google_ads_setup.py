#!/usr/bin/env python3
"""
Google Ads API Setup Helper
This script helps you set up and test your Google Ads API connection.
"""

import sys
import argparse
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def authenticate_google_ads():
    """Authenticate and create a Google Ads client."""
    try:
        # Initialize the Google Ads client
        # This will read configuration from google-ads.yaml
        client = GoogleAdsClient.load_from_storage("google-ads.yaml")
        print("✅ Successfully authenticated with Google Ads API!")
        return client
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created a Google Ads developer token")
        print("2. Set up OAuth2 credentials")
        print("3. Updated google-ads.yaml with your credentials")
        print("\nFor detailed setup instructions, visit:")
        print("https://developers.google.com/google-ads/api/docs/get-started/oauth-cloud-project")
        return None


def list_accessible_customers(client):
    """List all accessible customer accounts."""
    customer_service = client.get_service("CustomerService")
    
    try:
        accessible_customers = customer_service.list_accessible_customers()
        print("\n📊 Accessible Customer Accounts:")
        print("-" * 50)
        
        for resource_name in accessible_customers.resource_names:
            customer_id = resource_name.split('/')[-1]
            print(f"Customer ID: {customer_id}")
            
        return accessible_customers.resource_names
    except GoogleAdsException as ex:
        print(f"❌ Failed to list customers: {ex}")
        return []


def get_account_info(client, customer_id):
    """Get basic information about a customer account."""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone
        FROM customer
        LIMIT 1
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            customer = row.customer
            print(f"\n📋 Account Information for {customer.id}:")
            print("-" * 50)
            print(f"Name: {customer.descriptive_name}")
            print(f"Currency: {customer.currency_code}")
            print(f"Time Zone: {customer.time_zone}")
            
    except GoogleAdsException as ex:
        print(f"❌ Failed to get account info: {ex}")


def get_campaigns(client, customer_id):
    """List all campaigns for a customer."""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY campaign.id
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        print(f"\n📊 Campaigns for Customer {customer_id}:")
        print("-" * 80)
        print(f"{'ID':<10} {'Name':<30} {'Status':<15} {'Type':<20}")
        print("-" * 80)
        
        for row in response:
            campaign = row.campaign
            metrics = row.metrics
            
            print(f"{campaign.id:<10} {campaign.name:<30} {campaign.status.name:<15} {campaign.advertising_channel_type.name:<20}")
            print(f"   └─ Impressions: {metrics.impressions}, Clicks: {metrics.clicks}, Cost: ${metrics.cost_micros / 1_000_000:.2f}")
            
    except GoogleAdsException as ex:
        print(f"❌ Failed to get campaigns: {ex}")


def main():
    parser = argparse.ArgumentParser(description="Google Ads API Setup Helper")
    parser.add_argument("--customer-id", help="Customer ID to use for queries")
    parser.add_argument("--list-customers", action="store_true", help="List all accessible customers")
    parser.add_argument("--campaigns", action="store_true", help="List campaigns for the specified customer")
    
    args = parser.parse_args()
    
    print("🚀 Google Ads API Setup Helper")
    print("=" * 50)
    
    # Authenticate
    client = authenticate_google_ads()
    if not client:
        return
    
    # List customers if requested or no customer ID provided
    if args.list_customers or not args.customer_id:
        customers = list_accessible_customers(client)
        
        if not args.customer_id and customers:
            print("\n💡 To get more information about a specific customer, run:")
            print(f"   python google_ads_setup.py --customer-id <CUSTOMER_ID>")
            
    # Get account info and campaigns if customer ID is provided
    if args.customer_id:
        # Remove hyphens from customer ID
        customer_id = args.customer_id.replace("-", "")
        
        get_account_info(client, customer_id)
        
        if args.campaigns:
            get_campaigns(client, customer_id)


if __name__ == "__main__":
    main()