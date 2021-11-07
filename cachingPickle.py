import os
import pickle
import json

from functools import reduce


class cache_handler(object):
    # instanciate object
    def __init__(self, cachefile, cache_mode=True):
        self.cachefile = cachefile  
        self.cache_mode=cache_mode

    def load_cache(self):
        """
        if cache exists load it and return its content
        otherwise it will create a new empty dictionary
        """
        if self.cache_mode == False: # caching was disabled
            cache={}
            return(cache) 
        # if cache exists load it and return its content
        if os.path.exists(self.cachefile):
            with open(self.cachefile, 'rb') as cachehandle:
                print("using cached results from '%s'" % self.cachefile)
                cache = pickle.load(cachehandle)
                return(cache)
        else:
            print('creating new caching object')
            cache={}
            return(cache)


    def check_cache(self, loaded_cache):
        """
        will check if keys are appears in the loaded cache.
        if keys exist it will return results from the cache otherwise will run he function and update the loaded cache.

        Note! this method will not save the cache into a new pickle file! make sure to use the 'store_cache_onDisk' method 
        input:
        - loaded_cache - the loaded cache object must be defined as global variable
        - cache_mode - if True, process will try to use caching, if False, will skip caching
        output:
        - return results from caching if exist
        - return the 
        """
        cm = self.cache_mode
        def decorator(fn):  # define a decorator for a function "fn"
            def wrapped(self, *args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments
                if  cm == False: # caching was disabled
                    res = fn(self, *args, **kwargs)
                    return(res)
                # adding the args into the kwargs
                cnt=0
                for i in args:
                    cnt += 1
                    kwargs[str('var'+ str(cnt))] = tuple(i)

                target_key = frozenset(kwargs.items())

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
        store the results into a pickle file
        input:
        - loaded_cache - a global variable dictionary to store as cache in a pickle file
        """
        if self.cache_mode == False:
            print('cache mode is off. file was not saved')
        # write to cache file
        with open(self.cachefile, 'wb') as cachehandle:
            print("saving result to cache '%s'" % self.cachefile)
            pickle.dump(loaded_cache, cachehandle)



    def cached(self):
        """
        A function that creates a decorator which will use "self.cachefile" for caching the results of the decorated function "fn".
        """
        cm = self.cache_mode
        def decorator(fn):  # define a decorator for a function "fn"
            def wrapped(*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments  
                if cm == False: # caching was disabled
                    res = fn(self, *args, **kwargs)
                    return(res) 
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