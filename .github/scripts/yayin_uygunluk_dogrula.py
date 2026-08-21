from __future__ import annotations

from pathlib import Path
import re


KOK = Path(__file__).resolve().parents[2]

SAYFALAR = {
    "gizlilik": (
        KOK
        / "site-yonetimi"
        / "gizlilik-politikasi"
        / "index.html"
    ),
    "silme": (
        KOK
        / "site-yonetimi"
        / "hesap-ve-veri-silme"
        / "index.html"
    ),
    "kosullar": (
        KOK
        / "site-yonetimi"
        / "kullanim-kosullari"
        / "index.html"
    ),
    "destek": (
        KOK
        / "site-yonetimi"
        / "destek"
        / "index.html"
    ),
}

PLACEHOLDERLAR = (
    "YAYIN_ONCESI_",
    "TODO",
    "TBD",
    "PLACEHOLDER",
)

EPOSTA_DESENI = re.compile(
    r"[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\."
    r"[A-Za-z]{2,}"
)


def oku(yol: Path) -> str:
    if not yol.is_file():
        raise AssertionError(
            f"Eksik sayfa: {yol.relative_to(KOK)}"
        )

    return yol.read_text(
        encoding="utf-8",
        errors="strict",
    )


def ifade_zorunlu(
    metin: str,
    ifadeler: tuple[str, ...],
    sayfa: str,
) -> None:
    for ifade in ifadeler:
        if ifade not in metin:
            raise AssertionError(
                f"{sayfa}: zorunlu ifade eksik: "
                f"{ifade}"
            )


def main() -> None:
    metinler = {
        ad: oku(yol)
        for ad, yol in SAYFALAR.items()
    }

    tum = "\n".join(
        metinler.values()
    )

    for placeholder in PLACEHOLDERLAR:
        if placeholder in tum:
            raise AssertionError(
                "Yayin oncesi placeholder bulundu: "
                f"{placeholder}"
            )

    epostalar = EPOSTA_DESENI.findall(
        tum
    )

    if not epostalar:
        raise AssertionError(
            "Yayin icin destek e-postasi bulunamadi."
        )

    gizlilik = metinler["gizlilik"]

    ifade_zorunlu(
        gizlilik,
        (
            "Site Yönetimi",
            "Gizlilik Politikası",
            "İşlenebilecek bilgiler",
            "Kullanım amaçları",
            "Güvenlik",
            "Saklama ve silme",
            "İletişim",
        ),
        "Gizlilik Politikasi",
    )

    silme = metinler["silme"]

    ifade_zorunlu(
        silme,
        (
            "Site Yönetimi",
            "Hesap ve Veri Silme",
            "Silme talebi",
            "Kimlik doğrulama",
            "Silinecek veriler",
        ),
        "Hesap ve Veri Silme",
    )

    kosullar = metinler["kosullar"]

    ifade_zorunlu(
        kosullar,
        (
            "Site Yönetimi",
            "Kullanım Koşulları",
            "Kullanıcı sorumluluğu",
            "Yetkisiz kullanım",
        ),
        "Kullanim Kosullari",
    )

    destek = metinler["destek"]

    ifade_zorunlu(
        destek,
        (
            "Site Yönetimi",
            "Destek",
            "Destek kapsamı",
        ),
        "Destek",
    )

    print(
        "GREEN: Yayin placeholder'i yok."
    )
    print(
        "GREEN: Destek e-postasi mevcut."
    )
    print(
        "GREEN: Gizlilik Politikasi zorunlu "
        "bolumleri mevcut."
    )
    print(
        "GREEN: Hesap ve Veri Silme zorunlu "
        "bolumleri mevcut."
    )
    print(
        "GREEN: Kullanim Kosullari zorunlu "
        "bolumleri mevcut."
    )
    print(
        "GREEN: Destek sayfasi zorunlu "
        "bolumleri mevcut."
    )


if __name__ == "__main__":
    main()
