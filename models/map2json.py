import re
""" 2014/01/15 construct a query dict from a query matrix
By Song Anliang
"""

# Thread-unsafe, move back to local
# notflag = False

def map2json(mp):
        if not mp:
            return {}

        prioritymapping = {'end':0,'or':1,'and':2}
        json = {}
        relationstack = []
        expressionstack = []
        notflag = [False]

        def realgetexpr(key,value):
                if key in ('subject','from_','to','attach_txt','body_txt'):
                        # re object cannot be deep-copied, use the raw form
                        # return re.compile(re.escape(value))
                        return {'$regex': re.escape(value), '$options': 'i'}
                elif key=='start':
                        return {'$gte':value}
                elif key=='end':
                        return {'$lte':value}
                elif key in ['timezone','ip']:
                        return value
                else:
                        return 'error'		

        def getexpr(key,value):
                if key in ('subject','from_','to','attach_txt','body_txt'):
                        return {key:realgetexpr(key,value)}
                elif key=='start':
                        return {'date':realgetexpr(key,value)}
                elif key=='end':
                        return {'date':realgetexpr(key,value)}
                elif key in ['timezone','ip']:
                        return {key:realgetexpr(key,value)}
                else:
                        return 'error'

        def getnotexpr(key,value):
                return {key:{'$not':realgetexpr(key,value)}}

        def readexpression(line):
                if line['leftvalue'] and line['rightvalue']:
                        if line['logical']=='not':
                                return {'$and':[getexpr(line['key'],line['leftvalue']),getnotexpr(line['key'],line['rightvalue'])]}
                        elif line['logical']=='and':
                                return {'$and':[getexpr(line['key'],line['leftvalue']),getexpr(line['key'],line['rightvalue'])]}
                        elif line['logical']=='or':
                                return {'$or':[getexpr(line['key'],line['leftvalue']),getnotexpr(line['key'],line['rightvalue'])]}
                elif not line['leftvalue'] and not line['rightvalue']:
                        return None
                else:
                        if line['leftvalue']:
                                return getexpr(line['key'],line['leftvalue'])
                        else:
                                return getexpr(line['key'],line['rightvalue'])

        def readnotexpression(line):
                return {'$nor':[readexpression(line)]}

        def solveit(e1,e2,op):
                string = ''
                if op=='and':
                        string = '$and'
                elif op=='or':
                        string = '$or'
                else:
                        string = 'error'
                return {string:[e1,e2]}

        def solvetop():
                operator = relationstack.pop()
                expr1 = expressionstack.pop()
                expr2 = expressionstack.pop()
                expressionstack.append(solveit(expr1,expr2,operator))

        def readrelation(line):
                thislinerelation = ''
                if line['relation']=='not':
                        notflag[0] = True
                        thislinerelation = 'and'
                elif line['relation']=='and':
                        notflag[0] = False
                        thislinerelation = 'and'
                elif line['relation']=='or':
                        notflag[0] = False
                        thislinerelation = 'or'
                else:
                        return 'error'

                while relationstack and prioritymapping[relationstack[-1]]>=prioritymapping[thislinerelation]:
                        solvetop()

                return thislinerelation
        
        expressionstack.append(readexpression(mp[0]))
        #if expressionstack[-1]==None:
                #???
        for line in mp[1:]:
                relationstack.append(readrelation(line))
                if notflag[0]:
                        expressionstack.append(readnotexpression(line))
                else:
                        expressionstack.append(readexpression(line))
                if expressionstack[-1]==None:
                        expressionstack.pop()
                        relationstack.pop()
                #print line
                #print relationstack
                #print expressionstack

        while relationstack:
                solvetop()

        json = expressionstack.pop()
        return json

