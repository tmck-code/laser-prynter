#!/usr/bin/env python3

from pprint_ndjson.colour import c, gradient

for i in range(16, 232):
    cell = c.from_ansi(i)
    print(f'{i:3d} {str(cell.rgb):>16s}', cell.colorise(' '*8))

print('\n'+'~'*80+'\n')

coll = gradient.RGBCubeCollection({
    'bgr': gradient.RGBCube.from_ranges('b', 'g', 'r'),
    'rgb': gradient.RGBCube.from_ranges('r', 'g', 'b'),
    'grb': gradient.RGBCube.from_ranges('g', 'r', 'b'),
})
coll.print(padding_top=0, padding_bottom=1, cell_width=15)

for k in ('rgb', 'grb', 'bgr'):
    print('\n'+'~'*80+'\n'+k)
    for rot in range(4):
        f1 = coll.cubes[k].faces.faces[0][0].rot90(rot, flip=True)
        f1.print(padding_top=0, padding_bottom=1, cell_width=15)
        print()

        gradient.create_cube(
            f1=f1,
            f1_name=k,
            cube_collection=coll
        )
        input()
