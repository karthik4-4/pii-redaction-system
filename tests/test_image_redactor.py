import io
from PIL import Image
from app.anonymization.image_redactor import DocxImageRedactor

def test_docx_image_redactor():
    replacement_map = {
        ("ORGANIZATION", "Karthik and Thanush"): "Maharajan Tech",
    }
    redactor = DocxImageRedactor(replacement_map)

    assert redactor.orig_initials == "KT"
    assert redactor.syn_initials == "MT"

    # Create dummy original logo image
    img = Image.new("RGBA", (200, 100), (255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    original_bytes = buf.getvalue()

    redacted_bytes = redactor.redact_image_bytes(original_bytes, "image/png")
    assert redacted_bytes is not None
    assert len(redacted_bytes) > 0

    redacted_img = Image.open(io.BytesIO(redacted_bytes))
    assert redacted_img.size == (200, 100)
