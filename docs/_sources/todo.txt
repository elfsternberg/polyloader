Currently assumes that Polyloaders last for the lifetime of the Python
instance.  There is no standardized mechanism for removing a
compiler/suffix set from a running instance.

1. Create a standardized mechanism for removing a compiler/suffix from
   the running instance.

2. Create a 'with' context manager that creates a scope in which a
   Polyloader compiler/suffix pair is active, and automatically removes
   that pair upon leaving the scope.   
