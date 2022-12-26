#!/usr/bin/env python3
import argparse
import base64
import json
import os
import shlex
import subprocess
import yaml

def merge_list(l, append, name):
    return [c for c in l if c["name"] != name] + [append]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inventory", help="Ansible inventory")
    parser.add_argument("--ansible-arguments", help="Extra Ansible args")
    parser.add_argument("--host-pattern", default="all", help="Host pattern to read from")
    parser.add_argument("--no-become", action="store_true", help="Don't use --become")
    parser.add_argument("--path", default="/etc/rancher/k3s/k3s.yaml", help="Path to k3s.yaml")
    parser.add_argument("--kube-config", default="~/.kube/config", help="Path to existing kubeconfig")
    parser.add_argument("--master-host", help="Set k8s master explicitly instead of using ansible_host")
    parser.add_argument("--name", help="Set name of context/server/user instead of using ansible_host")
    parser.add_argument("--stdout", action="store_true", help="Output result to stdout instead of writing a new kubeconfig")
    args = parser.parse_args()

    if not args.inventory:
        raise Exception("-i inventory must be specified")

    ansible_cmd = ["ansible", args.host_pattern, "-i", args.inventory, "-m", "slurp", "-a", f"src={args.path}"]
    # TODO: make less clunky
    if not args.no_become:
        ansible_cmd.append("-b")
    if args.ansible_arguments:
        ansible_cmd.extend(shlex.split(args.ansible_arguments))

    env = {
        **os.environ,
        "ANSIBLE_LOAD_CALLBACK_PLUGINS": "1",
        "ANSIBLE_STDOUT_CALLBACK": "json",
    }

    new_kubeconfig = None
    master_host = None

    raw_output = subprocess.check_output(args=ansible_cmd, env=env)
    output = json.loads(raw_output)
    tasks = [task for play in output["plays"] for task in play["tasks"]]
    for task in tasks:
        for host, result in task["hosts"].items():
            if "msg" in result:
                print(f"{host}:", result["msg"])
            content = result.get("content", None)
            if not content:
                continue
            encoding = result["encoding"]
            if encoding != "base64":
                raise Exception(f"Unknown encoding {encoding}")
            content = base64.b64decode(content)
            name = host
            if args.name:
                name = args.name
            master_host = host
            if args.master_host:
                master_host = args.master_host
            content = content.replace(b"127.0.0.1", bytes(master_host, "utf-8"))
            break
        if content:
            break

    if not content:
        raise Exception(f"Could not read {args.path}")
    new_kubeconfig = yaml.safe_load(content)

    new_kubeconfig["users"][0]["name"] = name
    new_kubeconfig["clusters"][0]["name"] = name
    new_kubeconfig["contexts"][0]["name"] = name
    new_kubeconfig["contexts"][0]["context"]["cluster"] = new_kubeconfig["clusters"][0]["name"]
    new_kubeconfig["contexts"][0]["context"]["user"] = new_kubeconfig["users"][0]["name"]

    with open(os.path.expanduser(args.kube_config), "r") as f:
        kubeconfig = yaml.safe_load(f)
    kubeconfig["clusters"] = merge_list(kubeconfig["clusters"], new_kubeconfig["clusters"][0], name)
    kubeconfig["contexts"] = merge_list(kubeconfig["contexts"], new_kubeconfig["contexts"][0], name)
    kubeconfig["users"] = merge_list(kubeconfig["users"], new_kubeconfig["users"][0], name)
    if args.stdout:
        import sys
        yaml.safe_dump(kubeconfig, sys.stdout)
    else:
        with open(os.path.expanduser(args.kube_config), "w") as f:
            yaml.safe_dump(kubeconfig, f)


if __name__ == "__main__":
    main()
