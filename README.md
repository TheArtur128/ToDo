# ToDo
<details>
  <summary><h2>Desing</h2></summary>
  <img src="https://github.com/TheArtur128/ToDo/blob/main/images/design.webp"/>

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
