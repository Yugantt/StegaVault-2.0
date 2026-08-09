path = r"C:\Users\YUGANT\Desktop\StegaVault-2\templates\layouts\dashboard_base.html"

with open(path, encoding="utf-8") as f:
    lines = f.readlines()

# find the Security <li> block
sec = next(i for i, l in enumerate(lines) if "Security</span>" in l)
start = sec
while "{% if session" not in lines[start]:
    start -= 1
end = sec
while "{% endif %}" not in lines[end]:
    end += 1

block = lines[start:end + 1]
del lines[start:end + 1]

# drop blank lines left behind
while start < len(lines) and lines[start].strip() == "":
    del lines[start]

# insert before the Image menu item
img = next(i for i, l in enumerate(lines) if "startswith('image.')" in l)
lines[img:img] = block + ["\n"]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("done")