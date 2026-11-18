# Ansible baseline

This is an initial, deliberately conservative workstation configuration role.

## Requirements

- Ubuntu test VM matching the target architecture.
- Python 3 and Ansible Core installed on the controller.
- Install collection dependencies with `ansible-galaxy collection install -r requirements.yml`.

## Review before execution

The inventory is empty by default. Add only a disposable, authorised test VM. Inspect variables and network access before enabling firewall management. The firewall is disabled by default because blindly enabling it can interrupt remote access, printing, discovery and line-of-business services.

Disk partitioning, OS installation, identity integration, account creation, endpoint enrolment, backups and reboot are intentionally outside this first role. They require separate, customer-specific design and acceptance.

## Commands

```sh
ansible-playbook -i inventory/lab.yml site.yml --syntax-check
ansible-playbook -i inventory/lab.yml site.yml --check --diff
ansible-playbook -i inventory/lab.yml site.yml --diff
```

Run the final command only against a disposable test VM after reviewing the plan. Use a real inventory only after customer approval.

## Known limitations

- The selected package names and service units must be verified against the exact Ubuntu release and enabled repositories.
- The UFW tasks require the community.general collection.
- `failed_when: false` on service checks is a compatibility concession for minimal images; production acceptance must explicitly verify service state and report unsupported cases.
- This is not a CIS benchmark, compliance certification or complete endpoint security product.
