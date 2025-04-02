# learn-aws-config
How to use aws config to monitor and remediate

To track whether the IAM action you assigned to `AutomationAssumeRole` is insufficient, follow these steps:

### **1. Check AWS Systems Manager Automation Execution Logs**
- Navigate to **AWS Systems Manager** → **Automation**.
- Look for the execution history of your automation document.
- If the automation fails due to insufficient permissions, you will see error messages like `AccessDenied` or `IAM policy does not allow action`.

### **2. Use AWS CloudTrail to Monitor IAM Actions**
- Go to **AWS CloudTrail** → **Event History**.
- Filter by **Event Source**: `iam.amazonaws.com` and `ssm.amazonaws.com`.
- Look for `AccessDenied` or `UnauthorizedOperation` errors related to `AutomationAssumeRole`.

### **3. Enable AWS CloudWatch Logs for AWS Systems Manager**
- If logging is enabled for AWS Systems Manager, check **CloudWatch Logs** under the `AWS-SystemsManager-AutomationExecution` log group.
- Look for `AccessDeniedException` or similar errors in the log stream.

### **4. Check IAM Policy Simulator**
- Open the **IAM Policy Simulator**: [IAM Policy Simulator](https://policysim.aws.amazon.com/)
- Simulate the `AutomationAssumeRole` permissions with the exact actions your automation needs.
- Check if any required actions are being denied.

### **5. Debug Using AWS Config**
- If you have **AWS Config** enabled, check for non-compliant IAM policies that might be blocking access.

Let me know what errors you see, and I can help you fine-tune the IAM policy! 🚀

https://github.com/awslabs/aws-config-rules/tree/master/aws-config-conformance-packs
## Run this if you are running terraform in cloudshell
```bash
alias tf="terraform"; alias tfa="terraform apply --auto-approve"; alias tfd="terraform destroy --auto-approve"; alias tfm="terraform init; terraform fmt; terraform validate; terraform plan"; sudo yum install -y yum-utils shadow-utils; sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo; sudo yum -y install terraform; terraform init
```
### How to use this
- [ ] https://docs.aws.amazon.com/config/latest/developerguide/vpc-sg-open-only-to-authorized-ports.html
- [ ] https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs-sample.html
- [ ] https://aws.amazon.com/blogs/security/how-to-monitor-aws-account-configuration-changes-and-api-calls-to-amazon-ec2-security-groups/
