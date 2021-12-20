# safe_app

Opis projektu:
Aplikacja pozwala zalogowanemu użytkownikowi na przechowywanie notatek tekstowych. Niektóre notatki mogą być zaznaczone jako zaszyfrowane. Odszyfrowanie powinno wymagać podania tajnego hasła.

Użytkownik powinien móc się zarejestrować i zalogować za pomocą hasła.
Aplikacja pozwala na udostępnienie innym użytkownikom wybranych notatek (nieszyfrowanych). Dopuszczane są dwa rozwiązania:

    notatki udostępnione wybranym użytkownikom,
    notatki udostępnione publicznie.

Notatki powinny pozwalać na podstawowe ostylowanie, co najmniej: dodanie pogrubienia wybranego słowa, dodanie pochylenia wybranego słowa, dodanie nagłówku o wybranym poziomie (1-5).

Moduł uwierzytelniania powinien zakładać:

    walidację danych wejściowych (z negatywnym nastawieniem),
    opóźnienia i limity prób (żeby utrudnić zdalne zgadywanie i atak brute-force),
    ograniczone informowanie o błędach (np. o tym przyczynie odmowy uwierzytelenia),
    bezpieczne przechowywanie hasła (wykorzystanie kryptograficznych funcji mieszających, wykorzystanie soli, wielokrotne hashowanie)
    kontrola siły hasła, żeby uświadomić użytkownikowi problem
    monitorowanie pracy systemu (np. żeby poinformować użytkownika o nowych komputerach, które łączyły się z jego kontem)
    zarządzanie uprawnieniami do zasobów.

Na koniec należy przygotować krótką prezentację (5 min.). Kod musi zostać udostępniony do wglądu prowadzącemu przed prezentacją. Prezentacja może zawierać jako ostatni slajd bibliografię.

Wymagania:

    aplikacja posiada bazę danych (SQL, może być SQLite),
    bezpieczne połączenie z aplikacją (szyfrowane połączenie),
    wszystkie dane wejściowe od użytkownika podlegają walidacji z negatywnym nastawieniem,
    weryfikacja liczby nieudanych prób logowania,
    sprawdzanie jakości hasła (np. jego entropii),
    dodać opóźnienie podczas logowania,
    wykorzystując szkielet aplikacji (czy moduł) należy dokładnie wiedzieć jak jest on zaimplementowany.

Elementy dodatkowe (pożądane):

    skonteneryzowanie przy pomocą Docker
    $ docker-compose up lub $ sh run-docker.sh
    zabezpieczenie przeciwko Cross-Site Request Forgery (żetony CSRF/XSRF),
    możliwość odzyskania dostępu w przypadku utraty hasła:
    Użytkownik poprosił o zmianę hasła, wysłałbym mu link: ......
    na adres e-mail: .....
    informowanie użytkownika o nowych podłączeniach do jego konta,
    zostawienie honeypots,
    mechanizm Content-Security-Policy,
    wyłączenie nagłówka Server.
