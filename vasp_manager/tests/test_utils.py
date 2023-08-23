import json
from pathlib import Path

import importlib_resources
import numpy as np
from pymatgen.io.vasp import Poscar

from vasp_manager.utils import (
    NumpyEncoder,
    change_directory,
    get_pmg_structure_from_poscar,
    make_potcar_anonymous,
    pcat,
    pgrep,
    phead,
    ptail,
)

input_string = """DAV:   5    -0.677727844685E+01    0.16454E-04   -0.48875E-05  1776   0.450E-02    0.143E-02
DAV:   6    -0.677727668990E+01    0.17570E-05   -0.21379E-06   872   0.154E-02
   4 F= -.67772767E+01 E0= -.67772767E+01  d E =-.421689E-02
curvature:  -0.59 expect dE=-0.179E-04 dE for cont linesearch -0.179E-04
trial: gam= 0.00000 g(F)=  0.914E-61 g(S)=  0.301E-04 ort =-0.171E-03 (trialstep = 0.280E+01)
search vector abs. value=  0.301E-04
reached required accuracy - stopping structural energy minimisation
PROFILE, used timers:     369"""


def test_change_directory(tmp_path):
    with change_directory(tmp_path):
        assert Path.cwd().name == tmp_path.name


def test_numpy_encoder(tmp_path):
    data = {"array": np.linspace(0, 10, 11)}
    with open(tmp_path / "data.json", "w+") as fw:
        json.dump(data, fw, indent=2, cls=NumpyEncoder)


def test_pmg_structure(tmp_path):
    # symmetrized structure
    poscar_string = (
        importlib_resources.files("vasp_manager")
        .joinpath(
            str(Path("tests") / "calculations" / "material" / "rlx-coarse" / "POSCAR")
        )
        .read_text()
    )

    # original unsymmetrized structure
    orig_poscar_path = importlib_resources.files("vasp_manager").joinpath(
        str(Path("tests") / "calculations" / "material" / "POSCAR")
    )
    # symmetrize structure, write poscar, and compare
    symm_structure = get_pmg_structure_from_poscar(orig_poscar_path)
    poscar = Poscar(symm_structure)
    poscar_path = tmp_path / "POSCAR"
    poscar.write_file(poscar_path, significant_figures=8)
    with open(poscar_path, "r") as fr:
        symm_poscar_string = fr.read()
    print(poscar_string)
    print(symm_poscar_string)
    assert poscar_string == symm_poscar_string


def test_pcat(tmp_path):
    test_file = tmp_path / "pcat.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    cat_output = pcat(test_file)
    assert cat_output == input_string


def test_pgrep(tmp_path):
    test_file = tmp_path / "pcat.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    grep_output = pgrep(test_file, "DAV")
    assert len(grep_output) == 2
    grep_output_as_string = "\n".join([line for line in grep_output])
    matching_lines = "\n".join([line.strip() for line in input_string.split("\n")[:2]])
    assert grep_output_as_string == matching_lines


def test_pgrep_as_string(tmp_path):
    test_file = tmp_path / "pcat.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    grep_output_as_string = pgrep(test_file, "DAV", as_string=True)
    matching_lines = "\n".join([line.strip() for line in input_string.split("\n")[:2]])
    assert grep_output_as_string == matching_lines


def test_phead(tmp_path):
    test_file = tmp_path / "phead.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    n_lines = 2
    head_output = phead(test_file, n_head=n_lines)
    assert len(head_output) == 2
    head_output_as_string = "\n".join([line for line in head_output])
    matching_lines = "\n".join(
        [line.strip() for line in input_string.split("\n")[:n_lines]]
    )
    assert head_output_as_string == matching_lines


def test_phead_as_string(tmp_path):
    test_file = tmp_path / "pcat.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    head_output_as_string = pgrep(test_file, "DAV", as_string=True)
    matching_lines = "\n".join([line.strip() for line in input_string.split("\n")[:2]])
    assert head_output_as_string == matching_lines


def test_ptail(tmp_path):
    test_file = tmp_path / "ptail.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    n_lines = 2
    tail_output = ptail(test_file, n_tail=n_lines)
    assert len(tail_output) == 2
    tail_output_as_string = "\n".join([line for line in tail_output])
    matching_lines = "\n".join(
        [line.strip() for line in input_string.split("\n")[-n_lines:]]
    )
    assert tail_output_as_string == matching_lines


def test_ptail_as_string(tmp_path):
    test_file = tmp_path / "ptail.txt"
    with open(test_file, "w+") as fw:
        fw.write(input_string)
    n_lines = 2
    tail_output_as_string = ptail(test_file, n_tail=n_lines, as_string=True)
    matching_lines = "\n".join(
        [line.strip() for line in input_string.split("\n")[-n_lines:]]
    )
    assert tail_output_as_string == matching_lines
