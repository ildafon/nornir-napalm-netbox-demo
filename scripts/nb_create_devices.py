import textfsm

input_file = open("TLC-RUES-PE3-01", encoding='utf-8')
raw_text_data = input_file.read()
input_file.close()

template = open("show_running_config.textfsm")
re_table = textfsm.TextFSM(template)
fsm_results = re_table.ParseText(raw_text_data)

outfile_name = open("outfile.csv", "w+")
outfile = outfile_name

print(re_table.header)
for s in re_table.header:
    outfile.write("%s;" % s)
outfile.write("\n")

counter = 0
for row in  fsm_results:
    print(row)
    for s in row:
        outfile.write("%s;" % s)
    outfile.write("\n")
    counter +=1
print("Write %d records" % counter)