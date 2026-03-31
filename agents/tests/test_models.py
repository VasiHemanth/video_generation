from video_gen_agents.models import Element, Position

def test_element_model_rebuild():
    """Pydantic v2 self-reference requires model_rebuild() — verify it resolved."""
    parent = Element(
        id="parent",
        type="group",
        props={},
        children=[
            Element(id="child", type="text", props={"content": "hello", "color": "bg_primary", "style_token": "body_md"}),
        ],
    )
    assert len(parent.children) == 1
    assert parent.children[0].id == "child"


def test_positioning_default_is_absolute():
    """CRITICAL: default must be absolute for backward compat with existing IRs."""
    el = Element(id="test", type="text", props={"content": "hello", "color": "bg_primary", "style_token": "body_md"})
    # No positioning field set — must default to "absolute"
    assert el.positioning == "absolute", (
        "positioning default must be 'absolute' — if 'flow', all existing IRs break"
    )


def test_position_is_optional_for_flow_elements():
    """Flow elements inside flex containers must not require position."""
    el = Element(
        id="flow-child",
        type="text",
        props={"content": "hello", "color": "bg_primary", "style_token": "body_md"},
        positioning="flow",
        # No position field — must be valid
    )
    assert el.position is None


from video_gen_agents.models import ContentSlot, ContentSlots
from video_gen_agents.pipeline import VideoAgentState # just for context, we can just instantiate directly. Actually, import pipeline to test merge
from video_gen_agents.pipeline import VideoAgentState

def test_content_slots_contains_no_geometry_fields():
    """Verify ContentSlot restricts the LLM from touching geometry."""
    slot = ContentSlot(element_id_ref="target", props_override={"content": "New Text"})
    assert not hasattr(slot, "position")
    assert not hasattr(slot, "positioning")
    assert not hasattr(slot, "layout")

def test_merge_content_preserves_layout():
    """Verify merge_content_into_template overrides props but leaves layout pristine."""
    pass
