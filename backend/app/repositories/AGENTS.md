# Repository

## Method Naming

* Prefix methods with `find_` when looking up an entity that may not exist. These methods may return `None`.
* Prefix methods with `get_` when retrieving an entity that is expected to exist. These methods must raise an exception if the entity is not found.
