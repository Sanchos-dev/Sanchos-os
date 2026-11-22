
hyprctl binds | awk '
BEGIN {
    FS = "\n"
    RS = "\n\n"
    mod_order[1] = 64; mod_name[64] = "SUPER"
    mod_order[2] = 4;  mod_name[4]  = "CTRL"
    mod_order[3] = 8;  mod_name[8]  = "ALT"
    mod_order[4] = 1;  mod_name[1]  = "SHIFT"
}
{
    modmask = 0
    key = ""
    desc = ""
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^\tmodmask:/) {
            split($i, a, ": ")
            modmask = a[2] + 0
        } else if ($i ~ /^\tkey:/) {
            split($i, a, ": ")
            key = toupper(a[2])
        } else if ($i ~ /^\tdescription:/) {
            desc = substr($i, index($i, ": ") + 2)
        }
    }
    if (desc != "") {
        mods = ""
        for (j = 1; j <= 4; j++) {
            bit = mod_order[j]
            if (and(modmask, bit)) {
                mods = (mods == "" ? mod_name[bit] : mods " + " mod_name[bit])
            }
        }
        combo = (mods != "" && key != "") ? (mods " + " key) : (mods != "" ? mods : key)
        printf "%s\n➔ %s\0", combo, desc
    }
}' | rofi -dmenu -i -replace -p "Keybinds" -sep '\0' -eh 2
