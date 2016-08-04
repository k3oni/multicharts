#!/usr/bin/python
###############################################################################
'''
This code is used to generate multicharts code of EP with multiple levels.
'''

levelNum 	= 7
close 		= "close"
ep 			= "ep"

def genAccumulateLevelDiff(level):
    return "getAccumulateLevelDiff(levelDiffPerLevel_levelNum, levelDiffPerLevel_lds, %s)" % level    
    
isDayOpen	= "isDayOpen"
posPerLevel = "posPerLevel"
posPerLevelUp = posPerLevel + "Up"
posPerLevelDown = posPerLevel + "Down"
posPerLevelEP = posPerLevel + "EP"
allowEntry = "    if allowEntry = 1 and absvalue(currentContracts) < maxPosition then begin"
totalPosition = "totalPos"

def printUpOutLayerCode(level):
	print("if " + close + " >= " + ep + " + " \
		+ genAccumulateLevelDiff(level) + " then begin ")
	for i in reversed(range(0, level)):
		print('    buytocover ("Exit short at L' + str(i) + ' from UpOutRegion") '
				+ posPerLevelUp + str(i+1) + "  contract total next bar at "
				+ ep + "+" + genAccumulateLevelDiff(i) + " limit;")

	print(allowEntry)
	for i in range(1, level+1):
		print("        buy (\"Long at L-" + str(i) + " from UpOutRegion\") "
				+ posPerLevelDown + str(i) + " contract next bar at "
				+ ep + "-" + genAccumulateLevelDiff(i) + " limit;")
	print("    end;")
	print("end;");

def printDownOutLayerCode(level):
	print('if ' + close + '<=' + ep + '-' + genAccumulateLevelDiff(level) + ' then begin')
	print(allowEntry)
	for i in reversed(range(1, level+1)):
		print('        sellshort ("Short at L' + str(i) + ' from DownOutRegion ")'
				+ posPerLevelUp + str(i) + " contract next bar at "
				+ ep + "+" + genAccumulateLevelDiff(i) + " limit;")
	print('    end;')
	for i in range(0, level):
		print("    sell (\"Exit long at L-" + str(i) + " from DownOutRegion\") "
				+ posPerLevelDown + str(i+1) + " contract total next bar at "
				+ ep + "-" + genAccumulateLevelDiff(i) + " limit;")
	print("end;");
		

def printLevel_i_Level_i_plus_1(level):
	print("if " + close + ">=" + ep + "+" + genAccumulateLevelDiff(level) + \
             " and close <" + ep + " + " + genAccumulateLevelDiff(level+1) + " then begin ")
	
	levelAboveII1 = levelNum - level - 1
	levelBelowII1 = level - 1
	interval = 'L' + str(level) + 'L' + str(level+1) 
	print(allowEntry)
	for i in range(0, levelAboveII1):
		curLevel = levelNum - i
		print('        sellshort ("Short at L' + str(curLevel) + ' from ' + interval\
				 + '") ' + posPerLevelUp + str(curLevel) + ' contracts next '\
				 + 'bar at ' + ep  + '+' + genAccumulateLevelDiff(curLevel) + ' limit;') 	
		
	print('        if currentcontracts<' + totalPosition + '[' + str(level+1) + '] ' + ' then begin' )
	print('            sellshort("Short at L' + str(level+1) + ' from ' + interval \
					+ '") ' + posPerLevelUp + str(level+1) + ' contracts next bar at '\
					+ ep + "+" + genAccumulateLevelDiff(level+1) + ' limit; ')
	print('        end;')
	print('    end;')

	print('    if currentcontracts>=' + totalPosition + '[' + str(level+1) + '] then begin')
	print('        buytocover ("Exit short at L' + str(level) + ' from ' + interval\
			 		+ '") ' + posPerLevelUp + str(level+1) + ' contract total next bar'\
					+ ' at ' + ep + '+' + genAccumulateLevelDiff(level) + ' limit;')
	print('    end;')
	

	for i in reversed(range(0, level)):
		print('    buytocover ("Exit short at L' + str(i) + ' from ' + interval + '")'
				+ posPerLevelUp + str(i+1) + ' contract total next bar at '
				+ ep + "+" + genAccumulateLevelDiff(i) + " limit;")
	print(allowEntry)
	for i in range(1, levelNum+1):
		print('        buy ("Long at L-' + str(i) + ' from ' + interval + '")'
				+ posPerLevelDown + str(i) + " contract next bar at "
				+ ep + "-" + genAccumulateLevelDiff(i) + " limit;")
	print('    end;')
	print('end;')

