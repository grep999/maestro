# Windows discovery tool

`Collect-WindowsInventory.ps1` is an optional, read-only local inventory helper for an authorised readiness assessment.

## Run

Open PowerShell in the customer's approved environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\Collect-WindowsInventory.ps1 -OutputPath .\windows-inventory.json
```

Use the organisation's approved execution policy; do not weaken machine-wide policy. Run without elevation first. Some fields may be unavailable without elevated permissions, which is preferable to collecting more access than necessary.

## Data handling

- No network transmission or remote execution.
- No software installation or system modification.
- No credentials, user documents, browsing history or packet contents.
- Installed application names, hardware details and printer names can still be sensitive.
- Customer reviews, redacts and explicitly authorises any transfer.
- Delete local output according to the agreed retention policy.

The report is a discovery input only. It does not determine compatibility, security posture, migration readiness or savings.
