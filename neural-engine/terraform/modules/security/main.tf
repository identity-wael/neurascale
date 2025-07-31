# Security Module for NeuraScale Neural Engine
# Manages KMS keys, IAM policies, and security configurations

# Enable required APIs
resource "google_project_service" "kms_api" {
  project = var.project_id
  service = "cloudkms.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "secret_manager_api" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  disable_on_destroy = false
}

# KMS Keyring for encryption keys
resource "google_kms_key_ring" "neural_engine" {
  name     = "${var.environment}-neural-engine-keyring"
  location = var.region
  project  = var.project_id

  depends_on = [google_project_service.kms_api]

  lifecycle {
    prevent_destroy = true
  }
}

# KMS Key for database encryption
resource "google_kms_crypto_key" "database" {
  name     = "${var.environment}-database-key"
  key_ring = google_kms_key_ring.neural_engine.id

  rotation_period = var.key_rotation_period

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = var.hsm_protection ? "HSM" : "SOFTWARE"
  }

  lifecycle {
    prevent_destroy = true
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "database-encryption"
      compliance  = "hipaa"
    }
  )
}

# KMS Key for storage encryption
resource "google_kms_crypto_key" "storage" {
  name     = "${var.environment}-storage-key"
  key_ring = google_kms_key_ring.neural_engine.id

  rotation_period = var.key_rotation_period

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = var.hsm_protection ? "HSM" : "SOFTWARE"
  }

  lifecycle {
    prevent_destroy = true
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "storage-encryption"
      compliance  = "hipaa"
    }
  )
}

# KMS Key for application secrets
resource "google_kms_crypto_key" "application" {
  name     = "${var.environment}-application-key"
  key_ring = google_kms_key_ring.neural_engine.id

  rotation_period = var.key_rotation_period

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = var.hsm_protection ? "HSM" : "SOFTWARE"
  }

  lifecycle {
    prevent_destroy = true
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "application-secrets"
      compliance  = "hipaa"
    }
  )
}

# KMS Key for BigQuery encryption
resource "google_kms_crypto_key" "bigquery" {
  name     = "${var.environment}-bigquery-key"
  key_ring = google_kms_key_ring.neural_engine.id

  rotation_period = var.key_rotation_period

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = var.hsm_protection ? "HSM" : "SOFTWARE"
  }

  lifecycle {
    prevent_destroy = true
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "bigquery-encryption"
      compliance  = "hipaa"
    }
  )
}

# Service account for KMS operations
resource "google_service_account" "kms_admin" {
  account_id   = "kms-admin-${var.environment}"
  display_name = "KMS Administrator Service Account"
  description  = "Service account for managing encryption keys"
  project      = var.project_id
}

# IAM bindings for KMS keys
resource "google_kms_crypto_key_iam_member" "database_encrypter" {
  crypto_key_id = google_kms_crypto_key.database.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.database_service_account}"
}

resource "google_kms_crypto_key_iam_member" "storage_encrypter" {
  crypto_key_id = google_kms_crypto_key.storage.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.storage_service_account}"
}

resource "google_kms_crypto_key_iam_member" "application_encrypter" {
  crypto_key_id = google_kms_crypto_key.application.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.application_service_account}"
}

resource "google_kms_crypto_key_iam_member" "bigquery_encrypter" {
  crypto_key_id = google_kms_crypto_key.bigquery.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:bq-${data.google_project.project.number}@bigquery-encryption.iam.gserviceaccount.com"
}

# Data source for project number
data "google_project" "project" {
  project_id = var.project_id
}

# Secret Manager secrets for sensitive data
resource "google_secret_manager_secret" "database_password" {
  secret_id = "${var.environment}-database-password"
  project   = var.project_id

  replication {
    user_managed {
      replicas {
        location = var.region
        customer_managed_encryption {
          kms_key_name = google_kms_crypto_key.application.id
        }
      }
      # Add secondary region for HA
      dynamic "replicas" {
        for_each = var.enable_multi_region ? [1] : []
        content {
          location = var.secondary_region
          customer_managed_encryption {
            kms_key_name = google_kms_crypto_key.application.id
          }
        }
      }
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "database-credentials"
    }
  )

  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret" "api_keys" {
  secret_id = "${var.environment}-api-keys"
  project   = var.project_id

  replication {
    user_managed {
      replicas {
        location = var.region
        customer_managed_encryption {
          kms_key_name = google_kms_crypto_key.application.id
        }
      }
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "api-authentication"
    }
  )
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${var.environment}-jwt-secret"
  project   = var.project_id

  replication {
    user_managed {
      replicas {
        location = var.region
        customer_managed_encryption {
          kms_key_name = google_kms_crypto_key.application.id
        }
      }
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      purpose     = "jwt-signing"
    }
  )
}

