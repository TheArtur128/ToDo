## Deployment
To deploy this application locally:
- clone this repository
- optionally populate a `.env` file based on the `.env.template` file, or set the appropriate environment variables
- run within `docker`
```
git clone https://github.com/TheArtur128/ToDo.git
docker compose --project-directory ./ToDo up
```

## Desing

> This application is educational and created in the imaginary setting.

### Why
- Starting team of 15-20 people with permanent hiring
- Great need for speed in adding features
- Inconsistent workload in the near future
- Low fault-tolerance requirement at the start
- Low availability requirement at the start

### So
- Dividing all features into areas as units of operation
- Isolating areas by allocating separate django applications for them (On average, one application per area or a maximum of 3)
- Isolating applications by fixing all dependencies between each other with special input (`lib`) and output (`output`) modules only through which application dependencies can pass
- Minimizing the use of client-server relationships by introducing generating front on the backed part
- Separation of the UI periphery (`ui`) from the transport periphery (django `views` / `http`)
- Separation of general application and domain logic from the main part of applications by introducing contract modules (`cases` & `rules`) and implementation modules (`services` & `repos` & `event_buses`) for them
- Formation of stable and smaller modules (`controllers`) for logic use
- Splitting applications into microservices after 30 applications or when an inconsistent workload occurs.

Once separation begins, the original monolithic application becomes the `main` microservice.

The division is made in the following steps:
1. Complete removal of the `adapters` and `core` layers of the desired application into its microservice
2. Partial removal of the `ui` module into the microservice according to its implementation module actor
3. Optionally create/supplement a library of common functionality between microservices
4. Based on the `output` interface of the module and the actors that include the `views` module of the original application create RPC and RESTful APIs for the microservice used [FastAPI](https://github.com/tiangolo/fastapi) and implement eventing by using RabbitMQ and [FastStream](https://github.com/airtai/faststream) for it.
5. Change dependent applications of the `main` microservice so that they use APIs and message broker of the new microservice.

After separating all applications of the `main` microservice into separate microservices, it becomes the `front` microservice.

### Application structure map
<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://github.com/TheArtur128/ToDo/blob/main/assets/application-structure-map/dark-theme.png">
 <img src="https://github.com/TheArtur128/ToDo/blob/main/assets/application-structure-map/light-theme.png">
</picture>

#### Dependency types
- `A —> B` is a dependency between `A` and `B` when `A` uses `B`
- `A --> B` is a dependency between `A` and `B` when `A` implements protocols used by `B`

#### Element types
- Elements from which dependency arrows come out and into are modules
- Elements in which modules are nested are layers
- Elements in which layers are nested are applications

Modules nested within applications are global modules.

`Shared app` is a special application with an arbitrary structure that has no dependencies on other applications.</br>
All modules of this application are `output` modules.

### Application relationship map
<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://github.com/TheArtur128/ToDo/blob/main/assets/application-relationship-map/dark-theme.png">
 <img src="https://github.com/TheArtur128/ToDo/blob/main/assets/application-relationship-map/light-theme.png">
</picture>

#### Dependency types
- `A —> B` is a dependency between `A` and `B` when `A`'s `lib` module uses `B`'s `output` modules
- `A --> B` is a dependency between `A` and `B` when `A` reads a message from the local message bus sent by `B`

## Naming

Application verticals are identified by the same name, or a logically converted name for a specific element type in corresponding layers (`core`, `adapters`, `presentation`):
```py
authorization = val(...)  # rules

def authorize(...): ...  # cases

authorization = val(...)  # services

def authorized(...): ...  # controllers

authorization = val(...)  # ui
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

## Priorities

Use `type` and `struct` from the [act](https://github.com/TheArtur128/Act) library instead of `dataclass` if possible:
```py
# Bad
@dataclass
class Box:
    width: int
    height: int


# Good
Box = type(width=int, height=int)
```
