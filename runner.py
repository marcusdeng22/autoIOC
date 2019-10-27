import summary

if __name__ == "__main__":
    with open("data/apt1/malware/htran", "r") as f1:
        htranData = ""
        for l in f1:
            htranData += l
    # summary.summarize([htranData])
    sum = summary.summarize([htranData])
    print(sum)
