body1 = """
May be there are some text here

field |  content  
---|---  
Labels(A/B) |  PMO 
multi- line
here 
A  |  B
C  |  D
end  |


or at the end of the email
"""

if __name__ == "__main__":
    resultd = {}
    _key, _value = "", ""
    _start = False
    lines = body1.strip().splitlines()
    for i in range(len(lines)):
        # start of the table
        if "---|---" in lines[i]:
            _start = True
            continue

        # end of the table
        if "end" in lines[i] and "|" in lines[i]:
            _start = False
            break

        if not _start:
            continue

        parsed = lines[i].strip().split("|")
        if len(parsed) != 2:
            resultd[_key] += "\n " + parsed[0].strip()
        else:
            _key, _value = parsed
            _key = _key.strip()
            _value = _value.strip()
            resultd[_key] = _value

    print(resultd)
