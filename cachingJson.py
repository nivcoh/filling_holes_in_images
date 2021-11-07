import os
import pickle
import json

from functools import reduce



class cache_handler(object):
    # instanciate object
    def __init__(self, cachefile):
        self.cachefile = cachefile  

        
    def load_cache(self):
        """
        if cache exists load it and return its content
        otherwise it will create a new empty dictionary
        """
        # if cache exists load it and return its content
        if os.path.exists(self.cachefile):
            # Opening JSON file 
            with open(self.cachefile,'rb') as cachehandle: 
                print("using cached result from '%s'" % self.cachefile)
                cache = json.load(cachehandle) 
                return(cache)
        else:
            print('creating new caching object')
            cache={}
            return(cache)


    def check_cache(self, loaded_cache):
        """
        will check if keys are appears in the loaded cache.
        if keys exist it will return results from the cache otherwise will run he function and update the loaded cache.

        Note! this method will not save the cache into a new json file! make sure to use the 'store_cache_onDisk' method 
        input:
        - loaded_cache - the loaded cache object must be defined as global variable
        output:
        - return results from caching if exist
        - return the 
        """
        def decorator(fn):  # define a decorator for a function "fn"
            def wrapped(self,*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments
                # adding the args into the kwargs
                cnt=0
                for i in args:
                    cnt += 1
                    kwargs[str('var'+ str(cnt))] = tuple(i)

                target_key = str(frozenset(kwargs.items()))

                if target_key in loaded_cache:
                    return(loaded_cache[target_key])

                # target key was not found - execute the function with all arguments passed
                res = fn(self, *args, **kwargs)
                loaded_cache[target_key] = res # updateting global dictionary (cache)
                return(res)
            
            return(wrapped)

        return(decorator)  # return this "customized" decorator that uses "self.cachefile"

    def store_cache_onDisk(self, loaded_cache):
        """
        store the results into a json file
        input:
        - loaded_cache - a global variable dictionary to store as cache in a json file
        """
        # write to cache file
        with open(self.cachefile, 'w') as fp:
            json.dump(loaded_cache, fp)



    def cached(self):
        """
        A function that creates a decorator which will use "self.cachefile" for caching the results of the decorated function "fn".
        """
        def decorator(fn):  # define a decorator for a function "fn"
            def wrapped(*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments   
                target_key = kwargs
                target_key = frozenset(target_key.items())
                print(target_key)   
                # if cache exists load it and return its content
                if os.path.exists(self.cachefile):
                        with open(self.cachefile, 'rb') as cachehandle:
                            print("using cached result from '%s'" % self.cachefile)
                            cache = pickle.load(cachehandle)
                            if target_key in cache:
                                return(cache[target_key])
                else:
                    cache={}

                # execute the function with all arguments passed
                res = fn(*args, **kwargs)
                cache[target_key] = res
                # write to cache file
                with open(self.cachefile, 'wb') as cachehandle:
                    print("saving result to cache '%s'" % self.cachefile)
                    pickle.dump(cache, cachehandle)

                return(res)

            return(wrapped)

        return(decorator)  # return this "customized" decorator that uses "self.cachefile"