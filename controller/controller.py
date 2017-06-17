import csv
def save(Texto, txt):
	with open(txt, 'a', newline='') as csvfile:
	    spamwriter = csv.writer(csvfile, delimiter=',',quotechar=' ', quoting=csv.QUOTE_MINIMAL)
	    spamwriter.writerow(Texto)

