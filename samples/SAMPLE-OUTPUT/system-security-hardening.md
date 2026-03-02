# System Security Hardening

## Overview

Apply security hardening measures to Linux systems following CIS benchmarks

**Hosts**: `all`


**Tags**: security, hardening, compliance


## Parameters


| Parameter | Description |
|-----------|-------------|

| `ssh_port Custom SSH port (default` | 22) |



## Warnings


> ⚠️ **Important Notices:**
> 

> - This playbook will modify critical system security settings

> - Test in non-production environment first

> - Ensure you have alternative access before disabling root SSH

> - This will block all incoming traffic except explicitly allowed

> - Active SSH sessions may be affected



## Usage Examples



```yaml
ansible-playbook harden-system.yml -e "ssh_port=2222 disable_root_ssh=true"
```




## TODOs

| Location | Author | TODO |
|----------|--------|------|
| File | - | Add SELinux/AppArmor configuration |
| File | security | Implement file integrity monitoring with AIDE |
| File | ops | Add security audit logging configuration |
| File | - | SSH configuration needs validation before restart |
| Harden SSH configuration | ops | Add email notifications for update status |
| Restrict SSH to specific users | security | Add two-factor authentication support |



## Tasks

### Pre-Tasks

No pre-tasks defined.


### Main Tasks


| Task | Description | Notes | Warnings | Tags |
|------|-------------|-------|----------|------|
| **Update all packages**<br>*apt* |  |  |  |  |
| **Install security packages**<br>*apt* | Ensure all system packages are up-to-date | Cache valid for 1 hour to avoid excessive updates | Distribution upgrade may require system reboot | updates, maintenance |
| **Configure unattended-upgrades**<br>*copy* | Install essential security tools | AIDE provides file integrity monitoring<br>Auditd enables system call auditing |  | install, security |
| **Harden SSH configuration**<br>*lineinfile* | Enable automatic installation of security updates | Only security patches are auto-installed | Automatic updates may affect application compatibility | configuration, updates |
| **Restrict SSH to specific users**<br>*lineinfile* | Apply security best practices to SSH daemon | Custom port helps reduce automated attack attempts | Changes require SSH service restart<br>Ensure SSH keys are deployed before disabling passwords | ssh, security, compliance |
| | *implements CIS benchmark controls* | | | |
| **Configure UFW defaults**<br>*ufw* | Limit SSH access to approved user accounts | Implements principle of least privilege | Only users in this list can SSH to the system<br>Empty list means all users can access via SSH | ssh, security, access-control |
| **Allow SSH port**<br>*ufw* | @title Configure UFW firewall @description Set up UFW with default deny policy @param enable_firewall Whether to enable the firewall @warning This will block all incoming traffic except explicitly allowed |  |  |  |
| **Enable UFW**<br>*ufw* | @title Allow SSH through firewall @description Permit SSH connections on configured port @param ssh_port SSH port to allow |  |  |  |
| **Configure fail2ban**<br>*copy* | @title Enable UFW firewall @description Activate the UFW firewall |  |  |  |
| **Configure password policy**<br>*lineinfile* | @title Configure fail2ban @description Set up fail2ban to block brute-force attempts @param enable_fail2ban Whether to configure fail2ban |  |  |  |
| **Disable unused filesystems**<br>*kernel_blacklist* | @title Set password policy @description Configure password aging and complexity requirements @param password_max_age Maximum password age in days @param password_min_length Minimum password length |  |  |  |
| **Configure kernel security parameters**<br>*sysctl* | @title Disable unused filesystems @description Prevent loading of unused filesystem kernel modules |  |  |  |
| **Start auditd service**<br>*service* | @title Set kernel security parameters @description Configure sysctl security settings |  |  |  |


### Post-Tasks

No post-tasks defined.


### Handlers


- **Restart sshd** (*service*)

- **Restart fail2ban** (*service*)



## Execution Flow

```mermaid
graph TD
    Start([Start])

    subgraph MainTasks["Tasks"]
    
        T0["Update all packages"]
    
        T1["Install security packages"]
    
        T2["Configure unattended-upgrades"]
    
        T3["Harden SSH configuration"]
    
        T4["Restrict SSH to specific users"]
    
        T5["Configure UFW defaults"]
    
        T6["Allow SSH port"]
    
        T7["Enable UFW"]
    
        T8["Configure fail2ban"]
    
        T9["Configure password policy"]
    
        T10["Disable unused filesystems"]
    
        T11["Configure kernel security parameters"]
    
        T12["Start auditd service"]
    
    end

    Start --> MainTasks



    subgraph Handlers["Handlers"]
    
        H0["Restart sshd"]
    
        H1["Restart fail2ban"]
    
    end

    
    MainTasks
    --> End([Complete])
```


---

*Documentation generated by Anodyse v0.1.0*

