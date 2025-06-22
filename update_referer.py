import sys
import re

INPUT_FILE = "GreekSportsChannels.m3u8"

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_referer.py <new_referer_url>")
        sys.exit(1)

    new_url = sys.argv[1].rstrip('/')

    with open(INPUT_FILE, encoding='utf-8') as f:
        lines = f.readlines()

    pattern = re.compile(r'(Referer|Origin)=https?://[^/&]+/?')

    new_lines = []
    for line in lines:
        line = pattern.sub(lambda m: f"{m.group(1)}={new_url}/", line)
        new_lines.append(line)

    with open(INPUT_FILE, "w", encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
