# k3s-ansible

Fork of [k3s-io/k3s-ansible](https://github.com/k3s-io/k3s-ansible) be a little more modular.

## Example playbook

better example in progress

```yaml
- hosts: k3s_master
  become: true
  roles:
    - role: sapslaj.k3s_master

- hosts: k3s_node
  become: true
  roles:
    - role: sapslaj.k3s_node
      vars:
        k3s_master_hostname: k3smaster.sapslaj.com
        k3s_token: '{{ hostvars["k3smaster.sapslaj.com"]["k3s_token"] }}'
```
