# App Store Deployment Guide

**Multi-Store Mobile Application Distribution: Platform Entry Requirements, Remote CI/CD Automated Pipelines, and Agentic AI DevOps Orchestration**

---

## Platform Entry Requirements and Financial Gatekeeping

Transitioning an application from a newly compiled codebase hosted on a public GitHub repository to major digital distribution storefronts requires navigating platform-specific compliance, verification protocols, and financial architectures. For developers operating in restrictive banking jurisdictions, such as Nigeria, completing these transactions presents operational challenges that require alternative payment systems.

```
┌────────────────────────────────────────────────┐
│               Local Android/iOS App Source     │
│                      (on GitHub)               │
└───────────────────────────┬────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
      [Google Play Store]         [Apple App Store]
   - $25 (EverTry/USDT)       - $99/yr (Virtual Card)
   - 12-Tester 14-day rule    - No Store Credit Allowed
   - Verification             - macOS Cloud Compile
              │                           │
              └─────────────┬─────────────┘
                            │
                            ▼
                  [Samsung Galaxy Store]
               - Free Registration
               - Unique Package Names
               - Commercial Status
```

---

## Google Play Console Setup and International Payment Restrictions

### Registration Requirements
- **Fee**: $25 USD (one-time)
- **Payment Challenge (Nigeria)**: Central bank regulations cause international transaction declines on standard local debit cards

### Bypass Strategy: Virtual Dollar Cards
1. **Providers**: EverTry virtual cards
2. **Verification**: Bank Verification Number (BVN) or National Identification Number (NIN)
3. **Funding**: Local currency bank transfers or cryptocurrency (USDT)
4. **Card Requirements**:
   - Minimum balance: $27 USD (covers $25 fee + processing overhead)
   - Billing address must match Google account registration country
   - Active Visa or Mastercard with matching billing details

---

## Apple Developer Programme Enrollment

### Membership Details
- **Cost**: $99 USD (annual renewal)
- **Payment Restrictions**:
  - No App Store gift cards
  - No Apple ID balances
  - No prepaid debit cards
  - Card must be linked to applicant's name and match Apple ID region

### Cross-Platform Registration Strategy
For restricted currency markets:
1. Register Apple ID in open currency region (US/UK)
2. Use internationally valid virtual cards (Wise, Payoneer, Revolut)
3. Disable VPN/proxy during payment (mismatched locations trigger security locks)
4. Wait 24-48 hours for manual processing if status shows "Pending"

### Remote iOS Compilation (No Mac Required)

#### Option 1: Expo Application Services (EAS) Cloud
- For React Native/hybrid frameworks
- Command: `eas build -p ios`
- Handles code signing automatically
- Uploads directly to App Store Connect

#### Option 2: Codemagic CI/CD
- For Flutter multi-platform projects
- Provides remote macOS VMs
- GitHub integration
- Manages iOS certificates
- Automates App Store delivery via App Store Connect API

---

## Samsung Galaxy Store Integration

### Registration
- **Fee**: Free (no entry or annual fees)
- **Commission**: 20% standard (80% developer share), 15% for subscriptions
- **Requirements**:
  - Commercial Seller status application
  - Company domain email (Gmail rejected without justification)
  - Verified banking details or verified business PayPal account

### Cross-Store Overwrite Mitigation
**Problem**: Google Play updates can overwrite Galaxy Store installations if package names match.

**Solution**: Use unique package names per store:
```
Google Play:     com.example.app
Galaxy Store:    com.example.app.galaxy
```

This treats builds as separate applications, preventing file conflicts.

---

## Platform Comparison Matrix

| Metric | Google Play Store | Apple App Store | Samsung Galaxy Store |
|--------|-------------------|-----------------|----------------------|
| Registration Cost | $25 (one-time) | $99/year | Free |
| Commission | 15% (<$1M), 30% (>$1M) | 15% (Small Business), 30% | 20% (15% subscriptions) |
| Pre-Launch Gates | 12-tester closed testing × 14 days | Manual review (24-48h) | Seller certification |
| Compliance | Gov ID & Business Registry | Gov ID & D-U-N-S | Samsung Account & D-U-N-S |
| Payment Strategy | EverTry Virtual Card (Naira/USDT) | Wise, Payoneer, Revolut | Verified PayPal Business |

---

## Google Play's 12-Tester Closed Testing Quality Gate

### Mandatory For
Personal developer accounts created after November 13, 2023

### Requirements
```
[Closed Testing Launched]
         │
         ▼
[12 Unique Testers Opt In]
 (Via Play Store Link Only)
         │
         ▼
[14-Day Consecutive Testing]
(Must overlap continuously)
         │
    ┌────┴────┐
    ▼         ▼
{Tester    {Continuous
 Drops}     Succeeds}
    │         │
    ▼         ▼
  Timer   [Production
 Resets   Access Unlocked]
```

