"""
STEP 05

Merge multiple json (created by segmentation.py)

Require: ./seg_partials/seg[num].json
Produce: ./seg.json
"""
if __name__ == "__main__":
    import json
    maxIndex = 126 # change to yours
    dataList = []
    for i in range(maxIndex + 1):
        part = json.load(open("seg_partials/seg" + str(i) + ".json"))
        dataList += part
        print(i)
    json.dump(dataList, open("seg.json", "w"), separators=(',', ':'), ensure_ascii=False)
