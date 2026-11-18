# Migration tools

Prototype Windows-to-Ubuntu user-file copy and restore. It does not install Ubuntu, repartition disks, migrate applications, transfer credentials or delete source data.

## Before starting
- Use a separate external drive with enough free space. Prefer BitLocker To Go or approved encryption; keep its recovery key separately.
- Make OneDrive/SharePoint files available offline and confirm sync. Cloud placeholders may not contain file data.
- Run backup as the Windows user whose files are being migrated. Review redirected folders and application-specific data.
- Verify the backup on another device and open representative files.
- Keep the original Windows installation until Ubuntu restore and user acceptance are complete.

## Windows backup
~~~powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\Start-WindowsDataBackup.ps1 -Destination E:\
~~~
Add -IncludeDownloads to include Downloads. Defaults: Desktop, Documents, Pictures, Music, Videos and Favorites. The script creates a manifest with relative paths, sizes and SHA-256 hashes; it does not follow junctions.

## Ubuntu restore
~~~bash
python3 restore-to-ubuntu.py /media/$USER/DRIVE/Ubuntu-Migration-TIMESTAMP
python3 restore-to-ubuntu.py /media/$USER/DRIVE/Ubuntu-Migration-TIMESTAMP --apply
~~~
First command verifies and previews. Second copies into ~/Migration-Import. Existing files are skipped, never overwritten. Use --target for a different destination.

## Not automatically migrated
Windows applications/licences; Outlook/Exchange or Thunderbird archives; browser profiles/passwords/passkeys/cookies; certificates/SSH keys; cloud-only files; WSL/VMs/databases/ERP/CAD state; Windows permissions, EFS, NTFS alternate streams and system settings. Export through supported application workflows and validate separately. Do not copy credential stores wholesale.

## Release gate
Prototype only. Test disposable Windows and Ubuntu VMs with synthetic data. Validate interrupted copies, long paths, Unicode, OneDrive placeholders, reparse points, large data sets and rollback. Independent security review is required before customer use.

---

## Existing inventory helper

Collect-WindowsInventory.ps1 remains an optional, read-only discovery helper. Its output may contain sensitive hardware, application and printer metadata; review and authorise any transfer.
