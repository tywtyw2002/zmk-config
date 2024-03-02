import yaml
from pathlib import Path
from string import Template
from functools import reduce
from operator import iconcat


row_layout = {
    0: ["╭", "┬", "╮"],
    1: ["├", "┼", "┤"],
    2: ["├", "┼", "┤"],
    3: ["╰", "┴", "╯"],
}
key_space = 16
thumb_key_count = 3
row_key_count = 6

keymap_templates = Template("""
/ {
  keymap {
    compatible = "zmk,keymap";

    $layer_name {
      label = "$layer_id";
      bindings = <
$keybinds
      >;
    };
  };
};
""")


def gen_key_layout(key_count, layout):
    lay = "─" * key_space + layout[1]
    key_layout = layout[0] + lay * key_count

    return key_layout[:-1] + layout[2]


def build_layer_layout(layer):
    binds = []

    key_idx = 0
    for row_idx in range(len(layer["keymaps"])):
        keys = reduce(iconcat, layer["keymaps"][row_idx], [])
        key_count = int((len(keys) + 1) / 2)

        # layout header
        layout = gen_key_layout(key_count, row_layout[row_idx])
        binds.append(f"//  {layout}    {layout}")

        # key index
        key_index_layout = "//  │"
        key_bind_layout = " " * 5
        for idx in range(len(keys)):
            key_index_layout += f"{key_idx:<{key_space}}│"
            key_idx += 1

            # key binds
            key = keys[idx]
            if key == "_":
                key = "&none"
            elif key == ".":
                key = "&trans"
            elif key[0] != "&":
                key = f"&kp {key}"

            key_bind_layout += f"{key:<{key_space}} "

            if idx == key_count - 1:
                key_index_layout += "    │"
                key_bind_layout += "     "

        binds.append(key_index_layout)
        binds.append(key_bind_layout)

        # thumb key header
        if row_idx == 3:
            thumb_layout = "╰" + "─" * key_space
            key_lay = "┴" + "─" * key_space

            thumb_layout += key_lay * (row_key_count - thumb_key_count - 1)
            thumb_layout += ("┼" + "─" * key_space) * thumb_key_count
            thumb_layout += "┤"

            binds[-3] = f"//  {thumb_layout}    ├{thumb_layout[::-1][1:-1]}╯"

            # recalc the margin space
            margin_space = " " * (key_space + 1) * (row_key_count - thumb_key_count)
            binds[-2] = f"//  {margin_space}{key_index_layout[4:]}"
            binds[-1] = f"    {margin_space}{key_bind_layout[4:]}"
            binds.append(f"//  {margin_space}{layout}    {layout}")

    return binds


def main():
    with open("layout.yaml") as fp:
        layout = yaml.safe_load(fp)

    keymap_root = Path("keymaps")

    for layer in layout["layers"]:
        layer_name = layer["layer"]
        if name := layer.get("name", None):
            layer_name += f"_{name.lower()}"

        layer_file = keymap_root / f"{layer_name}.dtsi"

        layer_file.write_text(
            keymap_templates.substitute(
                keybinds="\n".join(build_layer_layout(layer)),
                layer_id=layer["layer"],
                layer_name=layer_name.lower(),
            )
        )

        print(f"Generate Layer <{layer['layer']}> -> {layer_name}")


if __name__ == "__main__":
    main()
