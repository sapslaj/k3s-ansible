
.PHONY: syncroles
syncroles:
	cp -r roles/sapslaj.k3s_master/tasks/prereq roles/sapslaj.k3s_node/tasks/prereq
	cp roles/sapslaj.k3s_master/tasks/main.yml roles/sapslaj.k3s_node/tasks/main.yml
	cp roles/sapslaj.k3s_master/tasks/prereq.yml roles/sapslaj.k3s_node/tasks/prereq.yml
	cp roles/sapslaj.k3s_master/tasks/download.yml roles/sapslaj.k3s_node/tasks/download.yml
	cp roles/sapslaj.k3s_master/tasks/raspberrypi.yml roles/sapslaj.k3s_node/tasks/raspberrypi.yml
