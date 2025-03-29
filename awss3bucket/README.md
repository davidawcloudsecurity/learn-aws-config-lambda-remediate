### **Account-Level Public Access Rules**
1. **s3-account-level-public-access-blocks**  
   - Ensures that public access block settings are configured at the account level.  
   - Status: NON_COMPLIANT if these settings are not configured.

2. **s3-account-level-public-access-blocks-periodic**  
   - Periodically checks if public access block settings match the required configuration at the account level.  
   - Status: NON_COMPLIANT if settings deviate from specified parameters.

### **Bucket-Level Configuration Rules**
1. **s3-bucket-default-lock-enabled**  
   - Verifies whether the default lock is enabled for S3 buckets.  
   - Status: NON_COMPLIANT if the lock is not enabled.

2. **s3-bucket-level-public-access-prohibited**  
   - Checks if S3 buckets are publicly accessible.  
   - Status: NON_COMPLIANT if a bucket is public and not listed in the `excludedPublicBuckets` parameter.

3. **s3-bucket-logging-enabled**  
   - Ensures logging is enabled for S3 buckets to track access and operations.  
   - Status: NON_COMPLIANT if logging is disabled.

4. **s3-bucket-policy-grantee-check**  
   - Validates that access granted by bucket policies is restricted to specific AWS principals, IP addresses, or VPCs.  
   - Status: NON_COMPLIANT if no bucket policy exists or access is unrestricted.
### **Security and Encryption Rules**
1. **s3-bucket-public-read-prohibited**  
   - Ensures S3 buckets do not allow public read access by checking ACLs and public access block settings.  
   - Status: NON_COMPLIANT if public read access is enabled.

2. **s3-bucket-public-write-prohibited**  
   - Ensures S3 buckets do not allow public write access by checking ACLs and public access block settings.  
   - Status: NON_COMPLIANT if public write access is enabled.

3. **s3-bucket-server-side-encryption-enabled**  
   - Verifies default encryption using AES-256 or AWS KMS for server-side encryption of objects in S3 buckets.  
   - Status: NON_COMPLIANT if encryption is disabled.

4. **s3-default-encryption-kms**  
   - Checks whether S3 buckets are encrypted with AWS Key Management Service (KMS).  
   - Status: NON_COMPLIANT if KMS encryption is not applied.
### **Replication and Versioning Rules**
1. **s3-bucket-replication-enabled**  
   - Ensures replication rules are enabled for S3 buckets to maintain data redundancy across regions.  
   - Status: NON_COMPLIANT if replication rules are absent or disabled.

2. **s3-bucket-versioning-enabled**  
   - Checks whether versioning is enabled for S3 buckets to preserve object versions in case of overwrites or deletions.  
   - Status: NON_COMPLIANT if versioning is disabled.
### **SSL/TLS Enforcement**
1. **s3-bucket-ssl-requests-only**  
   - Ensures S3 bucket policies require SSL/TLS for secure data transfer, disallowing HTTP requests.  
   - Status: NON_COMPLIANT if HTTP requests are allowed.
