# laser-prynter

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tmck-code/laser-prynter/ruff.yml)
![PyPI - Version](https://img.shields.io/pypi/v/laser-prynter)

terminal/cli/python helpers for colour and pretty-printing

- [laser-prynter](#laser-prynter)
  - [`laser_prynter`](#laser_prynter)
  - [`pbar`](#pbar)
  - [`bench`](#bench)

---

## `laser_prynter`


https://github.com/user-attachments/assets/cce8f690-e411-459f-a04f-8e9bef533e4a


---

## `pbar`

https://github.com/user-attachments/assets/8a2c2d99-1a11-4f9f-ac6a-8153f67e21c3

```python
from laser_prynter import pbar
with pbar(100) as bar:
    for i in range(100):
        # do something
        bar.update()
```

---

## `bench`


https://github.com/user-attachments/assets/4af823b0-8d18-4086-9754-c76c65b66898


```python
from laser_prynter import bench

bench.bench(
    tests=[
        (
            (range(2),), # args
            {},          # kwargs
            [0,1],       # expected
        )
    ],
    func_groups=[ [list] ],
    n=100
)
```
