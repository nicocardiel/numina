

import pytest

from ..cli import main


drpdata = """
    name: FAKE
    configurations:
        default: {}
    modes:
        - description: A recipe that always fails
          key: fail
          name: Fail
          tagger:
             - KEY1
             - KEY2
        - description: Bias
          key: bias
          name: Bias
          tagger:
             - KEY3
    pipelines:
        default:
            recipes:
                bias: fake.recipes.BiasRecipe
                fail: numina.core.utils.AlwaysFailRecipe
            version: 1
"""

drpdata2 = """
    name: FAKE2
    configurations:
        default: {}
    modes:
        - description: A recipe that always fails
          key: fail
          name: Fail
          tagger:
             - KEY1
             - KEY2
        - description: Bias
          key: bias
          name: Bias
          tagger:
             - KEY3
    pipelines:
        default:
            recipes:
                bias: fake.recipes.BiasRecipe
                fail: numina.core.utils.AlwaysFailRecipe
            version: 1
"""


def test_show_instrument(capsys, drpmocker):
    """Test that one instrumenst is shown"""
    drpmocker.add_drp('fake', drpdata)

    expected = ("Instrument: FAKE\n"
                " has configuration 'default'\n"
                " has pipeline 'default', version 1\n"
                )

    main(['show-instruments'])

    out, err = capsys.readouterr()
    assert out == expected


def test_show_2_instruments(capsys, drpmocker):
    """Test that two instruments are shown"""

    # FIXME: probably instruments can be output in any order
    drpmocker.add_drp('fake', drpdata)
    drpmocker.add_drp('fake2', drpdata2)

    expected = ["Instrument: FAKE2",
                " has configuration 'default'",
                " has pipeline 'default', version 1",
                "Instrument: FAKE",
                " has configuration 'default'",
                " has pipeline 'default', version 1",
                ""
                ]

    main(['show-instruments'])

    out, err = capsys.readouterr()
    out = out.split("\n")
    assert out == expected


@pytest.mark.usefixtures("drpmocker")
def test_show_no_instrument(capsys):
    """Test that no instruments are shown"""
    expected = ""

    main(['show-instruments'])

    out, err = capsys.readouterr()
    assert out == expected
