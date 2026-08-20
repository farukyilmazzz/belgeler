from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


KOK = Path(__file__).resolve().parents[2]

UYGULAMA = KOK / "site-yonetimi"

SAYFALAR = (
    UYGULAMA / "index.html",
    UYGULAMA / "gizlilik-politikasi" / "index.html",
    UYGULAMA / "hesap-ve-veri-silme" / "index.html",
    UYGULAMA / "kullanim-kosullari" / "index.html",
    UYGULAMA / "destek" / "index.html",
)

BEKLENEN_NAV_METINLERI = {
    "Belgeler",
    "Gizlilik Politikası",
    "Hesap ve Veri Silme",
    "Kullanım Koşulları",
    "Destek",
}


class SayfaCozumleyici(HTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.title_sayisi = 0
        self.h1_sayisi = 0
        self.viewport_var = False

        self.nav_derinligi = 0
        self.nav_linkleri: list[
            tuple[str, str, bool]
        ] = []

        self.css_hrefleri: list[str] = []

        self._aktif_link_href: str | None = None
        self._aktif_link_current = False
        self._aktif_link_metinleri: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[
            tuple[str, str | None]
        ],
    ) -> None:
        degerler = dict(attrs)

        if tag == "title":
            self.title_sayisi += 1

        if tag == "h1":
            self.h1_sayisi += 1

        if tag == "meta":
            if (
                degerler.get("name") == "viewport"
                and "width=device-width"
                in (
                    degerler.get("content")
                    or ""
                )
            ):
                self.viewport_var = True

        if (
            tag == "nav"
            and degerler.get("class") == "nav"
        ):
            self.nav_derinligi += 1

        if (
            tag == "a"
            and self.nav_derinligi > 0
        ):
            self._aktif_link_href = (
                degerler.get("href")
            )
            self._aktif_link_current = (
                degerler.get("aria-current")
                == "page"
            )
            self._aktif_link_metinleri = []

        if tag == "link":
            if degerler.get("rel") == "stylesheet":
                href = degerler.get("href")
                if href:
                    self.css_hrefleri.append(href)

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self._aktif_link_href is not None:
            self._aktif_link_metinleri.append(
                data
            )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        if (
            tag == "a"
            and self._aktif_link_href is not None
        ):
            metin = " ".join(
                "".join(
                    self._aktif_link_metinleri
                ).split()
            )

            self.nav_linkleri.append(
                (
                    metin,
                    self._aktif_link_href,
                    self._aktif_link_current,
                )
            )

            self._aktif_link_href = None
            self._aktif_link_current = False
            self._aktif_link_metinleri = []

        if (
            tag == "nav"
            and self.nav_derinligi > 0
        ):
            self.nav_derinligi -= 1


def yerel_hedef(
    sayfa: Path,
    href: str,
) -> Path | None:
    ayrik = urlparse(href)

    if ayrik.scheme or ayrik.netloc:
        return None

    yol = ayrik.path

    if not yol:
        return sayfa

    hedef = (
        sayfa.parent
        / yol
    ).resolve()

    if yol.endswith("/"):
        hedef = hedef / "index.html"

    return hedef


def sayfayi_dogrula(
    sayfa: Path,
) -> None:
    if not sayfa.is_file():
        raise AssertionError(
            f"Eksik sayfa: "
            f"{sayfa.relative_to(KOK)}"
        )

    metin = sayfa.read_text(
        encoding="utf-8",
        errors="strict",
    )

    parser = SayfaCozumleyici()
    parser.feed(metin)

    if parser.title_sayisi != 1:
        raise AssertionError(
            f"{sayfa}: tek title olmali."
        )

    if parser.h1_sayisi != 1:
        raise AssertionError(
            f"{sayfa}: tek h1 olmali."
        )

    if not parser.viewport_var:
        raise AssertionError(
            f"{sayfa}: mobil viewport eksik."
        )

    nav_metinleri = {
        metin
        for metin, _, _
        in parser.nav_linkleri
    }

    if nav_metinleri != BEKLENEN_NAV_METINLERI:
        raise AssertionError(
            f"{sayfa}: belge menusu eksik "
            "veya beklenmeyen oge iceriyor."
        )

    if len(parser.nav_linkleri) != 5:
        raise AssertionError(
            f"{sayfa}: tam 5 belge "
            "navigasyon linki olmali."
        )

    aktif_sayisi = sum(
        1
        for _, _, aktif
        in parser.nav_linkleri
        if aktif
    )

    if aktif_sayisi != 1:
        raise AssertionError(
            f"{sayfa}: tam bir aktif "
            "menu ogesi olmali."
        )

    for _, href, _ in parser.nav_linkleri:
        hedef = yerel_hedef(
            sayfa,
            href,
        )

        if (
            hedef is not None
            and not hedef.is_file()
        ):
            raise AssertionError(
                f"{sayfa}: kirik navigasyon "
                f"linki: {href} -> {hedef}"
            )

    if len(parser.css_hrefleri) != 1:
        raise AssertionError(
            f"{sayfa}: tam bir ortak CSS "
            "baglantisi olmali."
        )

    css = yerel_hedef(
        sayfa,
        parser.css_hrefleri[0],
    )

    if css is None or not css.is_file():
        raise AssertionError(
            f"{sayfa}: ortak CSS "
            "baglantisi kirik."
        )


def main() -> None:
    style = (
        KOK
        / "ortak"
        / "style.css"
    )

    if not style.is_file():
        raise AssertionError(
            "ortak/style.css bulunamadi."
        )

    for sayfa in SAYFALAR:
        sayfayi_dogrula(
            sayfa
        )

    print(
        "GREEN: 5 kamu sayfasi mevcut."
    )
    print(
        "GREEN: Her sayfada title ve h1 mevcut."
    )
    print(
        "GREEN: Mobil viewport mevcut."
    )
    print(
        "GREEN: Her sayfada 5'li ortak menu mevcut."
    )
    print(
        "GREEN: Her sayfada tek aktif menu ogesi mevcut."
    )
    print(
        "GREEN: Navigasyon linkleri kirik degil."
    )
    print(
        "GREEN: Ortak CSS baglantilari gecerli."
    )


if __name__ == "__main__":
    main()
