
keymap:
    python3.11 ./export.py

gen_svg: keymap
    keymap -c ./keymap_drawer.config.yaml parse -c 10 -z  ./config/corne.keymap > /tmp/keymap.yaml
    keymap -c ./keymap_drawer.config.yaml draw /tmp/keymap.yaml > layout.svg