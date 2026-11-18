# Read-only office package planner

Task: `LTF-PACKAGE-003` (VERIFYING)

The planner in `tools/plan-office-packages.py` produces a deterministic candidate plan for the selected distribution profile. It consumes an explicit JSON snapshot mapping package names to boolean availability values.

Example:

```json
{
  "firefox": true,
  "libreoffice-writer": true,
  "libreoffice-calc": true,
  "libreoffice-impress": true,
  "evince": true,
  "file-roller": true
}
```

Run:

```sh
python3 tools/plan-office-packages.py --profile ubuntu-desktop --availability availability.json
python3 -m unittest discover -s projects/linux-transition-foundry/tests -p 'test_package_planner.py'
```

Unknown or unavailable packages are never selected. If any category has no confirmed candidate, the plan is BLOCKED. A complete plan is only READY_FOR_HUMAN_REVIEW; it is not an installation authorization.

## Safety contract

- No APT, dpkg, shell subprocess, network or privileged operation.
- No package/service/repository/system mutation.
- `packages_to_install` is always empty.
- `mutations_permitted`, `network_accessed`, and `privilege_required` are always false.
- Availability snapshots may be stale or incomplete; live distro package metadata and suitability still require validation.
- Any future execution workflow requires separate human review and explicit approval.
