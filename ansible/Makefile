export SELF ?= $(MAKE)

PYENV ?= "/Users/xluffy/.pyenv/shims"
ANSIBLE ?= "$(PYENV)/ansible"
ANSIBLE-INVENTORY ?= "$(PYENV)/ansible-inventory"
ENV ?= "prod"

## Ensure all plugins can be fetched
ansible/facts:
	@$(ANSIBLE) --module-name="setup" --inventory-file="inventories/$(ENV)/hosts" all --tree="out/"

ansible/tasks: $(playbook)
	@$(ANSIBLE) --inventory-file="inventories/$(ENV)/hosts" --list-tasks "$(playbook)"

ansible/hosts:
	@$(ANSIBLE-INVENTORY) -i "inventories/$(ENV)/hosts" --graph

facts:
	$(SELF) ansible/facts

tasks:
	$(SELF) ansible/tasks

hosts:
	$(SELF) ansible/hosts
