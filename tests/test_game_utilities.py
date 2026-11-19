import pytest
from PIL import Image, features

from buzzinga.game_utilities import count_round_files, load_image

from conftest import write_image


@pytest.mark.skipif(not features.check("avif"), reason="Pillow built without AVIF support")
def test_load_image_reads_formats_pygame_cannot(tmp_path):
    Image.new("RGB", (40, 30), (0, 200, 0)).save(tmp_path / "Bild.avif")

    assert load_image("Bild.avif", str(tmp_path)).get_size() == (40, 30)


def test_load_image_raises_for_unreadable_files(tmp_path):
    (tmp_path / "Kaputt.png").write_bytes(b"not an image")

    with pytest.raises(FileNotFoundError):
        load_image("Kaputt.png", str(tmp_path))


def test_count_round_files_skips_solutions_and_other_types(tmp_path):
    write_image(tmp_path / "A.PNG")
    write_image(tmp_path / "A_solution.png")
    (tmp_path / "B.txt").write_bytes(b"")
    (tmp_path / "C.png").mkdir()

    assert count_round_files(tmp_path, (".png",)) == 1
