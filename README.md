# ToDo
<details>
  <summary><h2>Desing</h2></summary>
  <img src="https://github.com/TheArtur128/ToDo/blob/main/decor/design.webp"/>

## Legend
### Dependency types
- `A —> B` is a dependency of `A` on `B` when `A` knows about `B`
- `A --> B` is a dependency of `A` on `B` when `A` does not know about `B`

### Element types
- Elements from which dependency arrows come out and into are files</br>
- Elements in which files are nested are applications

`A` and `A contract` are the same file, but with the emphasis that changes occurring in files that `A` depends on will be suspended by introducing adaptation code to preserve the external behavior of `A`.</br>

## Dependencies between applications
From the outside of applications, all dependencies between applications are captured through `input` and `output` files, by committing all exported content of one application to others in that application's `output` file and importing this content from this file occurring in the `input` files of other applications.</br>

From within applications, all dependencies between applications are captured by splitting the imported content from `input` files into thematic files (`config`, `models`, `types`, `utils`).</br>

The exception is the `shared` application, which itself cannot import from other applications and whose files can be directly imported by other applications' `input` files.

</details>


<details>
  <summary><h2>Naming</h2></summary>

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

</details>


<details>
  <summary><h2>Priorities</h2></summary>

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
</details>
