import io
from PIL import Image
from app.anonymization.image_redactor import DocxImageRedactor

def test_contextual_docx_image_redactor():
    replacement_map = {
        ("ORGANIZATION", "Karthik and Thanush"): "Maharajan Tech",
        ("ORGANIZATION", "ICICI Securities Limited"): "Apex Capital Limited",
    }
    redactor = DocxImageRedactor(replacement_map)

    assert redactor.get_initials("Maharajan Tech") == "MT"
    assert redactor.get_initials("Apex Capital Limited") == "AC"
    assert redactor.get_initials("Karthik and Thanush") == "KT"

    # Create dummy image
    img = Image.new("RGBA", (200, 100), (255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    original_bytes = buf.getvalue()

    redacted_mt = redactor.generate_logo_bytes(original_bytes, "image/png", "Maharajan Tech")
    assert redacted_mt is not None
    assert len(redacted_mt) > 0

    redacted_ac = redactor.generate_logo_bytes(original_bytes, "image/png", "Apex Capital Limited")
    assert redacted_ac is not None
    assert len(redacted_ac) > 0

    # Ensure distinct logo image blobs for distinct companies
    assert redacted_mt != redacted_ac
