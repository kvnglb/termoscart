import subprocess

help_msg = subprocess.run(["poetry", "run", "termoscart", "-h"], capture_output=True, text=True).stdout
subs = help_msg.split("positional arguments:")[1].split("optional arguments:")[0].replace("{", "").replace("}", "").split(",")

for sub in subs:
    f_sub = sub.strip()
    out = subprocess.run(["poetry", "run", "termoscart", f_sub, "-h"], capture_output=True, text=True).stdout
    help_msg += "\n{}\n{}".format(f_sub.upper(), out)

with open("./README.template.md", "r") as fr, open("./README.md", "w") as fw:
    lines = fr.read()
    new_lines = lines.replace("<HELP_MESSAGE>", help_msg)
    fw.write(new_lines)
