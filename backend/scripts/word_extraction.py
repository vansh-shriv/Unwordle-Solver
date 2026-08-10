import json 

with open("data/unwordle.json","r",encoding="utf-8") as f:
    words = json.load(f)

with open("data/unwordle.txt","w",encoding="utf-8") as f:
    for word in words:
        f.write(word+"\n")

print(f"extracted {len(words)} words")
    