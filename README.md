# Desing
## Why
This application is educational and created in the following imaginary setting:
- Relatively large starting team
- Great need for speed in adding features
- Relatively heavy workload in the near future
- Relatively low availability requirement

Therefore the following decisions were taken:
- Dividing all features into areas as units of operation
- Isolating areas by allocating separate django applications for them (On average, one application per area or a maximum of 3)
- Isolating applications by fixing all dependencies between each other with special input (`lib` & `config`) and output (`output`) modules only through which application dependencies can pass
- Minimizing the use of client-server relationships by introducing generating front on the backed part
- Separation of general application and domain logic from the main part of the application by introducing cheap contracts (`cases` & `rules`)
- Separation of the periphery of representation formation from others (`ui`)
- Formation of stabilizing units of logic use (`services`)

In case of increasing complexity, it is necessary to divide applications into microservices, optionally combining them, forming an RPC API based on their output modules and separate libraries from common functionality.

After 30 applications, the transition is critical.

## Map
<img src="https://github.com/TheArtur128/ToDo/blob/main/decor/design.webp"/>

## Legend
### Dependency types
- `A —> B` is a dependency of `A` on `B` when `A` knows about `B`
- `A --> B` is a dependency of `A` on `B` when `A` does not know about `B`

### Element types
- Elements from which dependency arrows come out and into are files</br>
- Elements in which files are nested are applications

`A` and `A contract` are the same file, but with the emphasis that changes occurring in files that `A` depends on will be suspended by introducing adaptation code to preserve the external behavior of `A`.</br>

# Naming

Application verticals are identified by the same name, or a logically converted name for a specific element type in the corresponding layer files (`rules`, `cases`, `adapters`, `services`, `ui`):
```py
# rules
authorization = val(...)

# cases
def authorize(...): ...

# adapters
authorization = val(...)

# services
def authorized(...): ...

# ui
authorization = val(...)
```

For functions that create or receive a value, the name of that value should be an unfinished sentence in the name of the function so that it is still not confused with ordinary values:
```py
# Bad
create_user(email)
get_user(email)
user(email)


# Good
user_of(email)
```

If a function is a logical transition of a value from one type to another (can be represented as a procedure), then such a function must be named with an adjective (adjectival names for values are invalid):
```py
# Bad
user = authorize(user)
user = authorize(not_authorized)


# Good
user = authorized(user)


# Procedural form
assert authorize(user) is None
```

Values that are created using `class` syntax must be named as values, i.e. a noun in `snake_case`. Exception if this is a module and its name, together with the names of its functions/procedures, form the name of the functions/procedures:
```py
# Bad
@val
class Authorize:
    ...

@obj
class IsRegistred:
    ...


# Good
@val
class authorization:
    ...

@namespace
class registration_marks:
    ...

@obj
class send:
    via_email = ...  # send.via_email
    to_phone = ...  # send.to_phone
```

# Priorities

Use `type` and `struct` from the [`act`](https://github.com/TheArtur128/Act) library instead of `dataclass` if possible:
```py
# Bad
@dataclass
class Box:
    width: int
    height: int


# Good
Box = type(width=int, height=int)
```