def printLevel_i_Level_i_minus_1(level):
	levelAboveII1 = level - 1
	levelBelowII1 = levelNum - level - 1
	interval = 'L-' + str(level) + 'L-' + str(level-1) 

	print("if " + close + ">=" + ep + "-" + str(level) + "*" \
			+ genAccumulateLevelDiff(level) + " and close<" + ep + "-" + genAccumulateLevelDiff(level-1) \
			+ " then begin ")
	
	print(allowEntry)
	for i in range(0, levelNum):
		curLevel = levelNum - i
		print('        sellshort ("Short at L' + str(curLevel) + ' from ' + interval\
				 + '") ' + posPerLevelUp + str(curLevel) + ' contracts next '\
				 + 'bar at ' + ep  + '+' + genAccumulateLevelDiff(curLevel) + ' limit;') 	
	print('    end;')

	for i in range(0, levelAboveII1):
			print('    sell ("Exit long at L-' + str(i) + ' from ' + interval + \
					'") ' + posPerLevelDown + str(i+1) + ' contract total next bar at ' + ep + '-' + \
					genAccumulateLevelDiff(i) + ' limit;')

	print('    if currentcontracts>=' + totalPosition + '[' + str(level) + '] ' + ' then begin' )
	print('        sell("Exit long at L-' + str(level-1) + ' from ' + interval \
					+ '") ' + posPerLevelDown + str(level) + ' contracts total next bar at '\
					+ ep + "-" + genAccumulateLevelDiff(level-1) + ' limit; ')
	print('    end;')

	print(allowEntry)
	print('        if currentcontracts<' + totalPosition + '[' + str(level) + '] then begin')
	print('            buy ("Long at L-' + str(level) + ' from ' + interval\
			 		+ '") ' + posPerLevelDown + str(level) + ' contract next bar'\
					+ ' at ' + ep + '-' + genAccumulateLevelDiff(level) + ' limit;')
	print('        end;')

	for i in range(level+1, levelNum+1):
		print('        buy ("Long at L-' + str(i) + ' from ' + interval + '")'
				+ posPerLevelDown + str(i) + " contract next bar at "
				+ ep + "-" + genAccumulateLevelDiff(i) + " limit;")
	print('    end;')

	print('end;')

def printPosPerLevel(levelNum):
	for i in range(1, levelNum+1):
		print(posPerLevelUp + str(i) + '(0),')
		print(posPerLevelDown + str(i) + '(0),')
	
	print(' ')
	
	for i in range(1, levelNum+1):
		print('init' + posPerLevelDown + str(i) + '(1),')
		print('init' + posPerLevelUp + str(i) + '(1),')
	
	print(' ')	

	for i in range(1, levelNum+1):
		print(posPerLevelUp + str(i) + '= incPosition ' + ' + init' + posPerLevelUp + str(i) + ';')
		print(posPerLevelDown + str(i) + '= incPosition ' + ' + init' + posPerLevelDown + str(i) + ';')

	print(' ')
	

def main():
	printPosPerLevel(levelNum)
	printUpOutLayerCode(levelNum)
	for i in reversed(range(0, levelNum)):
		printLevel_i_Level_i_plus_1(i)
	for i in range(1, levelNum+1):
		printLevel_i_Level_i_minus_1(i)
	printDownOutLayerCode(levelNum)

if __name__ == "__main__":
	main()
