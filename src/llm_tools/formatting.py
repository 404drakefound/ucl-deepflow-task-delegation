def retry(func,times,*args,**kwargs):
    i=0
    while i<times:
        try:
            output=func(*args,**kwargs)
            break
        except Exception as e:
            print(e)
            i+=1
    if i<times:
        return output
    else:
        return None
    

if __name__=='__main__':
    def testfunc(num):
        import random
        if random.random()<0.5:
            1/0
        else:
            return "Good"+str(num)
        
    print(retry(testfunc,5,10))