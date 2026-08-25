"""Tests for the darkside component widgets."""
from mapper.widgets.components import (
    DsChip,
    DsPagination,
    DsProgress,
    DsSegmented,
    DsSlider,
    DsSpinner,
    DsStepper,
    DsSwitch,
    DsTextField,
)


def _render(widget):
    widget.refresh()
    return widget.render()


def test_switch_default_renders_on_off():
    w = DsSwitch(value=True)
    text = _render(w)
    assert "on" in text.plain
    assert "off" in text.plain


def test_stepper_default_renders_value_and_affordances():
    w = DsStepper(value=3)
    text = _render(w)
    assert "3" in text.plain
    assert "-" in text.plain
    assert "+" in text.plain


def test_slider_default_renders_track_and_handle():
    w = DsSlider(value=0.5, width=10)
    text = _render(w)
    assert "▮" in text.plain


def test_segmented_default_renders_options():
    w = DsSegmented(["a", "b"], active=0)
    text = _render(w)
    assert "a" in text.plain
    assert "b" in text.plain


def test_progress_renders_meter():
    w = DsProgress(filled=3, total=5)
    text = _render(w)
    assert text.plain == "▰▰▰▱▱"


def test_spinner_renders_braille_frame():
    w = DsSpinner(frame=0, label="cargando")
    text = _render(w)
    assert "cargando" in text.plain


def test_text_field_default_renders_value():
    w = DsTextField(value="sistema-leg")
    text = _render(w)
    assert "sistema-leg" in text.plain


def test_pagination_renders_page_total():
    w = DsPagination(page=2, total=5)
    text = _render(w)
    assert "2/5" in text.plain


def test_chip_renders_name():
    w = DsChip(label="legacy")
    text = _render(w)
    assert "legacy" in text.plain


def test_disabled_text_sinks_to_wordmark():
    w = DsTextField(value="x", disabled=True)
    text = _render(w)
    assert "x" in text.plain
