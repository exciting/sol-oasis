import yaml

with open('configs/allowed-users.yaml', 'r') as f_:
    users = yaml.safe_load(f_)

with open('configs/nomad-template.yaml', 'r') as f_:
    nomad_config = yaml.safe_load(f_)

nomad_config['oasis'].update(**users)

with open('configs/nomad.yaml', 'w') as f_:
    yaml.dump(nomad_config, f_, default_flow_style=False, sort_keys=False)