# VPC Service Controls (if enabled)
resource "google_access_context_manager_service_perimeter" "neural_engine" {
  count = var.enable_vpc_service_controls ? 1 : 0

  parent = "accessPolicies/${var.access_policy_id}"
  name   = "accessPolicies/${var.access_policy_id}/servicePerimeters/${var.environment}_neural_engine"
  title  = "${var.environment} Neural Engine Perimeter"

  status {
    resources = [
      "projects/${data.google_project.project.number}",
    ]

    restricted_services = var.restricted_services

    vpc_accessible_services {
      enable_restriction = true
      allowed_services   = var.restricted_services
    }

    ingress_policies {
      ingress_from {
        identity_type = "ANY_IDENTITY"
        sources {
          access_level = var.access_level_name
        }
      }

      ingress_to {
        resources = ["*"]
        operations {
          service_name = "storage.googleapis.com"
          method_selectors {
            method = "*"
          }
        }
      }
    }
  }

  use_explicit_dry_run_spec = false
}

# Organization Policy Constraints (if org-level permissions available)
resource "google_organization_policy" "enforce_encryption" {
  count = var.enable_org_policies ? 1 : 0

  org_id     = var.organization_id
  constraint = "constraints/compute.requireOsLogin"

  boolean_policy {
    enforced = true
  }
}

resource "google_organization_policy" "restrict_public_ip" {
  count = var.enable_org_policies && var.environment == "production" ? 1 : 0

  org_id     = var.organization_id
  constraint = "constraints/compute.vmExternalIpAccess"

  list_policy {
    deny {
      all = true
    }
  }
}

# Binary Authorization Policy (for GKE)
resource "google_binary_authorization_policy" "policy" {
  count = var.enable_binary_authorization ? 1 : 0

  project = var.project_id

  admission_whitelist_patterns {
    name_pattern = "gcr.io/${var.project_id}/*"
  }

  admission_whitelist_patterns {
    name_pattern = "${var.region}-docker.pkg.dev/${var.project_id}/*"
  }

  default_admission_rule {
    evaluation_mode  = "REQUIRE_ATTESTATION"
    enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"

    require_attestations_by = [
      google_binary_authorization_attestor.neural_engine[0].name,
    ]
  }

  cluster_admission_rules {
    cluster          = "${var.region}.${var.gke_cluster_name}"
    evaluation_mode  = "REQUIRE_ATTESTATION"
    enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    require_attestations_by = [
      google_binary_authorization_attestor.neural_engine[0].name,
    ]
  }
}

# Binary Authorization Attestor
resource "google_binary_authorization_attestor" "neural_engine" {
  count = var.enable_binary_authorization ? 1 : 0

  name    = "${var.environment}-neural-engine-attestor"
  project = var.project_id

  attestation_authority_note {
    note_reference = google_container_analysis_note.neural_engine[0].name

    public_keys {
      id = var.attestor_public_key_id
      pkix_public_key {
        public_key_pem      = var.attestor_public_key_pem
        signature_algorithm = "RSA_PSS_4096_SHA512"
      }
    }
  }
}

# Container Analysis Note for Binary Authorization
resource "google_container_analysis_note" "neural_engine" {
  count = var.enable_binary_authorization ? 1 : 0

  name    = "${var.environment}-neural-engine-attestor-note"
  project = var.project_id

  attestation_authority {
    hint {
      human_readable_name = "Neural Engine ${var.environment} Attestor"
    }
  }
}

# Workload Identity Bindings
resource "google_service_account_iam_member" "workload_identity_user" {
  for_each = var.workload_identity_bindings

  service_account_id = each.value.service_account
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${each.value.namespace}/${each.value.kubernetes_service_account}]"
}

# Audit Log Configuration
resource "google_project_iam_audit_config" "neural_engine" {
  project = var.project_id
  service = "allServices"

  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type         = "DATA_READ"
    exempted_members = var.audit_log_exempted_members
  }

  audit_log_config {
    log_type         = "DATA_WRITE"
    exempted_members = var.audit_log_exempted_members
  }
}

# Security Command Center Notification Config (if enabled)
resource "google_scc_notification_config" "neural_engine" {
  count = var.enable_security_center ? 1 : 0

  config_id    = "${var.environment}-neural-engine-notifications"
  organization = var.organization_id

  description = "Security notifications for Neural Engine ${var.environment}"

  pubsub_topic = var.security_notification_topic

  streaming_config {
    filter = "category=\"VULNERABILITY\" AND resource.project_display_name=\"${var.project_id}\""
  }
}
