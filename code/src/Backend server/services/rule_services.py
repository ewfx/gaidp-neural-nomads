import json
import os


def get_rules(file_path):
    with open(file_path, 'r') as file:
        rules = json.load(file)
    return rules

def edit_rule(file_path, rule_id, field_name, value):
    with open(file_path, 'r') as file:
        rules = json.load(file)
    for rule in rules.values():
        if rule["rule_id"] == rule_id:
            print(rule)
            rule[field_name] = value
            break
    with open(file_path, 'w') as file:
        json.dump(rules, file)
    return f"Rule with ID {rule_id} updated successfully."

def delete_rule(file_path, rule_id):
    with open(file_path, 'r') as file:
        rules = json.load(file)
    rules.pop(rule_id)
    with open(file_path, 'w') as file:
        json.dump(rules, file)
    return f"Rule with ID {rule_id} deleted successfully."