### Critical Rules
1. **Opt-In Verification**: Testers must accept via official Google Play opt-in link and install the app
2. **Temporal Continuity**: 14 consecutive days; if count drops below 12, timer resets to zero
3. **Engagement Tracking**: Testers must actively open app; Google checks DAU and crash logs
4. **Hardware Integrity**: Physical Android devices (Android 7-16) required; emulators/automated clouds are detected and discarded

### Production Access Questionnaire (10 Questions)
After 14-day testing, submit application. Vague answers trigger rejections:

1. **Recruitment**: Describe channels (personal networks, forums, QA platforms)
2. **Difficulty**: Multiple choice (Very Difficult to Very Easy)
3. **Engagement**: Summarize active testing metrics, user paths explored
4. **Feedback Summary**: Bug reports, UX suggestions gathered
5. **Target Audience**: Specific user group, core problem solved
6. **Value Proposition**: 2-3 core features or unique mechanics
7. **Download Estimate**: First-year projection (e.g., 10k-100k)
8. **Changes Made**: Technical updates, crash fixes, layout improvements
9. **Readiness Criteria**: Low crash rates, device compatibility, tester sign-offs
10. **Corrective Actions**: For re-submissions only

---

## Remote Deployment Frameworks and Cloud-Based Compilation

### Fastlane Match: Certificate Management

| Metric | Git Private Repo | AWS S3 Cloud Bucket |
|--------|------------------|---------------------|
| Auth | SSH Keys / PATs | IAM Roles & Policies |
| Performance | Slow (full history clone) | Fast (direct HTTP download) |
| Access Control | All-or-nothing | Fine-grained IAM |
| Audit | Basic Git history | AWS CloudTrail integration |
| Security Risk | Higher (repo compromise) | Lower (server-side encryption) |

### EAS Build Configuration (eas.json)
```json
{
  "cli": {
    "version": ">= 9.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "production": {
      "ios": {
        "simulator": false,
        "image": "macos-sonoma-15.0-xcode-16.0"
      },
      "android": {
        "buildType": "appbundle"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "developer-ops@company.co.uk",
        "ascAppId": "1606772645",
        "appleTeamId": "AB123C456D"
      }
    }
  }
}
```

### GitHub Actions Workflow (EAS)
```yaml
name: Remote iOS Compilation & Submission
on:
  push:
    branches:
      - main

jobs:
  compile-and-submit:
    name: Cloud Build and Store Submit
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Install Node.js Workspace
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install EAS CLI Globally
        run: npm install -g eas-cli

      - name: Authenticate with Expo Cloud Services
        run: eas login --username "${{ secrets.EXPO_USER }}" --password "${{ secrets.EXPO_PASS }}"
        env:
          EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}

      - name: Trigger Cloud Build & Submit to TestFlight
        run: |
          eas build --platform ios --profile production --non-interactive
          eas submit --platform ios --profile production --latest --non-interactive --no-wait
```

### Codemagic Configuration (Flutter)
```yaml
workflows:
  ios-release-workflow:
    name: Codemagic iOS App Store Pipeline
    max_build_duration: 60
    instance_type: mac_mini_m2
    environment:
      groups:
        - apple_credentials
      vars:
        XCODE_SCHEME: "Runner"
        APP_STORE_ID: "1606772645"
    triggering:
      events:
        - push
      branch_patterns:
        - target: main
    scripts:
      - name: Initialise Temporary iOS Keychain
        script: |
          keychain initialize
      - name: Fetch Apple Provisioning Profiles
        script: |
          app-store-connect fetch-signing-files $(xcode-project detect-bundle-id) \
            --platform IOS \
            --type IOS_APP_STORE \
            --create
      - name: Add Certificates to Local Keychain
        script: |
          keychain add-certificates
      - name: Update Xcode Project Profiles
        script: |
          xcode-project use-profiles
      - name: Resolve Project Dependencies
        script: |
          flutter packages pub get
      - name: Compile Production IPA Bundle
        script: |
          flutter build ipa --release --export-options-plist=$HOME/export_options.plist
    artifacts:
      - build/ios/ipa/*.ipa
    publishing:
      email:
        recipients:
          - dev-ops-alerts@company.co.uk
      app_store_connect:
        auth: integration
        submit_to_testflight: true
```

---

## Agentic AI DevOps Pipeline

### Role Definition
You are an **Autonomous Systems Engineering Agent specialized in Mobile DevOps**.

### Core Objective
Parse source directory, configure code-signing profiles, compile app bundle, and upload to app store.

### Execution Rules and Safety Constraints
1. Before modifying config files (`build.gradle`, `app.json`), switch to **Plan Mode**, describe change, request approval
2. For Android builds: verify target API ≥ 33 and contains 64-bit binaries before compilation
3. For iOS builds: pull code-signing certificates in read-only mode from AWS S3 bucket
4. **Never** execute destructive profile commands (e.g., `fastlane match nuke`)

