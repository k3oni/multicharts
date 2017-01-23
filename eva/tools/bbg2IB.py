#!/usr/bin/python
###############################################################################

def toIBContract(contract):
    if contract is None:
        infor('Cannot find IB contract name since contract is None.')
        return None
    ctr, suffix = contract.split(' ')
    name = ctr[:-2]
    month = ctr[-2]
    year = ctr[-1]

    nameDict = dict()
    nameDict['HC'] = 'HHI.'
    nameDict['HI'] = 'HSI_'

    monthDict = dict()
    monthcode = 'FGHJKMNQUVXZ'
    for i in range(0, len(monthcode)):
        monthDict[monthcode[i]] = i+1 

    month  = monthDict[month]
    ibname = '%s201%s%02dF000000' % (nameDict[name], year, month)        

    return ibname
