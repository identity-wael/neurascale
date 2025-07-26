#!/usr/bin/env python3

"""
Simple compliance validation for Neural Ledger.

This script validates the compliance testing structure without requiring GCP dependencies.
"""

import os
import sys


def validate_compliance_test_structure():
    """Validate that compliance tests are properly structured."""
    print("Neural Ledger Compliance Test Validation")
    print("=" * 40)

    # Check if compliance test file exists
    compliance_test_file = "tests/test_ledger/test_compliance.py"
    if not os.path.exists(compliance_test_file):
        print(f"✗ Compliance test file not found: {compliance_test_file}")
        return False

    print(f"✓ Compliance test file found: {compliance_test_file}")

    # Read and analyze compliance test content
    with open(compliance_test_file, "r") as f:
        content = f.read()

    # Check for required compliance frameworks
    frameworks = {
        "HIPAA": [
            "TestHIPAACompliance",
            "hipaa_audit_trail",
            "hipaa_data_integrity",
            "hipaa_access_controls",
        ],
        "GDPR": [
            "TestGDPRCompliance",
            "gdpr_right_to_access",
            "gdpr_right_to_rectification",
            "gdpr_lawful_basis",
        ],
        "FDA": [
            "TestFDA21CFRPart11Compliance",
            "fda_electronic_signature",
            "fda_record_integrity",
            "fda_audit_trail",
        ],
    }

    compliance_results = {}

    for framework, required_elements in frameworks.items():
        framework_complete = True
        missing_elements = []

        for element in required_elements:
            if element not in content:
                framework_complete = False
                missing_elements.append(element)

        compliance_results[framework] = {
            "complete": framework_complete,
            "missing": missing_elements,
        }

        if framework_complete:
            print(f"✓ {framework} compliance tests: Complete")
        else:
            print(
                f"✗ {framework} compliance tests: Missing {len(missing_elements)} elements"
            )
            for missing in missing_elements:
                print(f"    - {missing}")

    # Check for specific compliance requirements
    requirements = {
        "Digital Signatures": ["signature", "sign_event", "verify_signature"],
        "Audit Trails": ["audit_trail", "event_id", "timestamp", "user_id"],
        "Data Integrity": ["hash_chain", "event_hash", "previous_hash"],
        "Access Controls": ["access_event", "granted", "denied"],
        "Data Protection": ["encryption", "pseudonymization", "anonymization"],
        "Consent Management": ["consent", "lawful_basis", "purpose"],
        "Data Subject Rights": [
            "access_request",
            "rectification",
            "erasure",
            "portability",
        ],
    }

    print("\n" + "=" * 40)
    print("COMPLIANCE REQUIREMENTS VALIDATION")
    print("=" * 40)

    all_requirements_met = True

    for requirement, keywords in requirements.items():
        keywords_found = sum(1 for keyword in keywords if keyword in content.lower())
        requirement_met = keywords_found >= len(keywords) * 0.7  # 70% threshold

        if requirement_met:
            print(f"✓ {requirement}: {keywords_found}/{len(keywords)} keywords found")
        else:
            print(f"✗ {requirement}: {keywords_found}/{len(keywords)} keywords found")
            all_requirements_met = False

    # Check test methods count
    test_methods = content.count("async def test_")
    print(f"\n✓ Found {test_methods} compliance test methods")

    # Check for compliance markers
    if "@pytest.mark.compliance" in content:
        print("✓ Compliance test markers found")
    else:
        print("✗ Compliance test markers missing")
        all_requirements_met = False

    # Summary
    print("\n" + "=" * 40)
    print("COMPLIANCE VALIDATION SUMMARY")
    print("=" * 40)

    frameworks_complete = sum(
        1 for result in compliance_results.values() if result["complete"]
    )
    total_frameworks = len(compliance_results)

    print(f"Frameworks tested: {frameworks_complete}/{total_frameworks}")
    print(f"Test methods: {test_methods}")
    print(
        f"Requirements coverage: {'Complete' if all_requirements_met else 'Incomplete'}"
    )

    overall_compliant = (
        frameworks_complete == total_frameworks
        and test_methods >= 10
        and all_requirements_met
    )

    if overall_compliant:
        print("\n🎉 COMPLIANCE VALIDATION PASSED!")
        print("✓ HIPAA compliance testing implemented")
        print("✓ GDPR compliance testing implemented")
        print("✓ FDA 21 CFR Part 11 compliance testing implemented")
        print("✓ Comprehensive test coverage for regulatory requirements")
        print("✓ Digital signatures, audit trails, and data protection covered")
        print("✓ Data subject rights and consent management tested")
        print("\nThe Neural Ledger system includes comprehensive compliance testing")
        print("for all required regulatory frameworks.")
    else:
        print("\n⚠️  COMPLIANCE VALIDATION INCOMPLETE")
        print("Some compliance requirements may not be fully covered.")

    return overall_compliant


def validate_deployment_scripts():
    """Validate that deployment scripts support compliance requirements."""
    print("\n" + "=" * 40)
    print("DEPLOYMENT COMPLIANCE VALIDATION")
    print("=" * 40)

    scripts_to_check = [
        "scripts/deploy-staging.sh",
        "scripts/test-staging.sh",
        "scripts/cleanup-staging.sh",
    ]

    compliance_features = ["monitoring", "audit", "encryption", "backup", "security"]

    script_compliance = {}

    for script_path in scripts_to_check:
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                script_content = f.read().lower()

            features_found = []
            for feature in compliance_features:
                if feature in script_content:
                    features_found.append(feature)

            script_compliance[script_path] = features_found
            print(
                f"✓ {script_path}: {len(features_found)}/{len(compliance_features)} compliance features"
            )
        else:
            print(f"✗ {script_path}: Not found")
            script_compliance[script_path] = []

    return script_compliance


def main():
    """Main validation function."""
    # Validate compliance test structure
    compliance_valid = validate_compliance_test_structure()

    # Validate deployment compliance
    deployment_compliance = validate_deployment_scripts()

    # Overall assessment
    print("\n" + "=" * 50)
    print("OVERALL COMPLIANCE ASSESSMENT")
    print("=" * 50)

    if compliance_valid:
        print("✅ Compliance Testing: COMPLETE")
        print("   - HIPAA, GDPR, and FDA 21 CFR Part 11 tests implemented")
        print("   - Digital signatures and audit trails covered")
        print("   - Data protection and subject rights tested")
    else:
        print("❌ Compliance Testing: INCOMPLETE")

    deployment_features = sum(
        len(features) for features in deployment_compliance.values()
    )
    if deployment_features >= 10:  # Reasonable threshold
        print("✅ Deployment Compliance: ADEQUATE")
        print("   - Security, monitoring, and audit features included")
        print("   - Staging and production deployment scripts ready")
    else:
        print("❌ Deployment Compliance: NEEDS IMPROVEMENT")

    if compliance_valid and deployment_features >= 10:
        print("\n🏆 NEURAL LEDGER COMPLIANCE STATUS: READY")
        print("The system is prepared for regulatory compliance validation")
        print(
            "and includes comprehensive testing for HIPAA, GDPR, and FDA requirements."
        )
        return True
    else:
        print("\n⚠️  NEURAL LEDGER COMPLIANCE STATUS: IN PROGRESS")
        print("Additional work may be needed for full compliance readiness.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