### Output Specifications
- Detailed step-by-step progress with command invocations and file paths
- Error logs with full stack traces

### Error Response Protocol
1. Read log file and identify root cause
2. Implement code fix
3. Retry build
4. After 3 failures for same issue: compile logs, generate summary report, pause for human review

### Self-Healing Flow
```
[AI Agent Launches Build]
            │
            ▼
   {Gradle Compilation Error}
            │
            ▼
    [Agent Parses Build Log]
(Identifies Target SDK Mismatch)
            │
            ▼
    [Agent Switches to Plan Mode]
  (Proposes change to targetSdkVersion)
            │
            ▼
    [Agent Modifies build.gradle]
            │
            ▼
    [Agent Retries App Build]
            │
    ┌───────┴───────┐
    ▼               ▼
{Error         {Build
 Persists}    Succeeds}
    │               │
    ▼               ▼
(Log Re-analyze) [Submit to Store API]
(Max 3 attempts)
```

---

## Python Agent Implementation (Self-Healing Pipeline)

```python
import subprocess
import requests
from typing import Tuple

class AgenticDevOpsRunner:
    def __init__(self, workspace_path: str, api_key: str):
        self.workspace = workspace_path
        self.api_key = api_key
        self.retry_limit = 3

    def run_command(self, cmd: str) -> Tuple[int, str, str]:
        result = subprocess.run(
            cmd, shell=True, cwd=self.workspace,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode, result.stdout, result.stderr

    def analyze_error_with_llm(self, error_log: str) -> str:
        prompt = (
            "Analyze the following compilation error log. Identify the file path "
            "and suggest the exact code modification to resolve the issue.\n\n"
            f"Error Log:\n{error_log}"
        )
        api_url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["content"][0]["text"]

    def execute_self_healing_pipeline(self, build_cmd: str) -> bool:
        for attempt in range(1, self.retry_limit + 1):
            print(f"Executing App Build (Attempt {attempt}/{self.retry_limit})...")
            code, stdout, stderr = self.run_command(build_cmd)
            
            if code == 0:
                print("Build compiled successfully!")
                return True
                
            print(f"Compilation failed. Analysing build logs...")
            remediation_plan = self.analyze_error_with_llm(stderr)
            print(f"Proposed Remediation Plan:\n{remediation_plan}")
            
            self.apply_remediation(remediation_plan)
            
        print("Self-healing pipeline reached maximum retry limit. Human intervention required.")
        return False

    def apply_remediation(self, plan_text: str):
        # Implementation logic to modify target project files
        print("Applying changes to project files...")
        pass
```

---

## Strategic Implementation Roadmap

### Phase 1: Local Pipeline Validation
1. **Account Configuration**: Register with Google, Apple, Samsung; complete identity verifications
2. **Isolate Codebases**: Distinct package names/bundle IDs (use Gradle product flavors)
3. **Verify Signing Credentials**: Generate release keys locally before cloud import

### Phase 2: Remote CI/CD Automation
1. **Secure Credential Storage**: Add production keys, keystores, credentials as encrypted GitHub secrets
2. **Pipeline Workflows**: Configure Fastlane Match + AWS S3 for remote certificate management
3. **Cloud Builds**: Integrate EAS Build (React Native) or Codemagic (Flutter) for remote iOS compilation

### Phase 3: Agentic Release and Self-Healing
1. **Isolated Execution Sandboxes**: Docker containers with mobile dev CLI tools
2. **DevOps Commands as Tools**: Expose Git, EAS, Fastlane as agent-callable functions
3. **Prompt Contracts**: Enforce clear rules, constraints, outputs, exit criteria
4. **Self-Healing Loops**: Agent reads logs, writes build files, auto-resolves compile errors

---

## Samsung Galaxy Store: 2026 Compliance Updates

### Global Developer Verification
Starting September 2026:
- Identity verification required for apps in Brazil, Indonesia, Singapore, Thailand
- Rolling out globally through 2027
- Unverified accounts blocked on certified Android devices in those regions

### Technical Requirements
- **Target API**: Level 33 or higher
- **Architecture**: At least one 64-bit binary required

---

## References

- [Google Play Developer Fee Payment (Nigeria)](https://evertry.co)
- [Apple Developer Enrollment](https://developer.apple.com)
- [Samsung Galaxy Store Getting Started](https://developer.samsung.com)
- [Flutter CI/CD with Fastlane + GitHub Actions](https://nttdata-dach.github.io)
- [EAS Build + GitHub Actions iOS Deployment](https://medium.com)
- [Codemagic Flutter Deployment](https://docs.codemagic.io)
- [Fastlane Match Certificate Management](https://circleci.com)
- [Google Play 12-Tester Rules (2026)](https://primetestlab.com)