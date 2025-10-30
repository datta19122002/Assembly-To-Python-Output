from builtins import int 
import re
import warnings as w
# Read the file
with open("source.asm", "r") as f:
    content = f.read()


reg32 = {
    "eax": "000",
    "ecx": "001",
    "edx": "010",
    "ebx": "011",
    "esp": "100",
    "ebp": "101",
    "esi": "110",
    "edi": "111",
}
arithmeticIns = {
    "add": "000",
    "or": "001",
    "adc": "010",
    "sbb": "011",
    "and": "100",
    "sub": "101",
    "xor": "110",
    "cmp": "111"
}
reg8 = {
    "al": "000",
    "cl": "001",
    "dl": "010",
    "bl": "011",
    "ah": "100",
    "ch": "101",
    "dh": "110",
    "bh": "111"
}

opcoderr ={
    'add':"01",'sub':'29', 'cmp':'39', 'or':'09', 'adc':'11', 'sbb':'19','xor':'33'
}




# --- Extract the .data section only ---
data_match = re.search(r"section\s+\.data(.*?)(?=section\s+\.)", content, re.DOTALL)
if data_match:
    data_section = data_match.group(1).strip()
    print("----- .data Section -----")
    # --- Split into lines and process each one ---
    lines = [line.strip() for line in data_section.splitlines() if line.strip()]

    for line in lines:
        # Example line: "r1 dd 10"
        tokens = line.split()  # Split by spaces        
        
        if tokens[1] in "dd":
            value_str = " ".join(tokens[2:])
            
            try: 
                value = int(value_str)
                opcode =  hex(value)[2].upper().zfill(2) + f"000000\t\t {tokens[0]} {tokens[1]} {tokens[2]}"
                print(opcode)
            except ValueError:
                print(f" Warning: '{tokens[0]} {tokens[1]} {tokens[2]}' has non-integer value → {value_str}")
        
        elif tokens[1] in "db":
            value_str = " ".join(tokens[2:])
            try:
                value = str(value_str)[1:-1]           #  Suppose we take naem "Datta"--> Datta
                hexa = [f"{ord(c):02X}" for c in value] #  Conver Ascii value to hexadecimal values 
                hex_values = "".join(hexa)              # It will give array to join together 
                print(f"{hex_values} \t\t {tokens[0]} {tokens[1]} {tokens[2]}")
            except ValueError:
                print(f" Warning: '{tokens[0]} {tokens[1]} {tokens[2]}' has non-integer value → {value_str}")




# --- Extract the .text section only ---
text_match = re.search(r"section\s+\.text(.*)", content, re.DOTALL)
if text_match:
    print("------------| This is a text section | -----------------")
    text_section = text_match.group(1).strip()

    # --- Split into lines and process each one ---
    lines = [line.strip() for line in text_section.splitlines() if line.strip()]

    for line in lines:
        tokens = line.split()
        
        #  Check correctly
        if tokens[0].lower() == "mov":
            # Remove commas from operands
            r1 = tokens[1].replace(",", "").lower()
            r2 = tokens[2].replace(",", "").lower()
            try:
                # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "8B" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

                if reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "89" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                        
                
                if r1 in reg32 and r2 in reg32:
                    r = f"89{hex(int("11"+reg32[r2]+reg32[r1],2))[2:].upper()}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}"
                    print(r)
                if r1 in reg32 and r2.isdigit() :

                    movr = {
                        "eax": "B8",
                        "ecx": "B9",
                        "edx": "BA",
                        "ebx": "BB",
                        "esp": "BC",
                        "ebp": "BD",
                        "esi": "BD",
                        "edi": "BE"
                    }
                    r = f"{movr[r1]}{hex(int(r2))[2:].upper().zfill(2)}000000"
                    print(f"{r}\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
            except Exception as e:
                print(f"Error occurred: {e}")
        elif tokens[0] in arithmeticIns and tokens[1].replace(",","") in reg32 and tokens[2].isdigit() :  # add eax, 10 
            r = "83" + hex(int("11"+arithmeticIns[tokens[0]]+ reg32[tokens[1].replace(",","")],2))[2:].upper() + hex(int(tokens[2])).upper()[2:].zfill(2)
            print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")


        elif tokens[0].lower()=="add":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "03" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "01" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                

                if r1 in reg32 and r2 in reg32:
                    r = "01" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                    print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
            except:
                pass

            
            
        #----------------> Substraction<------------------

        elif tokens[0].lower()=="sub":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "2B" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "29" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

            except:
                pass    
            if r1 in reg32 and r2 in reg32:
                r = "29" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
            

        #-----------------------> Campairing <-------------------    
        elif tokens[0].lower()=="cmp":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "3B" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "39" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

            except:
                pass
            if r1 in reg32 and r2 in reg32:
                r = "39" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
        elif tokens[0].lower()=="or":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "0B" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "09" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

            except:
                pass
            if r1 in reg32 and r2 in reg32:
                r = "09" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
        elif tokens[0].lower()=="adc":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "13" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "11" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

            except:
                pass
            if r1 in reg32 and r2 in reg32:
                r = "11" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
        elif tokens[0].lower()=="sbb":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "1B" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "19" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

            except:
                pass
            if r1 in reg32 and r2 in reg32:
                r = "19" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
        elif tokens[0].lower()=="xor":
            r1 = tokens[1].replace(",","")
            r2 = tokens[2]
            try:
                
                 # SIB Calculate 
                pattern = r"^\s*\[\s*(\w+)\s*(?:\+\s*(\w+|\d+)\s*(?:\*\s*(\d+)\s*)?)?\s*\]\s*,?\s*$"

                reg1= re.match(pattern, r2.lower())
                reg2= re.match(pattern, r1.lower())
                b1 = {"1":"00", "2":"01","4":"10","8":"11"}
                if reg1:    # instruction : op reg sib
                    base = reg1.group(1)
                    index = reg1.group(2)
                    scale = reg1.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                            sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                            r = hex(int("00" + reg32[r1] + "100",2))[2:].upper().zfill(2)
                            op = "33" +r + sib
                            print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")
                elif reg2:        # instruction : op sib reg
                    base = reg2.group(1)
                    index = reg2.group(2)
                    scale = reg2.group(3)
                    if base in reg32 and index in reg32 and not(not(scale in b1)):
                        pass
                        sib = hex(int(b1[scale] + reg32[index] + reg32[base],2))[2:].upper().zfill(2) 
                        r = hex(int("00" + reg32[r2] + "100",2))[2:].upper().zfill(2)
                        op = "31" +r + sib
                        print(f"{op}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

            except:
                pass
            if r1 in reg32 and r2 in reg32:
                r = "33" + hex(int("11" + reg32[tokens[2]] + reg32[tokens[1].replace(",","")],2))[2:].upper().zfill(2)
                print(f"{r}\t\t\t {tokens[0]} {tokens[1]} {tokens[2]}")

        
        inc = {
            "eax": "40",
            "ecx": "41",
            "edx": "42",
            "ebx": "43",
            "esp": "44",
            "ebp": "45",
            "esi": "46",
            "edi": "47",            
        }
        dec = {
            "eax": "48",
            "ecx": "49",
            "edx": "4A",
            "ebx": "4B",
            "esp": "4C",
            "ebp": "4D",
            "esi": "4E",
            "edi": "4F",            
        }
        if tokens[0].lower() == "inc":
            r = inc[tokens[1]]
            print(f"{r}\t\t\t {tokens[0]} {tokens[1]}")
        elif tokens[0].lower() == "dec":
            r = dec[tokens[1]]
            print(f"{r}\t\t\t {tokens[0]} {tokens[1]}")



       



