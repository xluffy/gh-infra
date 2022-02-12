export SELF ?= $(MAKE)

ANSIBLE ?= ansible
ANSIBLE-INVENTORY ?= ansible-inventory
ENV ?= "prod"

## Ensure all plugins can be fetched
ansible/facts:
	@$(ANSIBLE) --module-name="setup" --inventory-file="inventories/$(ENV)/hosts" all --tree="out/"

ansible/tasks: $(playbook)
	@$(ANSIBLE) --inventory-file="inventories/$(ENV)/hosts" --list-tasks "$(playbook)"

ansible/hosts:
	@$(ANSIBLE-INVENTORY) -i "inventories/$(ENV)/hosts" --graph

ansible/infos:
	@$(ANSIBLE-INVENTORY) -i "inventories/$(ENV)/hosts" --list -y

facts:
	$(SELF) ansible/facts

tasks:
	$(SELF) ansible/tasks

hosts:
	$(SELF) ansible/hosts

infos:
	$(SELF) ansible/infos
