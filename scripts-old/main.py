import re

def main():
    with open("/home/adeshkin/Downloads/Орфографический словарь хакасского языка.docx.txt") as f:
        text = f.read().replace('́', '').replace('´', '').replace('́','')
    print(sorted(set(text)))
    print(len(sorted(set(re.findall(r'(\w+)-(\w+)', text.lower().replace('́', ''))))))
    print(*sorted(set(re.findall(r'(\w+)-(\w+)', text.lower()))), sep="\n")



if __name__ == "__main__":
    main()